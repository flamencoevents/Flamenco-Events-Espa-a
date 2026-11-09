#!/usr/bin/env python3
"""Finalize public Spanish website for the custom domain at deployment time."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from html import escape
import re
import xml.etree.ElementTree as ET

ROOT = Path("_site")
DOMAIN = "https://flamencoevents.net"
PAGES = ("index.html", "suite-flamenca.html", "son-del-alma.html",
         "guitarrista-flamenco.html", "eventos-exclusivos.html")

for name in PAGES:
    file = ROOT / name
    html = file.read_text(encoding="utf-8")
    html = re.sub(r'<meta\s+name="robots"\s+content="noindex,nofollow">', '<meta name="robots" content="index,follow">', html, flags=re.I)
    canonical = DOMAIN + ("/" if name == "index.html" else "/" + name)
    html = html.replace("</head>", f'<link rel="canonical" href="{canonical}"></head>', 1)
    if '<meta name="robots" content="index,follow">' not in html:
        raise ValueError(f"Missing production indexing directive in {name}")
    file.write_text(html, encoding="utf-8")

legacy = Path("legacy-urls.txt").read_text(encoding="utf-8").splitlines()
created = 0
for entry in legacy:
    entry = entry.strip()
    if not entry or entry.startswith("#"):
        continue
    path = unquote(urlparse(entry).path).strip("/")
    if not path:
        continue
    if path.startswith("en-gb/") or path == "en-gb":
        lang = "en"
        base = "https://flamencoeventsagency.com/"
    else:
        lang = "es"
        base = DOMAIN + "/"
    label = path.lower()
    if "sondelalma" in label:
        dest = "son-del-alma.html"
    elif "cuadro-de-baile" in label:
        dest = "suite-flamenca.html"
    elif "nachomarroco" in label:
        dest = "guitarrista-flamenco.html"
    elif "servicio-premium" in label or "otros-servicios" in label:
        dest = "eventos-exclusivos.html"
    elif "boda" in label:
        dest = "#bodas"
    else:
        dest = ""
    target = base + dest
    outfile = ROOT / path / "index.html"
    outfile.parent.mkdir(parents=True, exist_ok=True)
    safe = escape(target, quote=True)
    body = ("Esta dirección ha cambiado." if lang == "es" else "This page has moved.")
    outfile.write_text(
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="robots" content="noindex,follow">'
        f'<meta http-equiv="refresh" content="0;url={safe}">'
        f'<link rel="canonical" href="{safe}">'
        f'<title>Flamenco Events</title></head>'
        f'<body><p>{body} <a href="{safe}">{safe}</a></p></body></html>', encoding="utf-8")
    created += 1

(ROOT / "robots.txt").write_text(
    "User-agent: *\nAllow: /\nSitemap: https://flamencoevents.net/sitemap.xml\n", encoding="utf-8"
)
ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", ns)
root = ET.Element(f"{{{ns}}}urlset")
for name in PAGES:
    url = ET.SubElement(root, f"{{{ns}}}url")
    ET.SubElement(url, f"{{{ns}}}loc").text = DOMAIN + ("/" if name == "index.html" else "/" + name)
ET.ElementTree(root).write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)
assert not (ROOT / "portal.html").exists()
assert not (ROOT / "CNAME").exists()
print(f"Prepared {len(PAGES)} indexed commercial pages, {created} legacy HTML forwards, sitemap and robots.")
