#!/usr/bin/env python3
"""Builds ilovebookworm.com: every page in every language.

src/layout.html          the shell every page shares (head, nav, footer) with {{key}} placeholders
src/pages/<page>.html    one page's content, dropped into {{content}}
src/i18n/<lang>/common.json   words every page uses (nav, footer, themes)
src/i18n/<lang>/<page>.json   that page's words; a page is built in a language only once this file exists

A key missing from a translation falls back to English. Output: <lang path><slug>index.html, plus sitemap.xml.
The App Store rating is read live from Apple's public lookup; if that fails it is simply left out.

Run from anywhere:  python3 build.py
"""
import datetime
import hashlib
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
SITE = "https://ilovebookworm.com"
APP_ID = "6761390761"
APP_URL = f"https://apps.apple.com/app/id{APP_ID}"
LANGS = ["en", "pl", "es", "fr", "zh-hans", "hi", "ja", "ko", "pt-br"]

# id, slug, parent id (for breadcrumbs), kind
PAGES = [
    ("home", "", None, "home"),
    ("reading-goal-calculator", "reading-goal-calculator/", None, "page"),
    ("audiobook-tracker", "audiobook-tracker/", None, "page"),
    ("reading-habit-tracker", "reading-habit-tracker/", None, "page"),
    ("support", "support/", None, "page"),
    ("guides", "guides/", None, "page"),
    ("how-many-pages-a-day", "guides/how-many-pages-a-day/", "guides", "article"),
    ("build-a-reading-habit", "guides/build-a-reading-habit/", "guides", "article"),
    ("track-audiobooks", "guides/track-audiobooks/", "guides", "article"),
]
PAGES = [p for p in PAGES if (SRC / "pages" / f"{p[0]}.html").exists()]
BY_ID = {p[0]: p for p in PAGES}

layout = (SRC / "layout.html").read_text(encoding="utf-8")
SITE_CONFIG = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
assert SITE_CONFIG["posthog_key"].startswith("phc_"), "site.json must hold PostHog's public project key (phc_...), nothing else"
CAMPAIGN = SITE_CONFIG.get("app_store_pt", "").strip()  # App Store Connect campaign provider token, if set
ver = hashlib.sha1(b"".join((ROOT / "assets" / f).read_bytes() for f in ("site.css", "site.js"))).hexdigest()[:8]


def load(lang, name):
    f = SRC / "i18n" / lang / f"{name}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


common = {lang: load(lang, "common") for lang in LANGS}
words = {(lang, pid): load(lang, pid) for lang in LANGS for pid, *_ in PAGES}


def has(lang, pid):
    return words[(lang, pid)] is not None


def url(lang, pid):
    return SITE + common[lang]["_path"] + BY_ID[pid][1]


def text(html):
    """Plain text for JSON-LD: drop tags, decode the entities we use."""
    return re.sub(r"<[^>]+>", "", html).replace("&amp;", "&").replace("&nbsp;", " ").strip()


def app_rating():
    try:
        with urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={APP_ID}&country=us", timeout=10) as r:
            result = json.load(r)["results"][0]
        count = int(result.get("userRatingCount") or 0)
        value = float(result.get("averageUserRating") or 0)
        if count and value:
            return {"@type": "AggregateRating", "ratingValue": round(value, 1), "ratingCount": count, "bestRating": 5}
    except Exception as error:  # offline, rate limited, listing changed: leave the stars out
        print(f"rating lookup failed ({error}); building without stars")
    return None


RATING = app_rating()
TODAY = datetime.date.today().isoformat()


def secrets():
    """Every value in the app's private BookWorm.xcconfig except the public PostHog project key and host,
    plus the shapes of keys that must never be published (PostHog personal keys, RevenueCat keys)."""
    found = []
    xc = ROOT.parent / "BookWorm.xcconfig"
    if xc.exists():
        for line in xc.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("//"):
                value = line.split("=", 1)[1].strip()
                if len(value) >= 8 and not value.startswith("phc_") and "posthog.com" not in value:
                    found.append(value)
    return found


SECRETS = secrets()
SECRET_SHAPES = re.compile(r"\b(phx_[A-Za-z0-9]{10,}|appl_[A-Za-z0-9]{10,}|test_[A-Za-z0-9]{20,}|sk_[A-Za-z0-9]{20,})")


def leak_check(html, where):
    """Stops the build if a page would publish anything secret."""
    hit = SECRET_SHAPES.search(html)
    if hit or any(v in html for v in SECRETS):
        raise SystemExit(f"STOP: {where} would publish a secret ({'pattern ' + hit.group(1)[:5] + '...' if hit else 'a value from BookWorm.xcconfig'}). Nothing was written.")
TICK = '<svg class="tick" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'


def build(lang, pid):
    _, slug, parent, kind = BY_ID[pid]
    w = {**common["en"], **words[("en", pid)], **common[lang], **words[(lang, pid)]}
    home = common[lang]["_path"]
    here = url(lang, pid)
    langs_here = [l for l in LANGS if has(l, pid)]

    hreflang = "\n".join(f'<link rel="alternate" hreflang="{common[l]["_html_lang"]}" href="{url(l, pid)}">' for l in langs_here)
    if has("en", pid):
        hreflang += f'\n<link rel="alternate" hreflang="x-default" href="{url("en", pid)}">'

    menu = "\n        ".join(
        f'<a href="{common[l]["_path"] + (slug if has(l, pid) else "")}" hreflang="{l}" lang="{common[l]["_html_lang"]}"'
        + (' aria-current="page"' if l == lang else "")
        + f'>{common[l]["_native"]}{TICK}</a>'
        for l in LANGS if common[l]
    )

    # FAQ: every q<n>/a<n> pair in this page's words
    page_words = {**words[("en", pid)], **words[(lang, pid)]}
    pairs = [(page_words[f"q{i}"], page_words[f"a{i}"]) for i in range(1, 30) if f"q{i}" in page_words]
    faq = "\n      ".join(
        f'<details class="reveal"><summary>{q}<i aria-hidden="true"></i></summary><div class="answer"><p>{a}</p></div></details>'
        for q, a in pairs
    )

    # breadcrumbs: Home › (Guides ›) this page
    trail = [(w["crumb_home"], url(lang, "home"))]
    if parent:
        trail.append((text({**words[("en", parent)], **(words[(lang, parent)] or {})}["crumb"]), url(lang, parent)))
    if pid != "home":
        trail.append((text(w["crumb"]), here))
    crumbs_html = ""
    if pid != "home":
        items = "".join(
            f'<li><a href="{u}">{name}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{name}</li>'
            for i, (name, u) in enumerate(trail)
        )
        crumbs_html = f'<nav class="crumbs" aria-label="{w["crumb_label"]}"><ol>{items}</ol></nav>'

    graph = []
    if kind == "home":
        app = {
            "@type": "MobileApplication",
            "name": "BookWorm: Reading Tracker",
            "operatingSystem": "iOS 17.2 or later",
            "applicationCategory": "BookApplication",
            "url": here,
            "installUrl": APP_URL,
            "image": SITE + "/assets/icon.png",
            "description": w["jsonld_desc"],
            "inLanguage": [common[l]["_html_lang"] for l in LANGS],
            "author": {"@type": "Person", "name": "Adam Markocki"},
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        }
        if RATING:
            app["aggregateRating"] = RATING
        graph += [
            app,
            {"@type": "WebSite", "name": "BookWorm", "alternateName": "ilovebookworm.com", "url": SITE + "/", "inLanguage": w["_html_lang"]},
            {"@type": "Organization", "name": "BookWorm", "url": SITE + "/", "logo": SITE + "/assets/icon.png", "sameAs": [APP_URL]},
        ]
    else:
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(trail)],
        })
    if kind == "article":
        graph.append({
            "@type": "Article",
            "headline": text(w["h1"]),
            "description": w["meta_desc"],
            "inLanguage": w["_html_lang"],
            "datePublished": w.get("_published", TODAY),
            "dateModified": w.get("_modified", w.get("_published", TODAY)),
            "author": {"@type": "Person", "name": "Adam Markocki", "url": SITE + "/"},
            "publisher": {"@type": "Organization", "name": "BookWorm", "logo": {"@type": "ImageObject", "url": SITE + "/assets/icon.png"}},
            "image": SITE + "/assets/og-share-v2.jpg",
            "mainEntityOfPage": here,
        })
    if pairs:
        graph.append({
            "@type": "FAQPage",
            "inLanguage": w["_html_lang"],
            "mainEntity": [{"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in pairs],
        })
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    fills = {
        **w,
        "html_lang": w["_html_lang"],
        "canonical": here,
        "hreflang": hreflang,
        "og_locale": w["_og_locale"],
        "og_title": w.get("og_title", w["meta_title"]),
        "og_desc": w.get("og_desc", w["meta_desc"]),
        "is_en": "true" if lang == "en" else "false",
        "slug": slug,
        "jsonld": jsonld,
        "home": home,
        "lang_menu": menu,
        "lang_native": w["_native"],
        "lang_short": w["_short"],
        "badge": f'/assets/badges/{w["_badge"]}-black.svg',
        "faq_items": faq,
        "breadcrumb": crumbs_html,
        # with a campaign token, App Store Connect counts downloads per page (ct=web-<page>)
        "app_url": f"https://apps.apple.com/app/apple-store/id{APP_ID}?pt={CAMPAIGN}&ct=web-{pid}&mt=8" if CAMPAIGN else APP_URL,
        "page_id": pid,
        "lang_code": lang,
        "posthog_key": SITE_CONFIG["posthog_key"],
        "posthog_host": SITE_CONFIG["posthog_host"],
        "posthog_ui": SITE_CONFIG["posthog_ui"],
        "ver": ver,
    }

    def fill(match):
        key = match.group(1)
        if key not in fills:
            raise KeyError(f"{lang}/{pid}: no text for {{{{{key}}}}}")
        return fills[key]

    content = (SRC / "pages" / f"{pid}.html").read_text(encoding="utf-8")
    html = layout.replace("{{content}}", content)
    html = re.sub(r"\{\{(\w+)\}\}", fill, html)
    html = re.sub(r"\{\{(\w+)\}\}", fill, html)  # a page's words may themselves carry {{home}} links
    leak_check(html, f"{lang}/{pid}")
    out = ROOT / home.strip("/") / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    missing = sorted(k for k in {**common["en"], **words[("en", pid)]} if not k.startswith("_") and k not in {**common[lang], **words[(lang, pid)]})
    return missing


report = {}
for pid, *_ in PAGES:
    for lang in LANGS:
        if has(lang, pid):
            missing = build(lang, pid)
            report.setdefault(pid, []).append(lang + (f"({len(missing)} in English)" if missing else ""))
for pid, built in report.items():
    print(f"{pid:26} {' '.join(built)}")
print("stars:", f'{RATING["ratingValue"]} from {RATING["ratingCount"]} ratings' if RATING else "left out")

# sitemap: every page in every language it exists in, each listing its other languages
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for pid, *_ in PAGES:
    langs_here = [l for l in LANGS if has(l, pid)]
    for lang in langs_here:
        lines.append(f"  <url><loc>{url(lang, pid)}</loc><lastmod>{TODAY}</lastmod>")
        for l in langs_here:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{common[l]["_html_lang"]}" href="{url(l, pid)}"/>')
        lines.append("  </url>")
lines += [f"  <url><loc>{SITE}/privacy/</loc><lastmod>{TODAY}</lastmod></url>", "</urlset>", ""]
(ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")
