"""Build GroundState Mono and Hito Mono 0.1 from a pinned Geist Mono source.

Run: python3 build.py. Inputs and original licenses are in source/.
The advance widths and mark attachment anchors remain those of Geist Mono.
"""
from pathlib import Path
from copy import deepcopy
from array import array
import json, unicodedata, hashlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT=Path(__file__).resolve().parent
STYLES=[(400,'Regular'),(500,'Medium'),(600,'Semibold'),(700,'Bold')]
GS_TARGETS={'G','r','a','t','S','s','c','e','f','l'}
HITO_TARGETS={'o','O','Q','H','K','k','A','I','uni0307','period'}

def shift(g,i,dx=0,dy=0):
    x,y=g.coordinates[i];g.coordinates[i]=(round(x+dx),round(y+dy))

def replace_point(g,i,points):
    coords=list(g.coordinates);flags=list(g.flags)
    coords[i:i+1]=[(round(x),round(y)) for x,y in points]
    flags[i:i+1]=[1]*len(points);delta=len(points)-1
    g.coordinates=GlyphCoordinates(coords);g.flags=array('B',flags)
    g.endPtsOfContours=[v+delta if v>=i else v for v in g.endPtsOfContours]

def depends(font,n,targets,seen=None):
    if n in targets:return True
    seen=set() if seen is None else seen
    if n in seen:return False
    seen.add(n);g=font['glyf'][n]
    return g.isComposite() and any(depends(font,c.glyphName,targets,seen) for c in g.components)

def preserve_other_scripts(font,original,targets):
    gs=original.getGlyphSet();names=[]
    for cp,n in original.getBestCmap().items():
        un=unicodedata.name(chr(cp),'')
        if ('CYRILLIC' in un or 'GREEK' in un) and depends(original,n,targets):
            rec=DecomposingRecordingPen(gs);gs[n].draw(rec)
            pen=TTGlyphPen(None);rec.replay(pen);font['glyf'][n]=pen.glyph();names.append(n)
    return sorted(set(names))

def groundstate(font):
    g=font['glyf'];scale=(g['H'].coordinates[2][0]-g['H'].coordinates[0][0])/86
    for i,dx,dy in [(12,0,10*scale),(13,0,-10*scale),(29,20,0),(30,2,0)]:shift(g['G'],i,dx,dy)
    for i,dx,dy in [(13,-8,0),(14,-10,8),(15,-24,0),(16,-6,0)]:shift(g['r'],i,dx,dy)
    # The a foot lifts into a short diagonal finish without widening its cell.
    for i,dx,dy in [(25,-4,6),(26,-8,24),(27,2,10),(28,-4,0)]:shift(g['a'],i,dx,dy)
    for n in ['t','f']:
        for i,dx in [(12,-2),(13,10),(14,-12),(15,8)]:shift(g[n],i,dx,0)
    shift(g['t'],10,2,20);shift(g['t'],11,16,8)
    shift(g['f'],5,-12,0);shift(g['f'],6,5,0)
    shift(g['l'],14,-8,16);shift(g['l'],15,8,0)
    for n,upper in [('S',(29,30)),('s',(27,28))]:
        for i,dy in [(4,-12),(5,12),(upper[0],12),(upper[1],-12)]:shift(g[n],i,0,dy*scale)
    for i,dy in [(12,10),(13,-10),(25,10),(26,-10)]:shift(g['c'],i,0,dy*scale)
    shift(g['e'],20,0,10*scale);shift(g['e'],21,0,-10*scale)

def squared_curves(g,start,end,amount=.14):
    # Retain all extrema; move diagonal curve controls toward their quadrant corner.
    p=list(g.coordinates[start:end]);cx=(min(x for x,y in p)+max(x for x,y in p))/2
    cy=(min(y for x,y in p)+max(y for x,y in p))/2
    rx=(max(x for x,y in p)-min(x for x,y in p))/2
    ry=(max(y for x,y in p)-min(y for x,y in p))/2
    for i in range(start,end):
        if g.flags[i]&1:continue
        x,y=g.coordinates[i]
        dx=(1 if x>cx else -1)*amount*(rx-abs(x-cx)) if x!=cx else 0
        dy=(1 if y>cy else -1)*amount*(ry-abs(y-cy)) if y!=cy else 0
        g.coordinates[i]=(round(x+dx),round(y+dy))

def rounded_box(x0,y0,x1,y1,r):
    # Clockwise contour with quadratic corner curves.
    # Use tangent corners throughout, including the first corner at closing.
    p=TTGlyphPen(None);p.moveTo((x0+r,y0))
    p.qCurveTo((x0,y0),(x0,y0+r));p.lineTo((x0,y1-r))
    p.qCurveTo((x0,y1),(x0+r,y1));p.lineTo((x1-r,y1))
    p.qCurveTo((x1,y1),(x1,y1-r));p.lineTo((x1,y0+r))
    p.qCurveTo((x1,y0),(x1-r,y0));p.closePath();return p.glyph()

def hito(font):
    g=font['glyf']
    for n,ranges in [('o',[(0,16),(16,28)]),('O',[(0,16),(16,32)]),('Q',[(4,20),(20,37)])]:
        for start,end in ranges:squared_curves(g[n],start,end)
    for n in ['uni0307','period']:
        old=g[n];old.recalcBounds(g)
        cx=(old.xMin+old.xMax)/2;cy=(old.yMin+old.yMax)/2
        side=round(min(old.xMax-old.xMin,old.yMax-old.yMin)*(.94 if n=='period' else 1))
        x0=round(cx-side/2);y0=round(cy-side/2)
        g[n]=rounded_box(x0,y0,x0+side,y0+side,round(side*.20))
    for i in [3,4,5,6,11,12,13,14]:shift(g['H'],i,0,13)
    for i in [7,8,9,10]:shift(g['A'],i,0,-10)
    for n,i in [('K',11),('k',7)]:
        x,y=g[n].coordinates[i]
        replace_point(g[n],i,[(x-10,y+15),(x-20,y)])
    # Preserve the barred I, narrowing only the bars for a more compact silhouette.
    for i in [0,1,4,5]:shift(g['I'],i,14,0)
    for i in [6,7,10,11]:shift(g['I'],i,-14,0)

def remove_features(font,tags):
    # Remove source code-ligature registrations, keeping each ASCII cell literal.
    table=font['GSUB'].table;records=table.FeatureList.FeatureRecord
    keep=[i for i,r in enumerate(records) if r.FeatureTag not in tags];mapping={old:new for new,old in enumerate(keep)}
    for script in table.ScriptList.ScriptRecord:
        systems=[script.Script.DefaultLangSys]+[r.LangSys for r in script.Script.LangSysRecord]
        for lang in systems:
            if lang is None:continue
            lang.FeatureIndex=[mapping[i] for i in lang.FeatureIndex if i in mapping]
            lang.FeatureCount=len(lang.FeatureIndex)
            if lang.ReqFeatureIndex!=65535:lang.ReqFeatureIndex=mapping.get(lang.ReqFeatureIndex,65535)
    table.FeatureList.FeatureRecord=[records[i] for i in keep];table.FeatureList.FeatureCount=len(keep)

def metadata(f,family,style,weight):
    compact=family.replace(' ','');legacy=family if style in ['Regular','Bold'] else family+' '+style
    sub=style if style in ['Regular','Bold'] else 'Regular'
    copyright=f['name'].getDebugName(0) or ''
    values={0:copyright+'; 2026 GroundState and Hito modifications.',1:legacy,2:sub,
      3:f'{compact}-{style}-0.100',4:family+' '+style,5:'Version 0.100; Geist Mono derivative',
      6:compact+'-'+style,16:family,17:style,18:family+' '+style,
      10:f'{family} 0.1. Custom Latin details derived from Geist Mono. Fixed 600-unit text cells; coding ligatures disabled. SIL OFL 1.1.'}
    f['name'].names=[r for r in f['name'].names if r.nameID not in {1,2,3,4,5,6,10,16,17,18,21,22,25}]
    for id,val in values.items():
        f['name'].setName(val,id,3,1,0x409)
        f['name'].setName(val,id,1,0,0)
    f['OS/2'].usWeightClass=weight
    f['OS/2'].fsSelection=(f['OS/2'].fsSelection&~(1|32|64))|(32 if weight==700 else 64)
    f['head'].macStyle=1 if weight==700 else 0;f['head'].fontRevision=.100
    f['post'].isFixedPitch=1

def main():
    (ROOT/'fonts').mkdir(exist_ok=True);(ROOT/'source/reference').mkdir(exist_ok=True)
    reports=[]
    for weight,style in STYLES:
        original=instantiateVariableFont(TTFont(ROOT/'source/GeistMono-Variable.ttf'),{'wght':weight},inplace=True)
        original.save(ROOT/f'source/reference/GeistMono-{style}.ttf')
        for family in ['GroundState Mono','Hito Mono']:
            f=deepcopy(original);targets=GS_TARGETS|(HITO_TARGETS if family=='Hito Mono' else set())
            preserved=preserve_other_scripts(f,original,targets)
            groundstate(f)
            if family=='Hito Mono':hito(f)
            remove_features(f,{'liga','ss11'})
            for n in f.getGlyphOrder():
                if hasattr(f['glyf'][n],'program'):f['glyf'][n].program=Program()
            for tag in ['fpgm','prep','cvt ','hdmx','VDMX','DSIG']:
                if tag in f:del f[tag]
            removeOverlaps(f,removeHinting=True)
            for n in f.getGlyphOrder():
                glyph=f['glyf'][n];glyph.recalcBounds(f['glyf'])
                if hasattr(glyph,'xMin'):f['hmtx'][n]=(f['hmtx'][n][0],glyph.xMin)
            metadata(f,family,style,weight)
            for ext,flavor in [('ttf',None),('woff2','woff2'),('woff','woff')]:
                f.flavor=flavor;f.save(ROOT/f'fonts/{family.replace(" ","")}-{style}.{ext}')
            reports.append({'family':family,'style':style,'weight':weight,'edited_base_glyphs':sorted(targets),
              'preserved_other_script_glyphs':preserved,'advance_changes':0,'text_cell_units':600,'upm':1000,
              'coding_ligature_features_removed':['liga','ss11']})
    (ROOT/'design-changes.json').write_text(json.dumps(reports,indent=2))
    print('Built',len(reports),'faces in TTF, WOFF2 and WOFF.')

if __name__=='__main__':main()
