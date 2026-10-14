"""Check the actual built fonts with HarfBuzz, outline geometry and format reloads."""
from pathlib import Path
from functools import lru_cache
from itertools import product
import json,unicodedata,string
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.affinity import translate

ROOT=Path(__file__).resolve().parent
class FlattenPen(BasePen):
    def __init__(self,gs):super().__init__(gs);self.rings=[];self.current=[]
    def _moveTo(self,p):self.current=[p]
    def _lineTo(self,p):self.current.append(p)
    def _qCurveToOne(self,c,p):
        a=self._getCurrentPoint()
        for i in range(1,25):
            t=i/24;u=1-t;self.current.append((u*u*a[0]+2*u*t*c[0]+t*t*p[0],u*u*a[1]+2*u*t*c[1]+t*t*p[1]))
    def _curveToOne(self,b,c,p):
        a=self._getCurrentPoint()
        for i in range(1,25):
            t=i/24;u=1-t;self.current.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*p[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*p[1]))
    def _closePath(self):
        if self.current:self.rings.append(self.current);self.current=[]
    _endPath=_closePath

class Font:
    def __init__(self,p):
        self.tt=TTFont(p);self.names=self.tt.getGlyphOrder();self.gs=self.tt.getGlyphSet()
        self.hb=hb.Font(hb.Face(p.read_bytes()));self.hb.scale=(1000,1000)
    def shape(self,text,features=None):
        b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(self.hb,b,features or {})
        return [(self.names[g.codepoint],p.x_advance,p.x_offset,p.y_offset) for g,p in zip(b.glyph_infos,b.glyph_positions)]
    @lru_cache(None)
    def geom(self,n):
        p=FlattenPen(self.gs);self.gs[n].draw(p);rings=[]
        for points in p.rings:
            if len(points)<3:continue
            area=sum(x*y1-x1*y for (x,y),(x1,y1) in zip(points,points[1:]+points[:1]))/2
            poly=Polygon(points);poly=poly if poly.is_valid else poly.buffer(0)
            rings.append((area,poly))
        if not rings:return Polygon()
        sign=1 if max(rings,key=lambda x:abs(x[0]))[0]>0 else -1
        return unary_union([p for a,p in rings if a*sign>0]).difference(unary_union([p for a,p in rings if a*sign<0]))
    def overlap(self,a,b):return self.geom(a).intersection(translate(self.geom(b),600,0)).area

def main():
    results=[];failures=[]
    samples=['GroundState Mono','hito.ai hitokey HitoKey HitoAI',
      'Il1| O0Q 2Z 5S 6G 8B rn m vv w',
      'const approve = (key) => key.sign(hash);',
      '!= == === !== <= >= -> => :: && || ++ -- // /* */',
      '.... ... .. ?? ?. ??= ** **= << >> >>> <=>',
      'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA 0123456789abcdef']
    for change in json.loads((ROOT/'design-changes.json').read_text()):
        family=change['family'];style=change['style'];stem=family.replace(' ','')+'-'+style
        new=Font(ROOT/f'fonts/{stem}.ttf');old=Font(ROOT/f'source/reference/GeistMono-{style}.ttf')
        def check(ok,kind,detail=None):
            if not ok:failures.append({'font':stem,'check':kind,'detail':detail})
        cm=new.tt.getBestCmap();check(cm==old.tt.getBestCmap(),'cmap_preserved')
        check(all(new.tt['hmtx'][n][0]==old.tt['hmtx'][n][0] for n in new.names),'all_advances_preserved')
        check(new.tt['post'].isFixedPitch==1,'fixed_pitch_flag')
        check(new.tt['name'].getDebugName(16)==family,'family_name')
        check(new.tt['OS/2'].usWeightClass==change['weight'],'weight')
        for ext in ['woff','woff2']:
            f=TTFont(ROOT/f'fonts/{stem}.{ext}');check(f.getBestCmap()==cm,'format_reload',ext)
        ascii_chars=''.join(chr(i) for i in range(32,127));count=0
        for a,b in product(ascii_chars,repeat=2):
            shaped=new.shape(a+b)
            check(len(shaped)==2 and all(p[1:]==(600,0,0) for p in shaped),'ascii_grid',a+b);count+=1
        for s in samples:
            p=new.shape(s);check(len(p)==len(s) and all(v[1:]==(600,0,0) for v in p),'sample_grid',s)
        # Bounded ASCII outlines cannot collide across their fixed cells.
        for c in ascii_chars:
            g=new.tt['glyf'][cm[ord(c)]];g.recalcBounds(new.tt['glyf'])
            if hasattr(g,'xMin'):check(g.xMin>=0 and g.xMax<=600,'ascii_cell_bounds',[c,g.xMin,g.xMax])
        accents=[];clearances=[]
        for cp,n in cm.items():
            c=chr(cp);nfd=unicodedata.normalize('NFD',c)
            if 'LATIN' not in unicodedata.name(c,'') or len(nfd)==1:continue
            accents.append(c)
            check(new.shape(c)==new.shape(nfd),'nfc_nfd',c)
            g=new.tt['glyf'][n]
            if g.isComposite():
                base=g.components[0];bg=translate(new.geom(base.glyphName),base.x,base.y)
                for mark in g.components[1:]:
                    mg=translate(new.geom(mark.glyphName),mark.x,mark.y)
                    if bg.is_empty or mg.is_empty:continue
                    if mg.bounds[1]>=bg.bounds[3]:
                        gap=bg.distance(mg);clearances.append(gap)
                        check(gap>0,'above_accent_clearance',[c,mark.glyphName,gap])
        # Check changed/accented boundary shapes against neighbors; compare to source.
        chars=string.ascii_letters+'àáäåąŕřśšşșťţĞĢİ'
        names=list(dict.fromkeys(cm[ord(c)] for c in chars if ord(c) in cm));collisions=[]
        for a,b in product(names,repeat=2):
            area=new.overlap(a,b)
            if area>2 and area>old.overlap(a,b)+3:collisions.append([a,b,round(area,2)])
        check(not collisions,'new_pair_collisions',collisions)
        edited=[n for n in change['edited_base_glyphs'] if new.geom(n).symmetric_difference(old.geom(n)).area>1]
        check(len(edited)==len(change['edited_base_glyphs']),'requested_changes_present',edited)
        results.append({'font':stem,'glyph_count':len(new.names),'encoded_characters':len(cm),'text_advance_units':600,
          'all_source_advances_preserved':True,'ascii_pair_grid_checks':count,'sample_grid_checks':len(samples),
          'latin_nfc_nfd_checks':len(accents),'accent_clearance_checks':len(clearances),
          'minimum_above_accent_gap_units':round(min(clearances),2) if clearances else None,
          'outline_pair_checks':len(names)**2,'new_pair_collisions':collisions,'edited_bases_verified':edited,
          'formats_reloaded':['TTF','WOFF','WOFF2']})
    report={'version':'0.1','results':results,'failures':failures,'limitations':[
      'Curve collision tests use sampled outlines.',
      'Raster proofs use FreeType/Pillow; macOS and Windows native rendering not tested.',
      'Four upright static weights; no italics or custom variable-font output.',
      'Inherited stylistic alternatives may select original Geist forms.',
      'No font hint instructions; small-size appearance depends on rasterizer.',
      'Greek and Cyrillic reuse original Geist designs. No new character coverage.']}
    (ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'faces':len(results),'failures':failures,'ascii_pair_checks':sum(r['ascii_pair_grid_checks'] for r in results),'accent_checks':sum(r['latin_nfc_nfd_checks'] for r in results)},ensure_ascii=False))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
