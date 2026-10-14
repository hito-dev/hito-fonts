# Hito Mono — 0.1

A monospace companion to Hito Sans, based on Geist Mono. Hito Mono adds subtly squared o/O/Q bowls, rounded-square dots, a raised H bridge, chamfered K/k feet, a lower A crossbar and narrower bars on I.

GroundState fonts live in the separate [GroundState repository](https://github.com/herbstephens/GroundState). This package builds and distributes Hito Mono only; shared outline transformations remain part of its build.

## Included

- Four upright faces: Regular (400), Medium (500), Semibold (600), Bold (700).
- TTF for desktop installation; WOFF2 and WOFF for web embedding.
- `brand-mono.css`: all four web font declarations and example classes.
- `specimen.html`: offline specimen with editable sample text, size and weight controls, and light/dark mode. Keep it beside the CSS and fonts folder.
- Three rendered proofs in `proofs/`: overview, source comparison, and small-size/accent checks.
- Python build, validation and proof-rendering scripts; pinned upstream variable font; original licenses and provenance.

## Install

On macOS, select the TTF files in `fonts/`, open them in Font Book, and install. Choose **Hito Mono** in your app. Restart apps if the families do not appear immediately.

Regular and Bold use standard style linking. Medium and Semibold have separate legacy family names for older applications, while modern applications can group all four weights under the typographic family.

## Web use

Copy `brand-mono.css` and `fonts/` together, then load the stylesheet:

```html
<link rel="stylesheet" href="brand-mono.css">
<code class="hito-mono">git commit -S</code>
```

```css
.approval-details {
  font-family: "Hito Mono", ui-monospace, monospace;
  font-weight: 400;
  line-height: 1.5;
  font-kerning: none;
  font-variant-ligatures: none;
  font-synthesis: none;
}
```

Start with 14–16 px for dense code, 16–18 px for approval details, and Medium for compact labels. These are design starting points; test your actual background and device. For security-sensitive identifiers, preserve case and punctuation and avoid extra letter spacing.

## Mono behavior

Standard text occupies **600 units per character at 1000 units/em**, or 0.6 em. Combining marks have zero advance. All original advance widths are preserved, including alternate and special-purpose glyphs.

Source coding ligature features `liga` and `ss11` are removed from the active feature registrations. Operators such as `=>`, `!=` and `===` remain literal, separate characters by default. No pair kerning is added. Accent attachment is retained.

The original slashed zero, barred capital I, and distinct lowercase l and numeral 1 are retained. Hito's narrower I bars do not change its width.

## Validation

`validation.json` records checks on the exported fonts:

- 4 faces and all 3 export formats loaded successfully.
- 36,100 printable-ASCII pair shaping checks; every character stays on the 600-unit grid.
- 1,068 Latin NFC/NFD equivalence checks.
- Mark clearances and selected Latin/accented neighbor collisions checked against the source.
- All original Unicode mappings and advances preserved.
- Every intended base-glyph edit verified against the source.
- Actual font raster proofs reviewed at 12–68 px.

These are **version 0.1 development fonts**. Raster proofs use FreeType; macOS and Windows native rendering and installation have not been tested. Hint instructions are removed. Four static upright weights are supplied; no italics or custom variable-font output. The upstream variable font under `source/` is a rebuild input, not a branded variable release. Inherited stylistic alternatives can select original Geist forms. Existing Greek and Cyrillic designs are preserved; this project does not add language coverage.

## Rebuild

Use Python 3.12 and the dependency versions recorded in `requirements.txt`:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 build.py
python3 validate.py
python3 render.py
```

`render.py` uses the bundled Hito Sans for proof labels. HarfBuzz-backed Pillow text rendering is needed for the comparison proof.

## Source and license

Based on Geist Mono by the Geist Project Authors, from the official [vercel/geist-font repository](https://github.com/vercel/geist-font), pinned to the commit in `source/provenance.json`. The pinned variable font reports version 1.700.

The derivative family remains under **SIL Open Font License 1.1**. Commercial use, embedding and modification are permitted subject to the license. Preserve copyright and license notices when redistributing. The font software may not be sold by itself and must remain under OFL; documents and artwork made using it do not inherit that requirement. See `OFL.txt` and `source/AUTHORS.txt`.

The Python scripts in this package are licensed under MIT; see `LICENSE-BUILD.txt`.
