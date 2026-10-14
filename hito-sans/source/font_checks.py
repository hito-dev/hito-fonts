from pathlib import Path
from functools import lru_cache
import unicodedata,json,hashlib
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.affinity import translate
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
class FlattenPen(BasePen):
    def __init__(self,glyphset):
        super().__init__(glyphset);self.contours=[];self.current=[]
    def _moveTo(self,p):self.current=[p]
    def _lineTo(self,p):self.current.append(p)
    def _qCurveToOne(self,c,p):
        a=self._getCurrentPoint()
        for i in range(1,17):
            t=i/16;self.current.append(((1-t)**2*a[0]+2*t*(1-t)*c[0]+t*t*p[0],(1-t)**2*a[1]+2*t*(1-t)*c[1]+t*t*p[1]))
    def _curveToOne(self,b,c,p):
        a=self._getCurrentPoint()
        for i in range(1,17):
            t=i/16;u=1-t;self.current.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*p[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*p[1]))
    def _closePath(self):
        if self.current:self.contours.append(self.current);self.current=[]
    _endPath=_closePath
class Font:
    def __init__(self,path):
        self.path=path;self.f=TTFont(path);self.hb=hb.Font(hb.Face(path.read_bytes()));self.hb.scale=(2048,2048)
        self.gs=self.f.getGlyphSet();self.names=self.f.getGlyphOrder()
    def shape(self,text,kern=True):
        b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(self.hb,b,{'kern':kern})
        return [(self.names[i.codepoint],p.x_advance,p.y_advance,p.x_offset,p.y_offset) for i,p in zip(b.glyph_infos,b.glyph_positions)]
    @lru_cache(None)
    def geom(self,name):
        pen=FlattenPen(self.gs);self.gs[name].draw(pen);rings=[]
        for pts in pen.contours:
            if len(pts)<3:continue
            area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2
            polygon=Polygon(pts)
            rings.append((area,polygon if polygon.is_valid else polygon.buffer(0)))
        if not rings:return Polygon()
        sign=1 if max(rings,key=lambda x:abs(x[0]))[0]>0 else -1
        outer=unary_union([p for a,p in rings if a*sign>0])
        inner=unary_union([p for a,p in rings if a*sign<0])
        return outer.difference(inner)
    def collision(self,text):
        shapes=[];x=0
        for name,adv,ya,xo,yo in self.shape(text):
            shapes.append(translate(self.geom(name),x+xo,yo));x+=adv
        return sum(shapes[i].intersection(shapes[j]).area for i in range(len(shapes)) for j in range(i+1,len(shapes)))
def main():
    summary=[];failures=[]
    changes=json.loads((ROOT/'design-changes.json').read_text())
    for change in changes:
        style=change['style'];new=Font(ROOT/f'fonts/GroundStateSans-{style}.ttf');old=Font(ROOT/f'source/Inter-{style}.ttf')
        assert new.f.getBestCmap()==old.f.getBestCmap()
        assert all(new.f['name'].getDebugName(i).startswith('GroundState') for i in [1,4,6])
        for ext in ['woff','woff2']:assert TTFont(ROOT/f'fonts/GroundStateSans-{style}.{ext}').getBestCmap()==new.f.getBestCmap()
        accents=[]
        for cp in new.f.getBestCmap():
            char=chr(cp);nfd=unicodedata.normalize('NFD',char)
            if 'LATIN' in unicodedata.name(char,'') and len(nfd)>1:
                accents.append(char)
                if new.shape(char)!=new.shape(nfd):failures.append([style,'nfc_nfd_mismatch',char])
        # Confirm custom kerning is active in real HarfBuzz shaping.
        pair_checks={}
        for pair,delta in change['pair_deltas'].items():
            def kern_value(font):
                return sum(x[1] for x in font.shape(pair))-sum(x[1] for x in font.shape(pair,False))
            diff=kern_value(new)-kern_value(old);pair_checks[pair]=diff
            if diff!=delta:failures.append([style,'kerning_delta',pair,diff,delta])
        # Compare collisions against original to avoid blaming inherited design.
        chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàáâãäåāăąŕřŗśšşșťţ'
        novel=[]
        for a in chars:
            for b in chars:
                text=a+b
                area=new.collision(text)
                if area>1 and area>old.collision(text)+4:novel.append([text,round(area,2),round(old.collision(text),2)])
        if novel:failures.append([style,'new_pair_collisions',novel])
        # Above accents must clear their base, except intentional stroke/ogonek joins.
        clearances=[]
        for char in accents:
            name=new.f.getBestCmap()[ord(char)];g=new.f['glyf'][name]
            if not g.isComposite():continue
            base=g.components[0];base_geo=translate(new.geom(base.glyphName),base.x,base.y)
            for mark in g.components[1:]:
                mg=translate(new.geom(mark.glyphName),mark.x,mark.y)
                if not mg.is_empty and mg.bounds[1]>=base_geo.bounds[3]-4:
                    gap=base_geo.distance(mg);clearances.append(gap)
                    if gap<1:failures.append([style,'above_accent_touch',char,mark.glyphName])
        summary.append({'style':style,'glyphs':len(new.names),'latin_nfc_nfd_equivalence_cases':len(accents),'pairs_checked':len(chars)**2,'new_or_increased_pair_collisions':novel,'custom_kern_deltas_verified':pair_checks,'above_accent_min_clearance_units':round(min(clearances),2),'above_accent_checks':len(clearances),'font_formats_reloaded':['TTF','WOFF','WOFF2']})
    out={'version':'0.2','source_sha256':hashlib.sha256((ROOT/'source/Inter.ttf').read_bytes()).hexdigest(),'tests':summary,'failures':failures,'limits':['Approximate outline intersections use sampled curves','Visual review at 14-72 px; no user study','No Windows or macOS native rasterization QA','Static text optical size, no italics; no new variable masters']}
    (ROOT/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps(out,ensure_ascii=False,indent=2))
    # Accent and kerning proof at all three weights.
    im=Image.new('RGB',(1800,1680),'white');d=ImageDraw.Draw(im)
    ui='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    lines=['GroundState  Gr ro St ta at te  AV AW AY Ta To Va Wa Ya','à á â ã ä å ā ă ą  ắ ằ ẵ ặ ấ ầ ẫ ậ','Ŕ Ř Ŗ  ŕ ř ŗ  Ś Š Ş Ș  ś š ş ș  Ť Ţ ť ţ','Ğ Ǵ Ģ  Ġ Ĝ   à̄  á̄  ẗ  ř  ș','Größe · déjà · ação · źródło · ăsta · țară','A clear place for your documents, conversations and shared context.']
    for row,style in enumerate(['Regular','Medium','Semibold']):
        y=30+row*535
        d.text((60,y),style,font=ImageFont.truetype(ui,24),fill='#657166')
        for i,line in enumerate(lines):
            size=32 if i<5 else 20
            d.text((60,y+55+i*60),line,font=ImageFont.truetype(str(ROOT/f'fonts/GroundStateSans-{style}.ttf'),size),fill='#17251d')
    im.save(ROOT/'accent-kerning-proof.png')
    small=Image.new('RGB',(1600,1540),'#ffffff');d=ImageDraw.Draw(small)
    for row,style in enumerate(['Regular','Medium','Semibold']):
        y=24+row*505
        d.text((35,y),style,font=ImageFont.truetype(ui,22),fill='#657166');y+=40
        for size in [14,16,18,24,32,48,72]:
            d.text((35,y),str(size)+' px',font=ImageFont.truetype(ui,13),fill='#657166')
            line='GroundState — Clear context. Il1 à ä å ą.'
            d.text((115,y),line,font=ImageFont.truetype(str(ROOT/f'fonts/GroundStateSans-{style}.ttf'),size),fill='#17251d')
            y+=size+25
    small.save(ROOT/'reading-size-proof.png')
if __name__=='__main__':main()

