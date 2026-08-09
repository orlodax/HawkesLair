# Working on Hawke's Lair

Technical notes for maintaining this site. The public-facing description is in
[README.md](README.md).

Hugo (extended) static site, migrated from WordPress in 2026. 466 posts +
2 pages, deployed to GitHub Pages via Actions.

## Running locally

```bash
hugo server --renderToMemory
```

Opens on <http://localhost:1313/>, live reload on. The flag is already set in
`.claude/launch.json`.

**`--renderToMemory` is not optional.** Since Hugo 0.123 the dev server writes
to `public/` — the same directory `hugo` builds into. Run a production build
while the server is up and it silently overwrites the server's output, so the
site starts serving pages with the production `/HawkesLair/` prefix: no CSS,
every link 404. Rendering to memory keeps the two independent.

To inspect a production build while the server runs, send it elsewhere:

```bash
hugo --gc --minify -d public_prod
```

## Deploying

Push to `main`; `.github/workflows/deploy.yml` builds and publishes. Pages
source must be **GitHub Actions**, not a branch. Keep `HUGO_VERSION` in the
workflow in sync with local `hugo version` (currently 0.164.0).

### The repo name and `baseURL` are coupled

GitHub Pages serves a project site at `/<repo-name>/`, **case included**.
Renaming the repo without updating `baseURL` leaves the site live but
completely unstyled with dead links. A rename means changing, together:

1. `baseURL` in `hugo.toml`
2. `[params.giscus] repo` in `hugo.toml`
3. the repo link in `content/privacy/index.md`
4. the git remote

### Two configs, on purpose

Production is under a path; `hugo server` serves from the root and does **not**
strip that prefix.

| file | environment | `baseURL` |
|---|---|---|
| `hugo.toml` | production (`hugo`) | `https://orlodax.github.io/HawkesLair/` |
| `config/development/hugo.toml` | development (`hugo server`) | `http://localhost:1313/` |

Hugo selects automatically. Moving to a root domain means deleting
`config/development/` and dropping the path from `baseURL`.

### Never hand-build URLs

Two separate outages came from constructing paths by hand. Use the page
objects:

- `site.Home.RelPermalink`, not `"/" | relURL` — the latter drops the base path
- `.GetTerms "categories"` → `.RelPermalink`, not `printf "/categories/%s/" (. | urlize)`
  — Hugo slugs `MS I - Capitoli` as `ms-i---capitoli`, which `urlize` does not
  reproduce
- `site.GetPage "/archivio"` → `.RelPermalink` for internal page links

## Content

Every post is a page bundle — a folder holding `index.md` plus its images:

```
content/posts/2010/menti-selvagge-pt-4/
├── index.md
└── copertina.jpg
```

Images are referenced by bare filename (`![](copertina.jpg)`).
`layouts/_markup/render-image.html` resolves them against the bundle and adds
dimensions and lazy loading, so the same reference works on the post page and
in the home timeline (where a bare relative path would 404).

### Front matter

```yaml
title: "Menti selvagge – pt.4"
date: 2010-09-22T18:02:00+02:00
layout: chapter        # single | photo | chapter
theme: parchment       # parchment | ink | ember | moss  (optional)
accent: "#8b4513"      # one-off tint, no preset needed  (optional)
cover: cover-foo.jpg   # featured image — post header + list image
thumbnail: foo.jpg     # inferred from first inline image — list only
series: "Menti Selvagge"
series_order: 4
postLang: it           # NB: `lang` was removed from Hugo in 0.144
comments: false        # suppress Giscus on this post
```

### Layouts

| layout | for | behaviour |
|---|---|---|
| `single` | ordinary posts (371) | standard |
| `photo` | image-led posts (68) | wider measure, minimal chrome |
| `chapter` | the fiction serials (27) | series index, per-chapter prev/next, optional TOC |

There was a fourth, `note`, for the 247 posts under ~600 characters: no title
header, and the whole body rendered inline in the timeline instead of an
excerpt. It was dropped. An inline block of prose is a device to use *within* a
post, not a layout for a whole one — in the timeline it read as an unattributed
quotation wedged between its neighbours, with no picture and no linked title.
Every post now gets the same treatment. Don't reintroduce it.

### Covers vs thumbnails

Two fields because they mean different things:

- **`cover`** — a genuine WordPress featured image (`_thumbnail_id`). Full-width
  header on the post *and* the list image. 37 posts.
- **`thumbnail`** — the post's first inline image, chosen automatically when
  there is no featured image. Used **only** in the list, so the post does not
  open with the same picture its body already contains. 180 posts.

To add a cover by hand: drop the file in the bundle, add `cover: filename.jpg`.

## Theme

Follows the blog's original WordPress theme — Twenty Fourteen, dark scheme —
measured off the live site rather than approximated:

| | original | here |
|---|---|---|
| typeface | Lato | Lato, self-hosted in `static/fonts/` |
| body | 16px / 24px line-height | same |
| page | `#000` on `#eee` | same |
| accent | `#24890d` | `#41b32a` on dark, `#24890d` on light |
| titles | 33px, weight 300, uppercase | same |
| sidebar | 222px, left | same, collapses below 62rem |

`assets/css/tokens.css` defines every colour and size as a custom property;
nothing downstream hardcodes a value. `themes.css` holds the per-post presets.
A post's `theme`/`accent` becomes `data-post-theme` and a scoped `--accent` on
`<article>`, so one front-matter line retints the whole post.

Dark is the default (the original was dark-only). The sidebar toggle opts into
light and persists in `localStorage`; the sidebar stays dark in both.

### Width

```css
--measure: clamp(59rem, 82vw, 92rem);                 /* reading column */
.site    { max-width: 110rem; margin-inline: auto; }  /* whole shell    */
```

The `max-width` on `.site` matters most: without it the sidebar and column sat
against the left edge and dumped all leftover width on the right (754px of dead
space at 2400px), which reads as a narrow column even when it isn't.

Measured: 1180px → 910px column · 1920px → 1472px · 2400px → 1472px centred ·
375px → 335px stacked.

At the top end that is ~184 characters per line, wide for prose. For a
readability cap on post bodies without narrowing the lists, add
`.post .prose { max-width: 62rem; }` and exempt images and code blocks.

### Images

- **Never distorted.** Width follows the column, height is always `auto`, and
  the `width`/`height` attributes carry the resized file's real dimensions.
- **Never upscaled.** Each image gets an inline `max-width` equal to its own
  pixel width, so a small 2010 upload renders sharp rather than stretched.

## Comments

The 305 old WordPress comments live in each post's front matter as
`archived_comments`, rendered statically — history, not a live thread.

Giscus is wired up but **off**. To enable: turn on Discussions for the repo,
get the IDs from <https://giscus.app>, fill in `repoId`/`categoryId`, and set
`enable = true` under `[params.giscus]`.

## The WordPress migration

`tools/wp2hugo/` holds the converter. It is not part of the site build.

```bash
cd tools/wp2hugo
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe convert.py        # WXRexport.xml -> content/
.venv/Scripts/python.exe fetch_images.py   # images.json  -> page bundles
```

⚠️ **`convert.py` overwrites `content/posts/` wholesale.** Any hand-editing
there is lost. Once you start editing posts, stop re-running it.

What it handles, all of which was needed for real content in this export:

- Reimplements WordPress's `wpautop` for the 204 posts stored without `<p>` tags
- Converts per-paragraph styled `<div>`s into real paragraphs — unwrapping them
  welded one 121k-character chapter into a single block
- Rewrites 1,448 Italian dialogue dashes (`- Ciao`) to em dashes; Markdown would
  otherwise read them as bullet lists (one chapter produced 331 spurious `<li>`)
- Strips ~5,600 inline `style`/`class` attributes and legacy `<font>` tags
- Derives titles for the 74 Blogger-era posts that never had one; replaces 77
  numeric slugs
- Rewrites internal `?p=<id>` cross-links to Hugo `relref`
- Keeps every original permalink as an `alias`
- Skips WordPress' generated privacy page (`SKIP_SLUGS`), which is replaced by
  a hand-written `content/privacy/index.md`

## Known gaps

- **86 images are gone.** 81 at `wp-content/uploads/<file>` (no date folder) and
  5 under dated folders. They 404 on the old site, were absent from its
  filesystem, and are not in the Wayback Machine. Rendered as an inline
  "immagine perduta nella migrazione" marker.
- **74 posts lost their featured image.** An older `Thumbnail` postmeta points at
  `hawke.archidea.us`, a host predating Netsons. Dead, and the same filenames are
  among the lost uploads above. Those posts fall back to their first inline image.
- **249 posts have no image at all** — mostly the 2004–2011 text notes.
- ~38 lines across 9 posts still start with `- `. Most are genuine lists
  (recipes); a few may be dialogue the heuristic missed.
- `Emotions, Music` is one category inherited from WordPress
  (`/categories/emotions-music/`). It was plainly meant to be two; left as-is
  deliberately.
