#!/usr/bin/env python3
"""Share pictures (Open Graph, 1200x630) for every page in every language it exists in.

Each picture carries that page's eyebrow and headline, in its language, beside an app screenshot
(or, for a guide, a cloth-bound cover like the Guides shelf). The home page keeps assets/og-share-v2.jpg.
Output: assets/og/<lang>/<page>.jpg, which build.py uses when it exists.

Needs Google Chrome and ImageMagick. Run after changing a headline, then run build.py:
    python3 og.py && python3 build.py
"""
import html
import json
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LANGS = ["en", "pl", "es", "fr", "zh-hans", "hi", "ja", "ko", "pt-br"]

# the screenshot beside each page's headline; guides get a cover in that cloth instead
SHOT = {
    "reading-goal-calculator": "quests", "audiobook-tracker": "timer", "reading-habit-tracker": "calendar",
    "support": "profile", "guides": "bookshelf", "reading-journal-app": "bookshelf", "reading-log": "book",
    "reading-challenge": "profile", "goodreads-alternative": "quests", "storygraph-alternative": "timer",
}
CLOTH = {
    "how-many-pages-a-day": "#6E2A2A", "build-a-reading-habit": "#263A5A", "track-audiobooks": "#8A5A1C",
    "start-a-reading-journal": "#2F5D4A", "how-to-read-more-books": "#4E2F4A", "reading-challenge-ideas": "#3B4A4A",
    "best-reading-tracker-apps": "#263A5A",
}

PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:#FAF6EF;color:#2C1810;font-family:-apple-system,"Helvetica Neue",sans-serif;display:grid;grid-template-columns:1fr 420px;align-items:center;padding:0 0 0 76px}}
.brand{{display:flex;align-items:center;gap:14px;font:700 30px/1 ui-serif,"New York",Georgia,serif}}
.brand img{{width:56px;height:56px;border-radius:14px}}
.eyebrow{{margin-top:56px;font:700 18px/1.2 -apple-system,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#2F7A4C}}
h1{{margin-top:18px;font:700 {size}px/1.08 ui-serif,"New York",Georgia,serif;letter-spacing:-.01em;max-width:640px;text-wrap:balance}}
.url{{margin-top:36px;font:600 24px/1 -apple-system,sans-serif;color:#2F7A4C}}
.phone{{justify-self:center;width:330px;transform:rotate(4deg) translateY(90px)}}
.phone img{{display:block;width:100%}}
.cover{{justify-self:center;width:300px;aspect-ratio:2/3;border-radius:6px 14px 14px 6px;background:linear-gradient(90deg,rgba(0,0,0,.34) 0,rgba(0,0,0,.08) 5%,rgba(255,255,255,.10) 7%,transparent 12%),radial-gradient(120% 80% at 30% 0%,rgba(255,255,255,.14),transparent 60%),{cloth};color:#E9D9A6;padding:40px 34px 34px 44px;position:relative;transform:rotate(-3deg);box-shadow:10px 0 0 -3px #F3EBDC,12px 0 0 -3px rgba(0,0,0,.2),16px 0 0 -6px #E8DCC6,0 40px 60px -26px rgba(60,35,15,.6)}}
.cover::before{{content:"";position:absolute;inset:16px 16px 16px 26px;border:1.5px solid rgba(233,217,166,.45);border-radius:3px}}
.cover::after{{content:"";position:absolute;right:36px;bottom:-22px;width:16px;height:56px;background:#C9A84C;clip-path:polygon(0 0,100% 0,100% 100%,50% 80%,0 100%)}}
.cover small{{font:600 14px/1.2 -apple-system,sans-serif;letter-spacing:.2em;text-transform:uppercase;opacity:.85}}
.cover b{{display:block;margin-top:22px;font:700 30px/1.2 ui-serif,"New York",Georgia,serif}}
</style></head><body>
<div><div class="brand"><img src="{icon}">BookWorm</div><p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="url">ilovebookworm.com</p></div>
{art}
</body></html>"""


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def render(lang, pid, words, out):
    title = plain(words.get("og_title") or words["h1"])
    size = 64 if len(title) < 40 else 56 if len(title) < 60 else 48 if len(title) < 80 else 42
    if pid in CLOTH:
        art = f'<div class="cover"><small>BookWorm</small><b>{html.escape(plain(words["crumb"]))}</b></div>'
    else:
        art = f'<div class="phone"><img src="{(ROOT / "assets/shots/light" / (SHOT[pid] + "-720.webp")).as_uri()}"></div>'
    page = PAGE.format(lang=lang, size=size, cloth=CLOTH.get(pid, "#2F5D4A"), icon=(ROOT / "assets/icon-180.png").as_uri(),
                       eyebrow=html.escape(plain(words["eyebrow"])), title=html.escape(title), art=art)
    with tempfile.TemporaryDirectory() as tmp:
        f = pathlib.Path(tmp) / "og.html"
        f.write_text(page, encoding="utf-8")
        png = pathlib.Path(tmp) / "og.png"
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        "--virtual-time-budget=2000", "--window-size=1200,630", f"--screenshot={png}", f.as_uri()],
                       check=True, capture_output=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["magick", str(png), "-strip", "-quality", "82", str(out)], check=True)


for path in sorted((SRC / "pages").glob("*.html")):
    pid = path.stem
    if pid == "home":
        continue
    en = json.loads((SRC / "i18n/en" / f"{pid}.json").read_text(encoding="utf-8"))
    for lang in LANGS:
        f = SRC / "i18n" / lang / f"{pid}.json"
        if not f.exists():
            continue
        words = {**en, **json.loads(f.read_text(encoding="utf-8"))}
        render(lang, pid, words, ROOT / "assets/og" / lang / f"{pid}.jpg")
        print("og", lang, pid)
