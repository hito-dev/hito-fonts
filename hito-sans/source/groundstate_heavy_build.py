"""GroundState Sans 0.2: custom terminals, feet, and additive kerning."""
from pathlib import Path
from copy import deepcopy
from array import array
import json, unicodedata
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.otlLib.builder import buildPairPosGlyphsSubtable, buildLookup
from fontTools.ttLib.tables.otBase import ValueRecord
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source/Inter.ttf'
FAMILY='GroundState Sans'
WEIGHTS=[(400,'Regular'),(500,'Medium'),(600,'Semibold'),(700,'Bold'),(900,'Black')]
def shift(g,index,dx=0,dy=0):
    x,y=g.coordinates[index];g.coordinates[index]=(round(x+dx),round(y+dy))
def replace_points(g,start,stop,points):
    coords=list(g.coordinates); flags=list(g.flags)
    coords[start:stop]=[(round(x),round(y)) for x,y,on in points]
    flags[start:stop]=[int(on) for x,y,on in points]
    delta=len(points)-(stop-start)
    g.coordinates=GlyphCoordinates(coords);g.flags=array('B',flags)
    g.endPtsOfContours=[p+delta if p>=stop-1 else p for p in g.endPtsOfContours]
def base_root(f,name,seen=None):
    seen=set() if seen is None else seen
    if name in seen:return name
    seen.add(name);g=f['glyf'][name]
    return base_root(f,g.components[0].glyphName,seen) if g.isComposite() else name
def add_kerning(f,deltas):
    groups={};cmap=f.getBestCmap()
    for codepoint,name in cmap.items():
        char=chr(codepoint);decomp=unicodedata.normalize('NFD',char)
        if ('LATIN' in unicodedata.name(char,'') and decomp[0].isascii()
            and all(unicodedata.combining(c) for c in decomp[1:])):
            groups.setdefault(cmap[ord(decomp[0])],set()).add(name)
    pairs={}
    for pair,delta in deltas.items():
        a,b=[cmap[ord(c)] for c in pair]
        for left in groups.get(a,[a]):
            for right in groups.get(b,[b]):
                v=ValueRecord();v.XAdvance=delta;pairs[left,right]=(v,None)
    lookup=buildLookup([buildPairPosGlyphsSubtable(pairs,f.getReverseGlyphMap())])
    table=f['GPOS'].table
    index=len(table.LookupList.Lookup);table.LookupList.Lookup.append(lookup)
    table.LookupList.LookupCount=len(table.LookupList.Lookup)
    for feature in table.FeatureList.FeatureRecord:
        if feature.FeatureTag=='kern':
            feature.Feature.LookupListIndex.append(index)
            feature.Feature.LookupCount=len(feature.Feature.LookupListIndex)
    return len(pairs)
def build():
    (ROOT/'fonts').mkdir(exist_ok=True)
    report=[]
    for weight,style in WEIGHTS:
        original=instantiateVariableFont(TTFont(SOURCE,recalcTimestamp=False),{'wght':weight,'opsz':14},inplace=True)
        original.flavor=None;original.save(ROOT/f'source/Inter-{style}.ttf')
        f=deepcopy(original);glyf=f['glyf']
        # Some Cyrillic characters share Latin components. Detach their original
        # outlines so Latin customization does not silently redesign other scripts.
        changed_roots={'G','r','a','t','S','s','c','e','f','l'}
        detached=[];original_set=original.getGlyphSet()
        for cp,name in original.getBestCmap().items():
            if 'LATIN' not in unicodedata.name(chr(cp),'') and base_root(original,name) in changed_roots and name not in changed_roots:
                rec=DecomposingRecordingPen(original_set);original_set[name].draw(rec)
                pen=TTGlyphPen(None);rec.replay(pen);glyf[name]=pen.glyph();detached.append(name)
        stem=glyf['r'].coordinates[19][0]-glyf['r'].coordinates[0][0];scale=stem/180
        g=glyf['G']
        shift(g,13,-8,30*scale);shift(g,14,5,-12*scale)
        shift(g,33,28,0);shift(g,34,-8,10*scale)
        shift(g,35,-10,10*scale);shift(g,36,-10,0)
        g=glyf['r']
        for i,dx,dy in [(10,18,8),(11,-22,0),(9,10,8),(12,-20,0),(13,-12,0)]:shift(g,i,dx,dy)
        # Draw a new short curved foot on the double-storey a.
        g=glyf['a'];outer=g.coordinates[32][0];inner=g.coordinates[35][0];join=g.coordinates[35][1]
        foot=[(outer,join+52*scale,1),(outer,100*scale,0),
              (outer+30,94*scale,0),(outer+70,116*scale,1),
              (outer+99,-4*scale,1),(outer+50,-20*scale,0),
              (inner+48,-20*scale,0),(inner+6,64*scale,0),(inner+6,join,1)]
        replace_points(g,33,36,foot)
        for name in ['t','f']:
            g=glyf[name];shift(g,0,20,0);shift(g,1,-12,0)
        g=glyf['t']
        for i,dx,dy in [(11,16,0),(12,22,6),(13,20,-2),(14,12,0)]:shift(g,i,dx,dy)
        for name,lower,upper in [('S',(4,5),(29,30)),('s',(4,5),(26,27))]:
            g=glyf[name]
            for i in lower:shift(g,i,0,18*scale if i==lower[1] else -18*scale)
            for i in upper:shift(g,i,0,18*scale if i==upper[0] else -18*scale)
        for i in [17,18,19,40,41,42,43]:shift(glyf['S'],i,12,0)
        for name,indices in [('c',[13,14,32,33]),('e',[35,36])]:
            for i in indices:shift(glyf[name],i,0,10*scale if i in [13,32,35] else -10*scale)
        glyf['l']=deepcopy(glyf['l.ss02']);f['hmtx']['l']=f['hmtx']['l.ss02']
        shift(glyf['l'],12,4,8);shift(glyf['l'],13,2,-2)
        glyf['l.ss02']=deepcopy(glyf['l'])
        width_deltas={'a':72,'r':12,'t':16,'l':f['hmtx']['l'][0]-original['hmtx']['l'][0]}
        for name,delta in width_deltas.items():
            if name!='l':
                width,lsb=f['hmtx'][name];f['hmtx'][name]=(width+delta,lsb)
        affected=[]
        for name in f.getGlyphOrder():
            g=glyf[name]
            if g.isComposite():
                root=base_root(f,name)
                if root in width_deltas:
                    width,lsb=original['hmtx'][name];f['hmtx'][name]=(width+width_deltas[root],lsb);affected.append(name)
                    # Letter-letter composites need the second letter translated.
                    for component in g.components[1:]:
                        if component.x>=original['hmtx'][g.components[0].glyphName][0]-30 and f['hmtx'][component.glyphName][0]>0:
                            component.x+=width_deltas[root]
                if root=='a':
                    for component in g.components:
                        if component.glyphName=='ogonek.a':component.x+=62
                if root=='t':
                    for component in g.components:
                        if component.glyphName.startswith('commaaccentright'):component.x+=20
        for name in f.getGlyphOrder():
            g=glyf[name]
            if hasattr(g,'program'):g.program=Program()
            g.recalcBounds(glyf)
            if hasattr(g,'xMin'):
                width,_=f['hmtx'][name];f['hmtx'][name]=(width,g.xMin)
        for tag in ['fpgm','prep','cvt ','hdmx','VDMX','DSIG']:
            if tag in f:del f[tag]
        deltas={'Gr':-18,'ro':-12,'ru':-8,'ra':-6,'re':-8,'rt':6,
                'dS':8,'St':-18,'Sa':-8,'Se':-6,'ta':-12,'te':-8,
                'at':-8,'ar':-4,'aa':-4,'aV':6,'aW':6,'aY':8,
                'Ta':-8,'To':-6,'Va':-6,'Wa':-4,'Ya':-6,
                'ff':24,'ft':8,'tl':6,'lt':4,'rl':4}
        # At 700 the f/t crossbars overlap by eight units. Add twelve units
        # of advance, also expanded to canonical accented t variants below.
        if weight==700:deltas['ft']=20
        # The 900 t/f crossbars need six additional units, including accents.
        if weight==900:deltas['tf']=6
        count=add_kerning(f,deltas)
        f['head'].fontRevision=.200;f['OS/2'].usWeightClass=weight
        if weight>=700:
            f['OS/2'].fsSelection=(f['OS/2'].fsSelection&~(1|32|64))|32
            f['head'].macStyle=1
        names={1:FAMILY,2:style,3:f'GroundStateSans-{style}-0.200',4:f'{FAMILY} {style}',5:'Version 0.200; Inter-derived development font',6:f'GroundStateSans-{style}',16:FAMILY,17:style}
        if weight==900:
            # A separate legacy family keeps Black from taking Bold's style link.
            names[1]=FAMILY+' Black';names[2]='Regular'
            f['OS/2'].fsSelection=(f['OS/2'].fsSelection&~(1|32|64))|64
            f['head'].macStyle=0
        for record in f['name'].names:
            if record.nameID in names:record.string=names[record.nameID].encode(record.getEncoding(),errors='replace')
        if weight==900:
            for platform,encoding,language in [(3,1,0x409),(1,0,0)]:
                f['name'].setName(FAMILY,16,platform,encoding,language)
                f['name'].setName(style,17,platform,encoding,language)
        f['name'].setName('GroundState Sans 0.2. Custom G r a t S s c e f l details and additive kerning. Derived from Inter; SIL Open Font License 1.1.',10,3,1,0x409)
        for ext,flavor in [('ttf',None),('woff','woff'),('woff2','woff2')]:
            f.flavor=flavor;f.save(ROOT/f'fonts/GroundStateSans-{style}.{ext}')
        report.append({'style':style,'weight':weight,'modified_base_glyphs':['G','r','a','t','S','s','c','e','f','l'],'spacing_deltas':width_deltas,'composite_advances_updated':len(affected),'non_latin_outlines_preserved':len(set(detached)),'expanded_kerning_pairs':count,'pair_deltas':deltas})
    (ROOT/'design-changes.json').write_text(json.dumps(report,indent=2))
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))

