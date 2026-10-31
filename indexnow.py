#!/usr/bin/env python3
"""Tells Bing (and the other IndexNow search engines: Yandex, Seznam, Naver) about every page in sitemap.xml.

Run after a push, once GitHub Pages has published:  python3 indexnow.py
The key is meant to be public: it only proves this site owns the list of URLs. Its file is 4fe2911e5dceae32b85ba498ee5546e4.txt at the root.
"""
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
KEY = "4fe2911e5dceae32b85ba498ee5546e4"
urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
body = json.dumps({"host": "ilovebookworm.com", "key": KEY, "keyLocation": f"https://ilovebookworm.com/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=20) as r:
    print(r.status, f"sent {len(urls)} URLs")  # 200 or 202 means accepted
