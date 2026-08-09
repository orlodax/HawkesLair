"""
WordPress WXR  ->  Hugo page bundles.

Reads the export, cleans 22 years of accumulated editor markup, converts to
Markdown, and writes content/posts/<year>/<slug>/index.md. Images are not
downloaded here — they are recorded in images.json for fetch_images.py, so the
slow network step can be re-run without redoing the conversion.

    python convert.py [--limit N] [--dry-run]
"""

from __future__ import annotations

import argparse
import base64
import collections
import html
import json
import mimetypes
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, Comment, NavigableString
from markdownify import MarkdownConverter

ROOT      = Path(__file__).resolve().parents[2]
WXR       = ROOT / "WXRexport.xml"
CONTENT   = ROOT / "content"
TOOLDIR   = Path(__file__).resolve().parent
REPORT    = TOOLDIR / "report"
MANIFEST  = TOOLDIR / "images.json"
DEADFILE  = TOOLDIR / "dead_images.json"      # optional, produced by wayback probe

NS = {
    "wp":      "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "dc":      "http://purl.org/dc/elements/1.1/",
}

# Category -> (series name, layout). The fiction serials were filed by
# category rather than tagged, so this is the only place the mapping exists.
SERIES_BY_CATEGORY = {
    "MS I - Capitoli":          "Menti Selvagge",
    "MS II - Capitoli":         "Il ritorno dei Ra'Hesh",
    "Scynt - Capitoli":         "Scynt",
    "Viaggi mentali - Episodi": "Viaggi Mentali",
}

# Categories that are organisational noise rather than subjects.
DROP_CATEGORIES = {"Uncategorized"}

# WordPress' auto-generated privacy page is boilerplate describing comment
# forms, Gravatar and login cookies — none of which exist on a static site.
# It is replaced by a hand-written content/privacy/index.md; skip it so a
# re-run does not resurrect the template.
SKIP_SLUGS = {"privacy-policy-2"}

NOTE_MAX_CHARS  = 600     # below this, a post renders in full on the index
PHOTO_MIN_IMGS  = 2
PHOTO_MAX_CHARS = 1200

BLOCK_TAGS = (
    "table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li"
    "|pre|form|map|area|blockquote|address|math|style|p|h[1-6]|hr|fieldset|legend"
    "|section|article|aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary"
)

# Attributes that carry 2006-era styling and nothing else.
STRIP_ATTRS = {"style", "class", "id", "dir", "align", "border", "cellpadding",
               "cellspacing", "valign", "bgcolor", "color", "face", "size",
               "hspace", "vspace", "data-mce-src", "data-mce-style", "srcset",
               "sizes", "loading", "decoding", "onclick", "target", "rel"}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def slugify(text: str, maxlen: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[’'`]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > maxlen:
        text = text[:maxlen].rsplit("-", 1)[0]
    return text or "post"


def wpautop(text: str) -> str:
    """Reimplementation of WordPress's wpautop.

    WP stores post bodies without <p> tags and inserts them at render time.
    203 of the 466 posts here rely on that, so skipping this step collapses
    them into a single unbroken blob.
    """
    if not text.strip():
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"<br\s*/?>\s*<br\s*/?>", "\n\n", text, flags=re.I)
    text = re.sub(r"(<(?:" + BLOCK_TAGS + r")\b[^>]*>)", r"\n\n\1", text, flags=re.I)
    text = re.sub(r"(</(?:" + BLOCK_TAGS + r")>)", r"\1\n\n", text, flags=re.I)
    text = re.sub(r"\n{3,}", "\n\n", text)

    out = []
    for chunk in re.split(r"\n\s*\n", text):
        chunk = chunk.strip()
        if not chunk:
            continue
        # Don't wrap something that is already a block element.
        if re.match(r"^</?(?:" + BLOCK_TAGS + r")\b", chunk, flags=re.I):
            out.append(chunk)
        else:
            # Remaining single newlines inside a paragraph were line breaks.
            out.append("<p>" + re.sub(r"\n", "<br />\n", chunk) + "</p>")
    return "\n\n".join(out)


class HugoConverter(MarkdownConverter):
    """Markdownify with the tweaks this content needs."""

    def convert_img(self, el, text, parent_tags=None):
        src = el.get("src", "")
        alt = (el.get("alt") or "").strip()
        title = (el.get("title") or "").strip()
        if not src:
            return ""
        if src.startswith("MISSING:"):
            name = src[len("MISSING:"):]
            return f'\n\n<span class="img-missing">immagine perduta nella migrazione — {html.escape(name)}</span>\n\n'
        t = f' "{title}"' if title else ""
        return f"\n\n![{alt}]({src}{t})\n\n"

    def convert_iframe(self, el, text, parent_tags=None):
        src = el.get("src", "")
        if not src:
            return ""
        return f'\n\n<iframe src="{src}" loading="lazy" allowfullscreen></iframe>\n\n'


def to_markdown(soup_html: str) -> str:
    md = HugoConverter(
        heading_style="ATX",
        bullets="-",
        strong_em_symbol="*",
        escape_asterisks=False,
        escape_underscores=False,
        code_language="",
        newline_style="BACKSLASH",
    ).convert(soup_html)
    # A <br> with nothing before it becomes a lone "\" line — noise, not a break.
    md = re.sub(r"(?m)^\\[ \t]*$\n?", "", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = "\n".join(line.rstrip() for line in md.splitlines())
    return md.strip()


def parse_wp_date(s: str, fallback_gmt: str | None = None) -> datetime:
    tz = timezone(timedelta(hours=1))          # Europe/Rome, close enough pre-2004..now
    for raw in (s, fallback_gmt):
        if raw and raw != "0000-00-00 00:00:00":
            try:
                return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
            except ValueError:
                pass
    return datetime(2004, 1, 1, tzinfo=tz)


# --------------------------------------------------------------------------
# cleaning
# --------------------------------------------------------------------------

def clean_html(raw: str, stats: collections.Counter) -> BeautifulSoup:
    # Gutenberg block delimiters carry no content once the HTML is kept.
    raw = re.sub(r"<!--\s*/?wp:.*?-->", "", raw, flags=re.S)

    if "<p" not in raw.lower() and "<!-- wp:" not in raw:
        raw = wpautop(raw)
        stats["wpautop_applied"] += 1

    soup = BeautifulSoup(raw, "html.parser")

    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()

    # Must run while <div>/<p> wrappers are still intact: it decides what a
    # "line start" is from the block structure, and the unwrapping below
    # destroys exactly that.
    fix_dialogue_dashes(soup, stats)

    # <font> and <span> are inline: unwrapping them loses nothing.
    #
    # <div> is not. Several chapters use one styled <div> per paragraph, and
    # unwrapping those welded a 121k-character chapter into a single block —
    # so a div holding only inline content becomes a <p> instead.
    block_children = ["p", "div", "ul", "ol", "table", "blockquote", "pre",
                      "figure", "h1", "h2", "h3", "h4", "h5", "h6"]
    for tag in soup.find_all(["font", "span", "div"]):
        if tag.name == "div":
            if tag.find(block_children):
                tag.unwrap()
                stats["unwrapped_div"] += 1
            else:
                tag.name = "p"
                tag.attrs = {}
                stats["div_to_p"] += 1
        elif tag.name == "font" or not tag.attrs or set(tag.attrs) <= STRIP_ATTRS:
            tag.unwrap()
            stats["unwrapped_" + tag.name] += 1

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr in STRIP_ATTRS and not (tag.name == "img" and attr in ("src", "alt", "title")):
                del tag[attr]
                stats["attrs_stripped"] += 1

    # An <a> wrapping only an image is a lightbox link; the image is enough.
    for a in soup.find_all("a"):
        kids = [k for k in a.children if not (isinstance(k, NavigableString) and not k.strip())]
        if len(kids) == 1 and getattr(kids[0], "name", None) == "img":
            a.unwrap()
            stats["unwrapped_image_link"] += 1

    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["img", "iframe", "br"]):
            p.decompose()
            stats["empty_p_removed"] += 1

    return soup


def fix_dialogue_dashes(soup: BeautifulSoup, stats: collections.Counter) -> None:
    """Italian dialogue opens a paragraph with "- ", which Markdown reads as a
    bullet. The fiction serials are built almost entirely out of it — one
    chapter alone produced 331 spurious <li> elements. Promote the marker to a
    proper em dash, which is both correct typography and inert in Markdown."""
    LINE_BREAKERS = {"br", "p", "div", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6",
                     "hr", "section", "article", "td", "th", "li"}
    # No trailing-\S lookahead: the dash is often alone in its text node,
    # with the line's first word sitting inside a following <em>.
    DASH_START = r"[-–][ \t]+"

    for node in list(soup.descendants):
        if not isinstance(node, NavigableString) or isinstance(node, Comment):
            continue
        if node.find_parent(["ul", "ol", "li", "pre", "code", "a"]):
            continue
        s = str(node)
        if not s.strip():
            continue

        # Line starts *inside* the text node.
        out = re.sub(r"(?<=\n)([ \t]*)" + DASH_START, r"\1— ", s)

        # The node itself begins a line if nothing inline precedes it.
        prev = node.previous_sibling
        while prev is not None and isinstance(prev, NavigableString) and not str(prev).strip():
            prev = prev.previous_sibling
        begins_line = prev is None or getattr(prev, "name", None) in LINE_BREAKERS
        if begins_line:
            out = re.sub(r"^([ \t]*)" + DASH_START, r"\1— ", out)

        if out != s:
            stats["dialogue_dash_fixed"] += len(re.findall(r"— ", out)) - len(re.findall(r"— ", s))
            node.replace_with(out)


# --------------------------------------------------------------------------
# images
# --------------------------------------------------------------------------

class ImagePlanner:
    def __init__(self, dead_map: dict, lost: set):
        self.manifest: list[dict] = []
        self.dead_map = dead_map      # original url -> wayback url
        self.lost = lost              # urls with no copy anywhere
        self.stats = collections.Counter()

    def local_name(self, url: str, used: set) -> str:
        base = url.split("?")[0].split("/")[-1]
        base = re.sub(r"%[0-9A-Fa-f]{2}", "-", base)
        stem, _, ext = base.rpartition(".")
        if not stem:
            stem, ext = base, "jpg"
        # WordPress resize suffix: foo-300x200.jpg -> foo.jpg
        stem = re.sub(r"-\d+x\d+$", "", stem)
        name = f"{slugify(stem, 48)}.{(ext or 'jpg').lower()}"
        n = 1
        while name in used:
            n += 1
            name = f"{slugify(stem, 44)}-{n}.{(ext or 'jpg').lower()}"
        used.add(name)
        return name

    def queue(self, url: str, bundle: Path, used: set, post_title: str,
              source: str, prefix: str = "") -> str:
        """Add a URL to the download manifest and return its local filename."""
        name = self.local_name(url, used)
        if prefix:
            name = prefix + name
        self.manifest.append({
            "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
            "url": url, "original": url, "file": name,
            "source": source, "post": post_title,
        })
        self.stats["queued_" + source] += 1
        return name

    def plan(self, soup: BeautifulSoup, bundle: Path, post_title: str) -> set:
        used: set[str] = set()
        for img in soup.find_all("img"):
            src = (img.get("src") or "").strip()
            if not src:
                img.decompose()
                continue

            # Inline base64 image: decode straight into the bundle.
            if src.startswith("data:"):
                m = re.match(r"data:([^;,]+);base64,(.*)", src, flags=re.S)
                if m:
                    mime, b64 = m.group(1), re.sub(r"\s+", "", m.group(2))
                    ext = (mimetypes.guess_extension(mime) or ".jpg").lstrip(".")
                    name = f"inline-{len(used)+1}.{ext}"
                    used.add(name)
                    try:
                        bundle.mkdir(parents=True, exist_ok=True)
                        (bundle / name).write_bytes(base64.b64decode(b64))
                        img["src"] = name
                        self.stats["inline_base64_saved"] += 1
                        continue
                    except Exception:
                        pass
                img["src"] = "MISSING:immagine inline"
                self.stats["inline_base64_failed"] += 1
                continue

            if src.startswith("file:///"):
                img["src"] = "MISSING:" + src.split("/")[-1]
                self.stats["local_file_ref"] += 1
                continue

            if not src.startswith("http"):
                self.stats["skipped_relative"] += 1
                continue

            fetch_url, source = src, "other"
            if "blogspot" in src or "blogger" in src:
                # Blogger serves originals at /s0/; the posts embed /s400/.
                fetch_url = re.sub(r"/s\d+/", "/s0/", src)
                source = "blogger"
            elif "netsons" in src:
                source = "netsons"
                if src in self.dead_map:
                    fetch_url, source = self.dead_map[src], "wayback"
                elif src in self.lost:
                    img["src"] = "MISSING:" + src.split("/")[-1]
                    self.stats["lost"] += 1
                    continue

            name = self.local_name(src, used)
            img["src"] = name
            self.manifest.append({
                "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
                "url": fetch_url,
                "original": src,
                "file": name,
                "source": source,
                "post": post_title,
            })
            self.stats["queued_" + source] += 1
        return used


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not WXR.exists():
        print(f"missing {WXR}", file=sys.stderr)
        return 1

    dead_map, lost = {}, set()
    if DEADFILE.exists():
        d = json.loads(DEADFILE.read_text(encoding="utf-8"))
        dead_map = d.get("recoverable", {})
        lost = set(d.get("lost", []))
        print(f"dead-image map: {len(dead_map)} recoverable via Wayback, {len(lost)} lost")
    else:
        print("no dead_images.json — netsons 404s will be queued and fail at fetch time")

    chan = ET.parse(WXR).getroot().find("channel")
    items = chan.findall("item")

    # WordPress featured images: _thumbnail_id points at an attachment item.
    # (An older `Thumbnail` meta holds absolute URLs on hawke.archidea.us, a
    # host this blog lived on before Netsons — it is dead, every probe 404s,
    # so those are treated as unavailable rather than queued to fail.)
    attachment_url: dict[str, str] = {}
    for it in items:
        e = it.find("wp:post_type", NS)
        if e is not None and e.text == "attachment":
            pid = it.find("wp:post_id", NS)
            url = it.find("wp:attachment_url", NS)
            if pid is not None and url is not None and url.text:
                attachment_url[pid.text] = url.text

    stats = collections.Counter()
    planner = ImagePlanner(dead_map, lost)
    report_rows: list[dict] = []
    permalink_map: dict[str, str] = {}
    records = []

    # -------- pass 1: collect + decide slugs (needed for link rewriting) -----
    for it in items:
        def g(tag, ns=NS):
            e = it.find(tag, ns)
            return e.text if e is not None and e.text else ""

        ptype, status = g("wp:post_type"), g("wp:status")
        if ptype not in ("post", "page") or status != "publish":
            continue
        if g("wp:post_name") in SKIP_SLUGS:
            stats["skipped_by_slug"] += 1
            continue

        raw_title = (it.findtext("title") or "").strip()
        body = g("content:encoded")
        date = parse_wp_date(g("wp:post_date"), g("wp:post_date_gmt"))
        old_slug = g("wp:post_name")
        old_link = (it.findtext("link") or "").strip()

        plain_probe = BeautifulSoup(body, "html.parser").get_text(" ", strip=True)

        title = raw_title
        derived = False
        if not title:
            # 74 posts came over from Blogger with no title at all.
            snippet = re.sub(r"\s+", " ", plain_probe)[:70]
            title = snippet.rsplit(" ", 1)[0] if len(snippet) == 70 else snippet
            title = title.strip(" .,;:—–-") or f"Nota del {date:%d/%m/%Y}"
            derived = True
            stats["title_derived"] += 1

        slug = old_slug if old_slug and not re.fullmatch(r"\d+", old_slug) else slugify(title)
        if re.fullmatch(r"\d+", old_slug or ""):
            stats["numeric_slug_replaced"] += 1

        metas = {}
        for m in it.findall("wp:postmeta", NS):
            mk, mv = m.find("wp:meta_key", NS), m.find("wp:meta_value", NS)
            if mk is not None and mk.text:
                metas[mk.text] = mv.text if mv is not None and mv.text else ""

        records.append(dict(it=it, ptype=ptype, title=title, derived=derived, slug=slug,
                            date=date, body=body, old_link=old_link, old_slug=old_slug,
                            post_id=g("wp:post_id"), metas=metas))

    # Resolve slug collisions introduced by derived titles.
    postid_map: dict[str, str] = {}
    seen: dict[str, int] = {}
    for r in records:
        if r["ptype"] != "post":
            continue
        key = f"{r['date']:%Y}/{r['slug']}"
        if key in seen:
            seen[key] += 1
            r["slug"] = f"{r['slug']}-{seen[key]}"
            stats["slug_collision_resolved"] += 1
        else:
            seen[key] = 1
        if r["post_id"]:
            # The editor's own cross-links use ?p=<id>, not the pretty permalink.
            postid_map[r["post_id"]] = f"/posts/{r['date']:%Y}/{r['slug']}"
        if r["old_link"]:
            path = re.sub(r"^https?://[^/]+", "", r["old_link"]).rstrip("/") + "/"
            permalink_map[r["old_link"].rstrip("/") + "/"] = f"/posts/{r['date']:%Y}/{r['slug']}"
            permalink_map["https://orlotech.netsons.org" + path] = f"/posts/{r['date']:%Y}/{r['slug']}"
            permalink_map["http://orlotech.netsons.org" + path]  = f"/posts/{r['date']:%Y}/{r['slug']}"

    if args.limit:
        records = records[: args.limit]

    # -------- pass 2: convert + write ---------------------------------------
    for r in records:
        it, ptype = r["it"], r["ptype"]

        def g(tag, ns=NS):
            e = it.find(tag, ns)
            return e.text if e is not None and e.text else ""

        cats, tags = [], []
        for c in it.findall("category"):
            dom, txt = c.get("domain"), (c.text or "").strip()
            if not txt:
                continue
            if dom == "category" and txt not in DROP_CATEGORIES:
                cats.append(txt)
            elif dom == "post_tag":
                tags.append(txt)

        series = next((SERIES_BY_CATEGORY[c] for c in cats if c in SERIES_BY_CATEGORY), None)
        series_order = None
        if series:
            m = re.search(r"pt\.?\s*(\d+)", r["title"], flags=re.I)
            series_order = int(m.group(1)) if m else 999

        if ptype == "page":
            bundle = CONTENT / r["slug"]
        else:
            bundle = CONTENT / "posts" / f"{r['date']:%Y}" / r["slug"]

        soup = clean_html(r["body"], stats)
        used = planner.plan(soup, bundle, r["title"])

        # --- cover / thumbnail -------------------------------------------
        # `cover` is a real featured image and is shown as a post header.
        # `thumbnail` is inferred from the first inline image; it is used for
        # the timeline only, so the post does not show the same picture twice.
        cover = thumbnail = None
        tid = r["metas"].get("_thumbnail_id")
        if tid and attachment_url.get(tid):
            cover = planner.queue(attachment_url[tid], bundle, used, r["title"],
                                  "featured", prefix="cover-")
            stats["cover_from_featured"] += 1
        else:
            for img in soup.find_all("img"):
                src = (img.get("src") or "").strip()
                if src and not src.startswith(("MISSING:", "http", "data:")):
                    thumbnail = src
                    stats["thumb_from_inline"] += 1
                    break
            if thumbnail is None:
                stats["no_image_at_all"] += 1
                if r["metas"].get("Thumbnail"):
                    stats["cover_lost_archidea"] += 1

        # Internal cross-links -> Hugo relref, so they survive the new URLs.
        unresolved = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if "orlotech.netsons.org" not in href:
                continue
            target = permalink_map.get(href.rstrip("/") + "/")
            if not target:
                m = re.search(r"[?&](?:p|page_id)=(\d+)", href)
                if m:
                    target = postid_map.get(m.group(1))
            if target:
                a["href"] = '{{< relref "' + target + '" >}}'
                stats["internal_links_rewritten"] += 1
            elif "/wp-content/" not in href:
                unresolved += 1

        markdown = to_markdown(str(soup))
        # markdownify escapes the shortcode braces; put them back.
        markdown = markdown.replace("%7B%7B%3C", "{{<").replace("%3E%7D%7D", ">}}")
        markdown = re.sub(r"\\?\{\\?\{<\s*relref", "{{< relref", markdown)
        markdown = re.sub(r">\\?\}\\?\}", ">}}", markdown)

        plain = BeautifulSoup(str(soup), "html.parser").get_text(" ", strip=True)
        n_imgs = len(soup.find_all("img"))

        if series:
            layout = "chapter"
        elif len(plain) < NOTE_MAX_CHARS and n_imgs <= 1:
            layout = "note"
        elif n_imgs >= PHOTO_MIN_IMGS and len(plain) < PHOTO_MAX_CHARS:
            layout = "photo"
        else:
            layout = "single"
        stats["layout_" + layout] += 1

        comments = []
        for c in it.findall("wp:comment", NS):
            def cg(t):
                e = c.find(t, NS)
                return e.text if e is not None and e.text else ""
            if cg("wp:comment_approved") != "1":
                continue
            if (cg("wp:comment_type") or "comment") != "comment":
                continue
            ctext = cg("wp:comment_content")
            comments.append({
                "author": cg("wp:comment_author") or "anonimo",
                "date": (cg("wp:comment_date") or "")[:10],
                "content": wpautop(html.escape(ctext, quote=False)).replace("&lt;br /&gt;", "<br />"),
            })
        comments.sort(key=lambda x: x["date"])

        it_words = len(re.findall(r"\b(che|non|per|con|una|sono|come|questo|anche|della)\b", plain, re.I))
        en_words = len(re.findall(r"\b(the|and|that|with|this|have|from|which|about)\b", plain, re.I))
        postlang = "en" if en_words > it_words else "it"

        fm: dict = {"title": r["title"], "date": r["date"].isoformat(), "slug": r["slug"]}
        if ptype == "post":
            fm["layout"] = layout
        if cats:
            fm["categories"] = cats
        if tags:
            fm["tags"] = tags
        if series:
            fm["series"] = series
            fm["series_order"] = series_order
            fm["toc"] = len(plain) > 20000
        if cover:
            fm["cover"] = cover
        if thumbnail:
            fm["thumbnail"] = thumbnail
        fm["postLang"] = postlang
        if r["derived"]:
            fm["title_derived"] = True
        if r["old_link"]:
            alias = re.sub(r"^https?://[^/]+", "", r["old_link"]).rstrip("/") + "/"
            if alias and alias != "/":
                fm["aliases"] = [alias]
        fm["wp_original"] = r["old_link"]
        if comments:
            fm["archived_comments"] = comments

        front = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=100,
                               default_flow_style=False)
        doc = f"---\n{front}---\n\n{markdown}\n"

        if not args.dry_run:
            bundle.mkdir(parents=True, exist_ok=True)
            (bundle / "index.md").write_text(doc, encoding="utf-8")

        report_rows.append({
            "title": r["title"], "slug": r["slug"], "date": f"{r['date']:%Y-%m-%d}",
            "layout": layout if ptype == "post" else "page", "chars": len(plain),
            "imgs": n_imgs, "comments": len(comments), "series": series or "",
            "derived_title": r["derived"], "unresolved_links": unresolved,
        })
        stats["written_" + ptype] += 1

    # -------- output --------------------------------------------------------
    REPORT.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        MANIFEST.write_text(json.dumps(planner.manifest, indent=1, ensure_ascii=False), encoding="utf-8")
        (REPORT / "posts.json").write_text(json.dumps(report_rows, indent=1, ensure_ascii=False), encoding="utf-8")

    print("\n=== CONVERSION ===")
    for k in sorted(stats):
        print(f"  {k:28} {stats[k]}")
    print("\n=== IMAGES ===")
    for k in sorted(planner.stats):
        print(f"  {k:28} {planner.stats[k]}")
    print(f"  manifest entries             {len(planner.manifest)}")

    odd = [r for r in report_rows if r["unresolved_links"]]
    if odd:
        print(f"\n  posts with unresolved internal links: {len(odd)}")
        for r in odd[:10]:
            print(f"    {r['date']}  {r['title'][:50]}  ({r['unresolved_links']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
