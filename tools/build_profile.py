"""Build pixel headers from the portfolio's T-Rex sprite. Requires fonttools."""
import argparse, html, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/profile'
p=argparse.ArgumentParser()
p.add_argument('--cache',type=Path,required=True)
args=p.parse_args()
args.cache.mkdir(parents=True,exist_ok=True)
fonts={}
for key,name,url in [('pixel','PressStart2P.ttf','pressstart2p/PressStart2P-Regular.ttf'),('mono','GeistMono.ttf','geistmono/GeistMono%5Bwght%5D.ttf')]:
    f=args.cache/name
    if not f.exists():
        urllib.request.urlretrieve('https://raw.githubusercontent.com/google/fonts/main/ofl/'+url,f)
    fonts[key]=TTFont(f)
def text(value,x,y,size,kind='mono',color='#eeece6'):
    f=fonts[kind];gs=f.getGlyphSet();cm=f.getBestCmap();s=size/f['head'].unitsPerEm;parts=[]
    for char in value:
        glyph=gs[cm[ord(char)]];pen=SVGPathPen(gs);glyph.draw(pen)
        if pen.getCommands():
            parts.append(f'<path transform="translate({x:.3f} {y}) scale({s:.6f} {-s:.6f})" d="{pen.getCommands()}"/>')
        x+=glyph.width*s
    return f'<g fill="{color}">'+''.join(parts)+'</g>'
# Same body and running poses as portfolio DinoPreloader.tsx.
BODY=['                  ######### ','                 ### # #####','                 ###########','                 ###########','                 ########   ','                 ###########',' #              ########    ',' ##            #########    ',' ###          ##########    ',' ####        ###########    ',' ######     ############    ','  #####################     ','   ###################      ','    #################       ','     ###############        ','      #############         ','       ###########          ','        #########           ']
POSES=[BODY+['         ##  ##','         ##   #','         #','         ##'],BODY+['         ##  ##','          #  ##','              #','             ##']]
def sprite(rows,x,y,u):
    return '<g fill="#eeece6" shape-rendering="crispEdges">'+''.join(f'<rect x="{x+c*u}" y="{y+r*u}" width="{u}" height="{u}"/>' for r,row in enumerate(rows) for c,char in enumerate(row) if char=='#')+'</g>'
for mobile in (False,True):
    w,h=(720,280) if mobile else (1200,270)
    x=32 if mobile else 44
    content=f'<rect width="{w}" height="{h}" fill="#080808"/>'
    content+=text('> JEUSH SAMUEL BANTAYAON',x,35,16,color='#a8b0ad')
    content+=text('JEUSHDEV',x,145 if mobile else 157,66 if mobile else 88,'pixel')
    dx,dy,u=(590,182,2.5) if mobile else (1010,92,4)
    for i,pose in enumerate(POSES):
        content+=f'<g class="frame frame-{i}">'+sprite(pose,dx,dy,u)+'</g>'
    line=248 if mobile else 204
    content+=f'<path d="M {x} {line} H {w-x}" stroke="#434b48" stroke-dasharray="9 8"/>'
    if mobile:
        content+=text('FULL-STACK DEVELOPMENT',x,198,19)
        content+=text('AI & WORKFLOW AUTOMATION',x,228,19)
    else:
        content+=text('FULL-STACK DEVELOPMENT / AI & WORKFLOW AUTOMATION',x,243,20)
    style='<style>.frame-1{opacity:0}.frame-0{animation:step0 .28s steps(1,end) infinite}.frame-1{animation:step1 .28s steps(1,end) infinite}@keyframes step0{0%,100%{opacity:1}50%{opacity:0}}@keyframes step1{0%,100%{opacity:0}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.frame{animation:none}.frame-1{opacity:0}}</style>'
    label='jeushdev — Full-stack development, AI and workflow automation. Pixel T-Rex from the portfolio intro.'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}"><title>{html.escape(label)}</title>{style}{content}</svg>\n'
    (OUT/('hero-mobile.svg' if mobile else 'hero.svg')).write_text(svg,encoding='utf-8')
print('Built desktop and mobile pixel headers.')
