#!/usr/bin/env python3
"""Añade al sitio los episodios nuevos que aparezcan en el feed de Libsyn.
Datos que salen solos: título, fecha, duración (Libsyn) y enlace de YouTube (feed público del canal).
Apple Podcasts: se intenta con la consulta pública de iTunes. Spotify: solo si hay credenciales (SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET).
Lo que no se encuentra queda vacío y se anota en PENDIENTES.md; jamás se inventa un enlace."""
import os,re,json,sys,base64,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
HERE=os.path.dirname(os.path.abspath(__file__))
FEED=os.environ.get('LIBSYN_RSS','https://feeds.libsyn.com/511708/rss')
YT_CHANNEL='UCa_OLA8xEhZtSo0rYbUHhqA'
APPLE_ID='1731715409'; SPOTIFY_SHOW='181uvsFpNIjS7htYHcft4v'
TZ=ZoneInfo('America/Cancun')
ITUNES='{http://www.itunes.com/dtds/podcast-1.0.dtd}'
def get(url,headers=None):
    req=urllib.request.Request(url,headers=headers or {'User-Agent':'gritones-site-updater'})
    return urllib.request.urlopen(req,timeout=30).read()
def num_from(text):
    m=re.search(r'#\s*0*(\d{1,3})(?:-(\d))?\b',text) or re.search(r'[Ee]pisodio\s*#?\s*0*(\d{1,3})(?:-(\d))?\b',text)
    return (f'{int(m.group(1)):03d}'+(f'-{m.group(2)}' if m.group(2) else '')) if m else None
def clean_title(t):
    t=re.sub(r'^[^\w#]+','',t).strip()
    t=re.sub(r'^(Episodio\s*)?#?\s*\d{1,3}(-\d)?\s*[:.\-–—]\s*','',t,flags=re.I).strip()
    return t
def norm_dur(v):
    v=(v or '').strip()
    if v.isdigit():
        s=int(v);return f'{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}'
    p=v.split(':')
    if len(p)==2:p=['0']+p
    return ':'.join(f'{int(x):02d}' for x in p) if len(p)==3 and all(x.isdigit() for x in p) else None
def libsyn_items(xml_bytes):
    root=ET.fromstring(xml_bytes); out=[]
    for it in root.iter('item'):
        title=(it.findtext('title') or '').strip()
        ep=(it.findtext(ITUNES+'episode') or '').strip()
        n=num_from(title) or (f'{int(ep):03d}' if ep.isdigit() else None)
        dt=parsedate_to_datetime(it.findtext('pubDate')).astimezone(TZ)
        out.append({'n':n,'raw':title,'h':clean_title(title),'d':dt.strftime('%d.%m.%Y'),'y':str(dt.year),'u':norm_dur(it.findtext(ITUNES+'duration'))})
    return out
def youtube_links():
    try:
        root=ET.fromstring(get(f'https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL}'))
    except Exception as ex:
        print('YouTube no disponible:',ex);return {}
    ns={'a':'http://www.w3.org/2005/Atom'};res={}
    for e in root.findall('a:entry',ns):
        t=e.findtext('a:title',namespaces=ns) or '';n=num_from(t)
        l=e.find('a:link',ns)
        if n and l is not None:res[n]=l.get('href')
    return res
def apple_links():
    try:
        d=json.loads(get(f'https://itunes.apple.com/lookup?id={APPLE_ID}&entity=podcastEpisode&limit=200'))
    except Exception as ex:
        print('Apple no disponible:',ex);return {}
    res={}
    for r in d.get('results',[]):
        if r.get('wrapperType')!='podcastEpisode':continue
        n=num_from(r.get('trackName',''));u=r.get('trackViewUrl','')
        if n and u:res[n]=u.split('&uo=')[0]
    return res
def spotify_links():
    cid,sec=os.environ.get('SPOTIFY_CLIENT_ID'),os.environ.get('SPOTIFY_CLIENT_SECRET')
    if not (cid and sec):return {}
    try:
        tok=json.loads(urllib.request.urlopen(urllib.request.Request('https://accounts.spotify.com/api/token',data=b'grant_type=client_credentials',headers={'Authorization':'Basic '+base64.b64encode(f'{cid}:{sec}'.encode()).decode()}),timeout=30).read())['access_token']
        res={};url=f'https://api.spotify.com/v1/shows/{SPOTIFY_SHOW}/episodes?limit=50&market=MX'
        while url:
            d=json.loads(get(url,{'Authorization':'Bearer '+tok}))
            for e in d['items']:
                n=num_from(e['name'])
                if n:res[n]=e['external_urls']['spotify']
            url=d.get('next')
        return res
    except Exception as ex:
        print('Spotify no disponible:',ex);return {}
def main():
    eps=json.load(open(os.path.join(HERE,'episodes.json'),encoding='utf-8'))
    hold=set(json.load(open(os.path.join(HERE,'hold.json'))))
    src=os.environ.get('LIBSYN_RSS_FILE')
    items=libsyn_items(open(src,'rb').read() if src else get(FEED))
    known={e['n'].lower() for e in eps}
    yt,ap,sp=youtube_links(),apple_links(),spotify_links()
    new=[];notes=[]
    for it in items:
        if it['n'] is None:
            notes.append(f'Sin número reconocible en el feed: «{it["raw"]}» (no se agregó)');continue
        if it['n'] in known:continue
        if it['n'] in hold or str(int(it['n'][:3])) in hold:
            notes.append(f'#{it["n"]} está en hold.json (no se publica hasta que lo quites)');continue
        if not it['u']:
            notes.append(f'#{it["n"]}: el feed no trae duración (no se agregó)');continue
        e={'n':it['n'],'h':it['h'],'d':it['d'],'y':it['y'],'u':it['u']}
        if it['n'] in yt:e['yt']=yt[it['n']]
        if it['n'] in ap:e['ap']=ap[it['n']]
        if it['n'] in sp:e['sp']=sp[it['n']]
        new.append(e);notes.append(f'#{it["n"]} agregado: «{it["raw"]}» → título del sitio «{it["h"]}» (revisar formato «Invitado | Tema»)')
    # completar enlaces que faltaban en los 12 más recientes
    for e in eps[:12]:
        for k,src_d in (('yt',yt),('ap',ap),('sp',sp)):
            if not e.get(k) and e['n'] in src_d:e[k]=src_d[e['n']];notes.append(f'#{e["n"]}: se completó el enlace {k}')
    if len(new)>3:
        lista=', '.join('#'+e['n'] for e in new)
        notes=[n for n in notes if ' agregado: ' not in n]
        notes.append(f'ALTO: el feed trae {len(new)} episodios nuevos de golpe; por seguridad no se agregó ninguno. Revisa a mano: '+lista)
        new=[]
    if new:
        new.sort(key=lambda e:(e['y'],e['d'].split('.')[1],e['d'].split('.')[0]),reverse=True)
        eps=new+eps
    if new or any('se completó' in n for n in notes):
        json.dump(eps,open(os.path.join(HERE,'episodes.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    missing=[f'#{e["n"]} sin {", ".join(l for k,l in (("sp","Spotify"),("ap","Apple"),("yt","YouTube")) if not e.get(k))}' for e in eps[:12] if not all(e.get(k) for k in ('sp','ap','yt'))]
    with open(os.path.join(HERE,'PENDIENTES.md'),'w',encoding='utf-8') as f:
        f.write('# Pendientes del sitio\n\nGenerado automáticamente en cada revisión.\n\n## Enlaces que faltan (12 episodios más recientes)\n'+('\n'.join('- '+m for m in missing) or '- Ninguno')+'\n\n## Notas de la última revisión\n'+('\n'.join('- '+n for n in notes) or '- Sin cambios')+'\n')
    print('\n'.join(notes) or 'Sin cambios');print('nuevos:',len(new))
    if new or any('se completó' in n for n in notes):os.system(f'{sys.executable} {os.path.join(HERE,"site_build.py")}')
main()
