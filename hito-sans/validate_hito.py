from pathlib import Path
import sys,json,unicodedata
from fontTools.ttLib import TTFont
from shapely.geometry import Polygon
from shapely.affinity import translate
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
from font_checks import Font,FlattenPen
def main():
    reports=[];failures=[]
    for change in json.loads((ROOT/'design-changes.json').read_text()):
        style=change['style'];new=Font(ROOT/f'fonts/HitoSans-{style}.ttf');old=Font(ROOT/f'source/GroundStateSans-{style}.ttf')
        cmap=new.f.getBestCmap()
        assert cmap==old.f.getBestCmap()
        for ext in ['woff','woff2']:
            f=TTFont(ROOT/f'fonts/HitoSans-{style}.{ext}');assert f.getBestCmap()==cmap
        assert new.f['name'].getDebugName(1)=='Hito Sans'
        assert new.f['OS/2'].usWeightClass == change['weight']
        assert new.f['name'].getDebugName(6) == 'HitoSans-' + style
        accents=[]
        for cp in cmap:
            c=chr(cp);nfd=unicodedata.normalize('NFD',c)
            if 'LATIN' in unicodedata.name(c,'') and len(nfd)>1:
                accents.append(c)
                if new.shape(c)!=new.shape(nfd):failures.append([style,'accent_normalization',c])
        kern={}
        for pair,delta in change['pair_deltas'].items():
            def value(f):return sum(x[1] for x in f.shape(pair))-sum(x[1] for x in f.shape(pair,False))
            actual=value(new)-value(old);kern[pair]=actual
            if actual!=delta:failures.append([style,'kerning',pair,actual,delta])
        chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàáäåąíïīİöóõőķýÿ'
        collisions=[]
        for a in chars:
            for b in chars:
                text=a+b;area=new.collision(text)
                if area>1 and area>old.collision(text)+4:collisions.append([text,round(area,2),round(old.collision(text),2)])
        if collisions:failures.append([style,'new_pair_intersections',collisions])
        clearance=[];above_count=0
        for c in accents:
            g=new.f['glyf'][cmap[ord(c)]]
            if not g.isComposite():continue
            base=g.components[0];bg=translate(new.geom(base.glyphName),base.x,base.y)
            for mark in g.components[1:]:
                mg=translate(new.geom(mark.glyphName),mark.x,mark.y)
                if not mg.is_empty and mg.bounds[1]>=bg.bounds[3]-4:
                    gap=bg.distance(mg);clearance.append(gap);above_count+=1
                    if gap<1:failures.append([style,'accent_touch',c,mark.glyphName])
        # No newly invalid contours relative to the parent source.
        new_invalid=[]
        for name in change['hito_modified_glyphs']+['hito.dot']:
            pn=FlattenPen(new.gs);new.gs[name].draw(pn)
            nbad=sum(not Polygon(c).is_valid for c in pn.contours if len(c)>2)
            obad=0
            if name in old.names:
                po=FlattenPen(old.gs);old.gs[name].draw(po)
                obad=sum(not Polygon(c).is_valid for c in po.contours if len(c)>2)
            if nbad>obad:new_invalid.append(name)
        if new_invalid:failures.append([style,'new_invalid_contours',new_invalid])
        words={}
        for text in ['hito.ai','hitokey','HitoKey','HitoAI','Hito','hito']:
            shape=new.shape(text)
            assert all(n!='.notdef' for n,*_ in shape)
            words[text]={'advance_units':sum(x[1] for x in shape),'collision_area':round(new.collision(text),3)}
        reports.append({'style':style,'format_checks':['TTF','WOFF','WOFF2'],'glyph_count':len(new.names),'latin_accent_cases':len(accents),'pair_cases':len(chars)**2,'new_pair_intersections':collisions,'custom_kern_deltas':kern,'above_accent_checks':above_count,'above_accent_min_gap':round(min(clearance),2),'new_invalid_contours':new_invalid,'wordmarks':words})
    out={'family':'Hito Sans','version':'0.1','tests':reports,'failures':failures,'limits':['Sampled curves for approximate geometric checks','No native Windows/macOS browser validation','Five static weights at text optical size; no italics or variable masters','Geometric clearance and visual review do not prove accessibility or recognition']}
    (ROOT/'validation.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
    print(json.dumps(out,indent=2,ensure_ascii=False))
    if failures: raise SystemExit('Font validation failed; inspect validation.json')
if __name__=='__main__':main()

