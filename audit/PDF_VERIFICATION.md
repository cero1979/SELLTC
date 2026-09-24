# Final manuscript build and visual verification

Date: 23 September 2026. Final output: `SELLTCFULL.pdf`, 23 US-letter pages.

## Build

Executed from the repository root with native arm64 Tectonic 0.17.0:

```sh
audit/toolchains/tectonic/tectonic --keep-logs --keep-intermediates SELLTCFULL.tex
pdfinfo SELLTCFULL.pdf
pdftoppm -scale-to 1500 -png SELLTCFULL.pdf audit/rendered-pages/page
```

The final build exits zero and runs BibTeX plus the required reference-resolution passes. `audit/evidence/manuscript-build.txt` is its output; `audit/evidence/pdf-info.txt` records PDF metadata. The final engine log contains no undefined references/citations, font warning, or overfull/underfull box. There are 16 bibliography entries. Extraction with pypdf found no unresolved `??` tokens.

The current official LMCS class is retained byte-for-byte. The manuscript uses its theorem environments, default fonts, ORCID macro and alphaurl bibliography. The XeTeX hyperref driver is explicit. The class's empty first-page header has undersized fixed boxes under this engine; a documented preamble patch expands only those header boxes and offsets head separation to preserve the text block. This eliminates class-origin vertical box warnings. No `sloppy`, manual body spacing or font replacement masks content overflow. The long Feldman bibliography URL was replaced by its directly verified DOI, and bibliography entries are kept together across page boundaries.

The class automatically prints preprint/copyright boilerplate. That boilerplate is not evidence of an actual journal submission or a new public release; neither was performed.

## Visual inspection

All 23 pages were rendered at 1500-pixel maximum dimension and inspected through six four-page contact sheets. The review checked title/author/ORCID placement, abstract length, page headers, margins, mathematical glyphs, theorem/proof breaks, displayed equations, table widths, all four figure labels/legends/captions, references and final-page boilerplate. Tables and figures are readable and remain within the text block; no clipping, overlap, blank page or unresolved reference was found.

After the final bibliography/Proposition-reference adjustment, pages 1–20 rendered byte-identically to the inspected version. Pages 21–23 were inspected again individually at full rendered size. The updated contact sheets now correspond to the final PDF. `pdf-page-hashes.json` records the final page rasters; `pdf-prior-page-hashes.json` records the comparison used to avoid claiming an unseen replacement page was reviewed.

Compact review evidence is retained in `audit/evidence/pdf-contact-01.jpg` through `pdf-contact-06.jpg`; full page PNGs are local ignored QA intermediates. `manuscript-extracted.txt` is a supplementary text check, not a substitute for the visual inspection. The host did not provide `pdftotext`, so pypdf was used for extraction; PDF rendering itself succeeded through Poppler.

## Source/output binding

`audit/evidence/final-artifact-hashes.json` includes the final PDF, master TeX, every included paper fragment, bibliography, class, included generated TeX tables/results and all four figure PNGs, together with the code/configuration and raw data. No source or output was edited after the final successful build. PDF timestamps can differ in a future build, so bit-for-bit cross-run PDF identity is not promised; the checked-in output is bound to this final source set and compile record.

The abstract occupies 15 rendered lines, below the normal 20-line LMCS guidance. The 23-page manuscript is below its usual 50-page limit. Author information and the affiliation are preserved from the supplied manuscript. Scientific originality, author approval and public archival preparation are assessed separately in `PUBLICATION_READINESS.md`.
