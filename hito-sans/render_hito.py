from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb
import base64,json,html
ROOT=Path(__file__).resolve().parent
WORDS=[('hito.ai','hito-ai-domain'),('hitokey','hitokey-lowercase'),('HitoKey','hitokey-titlecase'),('HitoAI','hitoai-titlecase'),('hito','hito-lowercase'),('Hito','hito-titlecase')]
def font(style='Regular',size=30):return ImageFont.truetype(str(ROOT/f'fonts/HitoSans-{style}.ttf'),size)
def label_font(size):
    for name in ('DejaVuSans.ttf','Arial.ttf'):
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default(size=size)
def vectors():
    p=ROOT/'fonts/HitoSans-Semibold.ttf';f=TTFont(p);gs=f.getGlyphSet();order=f.getGlyphOrder()
    h=hb.Font(hb.Face(p.read_bytes()));h.scale=(2048,2048)
    for word,filename in WORDS:
        b=hb.Buffer();b.add_str(word);b.guess_segment_properties();hb.shape(h,b,{'kern':True})
        x=0;paths=[];bounds=[]
        for info,pos in zip(b.glyph_infos,b.glyph_positions):
            name=order[info.codepoint];pen=SVGPathPen(gs);gs[name].draw(pen)
            bp=BoundsPen(gs);gs[name].draw(bp)
            dx=x+pos.x_offset;dy=pos.y_offset
            if bp.bounds:
                a,c,e,g=bp.bounds;bounds.append((dx+a,-dy-g,dx+e,-dy-c))
            paths.append(f'<path transform="translate({dx} {-dy}) scale(1 -1)" d="{pen.getCommands()}"/>')
            x+=pos.x_advance
        x0=min(b[0] for b in bounds)-100;y0=min(b[1] for b in bounds)-100
        x1=max(b[2] for b in bounds)+100;y1=max(b[3] for b in bounds)+100
        w=x1-x0;hh=y1-y0
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {hh}" width="{round(w/hh*180)}" height="180" role="img" aria-label="{html.escape(word)}"><title>{html.escape(word)} — Hito Sans Semibold</title><g fill="#17231f">'+''.join(paths)+'</g></svg>'
        (ROOT/f'wordmarks/{filename}-outlined.svg').write_text(svg)
        # The live-text version remains editable as text with Hito Sans installed.
        live=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x+200} 2150"><title>{html.escape(word)} — editable text</title><text x="100" y="1670" fill="#17231f" font-family="Hito Sans" font-size="2048" font-weight="600" style="font-kerning:normal">{html.escape(word)}</text></svg>'
        (ROOT/f'wordmarks/{filename}-editable-text.svg').write_text(live)

def render():
    im=Image.new('RGB',(1800,1820),'#f3f5f1');d=ImageDraw.Draw(im)
    def text(x,y,s,size=24,style='Regular',fill='#17231f',usefont=None):
        d.text((x,y),s,font=usefont or font(style,size),fill=fill)
    text(70,42,'Hito Sans',54,'Semibold')
    text(70,125,'A tailored family for human approval and control.',27)
    for i,(word,_) in enumerate(WORDS[:4]):
        col=i%2;row=i//2;x=70+col*850;y=245+row*270
        text(x,y,'0'+str(i+1)+'  /  '+['DOMAIN','LOWERCASE','PRODUCT','AI NAME'][i],18,fill='#728177',usefont=label_font(18))
        text(x,y+45,word,126,'Semibold')
    d.line((70,840,1730,840),fill='#c9d2c9',width=2)
    text(70,879,'Same roots. Different character.',38,'Medium')
    gs=ImageFont.truetype(str(ROOT/'source/GroundStateSans-Semibold.ttf'),64)
    text(70,965,'GROUNDSTATE SANS',17,fill='#728177',usefont=label_font(17))
    text(70,1003,'Clarity Wallet  HitoAI  Il1',usefont=gs)
    text(70,1114,'HITO SANS',17,fill='#728177',usefont=label_font(17))
    text(70,1152,'Clarity Wallet  HitoAI  Il1',64,'Semibold')
    d.line((70,1277,1730,1277),fill='#c9d2c9',width=2)
    text(70,1320,'Your tools ask. You decide.',47,'Medium')
    text(70,1401,'Review the request. Approve with your key.',29)
    text(70,1458,'HitoKey  /  Request details  /  Approve  /  Cancel',21)
    text(70,1526,'Größe · clé privée · ação · Ī Í Ï · Il1 · 0O · 0123456789',29)
    text(70,1620,'Softly squared bowls. Rounded-square dots. A compact barred I.',23,fill='#728177')
    text(70,1671,'Regular · Medium · Semibold · Bold · ExtraBold · Black',21,fill='#728177')
    text(70,1713,'Development version 0.101 — derived from GroundState Sans and Inter.',19,fill='#728177')
    im.save(ROOT/'hito-sans-specimen.png')
    # Compare reading at small sizes and across weights.
    im=Image.new('RGB',(1650,1740),'white');d=ImageDraw.Draw(im)
    for row,style in enumerate(['Regular','Medium','Semibold']):
        y=40+row*570
        d.text((45,y),style,font=label_font(23),fill='#728177');y+=50
        for size in [14,16,20,32,48,72]:
            s='Clarity Wallet · HitoAI · Il1 0O'
            d.text((45,y),str(size)+'px',font=label_font(14),fill='#728177')
            d.text((110,y),s,font=font(style,size),fill='#17231f');y+=size+23
        d.text((110,y+10),'Í Î Ï Ĩ Ī Ĭ Į İ · í ï ī · ö ó õ ő · Ķ ķ · ý ÿ',font=font(style,28),fill='#17231f')
    im.save(ROOT/'hito-reading-accents.png')
    # Offline interactive specimen with exact installed font bytes.
    faces=''
    for style,weight in [('Regular',400),('Medium',500),('Semibold',600),('Bold',700),('ExtraBold',800),('Black',900)]:
        data=base64.b64encode((ROOT/f'fonts/HitoSans-{style}.woff2').read_bytes()).decode()
        faces+=f'@font-face{{font-family:Hito;src:url(data:font/woff2;base64,{data});font-weight:{weight}}}'
    gsdata=base64.b64encode((ROOT/'source/GroundStateSans-Regular.ttf').read_bytes()).decode()
    faces+='@font-face{font-family:GroundState;src:url(data:font/ttf;base64,'+gsdata+')}'
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Hito Sans specimen</title><style>'''+faces+'''body{max-width:1100px;margin:48px auto;padding:0 24px;background:#f3f5f1;color:#17231f;font:18px system-ui}h1{font:600 48px Hito}.names{display:grid;grid-template-columns:1fr 1fr;gap:25px}.name{font:600 clamp(40px,7vw,80px) Hito;border-top:1px solid #c9d2c9;padding:25px 0}textarea{box-sizing:border-box;width:100%;min-height:110px;padding:16px;font:22px Hito;background:white;border:1px solid #bec8bd;border-radius:8px}.controls{display:flex;flex-wrap:wrap;gap:25px;margin:24px 0}select{font:inherit}.sample{font:48px/1.5 Hito;overflow-wrap:anywhere;white-space:pre-wrap}.label{font-size:13px;letter-spacing:.08em;color:#728177}section{border-top:1px solid #c9d2c9;padding:24px 0}a{color:inherit}small{color:#728177}@media(max-width:650px){.names{grid-template-columns:1fr}}</style><h1>Hito Sans</h1><p>A tailored branch of GroundState Sans for Hito and HitoKey.</p><div class="names"><div class="name">hito.ai</div><div class="name">hitokey</div><div class="name">HitoKey</div><div class="name">HitoAI</div></div><section><textarea id="copy">HitoKey — Your tools ask. You decide.
HitoAI · hito.ai · hitokey · Il1 · 0O</textarea><div class="controls"><label>Size <input id="size" type="range" min="14" max="110" value="48"><output id="px">48px</output></label><label>Weight <select id="weight"><option>400</option><option>500</option><option selected>600</option></select></label><label><input id="kern" type="checkbox" checked>Kerning</label></div><div id="sample" class="sample"></div></section><section><p class="label">READING AND ACCENTS</p><div style="font:24px/1.8 Hito">Review the request. Approve with your key.<br>Größe · clé privée · ação · Í Ï Ī İ · Ķ ķ · ý ÿ<br>Il1 0O · 0123456789 · € 12,50 · Ваши ключи</div></section><small>0.1 development build. Three static weights. The outlined SVG wordmarks require no font installation; editable text SVGs require Hito Sans. See README for validation and licensing.</small><script>const c=document.getElementById('copy'),s=document.getElementById('size'),w=document.getElementById('weight'),k=document.getElementById('kern'),p=document.getElementById('sample');function update(){p.textContent=c.value;p.style.fontSize=s.value+'px';p.style.fontWeight=w.value;p.style.fontKerning=k.checked?'normal':'none';document.getElementById('px').textContent=s.value+'px'}[c,s,w,k].forEach(e=>e.addEventListener('input',update));update()</script></html>'''
    page=page.replace('HitoAI · hito.ai · hitokey · Il1 · 0O</textarea>', 'Clarity Wallet · HitoAI · Il1 · 0O</textarea>')
    page=page.replace('<option selected>600</option></select>', '<option selected>600</option><option>700</option><option>800</option><option>900</option></select>')
    page=page.replace('0.1 development build. Three static weights.', '0.101 development build. Six static weights.')
    (ROOT/'specimen.html').write_text(page)
if __name__=='__main__':vectors();render()

