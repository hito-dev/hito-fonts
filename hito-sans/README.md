# Hito Sans 0.1

A tailored branch of GroundState Sans 0.2 for **hito.ai**, **hitokey**, **HitoKey**, and **HitoAI**. Three weights: Regular 400, Medium 500, Semibold 600.

## Direction

Hito's emphasis on human approval and control suggested a precise, calm design with a tactile character. The intended result is clearer name recognition and comfortable approval screens; these are design goals, not measured usability claims.

The design retains the parent font's double-storey a, angled terminals, and curved feet. Hito adds:
- Softly squared o/O bowls, repeated in Q.
- Rounded-square dots on i/j and the domain period.
- A slightly raised H bridge.
- Matched small chamfers on K/k.
- A lower A crossbar and refined y exit.
- A compact barred capital I, distinguishing HitoAI and I/l/1.
- Twenty added kerning adjustments focused on the Hito names and adjacent pairs. Accent variants inherit applicable pair values.

The wider capital I receives adjusted advances, precomposed accent placement, and dynamic mark anchors. Inter's optional I alternates remain available in their original form; enabling alternate OpenType features may select other shapes.

## Files

- fonts/: nine font files — three weights in TTF, WOFF, WOFF2.
- hito-sans.css: ready-to-use web font declarations.
- specimen.html: offline interactive specimen with size, weight, and kerning controls.
- hito-sans-specimen.png: all four requested names plus comparison with GroundState Sans.
- hito-reading-accents.png: reading sizes and accent samples.
- wordmarks/: six names, each as an outlined SVG and editable-text SVG.
- build_hito.py, render_hito.py, validate_hito.py: reproducible build and validation.
- source/: parent font binaries, reference Inter instances, and helper source.
- design-changes.json, validation.json: exact changes and check results.
- OFL.txt: original Inter attribution and SIL Open Font License.

## Wordmarks

| Text | Filename stem |
| --- | --- |
| hito.ai | hito-ai-domain |
| hitokey | hitokey-lowercase |
| HitoKey | hitokey-titlecase |
| HitoAI | hitoai-titlecase |
| hito | hito-lowercase |
| Hito | hito-titlecase |

The outlined SVGs contain editable vector paths and do not depend on installed fonts. These paths use the Semibold font's actual shaping and kerning.

The editable-text SVGs keep the name as editable text and require Hito Sans to be installed in the design application. Outlined SVG is the more portable website asset. All filenames are distinct on case-insensitive filesystems.

## Usage

Install the TTF files for design applications.

For web use, copy fonts/ and hito-sans.css into the same project directory and load the stylesheet:

    body { font-family: "Hito Sans", system-ui, sans-serif; }
    h1, h2, .wordmark { font-weight: 600; }
    button, nav { font-weight: 500; }

Start with default letter spacing. The brand pairs already have custom kerning. Use Semibold for the wordmarks and Regular for long text.

## Validation

All font formats reopen successfully and preserve the original character map. HarfBuzz shaping checks 497 Latin NFC/NFD accent cases per weight. The default-feature kerning deltas are verified against the parent family. A corpus of 4,624 letter pairs per weight is checked for new geometric overlaps. Above accents receive clearance checks; the wordmarks and 14–72 px specimens are visually reviewed.

Geometric checks use sampled curves and do not prove universal readability or optimal spacing. The build retains inherited contour overlaps in some letters. Native Windows/macOS browser rendering has not been tested. The preview HTML is provided for local review.

This release has three static text-size weights. It does not include true italics or new variable optical-size masters. Non-Latin forms are preserved where affected components are shared; they are not a newly designed Hito script system.

## Rebuild

Python dependencies: fonttools, brotli, Pillow, uharfbuzz, shapely.

    python build_hito.py
    python validate_hito.py
    python render_hito.py

For proof rendering on macOS or Windows, change the Linux DejaVu Sans label-font path in `render_hito.py` to an installed font.

The GroundState Sans font files in source/ are the exact parent inputs. Their hashes are recorded in design-changes.json.

## License and references

Derived from GroundState Sans 0.2 and Inter.
Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter).
Font software remains under SIL Open Font License 1.1. Keep OFL.txt with redistributed font files. This is an open-font derivative, not an exclusively proprietary font.

Product context reviewed:
https://hito.ai/
https://hito.ai/key/

