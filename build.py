#!/usr/bin/env python3
"""Builds the landing page in every language.

src/template.html holds the page once, with {{key}} placeholders.
src/i18n/<lang>.json holds the words. A key missing from a translation falls back to English,
so a half-translated language still builds. Output: index.html (English) and <lang>/index.html.

Run from anywhere:  python3 build.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = "https://ilovebookworm.com"
ORDER = ["en", "pl", "es", "fr", "zh-hans", "hi", "ja", "ko", "pt-br"]
# a language joins the menu as soon as its file exists
ORDER = [c for c in ORDER if (ROOT / "src" / "i18n" / f"{c}.json").exists()]

template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
langs = {code: json.loads((ROOT / "src" / "i18n" / f"{code}.json").read_text(encoding="utf-8")) for code in ORDER}
en = langs["en"]


def text(html):
    """Plain text for JSON-LD: drop tags, decode the two entities we use."""
    return re.sub(r"<[^>]+>", "", html).replace("&amp;", "&").replace("&nbsp;", " ")


def build(code):
    words = {**en, **langs[code]}
    path = words["_path"]
    url = SITE + path

    hreflang = "\n".join(
        f'<link rel="alternate" hreflang="{langs[c]["_html_lang"]}" href="{SITE}{langs[c]["_path"]}">' for c in ORDER
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/">'

    tick = '<svg class="tick" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
    menu = "\n        ".join(
        f'<a href="{langs[c]["_path"]}" hreflang="{c}" lang="{langs[c]["_html_lang"]}"'
        + (' aria-current="page"' if c == code else "")
        + f'>{langs[c]["_native"]}{tick}</a>'
        for c in ORDER
    )

    faq = []
    qa = []
    for i in range(1, 9):
        q, a = words[f"q{i}"], words[f"a{i}"]
        faq.append(
            f'<details class="reveal"><summary>{q}<i aria-hidden="true"></i></summary>'
            f'<div class="answer"><p>{a}</p></div></details>'
        )
        qa.append({"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}})

    jsonld = json.dumps(
        [
            {
                "@context": "https://schema.org",
                "@type": "MobileApplication",
                "name": "BookWorm",
                "operatingSystem": "iOS 17.2 or later",
                "applicationCategory": "BookApplication",
                "url": url,
                "installUrl": "https://apps.apple.com/app/id6761390761",
                "image": SITE + "/assets/icon.png",
                "description": words["jsonld_desc"],
                "inLanguage": [langs[c]["_html_lang"] for c in ORDER],
            },
            {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": words["_html_lang"], "mainEntity": qa},
        ],
        ensure_ascii=False,
        indent=2,
    )

    fills = {
        **words,
        "html_lang": words["_html_lang"],
        "canonical": url,
        "hreflang": hreflang,
        "og_locale": words["_og_locale"],
        "is_root": "true" if code == "en" else "false",
        "jsonld": jsonld,
        "home": path,
        "lang_menu": menu,
        "lang_native": words["_native"],
        "lang_short": words["_short"],
        "badge": f'/assets/badges/{words["_badge"]}-black.svg',
        "faq_items": "\n      ".join(faq),
    }

    def fill(match):
        key = match.group(1)
        if key not in fills:
            raise KeyError(f"{code}: no text for {{{{{key}}}}}")
        return fills[key]

    html = re.sub(r"\{\{(\w+)\}\}", fill, template)
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    missing = sorted(k for k in en if not k.startswith("_") and k not in langs[code])
    print(f"{code:8} -> {out.relative_to(ROOT)}" + (f"  ({len(missing)} keys fall back to English)" if missing else ""))


for c in ORDER:
    build(c)

sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sitemap += [f'  <url><loc>{SITE}{langs[c]["_path"]}</loc></url>' for c in ORDER]
sitemap += [f"  <url><loc>{SITE}/privacy/</loc></url>", "</urlset>", ""]
(ROOT / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")
