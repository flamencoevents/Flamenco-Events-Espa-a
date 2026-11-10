from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PAGES=["index.html","catalogo.html","quienes-somos.html","contacto.html","espacio-cliente.html"]
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for attr in ("href","src"):
   if attr in a:self.links.append(a[attr])
for p in PAGES:
 f=ROOT/p;assert f.exists(),p
 s=f.read_text(encoding="utf-8")
 assert '<html lang="es">' in s and 'noindex,nofollow' in s,p
 assert "portal.html" not in s and "supabase" not in s.lower(),p
 parser=Links();parser.feed(s)
 for url in parser.links:
  if url.startswith(("http","mailto:","tel:","#")):continue
  assert (ROOT/url.split("#")[0]).exists(),(p,url)
assert not (ROOT/"CNAME").exists()
assert "Disallow: /" in (ROOT/"robots.txt").read_text()
print("Show Planner Spain: 5 páginas validadas. Sin conexiones privadas ni indexación.")
