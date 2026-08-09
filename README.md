# Hawke's Lair

The blog, migrated off WordPress (`orlotech.netsons.org`) to Hugo + GitHub Pages.
466 posts and 2 pages, 2004–2026.

## Running it locally

Hugo Extended is required (installed via `winget install Hugo.Hugo.Extended`).

```bash
hugo server --renderToMemory
```

Then open <http://localhost:1313/>. Live reload is on.

**`--renderToMemory` matters.** Since Hugo 0.123 the dev server writes to
`public/` on disk — the same directory `hugo` builds into. Run a production
build while the server is up and it overwrites the server's output, so the
site starts serving pages with the production `/hawkeslair/` prefix: no CSS,
every link 404. Rendering to memory keeps the two completely independent.

The same flag is already set in `.claude/launch.json`.

If you want a production build to inspect while the server runs, send it
somewhere else:

```bash
hugo --gc --minify -d public_prod
```

To produce the deployable output in `public/`:

```bash
hugo --gc --minify
```

## Deploying

Target: `https://orlodax.github.io/HawkesLair/` — a repo named `HawkesLair`
under the `orlodax` account.

**The repo name and `baseURL` are coupled.** GitHub Pages serves a project
site at `/<repo-name>/`, case included, so renaming the repo without updating
`baseURL` leaves the site live but unstyled with dead links. Both must change
together, plus `[params.giscus] repo`.

1. Create the repo and push `main`.
2. **Settings → Pages → Source → GitHub Actions** (not a branch).

`.github/workflows/deploy.yml` builds with Hugo 0.164.0 and publishes. Keep
`HUGO_VERSION` in sync with your local `hugo version`.

### Why there are two configs

Production lives under the `/hawkeslair/` path, but `hugo server` serves from
the root and does **not** strip that prefix — which loads the site with no CSS
and 404s on every link. So:

| file | environment | `baseURL` |
|---|---|---|
| `hugo.toml` | production (`hugo`) | `https://orlodax.github.io/HawkesLair/` |
| `config/development/hugo.toml` | development (`hugo server`) | `http://localhost:1313/` |

Hugo picks the right one automatically. If you ever move to a root domain,
delete `config/development/` and drop the path from `baseURL`.

## Layout of the content

Every post is a *page bundle* — a folder holding `index.md` plus that post's
images:

```
content/posts/2010/menti-selvagge-pt-4/
├── index.md
└── copertina.jpg
```

Images are referenced by bare filename (`![](copertina.jpg)`).
`layouts/_markup/render-image.html` resolves them to absolute URLs and adds
dimensions and lazy loading, so the same reference works on the post page and
in the home timeline.

## Front matter

```yaml
title: "Menti selvagge – pt.4"
date: 2010-09-22T18:02:00+02:00
layout: chapter        # note | single | photo | chapter
theme: parchment       # parchment | ink | ember | moss  (optional)
accent: "#8b4513"      # one-off tint, no preset needed  (optional)
cover: cover-foo.jpg   # WordPress featured image — header + list thumbnail
thumbnail: foo.jpg     # inferred from first inline image — list thumbnail only
series: "Menti Selvagge"
series_order: 4
postLang: it           # NB: `lang` was removed from Hugo in 0.144
comments: false        # suppress Giscus on this post
```

### Covers and thumbnails

Two distinct fields, because they mean different things:

- **`cover`** — a genuine WordPress featured image (`_thumbnail_id`). Rendered
  as a full-width header on the post *and* as the list thumbnail. 37 posts.
- **`thumbnail`** — the post's first inline image, picked automatically when
  there is no featured image. Used **only** in the list, so the post does not
  open with the same picture the body already contains. 180 posts.

To give a post a cover by hand, drop the image in its bundle and add
`cover: filename.jpg`.

### Layouts

| layout | for | behaviour |
|---|---|---|
| `note` | posts under ~600 chars (247 of them) | no title header; **renders in full on the index** |
| `single` | ordinary posts | standard |
| `photo` | image-led posts | wider measure, minimal chrome |
| `chapter` | the fiction serials | series index, per-chapter prev/next, optional TOC |

### Theming

The look follows the blog's original WordPress theme — **Twenty Fourteen in
its dark scheme** — measured directly off the live site rather than guessed:

| | original | here |
|---|---|---|
| typeface | Lato | Lato (self-hosted, `static/fonts/`) |
| body | 16px / 24px line-height | same |
| page | `#000` on `#eee` | same |
| accent | `#24890d` | `#41b32a` on dark, `#24890d` on light |
| titles | 33px, weight 300, uppercase | same |
| sidebar | 222px, left | same, collapses below 62rem |
| content | 945px | 944px at that window width, but fluid |

`assets/css/tokens.css` defines every colour and size as a custom property;
nothing downstream hardcodes a value. `themes.css` holds the named per-post
presets. A post's `theme`/`accent` is emitted as `data-post-theme` and a scoped
`--accent` on `<article>`, so one front-matter line retints the whole post
without a separate stylesheet.

Dark is the default, since the original was dark-only. The sidebar toggle opts
into light and persists in `localStorage`. The sidebar itself stays dark in
both schemes, as it did originally.

### Width

Two things control it, in `tokens.css` and `base.css`:

```css
--measure: clamp(59rem, 82vw, 92rem);          /* the reading column      */
.site    { max-width: 110rem; margin-inline: auto; }  /* the whole shell  */
```

The `max-width` on `.site` is the important one. Without it the sidebar and
column sat hard against the left edge and dumped every leftover pixel on the
right — 754px of dead space at 2400px wide — which reads as "too narrow" even
though the column was generous. Centring the shell fixed the perception; the
raised `--measure` did the rest.

Measured: 1180px window → 910px column · 1920px → 1472px · 2400px → 1472px
centred with even margins · 375px → 335px stacked.

At the top end that is ~184 characters per line, which is wide for prose. If
you ever want a readability cap on post bodies without narrowing the lists,
add `.post .prose { max-width: 62rem; }` — images and code blocks would need
to be exempted to keep spanning the full column.

### Images

Two rules, everywhere:

- **Never distorted.** Width follows the column, height is always `auto`, and
  the `width`/`height` attributes carry the resized file's real dimensions.
- **Never upscaled.** Each image also gets an inline `max-width` equal to its
  own pixel width, so a small 2010 upload renders sharp and centred instead of
  being stretched across a 1200px column.

List images sit above the title at column width, as the original did.

## Comments

Old WordPress comments (305 of them) are baked into each post's front matter as
`archived_comments` and rendered statically — history, not a live thread.

Giscus is wired up but **off**. To enable: turn on Discussions for the repo,
get the IDs from <https://giscus.app>, then fill in `repoId`/`categoryId` and
set `enable = true` under `[params.giscus]` in `hugo.toml`.

## Re-running the migration

`tools/wp2hugo/` holds the converter. It is not part of the site build.

```bash
cd tools/wp2hugo
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe convert.py        # WXRexport.xml -> content/
.venv/Scripts/python.exe fetch_images.py   # images.json  -> page bundles
```

`convert.py` is destructive — it overwrites `content/posts/`. Anything edited
by hand there will be lost, so once you start editing posts, stop re-running it.

### What the conversion does

- Reimplements WordPress's `wpautop` for the 204 posts stored without `<p>` tags
- Turns per-paragraph styled `<div>`s into real paragraphs (unwrapping them
  welded one 121k-character chapter into a single block)
- Rewrites 1,448 Italian dialogue dashes (`- Ciao`) to em dashes, which
  Markdown would otherwise read as bullet lists
- Strips ~5,600 inline `style`/`class` attributes and legacy `<font>` tags
- Derives titles for the 74 Blogger-era posts that never had one, and replaces
  77 numeric slugs
- Rewrites internal `?p=<id>` cross-links to Hugo `relref`
- Keeps every original permalink as an `alias`

## Privacy page

`content/privacy/index.md` is hand-written and replaces WordPress' generated
one, which was untouched boilerplate: it named the old netsons domain and
described comment forms, Gravatar, login cookies and media uploads that do not
exist on a static site. The replacement states what is actually true — no
cookies, no analytics, no forms — and covers the two things that *are* real:
GitHub Pages' own server logs, and the third-party embeds in some posts.

The old `/privacy-policy-2/` URL is kept as an alias, and that slug is in
`SKIP_SLUGS` in `convert.py` so re-running the converter will not restore the
boilerplate.

## Known gaps

- **86 images are gone.** 81 lived at `wp-content/uploads/<file>` (no date
  folder) and 5 more under dated folders. They 404 on the live site, are absent
  from the server's filesystem, and were never captured by the Wayback Machine.
  They render as an inline "immagine perduta nella migrazione" marker.
- **74 posts lost their featured image.** An older `Thumbnail` postmeta points
  at `hawke.archidea.us`, a host this blog lived on before Netsons. It is dead
  (every probe 404s) and the same filenames are among the lost uploads above.
  Those posts fall back to their first inline image where they have one.
- **249 posts have no image at all** — mostly the 2004–2011 text notes.
- ~38 lines across 9 posts still begin with `- `. Most are genuine lists
  (recipes); a few may be dialogue the heuristic missed.
- `Emotions, Music` is a single category inherited from WordPress. It works
  (`/categories/emotions-music/`), but it was plainly meant to be two.
