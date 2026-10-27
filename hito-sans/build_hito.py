"""Build Hito Sans 0.1 from the validated GroundState Sans 0.2 branch."""
from pathlib import Path
from copy import deepcopy
import sys,json,unicodedata,hashlib
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
from groundstate_build import shift,replace_points,base_root,add_kerning
STYLES=[(400,'Regular'),(500,'Medium'),(600,'Semibold'),(700,'Bold'),(800,'ExtraBold'),(900,'Black')]

def square_bowl(g,start,end,amount=.12):
    """Push diagonal off-curve controls toward corners, retaining extrema."""
    coords=g.coordinates
    for first,last in [(start,start+(end-start)//2), (start+(end-start)//2,end)]:
        points=list(coords[first:last])
        cx=(min(x for x,y in points)+max(x for x,y in points))/2
        cy=(min(y for x,y in points)+max(y for x,y in points))/2
        rx=(max(x for x,y in points)-min(x for x,y in points))/2
        ry=(max(y for x,y in points)-min(y for x,y in points))/2
        for i in range(first,last):
            x,y=coords[i]
            if not g.flags[i]&1:
                nx=x+(1 if x>cx else -1)*amount*(rx-abs(x-cx)) if x!=cx else x
                ny=y+(1 if y>cy else -1)*amount*(ry-abs(y-cy)) if y!=cy else y
                coords[i]=(round(nx),round(ny))

def rounded_box(x0,y0,x1,y1,r):
    p=TTGlyphPen(None)
    p.moveTo((x0+r,y0));p.lineTo((x1-r,y0));p.qCurveTo((x1,y0),(x1,y0+r))
    p.lineTo((x1,y1-r));p.qCurveTo((x1,y1),(x1-r,y1))
    p.lineTo((x0+r,y1));p.qCurveTo((x0,y1),(x0,y1-r))
    p.lineTo((x0,y0+r));p.qCurveTo((x0,y0),(x0+r,y0));p.closePath()
    # TrueType outer contours use clockwise winding.
    from fontTools.pens.reverseContourPen import ReverseContourPen
    from fontTools.pens.recordingPen import RecordingPen
    g=p.glyph(); rec=RecordingPen();g.draw(rec,None)
    out=TTGlyphPen(None);rec.replay(ReverseContourPen(out))
    return out.glyph()

def soften_l_foot(g):
    """Retain the curved exit while reducing its reach past the stem."""
    stem_right=g.coordinates[5][0]
    for i in range(8,16):
        x,y=g.coordinates[i]
        if x>stem_right:
            g.coordinates[i]=(stem_right+round((x-stem_right)*.7),y)

def dependency(f,name,targets,seen=None):
    seen=set() if seen is None else seen
    if name in seen:return False
    if name in targets:return True
    seen.add(name);g=f['glyf'][name]
    return g.isComposite() and any(dependency(f,c.glyphName,targets,seen) for c in g.components)

def anchors_for_I(f,dx):
    def visit(st,kind):
        if kind==4 and st.BaseCoverage:
            if 'I' in st.BaseCoverage.glyphs:
                ix=st.BaseCoverage.glyphs.index('I')
                for anchor in st.BaseArray.BaseRecord[ix].BaseAnchor:
                    if anchor:anchor.XCoordinate+=dx
    for lookup in f['GPOS'].table.LookupList.Lookup:
        for st in lookup.SubTable:
            if lookup.LookupType==9:visit(st.ExtSubTable,st.ExtensionLookupType)
            else:visit(st,lookup.LookupType)

def build(styles=None):
    selected=[item for item in STYLES if styles is None or item[1] in styles]
    # Partial builds preserve existing binaries and their provenance records.
    previous=ROOT/'design-changes.json'
    reports=json.loads(previous.read_text()) if styles is not None and previous.exists() else []
    reports=[entry for entry in reports if entry['style'] not in {style for _,style in selected}]
    for weight,style in selected:
        src=ROOT/f'source/GroundStateSans-{style}.ttf'
        old=TTFont(src);f=deepcopy(old);glyf=f['glyf'];gs=old.getGlyphSet()
        targets={'o','O','Q','H','K','k','A','y','I','i','j','period','l','l.ss02'}
        preserved=[]
        # Preserve non-Latin glyphs that reuse any affected Latin component.
        for cp,name in old.getBestCmap().items():
            if 'LATIN' not in unicodedata.name(chr(cp),'') and name not in targets and dependency(old,name,targets):
                rec=DecomposingRecordingPen(gs);gs[name].draw(rec);p=TTGlyphPen(None);rec.replay(p)
                glyf[name]=p.glyph();preserved.append(name)
        for n in ['o','O']:square_bowl(glyf[n],0,32,.14)
        square_bowl(glyf['Q'],8,40,.14)
        # Short, optically consistent rounded-square dot on i and j.
        dot=old['glyf']['uni0307'];dot.recalcBounds(old['glyf'])
        cx=(dot.xMin+dot.xMax)/2;cy=(dot.yMin+dot.yMax)/2
        side=round((dot.xMax-dot.xMin)*.92);radius=round(side*.20)
        glyf['hito.dot']=rounded_box(round(cx-side/2),round(cy-side/2),round(cx+side/2),round(cy+side/2),radius)
        f.setGlyphOrder(list(dict.fromkeys(f.getGlyphOrder()+['hito.dot'])));f['hmtx']['hito.dot']=(0,round(cx-side/2))
        for n in ['i','j']:
            for c in glyf[n].components:
                if c.glyphName=='uni0307':c.glyphName='hito.dot'
        p=old['glyf']['period'];p.recalcBounds(old['glyf'])
        cx=(p.xMin+p.xMax)/2;cy=(p.yMin+p.yMax)/2
        side=round((p.xMax-p.xMin)*.88)
        glyf['period']=rounded_box(round(cx-side/2),round(cy-side/2),round(cx+side/2),round(cy+side/2),round(side*.20))
        # H bridge: slightly raised for a firmer, more architectural silhouette.
        for i in [3,4,9,10]:shift(glyf['H'],i,0,26)
        # Matched chamfer at the end of the diagonal K/k leg.
        for n,i in [('K',20),('k',14)]:
            g=glyf[n];x,y=g.coordinates[i]
            replace_points(g,i,i+1,[(x-3,28,1),(x-28,y,1)])
        # A's crossbar sits slightly lower, opening the triangular counter.
        for i in [14,15,16,17]:shift(glyf['A'],i,0,-18)
        # The y exit echoes the angle of the inherited t/l feet.
        shift(glyf['y'],0,14,2);shift(glyf['y'],1,0,6)
        # Shorten the inherited l hook, including its matching alternate.
        for name in ['l','l.ss02']:soften_l_foot(glyf[name])
        # Compact barred I to make HitoAI and I/l/1 unambiguous.
        oldw=old['hmtx']['I'][0];neww=oldw+128;center=neww/2
        g=deepcopy(old['glyf']['I.1'])
        xs=sorted(set(x for x,y in g.coordinates))
        left,stemleft,stemright,right=xs
        stemwidth=stemright-stemleft
        mapping={left:100,stemleft:round(center-stemwidth/2),stemright:round(center+stemwidth/2),right:neww-100}
        for i,(x,y) in enumerate(g.coordinates):g.coordinates[i]=(mapping[x],y)
        glyf['I']=g
        f['hmtx']['I']=(neww,100)
        # Precomposed I accents and dynamic mark attachment follow the new center.
        for name in f.getGlyphOrder():
            gg=glyf[name]
            if gg.isComposite() and base_root(f,name)=='I':
                w,lsb=old['hmtx'][name];f['hmtx'][name]=(w+128,lsb)
                for component in gg.components[1:]:component.x+=64
        anchors_for_I(f,64)
        # Tighten just selected brand pairs; do not compress the whole family.
        deltas={'Hi':-12,'hi':-8,'it':-12,'to':-20,'oK':-14,'Ke':-14,'ey':-8,
                'ok':-8,'ke':-10,'oA':-14,'AI':-14,'o.':-10,'.a':-16,'oI':-8,
                'Ho':-8,'HI':4,'Il':8,'II':6,'KI':4,'Ay':-4}
        pairs=add_kerning(f,deltas)
        for name in f.getGlyphOrder():
            gg=glyf[name]
            if hasattr(gg,'program'):gg.program=Program()
            gg.recalcBounds(glyf)
            if hasattr(gg,'xMin'):
                w,_=f['hmtx'][name];f['hmtx'][name]=(w,gg.xMin)
        f['head'].fontRevision=.101
        names={1:'Hito Sans',2:style,3:f'HitoSans-{style}-0.101',4:f'Hito Sans {style}',5:'Version 0.101; GroundState Sans / Inter derivative',6:f'HitoSans-{style}',16:'Hito Sans',17:style}
        for rec in f['name'].names:
            if rec.nameID in names:rec.string=names[rec.nameID].encode(rec.getEncoding(),errors='replace')
        f['name'].setName('Hito Sans. Tailored for Hito, hito.ai, HitoKey and HitoAI. Derived from GroundState Sans 0.2 and Inter. SIL Open Font License 1.1.',10,3,1,0x409)
        for ext,flavor in [('ttf',None),('woff','woff'),('woff2','woff2')]:
            f.flavor=flavor;f.save(ROOT/f'fonts/HitoSans-{style}.{ext}')
        reports.append({'style':style,'weight':weight,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'hito_modified_glyphs':sorted(targets),'new_glyph':'hito.dot','preserved_non_latin_glyphs':len(set(preserved)),'pair_deltas':deltas,'expanded_custom_pairs':pairs,'I_advance_delta':128,'I_anchor_shift':64})
    reports.sort(key=lambda entry: entry['weight'])
    (ROOT/'design-changes.json').write_text(json.dumps(reports,indent=2))
    print(json.dumps(reports,indent=2))
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--styles', nargs='+', choices=[style for _,style in STYLES])
    build(parser.parse_args().styles)

