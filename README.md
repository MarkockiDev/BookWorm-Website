# ilovebookworm.com

The BookWorm website, live at https://ilovebookworm.com (GitHub Pages from `main`, root).
Plain HTML, CSS and a little JavaScript. One small Python script builds every page in nine languages.

```
src/layout.html                the shell every page shares: head, nav, footer
src/pages/<page>.html          one page's content
src/i18n/<lang>/common.json    words every page uses (nav, footer, cards, themes)
src/i18n/<lang>/<page>.json    one page's words; a page is built in a language once this file exists
build.py                       builds <lang path><slug>/index.html for every page and language, plus sitemap.xml
assets/site.css, site.js       shared styles and behaviour (cached across pages)
assets/shots/<theme>/          App Store 4.0 screenshots cropped for the web, per theme
assets/badges/                 Apple's official App Store badges, one per language
privacy/index.html             privacy policy (English only, not built)
404.html, CNAME, robots.txt
```

Pages: home, `reading-goal-calculator/`, `audiobook-tracker/`, `reading-habit-tracker/`, `support/`,
`guides/` and three guides under it. Languages live under `/pl/`, `/es/`, `/fr/`, `/zh-hans/`, `/hi/`, `/ja/`,
`/ko/`, `/pt-br/` with the same slugs.

## Changing the site

1. Edit `src/layout.html`, `src/pages/*.html`, `assets/site.css`/`site.js`, or the words in `src/i18n/`.
2. Run `python3 build.py`. It rewrites every generated `index.html` and `sitemap.xml`, and prints any
   language that is still missing words (those fall back to English).
3. Never edit generated `index.html` files by hand; the next build overwrites them.

**Adding a page:** add `src/pages/<id>.html`, add `src/i18n/en/<id>.json` (with `meta_title`, `meta_desc`,
`crumb`), add the page to `PAGES` in `build.py`, then translate the JSON into the other languages.
**Adding a guide:** same, with kind `article` and parent `guides`; give it `_published`, `date_label`,
`minutes` and `body` (HTML), and link it from `src/pages/guides.html` and the footer.

## What build.py does for search engines

- A title, description, canonical URL and links to every language version on each page.
- Breadcrumbs on inner pages, `Article` data on guides, `FAQPage` data wherever a page has questions.
- On the home page: the app with its live App Store rating (fetched from Apple at build time, left out
  if the lookup fails), price, `WebSite` and `Organization`.
- `sitemap.xml` listing every page in every language, each with its other languages.

Rebuild now and then so the rating in search results stays current.

## Preview locally

```bash
python3 -m http.server 8765 --directory "NEW WEBSITE"
```

## Things only Adam can do

- **Google Search Console:** submit `https://ilovebookworm.com/sitemap.xml` (Sitemaps), then use
  URL Inspection → Request indexing for the home page, the calculator and the guides.
- **App Store Connect:** Marketing URL `https://ilovebookworm.com/`, Support URL
  `https://ilovebookworm.com/support/`, Privacy Policy URL `https://ilovebookworm.com/privacy/`.
- **Rich Results Test** (search.google.com/test/rich-results) on the home page and a guide, once live.

## Hosting

Repository: `MarkockiDev/BookWorm-Website`. DNS in Cloudflare: four `A` records for `@` to
`185.199.108.153`, `.109`, `.110`, `.111`, and `www` CNAME to `markockidev.github.io`, all **DNS only**.
HTTPS is enforced in the repository's Pages settings. Leave the MX and TXT records alone (email).
Commits use `markocki.adam@gmail.com` so they count on Adam's GitHub profile.
