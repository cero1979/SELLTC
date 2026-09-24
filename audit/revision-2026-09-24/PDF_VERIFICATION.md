# Revised manuscript PDF verification

Date: 24 September 2026. Final output: `SELLTCFULL.pdf`, **27 US-letter pages**, built with native Tectonic 0.17.0.

The final compiler run exits zero with no overfull/underfull boxes, LaTeX warnings, undefined references/citations or duplicate labels. Bibliography has 16 entries. Text extraction contains no unresolved `??` tokens. The abstract occupies **18 rendered lines**. The original LMCS class, font choices, author data and text-block geometry are preserved. `needspace` keeps the complete principal theorem statement on one page without forcing global paragraph stretching; Theorem 6.10 begins page 15 and retains its complete proof there.

All 27 pages were rendered with Poppler at maximum dimension 1500 pixels. Seven four-page contact sheets cover the complete manuscript (the last has three pages). Inspection included the title and abstract, headers, margins, all equations, new abstract proposition and its proof, main theorem, label-erasure result, representation-boundary table, Lean declaration table, all four figures, generated experiment tables, conclusion and bibliography. No clipping, overlap, unreadable glyphs, blank manuscript page or broken caption was found. The main theorem page was additionally inspected at full rendered size.

After the first complete inspection, a layout pass kept the principal theorem together and shortened two prose passages without changing mathematical content. Final rendered pages 1--2 and 14--27 were different and were inspected again through updated contact sheets; pages 3--13 remained byte-identical to the already inspected renders. `pdf-first-pass-hashes.json` and `pdf-page-hashes.json` record that comparison. All retained `pdf-contact-*.jpg` sheets now show the final PDF.

The new scope table shifts the automatic table numbering but changes none of the generated experiment table contents or source bytes. Figure sources and captions, all trial counts, timings and uncertainty intervals remain unchanged. Scientific claims and original proofs have separate review/preservation evidence; successful rendering is not used as a mathematical or runtime-verification claim.

The class's automatic preprint/copyright boilerplate is not evidence of journal submission. The 23 September PDF report and old hash snapshot describe the earlier 23-page artifact; this dated report and `final-artifact-hashes.json` bind the current output and sources. No manuscript source or figure/table input was edited after the final successful build.
