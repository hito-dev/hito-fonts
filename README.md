# Hito Fonts

Hito Sans and Hito Mono for Hito apps, websites and documents. This repository contains font files, source inputs, build tools, specimens and validation reports.

| Family | Weights | Formats | Package |
| --- | --- | --- | --- |
| Hito Sans 0.1 | Regular 400, Medium 500, Semibold 600 | TTF, WOFF, WOFF2 | [hito-sans](hito-sans/) |
| Hito Mono 0.1 | Regular 400, Medium 500, Semibold 600, Bold 700 | TTF, WOFF, WOFF2 | [hito-mono](hito-mono/) |

These are development releases. The family READMEs describe design changes, checks and known limitations. No GitHub release or version tag has been created by this import.

## Use

Install TTF files from each package's `fonts/` folder for desktop use, or bundle them in applications. Use WOFF2 for websites. Copy the relevant fonts and their OFL notice into consuming projects and record the version used.

For websites, keep each stylesheet beside its `fonts/` directory:

```html
<link rel="stylesheet" href="hito-sans/hito-sans.css">
<link rel="stylesheet" href="hito-mono/brand-mono.css">
```

```css
body { font-family: "Hito Sans", system-ui, sans-serif; }
code, pre { font-family: "Hito Mono", ui-monospace, monospace; }
```

Open `hito-sans/specimen.html` or `hito-mono/specimen.html` to inspect the families locally. Sans includes outlined and editable wordmarks. GroundState fonts are maintained in the separate [GroundState repository](https://github.com/herbstephens/GroundState). Hito Mono includes only the four Hito weights; Sans retains its exact GroundState Sans source inputs for rebuilding.

## Build and validate

Run commands from the relevant family folder. Use a separate Python virtual environment for each package. See the family READMEs for dependencies and commands:

- [Hito Sans build and validation](hito-sans/README.md#rebuild)
- [Hito Mono build and validation](hito-mono/README.md#rebuild)

The scripts use font inputs kept in `source/`. The Sans rendering script references a Linux DejaVu Sans path for proof labels; adjust it on other systems as described in its README. Mono uses the bundled Hito Sans for labels. Mono proofs and validation were regenerated for the Hito-only package; Sans reports were imported with its source package.

## Licence

Font software is licensed under **SIL Open Font License 1.1**; see [LICENSE](LICENSE). Retain each family's copyright and licence notices when redistributing:

- Hito Sans derives from [GroundState Sans](https://github.com/herbstephens/GroundState) and [Inter by Rasmus Andersson and the Inter Project Authors](https://github.com/rsms/inter). See [hito-sans/OFL.txt](hito-sans/OFL.txt).
- Hito Mono derives from Geist Mono. See [hito-mono/OFL.txt](hito-mono/OFL.txt) and the upstream notices in `hito-mono/source/`.
- Mono's original build/validation scripts and specimen have the separate MIT terms in [hito-mono/LICENSE-BUILD.txt](hito-mono/LICENSE-BUILD.txt). The root font licence does not replace that notice.
