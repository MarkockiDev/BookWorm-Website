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
`guides/` and seven guides under it, plus `reading-journal-app/`, `reading-log/`, `reading-challenge/`,
`goodreads-alternative/` and `storygraph-alternative/`. Everything added after the first nine pages is **English only for now** (translate the ones Search Console
shows working). Links to a page that may not exist in every language are wrapped in `<!--if:page-id-->…<!--/if-->`,
which `build.py` keeps only where that page exists, so no language links to a missing page. The printable reading
log is `src/printables/reading-log.html`, rendered to `assets/bookworm-reading-log-{a4,letter}.pdf` (see below).

Languages live under `/pl/`, `/es/`, `/fr/`, `/zh-hans/`, `/hi/`, `/ja/`,
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

## Website analytics (PostHog)

The site sends to the **same PostHog project as the app** (EU cloud), cookieless: `persistence: 'memory'`,
no person profiles, no autocapture, and session recording only for visitors who opt in. The key in `src/site.json` is PostHog's public
*project* key: it can only send events. `build.py` refuses to write any page that contains a PostHog personal
key (`phx_`), a RevenueCat key, or any other value from the app's private `BookWorm.xcconfig`.

PostHog only loads on `ilovebookworm.com`. Session replay is opt-in only (see below). To test locally, open a page with `?ph=1`; those events carry
`env = preview`.

Every website event carries `platform = web`, `site = ilovebookworm.com`, `env`, `page_id` (e.g. `home`,
`reading-goal-calculator`, `how-many-pages-a-day`) and `page_lang` (e.g. `en`, `pl`). App events don't have
`platform = web`, which is how the two are told apart.

| Event | When | Properties |
|---|---|---|
| `$pageview` | every page load | PostHog's own: URL, referrer, UTM tags, country, device |
| `$pageleave` | leaving a page | includes `$prev_pageview_max_scroll_percentage` (scroll depth) |
| `website_app_store_clicked` | any App Store button or link | `placement` (`nav`, `hero`, `page-top`, `calculator`, `closing`, `footer`), `theme` |
| `website_theme_changed` | a different look is picked | `theme`, `from`, `source` (`nav` or `section`) |
| `website_language_changed` | a language is picked in the menu | `to`, `from` |
| `website_faq_opened` | a question is opened | `question` (its number on that page) |
| `website_printable_downloaded` | a printable reading log PDF is downloaded | `size` (`a4` or `letter`) |
| `website_replay_consent` | Allow or No thanks on the recording card | `choice` (`allow` or `decline`) |
| `website_calculator_used` | once per mode per visit, after the visitor stops changing things | `mode` (`year` or `book`), `pages_per_day` (the number on screen), `year` (`this` or `next`, year mode only) |

Event names never change once shipped (same rule as the app).

### App Store campaign links

Add `"app_store_pt": "<provider token>"` to `src/site.json` and rebuild. Every App Store link then becomes
`apps.apple.com/app/apple-store/id6761390761?pt=<token>&ct=web-<page>&mt=8`, and App Store Connect →
App Analytics → Acquisition → Campaigns shows downloads per page.

## Session replay (opt-in)

Replay runs only for visitors who tap **Allow** on the consent card (`#consent` in `layout.html`, logic at the end of
`site.js`). The answer lives in `localStorage['bw-replay']` (`yes` / `no`); unanswered visitors are asked once per
visit, ~6 s in or after a scroll, and only where PostHog runs. With `yes`, the head snippet starts PostHog with
`localStorage+cookie` persistence and recording on (`maskAllInputs`); everyone else gets the cookieless setup.
**Recording choices** in the footer reopens the card; saying no there stops recording, resets PostHog and clears its
storage. Every event carries `replay = on|off`, and the choice itself is `website_replay_consent { choice }`.
In PostHog: Session replay → **Record user sessions** on, and `https://ilovebookworm.com` under Authorized domains.

## Share pictures

Every page has its own 1200×630 share picture in each language, at `assets/og/<lang>/<page>.jpg`, with that
page's eyebrow and headline beside an app screenshot (or a cloth cover for a guide). The home page keeps
`assets/og-share-v2.jpg`. After changing a headline or adding a page: `python3 og.py && python3 build.py`.

## IndexNow (Bing, DuckDuckGo's source, Yandex, Naver)

After a push has gone live, run `python3 indexnow.py`. It sends every URL in the sitemap. The key file at the root
(`<key>.txt`) is public on purpose: it only proves the list comes from this site.

## App Store custom product pages

`src/site.json` → `product_pages` maps a page id to an App Store Connect custom product page id (`ppid`).
Paste an id, rebuild, and that page's App Store buttons open its own App Store page.

## Printable reading log

Edit `src/printables/reading-log.html`, then render both sizes with headless Chrome:

```bash
for s in a4 letter; do "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=3000 --print-to-pdf="assets/bookworm-reading-log-$s.pdf" "file://$PWD/src/printables/reading-log.html?size=$s"; done
```

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
