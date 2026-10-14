"""Render actual font files, rather than simulated letterform images."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
UI='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(family,style,size):return ImageFont.truetype(str(ROOT/f'fonts/{family}-{style}.ttf'),size)
def ui(size):return ImageFont.truetype(UI,size)
def main():
    im=Image.new('RGB',(1800,1380),'#f1f1ec');d=ImageDraw.Draw(im)
    d.text((65,45),'GROUNDSTATE / HITO',font=ui(21),fill='#516055')
    d.text((65,91),'Two voices. One precise grid.',font=ui(46),fill='#16251f')
    d.text((65,160),'Custom monospace families · Version 0.1 · 400 / 500 / 600 / 700',font=ui(23),fill='#617067')
    for family,title,x,bg,fg,accent in [('GroundStateMono','GroundState Mono',55,'#e3eae1','#213c2c','#507253'),('HitoMono','Hito Mono',925,'#182323','#f0f3eb','#9dbc8f')]:
        d.rounded_rectangle((x,225,x+820,1160),radius=20,fill=bg)
        d.text((x+36,263),title,font=font(family,'Medium',37),fill=fg)
        d.text((x+36,330),'GroundState' if family=='GroundStateMono' else 'hito.ai',font=font(family,'Semibold',68),fill=fg)
        d.text((x+36,430),'G r a t S' if family=='GroundStateMono' else 'H i t o K A',font=font(family,'Regular',66),fill=fg)
        d.text((x+36,540),'Angled terminals. Open rhythm.' if family=='GroundStateMono' else 'Soft bowls. Rounded-square dots.',font=ui(23),fill=accent)
        lines=['state: ready','context: shared','members: 0003','hash: 9f3a7c21'] if family=='GroundStateMono' else ['HitoKey / HitoAI','action: git commit','device: verified','approval: required']
        for i,line in enumerate(lines):d.text((x+36,613+i*53),line,font=font(family,'Regular',28),fill=fg)
        d.line((x+36,862,x+784,862),fill=accent,width=1)
        for i,style in enumerate(['Regular','Medium','Semibold','Bold']):
            d.text((x+36,900+i*52),style.ljust(10)+'Il1  O0Q  {}  ->',font=font(family,style,27),fill=fg)
    d.text((65,1210),'600-unit cells. Literal operators. Accents checked.',font=ui(27),fill='#243c2d')
    d.text((65,1264),'Geist Mono foundation · Original brand details · TTF / WOFF2 / WOFF',font=ui(23),fill='#617067')
    im.save(ROOT/'proofs/brand-mono-preview.png')
    # Baseline comparison at actual font sizes, including diacritics and code.
    im=Image.new('RGB',(1800,1470),'white');d=ImageDraw.Draw(im)
    names=[('Geist Mono','source/reference/GeistMono-Regular.ttf'),('GroundState Mono','fonts/GroundStateMono-Regular.ttf'),('Hito Mono','fonts/HitoMono-Regular.ttf')]
    for row,(label,path) in enumerate(names):
        y=35+row*475;d.text((48,y),label,font=ui(22),fill='#627468')
        for i,(text,size) in enumerate([('GroundState  hito.ai  HitoKey  HitoAI',48),('G r a t S  H K A I  o O Q  i j .',52),('à á â ã ä å ā ą · ŕ ř ś š ș ţ ť · İ ï',29),('Größe · déjà · ação · źródło · țară',29),('const approve = (key) => key.sign(hash);',24)]):
            d.text((48,y+48+i*76),text,font=ImageFont.truetype(str(ROOT/path),size),fill='#183225',features=['-liga','-calt'])
    im.save(ROOT/'proofs/source-comparison.png')
    im=Image.new('RGB',(1800,1900),'white');d=ImageDraw.Draw(im)
    for col,family in enumerate(['GroundStateMono','HitoMono']):
        for row,style in enumerate(['Regular','Medium','Semibold','Bold']):
            x=40+col*900;y=30+row*465
            d.text((x,y),family+' / '+style,font=ui(19),fill='#536c5b')
            y+=42
            for size in [12,14,16,20,28,40]:
                d.text((x,y),str(size)+' px',font=ui(13),fill='#63796c')
                text='GroundState / HitoAI Il1 O0' if size<28 else 'HitoKey à 0O Il1'
                d.text((x+63,y),text,font=font(family,style,size),fill='#17271d');y+=size+17
            d.text((x,y+10),'àáâãäåą  ĞĢŕřśšşșťţ  i\u0307 a\u0301',font=font(family,style,22),fill='#17271d')
    im.save(ROOT/'proofs/small-size-accents.png')
    print('Rendered preview, source comparison and reading-size/accent proofs.')
if __name__=='__main__':main()
