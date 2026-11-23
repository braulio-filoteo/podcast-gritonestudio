import re,json,html,unicodedata,os,shutil
SRC='/home/claude/art/project/Main.dc.html'
s=open(SRC).read()
eps=json.loads(re.search(r'const all=(\[.*?\]);\n',s,re.S).group(1))
BASE='https://podcast.gritonestudio.com'
OUT='/home/claude/site'
esc=html.escape
for e in eps:
    e['n']=e['n'].lower()
    if e['n']=='bono': e['n']='bono-116'; e['h']='Bono #116 | '+e['h']
    if e['n']=='trailer': e['h']='Tráiler de GRITones con Braulio Filoteo'
def slug(t):
    t=unicodedata.normalize('NFD',t.lower());t=''.join(c for c in t if unicodedata.category(c)!='Mn')
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',t)).strip('-')[:80]
def iso(d):
    dd,mm,yy=d.split('.');return f'{yy}-{mm}-{dd}'
def dur(u):
    p=[int(x) for x in u.split(':')]
    if len(p)==2:p=[0]+p
    h,m,sec=p;return 'PT'+(f'{h}H' if h else '')+(f'{m}M' if m else '')+f'{sec}S'
for e in eps:
    n=e['n']; e['slug']=(n+'-'+slug(e['h'])) if n[0].isdigit() else slug(n)+'-'+slug(e['h']) if n!='trailer' else 'trailer'
    if n=='trailer': e['slug']='tráiler'.replace('á','a')
    e['title']=e['h']
    if n=='trailer': e['slug']='trailer'
    if n.startswith('bono'): e['slug']='bono-116-la-historia-del-album-panini'
FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@900&family=Inter:wght@400;500;700&family=Instrument+Serif:ital@1&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">'
CSS='''body{margin:0;background:#F2F2F0;font-family:Inter,system-ui,sans-serif;color:#111}a{color:#111}a:hover{color:#C23B00}
.mono{font-family:'Space Mono',monospace;font-size:13px;letter-spacing:.5px;text-transform:uppercase}
.btn{display:inline-flex;align-items:center;gap:10px;padding:14px 22px;font-family:'Space Mono',monospace;font-size:13px;text-transform:uppercase;text-decoration:none;border:1px solid #111;color:#111}
.btn.pri{background:#FE6500}.btn:hover{color:#111;background:#FE6500}
.chip{cursor:pointer;border:1px solid #111;background:transparent;color:#111;padding:10px 14px;border-radius:0;font-family:'Space Mono',monospace;font-size:12px;text-transform:uppercase;min-height:44px}.chip[aria-pressed=true]{background:#111;color:#F2F2F0}
.ep{display:grid;grid-template-columns:72px minmax(0,1fr);gap:8px 20px;padding:20px 0;border-top:1px solid #111}
.ep .n{font-family:'Space Mono',monospace;font-size:20px;font-weight:700;color:#C23B00}
.ep h3{font-size:22px;font-weight:500;line-height:1.25;margin:0}.ep h3 a{text-decoration:none}
.links{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:10px;font-family:'Space Mono',monospace;font-size:12px;text-transform:uppercase}
.sr{position:absolute;left:-9999px}
@media(max-width:560px){.ep{grid-template-columns:52px minmax(0,1fr)}}'''
YT='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" style="flex:none"><rect x="2" y="5" width="20" height="14" rx="4"/><path d="M10 9l5 3-5 3z" fill="currentColor" stroke="none"/></svg>'
IG='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" style="flex:none"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>'
HEADER=f'''<header style="border-bottom:1px solid #111;padding:14px 32px;display:flex;flex-wrap:wrap;gap:12px 32px;align-items:center;justify-content:space-between">
<a href="/" aria-label="GRITones Podcast, inicio" style="display:flex"><img src="/assets/logo-claro.jpg" width="34" height="34" alt="GRITones con Braulio Filoteo" style="display:block;height:34px;width:auto;mix-blend-mode:multiply"></a>
<nav class="mono" style="display:flex;flex-wrap:wrap;align-items:center;gap:8px 28px"><a href="/#episodios" style="text-decoration:none">Episodios</a><a href="/#receta-grit" style="text-decoration:none">Receta GRIT</a><a href="/#preguntas" style="text-decoration:none">Preguntas</a><a href="https://brauliofiloteo.com" style="text-decoration:none;color:#C23B00">brauliofiloteo.com</a><span style="display:flex;align-items:center;gap:14px"><a href="https://www.youtube.com/@brauliofiloteo" aria-label="Trainings gratis en YouTube" title="Trainings gratis en YouTube" style="display:flex">{YT}</a><a href="https://www.instagram.com/brauliofiloteo/" aria-label="Sígueme en Instagram" title="Sígueme en Instagram" style="display:flex">{IG}</a></span></nav></header>'''
BAND=f'''<section style="background:#111;color:#F2F2F0;padding:56px 28px;text-align:center"><div class="mono" style="font-size:12px;letter-spacing:1px;color:#FF8A4D">Sígueme</div><p style="font-size:clamp(22px,5vw,28px);line-height:1.35;max-width:640px;margin:14px auto 0">¿Tienes una historia que contar? Crea y lanza tu propio podcast con mis trainings gratuitos.</p><div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-top:28px"><a class="btn" href="https://www.youtube.com/@brauliofiloteo" style="background:#FE6500;border-color:#FE6500">{YT}Ver los trainings gratis</a><a class="btn" href="https://ig.me/m/brauliofiloteo" style="border-color:#F2F2F0;color:#F2F2F0">{IG}Escríbeme por Instagram</a></div></section>'''
FOOTER='''<footer style="background:#000;color:#F2F2F0;align-items:center;padding:28px 32px;display:flex;flex-wrap:wrap;gap:16px 24px;justify-content:space-between" class="mono"><img src="/assets/logo-oscuro.jpg" width="160" height="160" alt="GRITones con Braulio Filoteo" style="display:block;width:160px;height:auto"><a href="https://www.instagram.com/brauliofiloteo/" style="color:#F2F2F0">@brauliofiloteo ↗</a><span style="font-size:12px">GRITONES STUDIO™ · © 2024 · Lo que cuentas, cuenta.</span></footer>'''
def page(title,desc,path,body,ld,og_type='website'):
    url=BASE+path
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<link rel="icon" href="/assets/favicon.png" type="image/png"><meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="GRITones Podcast"><meta property="og:locale" content="es_MX"><meta property="og:image" content="{BASE}/assets/logo-claro.jpg"><meta name="twitter:card" content="summary">
<link rel="alternate" type="text/plain" href="/llms.txt">
{FONTS}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script></head><body>
{HEADER}<main>{body}</main>{BAND}{FOOTER}</body></html>'''
SERIES={"@type":"PodcastSeries","@id":BASE+"/#podcast","name":"GRITones con Braulio Filoteo","url":BASE+"/","inLanguage":"es","author":{"@type":"Person","name":"Braulio Filoteo","url":"https://brauliofiloteo.com"},
 "description":"Podcast en español de historias de reinvención, resiliencia y momentos de cambio, conducido por Braulio Filoteo.",
 "sameAs":["https://open.spotify.com/show/181uvsFpNIjS7htYHcft4v","https://podcasts.apple.com/mx/podcast/gritones-con-braulio-filoteo/id1731715409","https://www.youtube.com/@GRITonespodcast","https://www.instagram.com/brauliofiloteo/"]}
def links(e,cls=''):
    out=[]
    if e.get('sp'):out.append(f'<a href="{e["sp"]}" rel="noopener">Spotify ↗</a>')
    if e.get('ap'):out.append(f'<a href="{e["ap"]}" rel="noopener">Apple Podcasts ↗</a>')
    if e.get('yt'):out.append(f'<a href="{e["yt"]}" rel="noopener">YouTube ↗</a>')
    return out
# episode pages
for i,e in enumerate(eps):
    n=e['n']; tag='Tráiler' if n=='trailer' else ('Bono' if n.startswith('bono') else f'Episodio {n.lstrip("0") if n[0].isdigit() and "-" not in n else n}')
    label=tag
    short='Tráiler' if n=='trailer' else e['h']
    title=(f'{e["h"]} | GRITones #{n}' if n[0].isdigit() else f'{e["h"]} | GRITones')[:110]
    desc=f'{e["h"]}. {label} de GRITones con Braulio Filoteo ({e["u"]}, {e["d"]}). Escúchalo en Spotify, Apple Podcasts o YouTube.'
    path=f'/episodio/{e["slug"]}'
    prev=eps[i+1] if i+1<len(eps) else None; nxt=eps[i-1] if i>0 else None
    btns=''.join(f'<a class="btn {"pri" if k==0 else ""}" href="{h}" rel="noopener">{t} ↗</a>' for k,(h,t) in enumerate([(e[x],t) for x,t in (('sp','Escuchar en Spotify'),('ap','Apple Podcasts'),('yt','Ver en YouTube')) if e.get(x)]))
    nav=''.join(f'<a href="/episodio/{x["slug"]}" style="text-decoration:none">{lab} · {esc(x["h"])}</a>' for lab,x in (('← Anterior',prev),('Siguiente →',nxt)) if x)
    body=f'''<article style="padding:48px 32px 72px"><div style="max-width:860px;margin:0 auto"><div class="mono"><a href="/" style="text-decoration:none">GRITones Podcast</a> / {esc(label)}</div>
<h1 style="font-size:clamp(30px,5vw,44px);font-weight:700;line-height:1.12;letter-spacing:-1px;margin:28px 0 24px">{esc(e["h"])}</h1>
<dl style="margin:0;border-top:1px solid #111"><div style="display:grid;grid-template-columns:140px minmax(0,1fr);gap:12px;padding:12px 0;border-bottom:1px solid #111"><dt class="mono" style="color:#555">Publicado</dt><dd style="margin:0"><time datetime="{iso(e["d"])}">{e["d"]}</time></dd></div><div style="display:grid;grid-template-columns:140px minmax(0,1fr);gap:12px;padding:12px 0;border-bottom:1px solid #111"><dt class="mono" style="color:#555">Duración</dt><dd style="margin:0">{e["u"]}</dd></div><div style="display:grid;grid-template-columns:140px minmax(0,1fr);gap:12px;padding:12px 0;border-bottom:1px solid #111"><dt class="mono" style="color:#555">Programa</dt><dd style="margin:0"><a href="/">GRITones con Braulio Filoteo</a>, historias de reinvención, resiliencia y momentos de cambio</dd></div></dl>
<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:32px">{btns}</div>
<nav aria-label="Episodios cercanos" class="mono" style="display:flex;flex-direction:column;gap:12px;margin-top:56px;font-size:12px">{nav}</nav></div></article>'''
    ld={"@context":"https://schema.org","@graph":[SERIES,{"@type":"PodcastEpisode","name":e["h"],"url":BASE+path,"datePublished":iso(e["d"]),"timeRequired":dur(e["u"]),"inLanguage":"es","partOfSeries":{"@id":BASE+"/#podcast"},"author":{"@type":"Person","name":"Braulio Filoteo"},"sameAs":[e[x] for x in ('sp','ap','yt') if e.get(x)]},
      {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"GRITones Podcast","item":BASE+"/"},{"@type":"ListItem","position":2,"name":e["h"],"item":BASE+path}]}]}
    d=f'{OUT}{path}';os.makedirs(d,exist_ok=True);open(d+'/index.html','w').write(page(title,desc,path,body,ld,'article'))
# home
FAQ=[("¿De qué trata GRITones Podcast?","Son conversaciones con personas que transformaron sus momentos más difíciles en fuerza interior: historias de reinvención, resiliencia y momentos de cambio. Lo conduce Braulio Filoteo."),
("¿Dónde encuentro historias de reinvención?","En la lista de episodios, con el buscador: escribe reinvención, resiliencia o el tema que te mueve. Cada episodio tiene su página con enlaces para escucharlo en Spotify, Apple Podcasts y YouTube."),
("¿Cada cuánto sale un episodio nuevo?","Los episodios recientes han salido cada miércoles."),
("¿Dónde puedo escuchar GRITones?","En Spotify, Apple Podcasts y YouTube. Cada episodio de esta página tiene sus enlaces.")]
years=['Todos','2026','2025','2024']
chips=''.join(f'<button class="chip" type="button" data-y="{y}" aria-pressed="{"true" if y=="Todos" else "false"}">{y}</button>' for y in years)
items=''.join(f'<article class="ep" data-y="{e["y"]}" data-t="{esc(e["h"].lower())}"><div class="n">{esc(e["n"] if e["n"][0].isdigit() else ("Bono" if e["n"].startswith("bono") else "Tráiler"))}</div><div><h3><a href="/episodio/{e["slug"]}">{esc(e["h"])}</a></h3><div class="mono" style="font-size:12px;color:#555;margin-top:8px">{e["d"]} · {e["u"]}</div><div class="links">{" ".join(links(e))}</div></div></article>' for e in eps)
receta=[("G","Gente","¿Qué gente confió en ti antes de que tú confiaras en ti?","¿Quién te cerró puertas y quién te las abrió?"),("R","Resiliencia","¿Qué cicatriz nunca borrarías, aunque pudieras?","¿Cuál fue el hoyo más profundo del que has salido?"),("I","Impacto","¿A cuánta gente has impactado sin darte cuenta, en tu metro cuadrado?","¿Quién ha impactado en ti?"),("T","Trascendencia","¿Qué quieres que digan de ti cuando no estás en la habitación?","¿Qué quieres dejarles a tus hijos más allá de lo material y los éxitos?")]
rec=''.join(f'<div style="border-top:1px solid #111;padding:20px 0"><div style="font-family:Epilogue,sans-serif;font-weight:900;font-size:44px;line-height:1;color:#C23B00">{l}</div><h3 style="font-size:22px;margin:8px 0 10px">{n}</h3><p style="margin:0 0 8px;font-size:17px;line-height:1.45">{a}</p><p style="margin:0;font-size:17px;line-height:1.45">{b}</p></div>' for l,n,a,b in receta)
faq=''.join(f'<div style="border-top:1px solid #111;padding:22px 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px 32px"><h3 style="font-size:20px;font-weight:700;margin:0">{q}</h3><p style="font-size:17px;line-height:1.55;color:#333;margin:0">{a}</p></div>' for q,a in FAQ)
home=f'''<section style="padding:96px 32px 72px"><div style="max-width:1120px;margin:0 auto"><h1 style="font-family:'Space Mono',monospace;font-weight:400;font-size:clamp(22px,4vw,28px);line-height:1.4;margin:0;max-width:760px">Historias de reinvención, resiliencia y momentos de cambio. Más de 140 conversaciones.</h1>
<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:32px"><a class="btn pri" href="https://open.spotify.com/show/181uvsFpNIjS7htYHcft4v" rel="noopener">Escuchar en Spotify ↗</a><a class="btn" href="https://www.youtube.com/@GRITonespodcast" rel="noopener">Ver en YouTube ↗</a><a class="btn" href="https://podcasts.apple.com/mx/podcast/gritones-con-braulio-filoteo/id1731715409" rel="noopener">Apple Podcasts ↗</a></div></div></section>
<section id="episodios" style="padding:0 32px 72px"><div style="max-width:1120px;margin:0 auto"><label for="q" class="mono" style="display:block;margin-bottom:12px">Buscar en las {len(eps)} historias</label><input id="q" type="search" placeholder="Escribe un tema, un invitado o una palabra" style="width:100%;box-sizing:border-box;border:1px solid #111;background:#fff;padding:16px;font-family:Inter,sans-serif;font-size:18px;border-radius:0;margin-bottom:16px"><div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:28px">{chips}</div><div id="list">{items}</div><p id="empty" hidden>Sin resultados. Prueba con otra palabra o con “Todos”.</p><p class="mono" style="font-size:12px;color:#555;margin-top:20px">{len(eps)} episodios publicados, incluidos un tráiler y un episodio bono.</p></div></section>
<section id="receta-grit" style="padding:0 32px 72px"><div style="max-width:1120px;margin:0 auto"><h2 class="mono" style="font-weight:700;margin:0 0 12px">La Receta GRIT</h2><p style="font-size:20px;line-height:1.5;max-width:640px;margin:0 0 24px">Cuatro letras, cuatro preguntas. Cada conversación de GRITones las recorre.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:0 32px">{rec}</div><p class="mono" style="font-size:12px;color:#555;margin-top:24px">También se buscan por: resiliencia · reinvención · reinventarse · momentos de cambio · historias de vida · emprendimiento · coraje personal · grit · propósito · marca personal</p></div></section>
<section id="preguntas" style="padding:0 32px 80px"><div style="max-width:1120px;margin:0 auto"><h2 class="mono" style="font-weight:700;margin:0 0 16px">Preguntas frecuentes</h2>{faq}<div style="border-top:1px solid #111"></div></div></section>
<script>(function(){{var y='Todos',q='',L=[].slice.call(document.querySelectorAll('#list .ep')),E=document.getElementById('empty');function norm(s){{return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase()}}function run(){{var v=0;L.forEach(function(e){{var ok=(y==='Todos'||e.dataset.y===y)&&(!q||norm(e.dataset.t).indexOf(q)>=0);e.hidden=!ok;if(ok)v++}});E.hidden=v>0}}document.getElementById('q').addEventListener('input',function(e){{q=norm(e.target.value).trim();run()}});[].forEach.call(document.querySelectorAll('.chip'),function(b){{b.addEventListener('click',function(){{y=b.dataset.y;[].forEach.call(document.querySelectorAll('.chip'),function(c){{c.setAttribute('aria-pressed',c===b?'true':'false')}});run()}})}})}})();</script>'''
ld={"@context":"https://schema.org","@graph":[SERIES,{"@type":"WebSite","name":"GRITones Podcast","url":BASE+"/","inLanguage":"es","publisher":{"@type":"Organization","name":"GRITones Studio LLC"}},
 {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]},
 {"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":BASE+f'/episodio/{e["slug"]}',"name":e["h"]} for i,e in enumerate(eps)]}]}
open(OUT+'/index.html','w').write(page('GRITones Podcast con Braulio Filoteo: historias de reinvención, resiliencia y momentos de cambio','Podcast en español de historias de reinvención, resiliencia y momentos de cambio. Más de 140 conversaciones con Braulio Filoteo sobre emprendimiento, coraje personal y grit.','/',home,ld))
# sitemap etc
urls=['/']+[f'/episodio/{e["slug"]}' for e in eps]
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}{u}</loc>'+(f'<lastmod>{iso(next(e["d"] for e in eps if "/episodio/"+e["slug"]==u))}</lastmod>' if u!='/' else '')+'</url>\n' for u in urls)+'</urlset>\n')
open(OUT+'/robots.txt','w').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
open(OUT+'/llms.txt','w').write(f'''# GRITones con Braulio Filoteo
> Podcast en español de historias de reinvención, resiliencia y momentos de cambio. Conducido por Braulio Filoteo (GRITones Studio LLC). Más de 140 conversaciones sobre emprendimiento, coraje personal y grit.

- Sitio: {BASE}/
- Spotify: https://open.spotify.com/show/181uvsFpNIjS7htYHcft4v
- Apple Podcasts: https://podcasts.apple.com/mx/podcast/gritones-con-braulio-filoteo/id1731715409
- YouTube: https://www.youtube.com/@GRITonespodcast
- Braulio Filoteo: https://brauliofiloteo.com

## Episodios
'''+''.join(f'- [{e["h"]}]({BASE}/episodio/{e["slug"]}): {e["d"]}, {e["u"]}\n' for e in eps))
open(OUT+'/vercel.json','w').write(json.dumps({"cleanUrls":True,"trailingSlash":False,"headers":[{"source":"/assets/(.*)","headers":[{"key":"Cache-Control","value":"public, max-age=31536000, immutable"}]}]},indent=1))
print(len(eps),'episodios')
