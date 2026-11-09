#!/usr/bin/env python3
"""Sanity-check the isolated Spanish-language Agency staging site."""
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PAGES = ("index.html", "suite-flamenca.html", "son-del-alma.html",
         "guitarrista-flamenco.html", "eventos-exclusivos.html")
class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("src", "href"):
            url = a.get(key)
            if url and tag in ("a", "img", "script", "link", "source"):
                self.urls.append(url)

issues = []
for name in PAGES:
    p = ROOT / name
    if not p.exists():
        issues.append(f"Missing page {name}")
        continue
    html = p.read_text(encoding="utf-8")
    if '<html lang="es">' not in html or 'noindex,nofollow' not in html:
        issues.append(f"Spanish language or preview safety missing: {name}")
    if '../portal.html' in html or 'supabase' in html.lower():
        issues.append(f"Private application reference: {name}")
    refs = References()
    refs.feed(html)
    for url in refs.urls:
        if url.startswith(("https://", "http://", "mailto:", "tel:", "#", "data:")):
            continue
        local = url.split("#", 1)[0].split("?", 1)[0]
        if local and not (ROOT / local).is_file():
            issues.append(f"{name}: broken internal reference {url}")
    if 'flamencoeventsagency.com' not in html:
        issues.append(f"English sister domain missing on {name}")
if (ROOT / "CNAME").exists():
    issues.append("Custom domain must remain unattached in staging")
robots = ROOT / "robots.txt"
if not robots.is_file() or "Disallow: /" not in robots.read_text(encoding="utf-8"):
    issues.append("Staging must block indexing")
for p in (ROOT / "assets").rglob("*"):
    if not p.is_file():
        continue
    b = p.read_bytes()
    valid = ((p.suffix.lower() in (".jpg", ".jpeg") and b.startswith(bytes.fromhex("ffd8ff")))
             or (p.suffix.lower() == ".png" and b.startswith(bytes.fromhex("89504e470d0a1a0a")))
             or (p.suffix.lower() == ".webp" and b[:4] == b"RIFF" and b[8:12] == b"WEBP"))
    if not valid:
        issues.append(f"Invalid asset signature {p}")
if issues:
    print("\n".join(issues), file=sys.stderr)
    raise SystemExit(1)
print("Spanish Agency staging validated: five pages, internal links, media and no private portal.")
