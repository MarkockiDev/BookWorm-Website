# ilovebookworm.com

The BookWorm landing page, live at https://ilovebookworm.com (GitHub Pages from `main`, root).
Plain HTML, CSS and a little JavaScript. One small Python script builds the nine language versions.

```
src/template.html     the page, written once, with {{key}} placeholders
src/i18n/<lang>.json  the words for each language (en, pl, es, fr, zh-hans, hi, ja, ko, pt-br)
build.py              fills the template: index.html (English) and <lang>/index.html, plus sitemap.xml
privacy/index.html    the privacy policy (English only)
404.html              shown by GitHub Pages for any missing page
CNAME                 ilovebookworm.com
assets/               icons, worms, portrait, the cover used in the widget mock-ups, og-image.jpg
assets/badges/        Apple's official "Download on the App Store" badges, one per language
assets/shots/<theme>/ App Store 4.0 screenshots cropped for the web: light, dark, retro, marginalia
```

## Changing the page

1. Edit `src/template.html` (layout, styles, script) or `src/i18n/*.json` (words).
2. Run `python3 build.py`. It rewrites `index.html` and every `<lang>/index.html`.
   A key missing from a translation falls back to English, and the script says how many.
3. Never edit the generated `index.html` files by hand; the next build overwrites them.

## Preview locally

```bash
python3 -m http.server 8765 --directory "NEW WEBSITE"
```

Then open http://localhost:8765. The theme you pick is remembered in the browser; clear it with
`localStorage.removeItem('bw-theme')` in the console to see the system light/dark default again.

## How the page behaves

- **Theme.** Light, Dark, Retro and Marginalia restyle the whole page, and every screenshot swaps to the
  same theme. Until a visitor picks one, the page follows the system's light or dark setting.
- **Language.** The English page sends a first-time visitor whose browser prefers one of the other eight
  languages to that version, once. Picking a language in the menu is remembered and stops the redirect.
- **Widgets section.** The Home Screen and Lock Screen are drawn in HTML and CSS, not screenshots, and follow
  only light and dark, exactly like the real widgets.

## Hosting

Repository: `MarkockiDev/BookWorm-Website`. DNS lives in Cloudflare: four `A` records for `@` to
`185.199.108.153`, `.109`, `.110`, `.111`, and `www` CNAME to `markockidev.github.io`, all **DNS only**
(grey cloud). HTTPS is enforced in the repository's Pages settings. Leave the MX and TXT records alone:
they carry the domain's email.

## New screenshots

Crop the phone from each App Store panel (1206×2622) and save two widths per screen and theme:

```bash
magick in.png -crop 1126x1887+40+735 +repage -resize 720x -quality 80 out-720.webp
```

and again with `-resize 420x` for `-420.webp`. The hero (`hero-900/1600.webp`) joins Intro-A and Intro-B
side by side; see the git history for the exact command.
