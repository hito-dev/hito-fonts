"""Render Hito Mono font files and compare them with the upstream Geist source."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
UI = ROOT.parent / 'hito-sans/fonts/HitoSans-Regular.ttf'
STYLES = ['Regular', 'Medium', 'Semibold', 'Bold']
BG, FG, MUTED = '#F7F2E8', '#1C1F2A', '#656B61'


def font(style, size):
    return ImageFont.truetype(str(ROOT / f'fonts/HitoMono-{style}.ttf'), size)


def ui(size):
    return ImageFont.truetype(str(UI), size)


def main():
    (ROOT / 'proofs').mkdir(exist_ok=True)
    im = Image.new('RGB', (1200, 1000), BG)
    d = ImageDraw.Draw(im)
    d.text((50, 40), 'Hito Mono · Version 0.1', font=ui(30), fill=MUTED)
    d.text((50, 110), 'hito.ai / HitoKey', font=font('Semibold', 64), fill=FG)
    for i, style in enumerate(STYLES):
        y = 240 + i * 160
        d.text((50, y), style, font=ui(24), fill=MUTED)
        d.text((50, y + 45), 'Il1 O0Q {} ->  git commit -S', font=font(style, 34), fill=FG)
    d.text((50, 920), '600-unit cells · Literal operators · TTF / WOFF2 / WOFF', font=ui(24), fill=MUTED)
    im.save(ROOT / 'proofs/brand-mono-preview.png')

    im = Image.new('RGB', (1600, 1000), BG)
    d = ImageDraw.Draw(im)
    for row, (label, path) in enumerate([
        ('Geist Mono', ROOT / 'source/reference/GeistMono-Regular.ttf'),
        ('Hito Mono', ROOT / 'fonts/HitoMono-Regular.ttf'),
    ]):
        y = 35 + row * 475
        d.text((48, y), label, font=ui(24), fill=MUTED)
        for i, (text, size) in enumerate([
            ('hito.ai  HitoKey  HitoAI', 48),
            ('G r a t S  H K A I  o O Q  i j .', 48),
            ('à á â ã ä å ā ą · ŕ ř ś š ș ţ ť · İ ï', 29),
            ('Größe · déjà · ação · źródło · țară', 29),
            ('const approve = (key) => key.sign(hash);', 24),
        ]):
            d.text((48, y + 48 + i * 76), text,
                   font=ImageFont.truetype(str(path), size), fill=FG, features=['-liga', '-calt'])
    im.save(ROOT / 'proofs/source-comparison.png')

    im = Image.new('RGB', (1000, 1900), BG)
    d = ImageDraw.Draw(im)
    for row, style in enumerate(STYLES):
        y = 30 + row * 465
        d.text((40, y), 'Hito Mono / ' + style, font=ui(21), fill=MUTED)
        y += 42
        for size in [12, 14, 16, 20, 28, 40]:
            d.text((40, y), str(size) + ' px', font=ui(13), fill=MUTED)
            d.text((103, y), 'HitoKey / HitoAI Il1 O0', font=font(style, size), fill=FG)
            y += size + 17
        d.text((40, y + 10), 'àáâãäåą  ĞĢŕřśšşșťţ  i\u0307 a\u0301', font=font(style, 22), fill=FG)
    im.save(ROOT / 'proofs/small-size-accents.png')
    print('Rendered Hito Mono preview, Geist comparison and reading-size proofs.')


if __name__ == '__main__':
    main()
