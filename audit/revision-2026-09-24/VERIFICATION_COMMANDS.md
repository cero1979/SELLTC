# Verification commands and outcomes

Date: 24 September 2026. Commands were run from the repository root unless stated otherwise. All final verification commands exited zero. Native cached runtimes were used because unrelated system tools on this host include x86_64 installations.

## Repository and preserved artifacts

`/usr/bin/git status --short --branch`, `/usr/bin/git log`, `/usr/bin/git ls-files`, `rg --files` and targeted source reads established the clean starting branch `codex/publication-audit` at `d277e952e256cabbac39c08af8a66f4b5f85a612`. `GIT_TERMINAL_PROMPT=0 /usr/bin/git ls-remote --heads origin codex/publication-audit main` confirmed that remote branch SHA and main at `6bb47d9781d813dff526e043c9d0ad35d37ed0a4`.

An inline `.venv-publication/bin/python` inventory/hash command recorded all 223 tracked starting files in `repository-inventory.txt` and `pre-revision-hashes.json`. The final inline preservation check compares the selected protected paths with those hashes: **105 unchanged files**. Separate textual extraction compared all 18 original labelled lemma/proposition/theorem statement-and-proof blocks with `git show HEAD:<path>` before the revision commit; every block matches. `integrity-checks.json` records the label/citation/numbering checks. `git diff --check` passes.

## Lean

From `lean4/`:

```sh
export PATH='/Users/cero/Downloads/Articulos/SELLTeoCod/SELLTCFULL_bundle/audit/toolchains/lean-4.14.0-darwin_aarch64/bin:/usr/bin:/bin:/usr/sbin:/sbin'
./verify.sh --clean
lake env lean StatementAudit.lean
```

Both exit **0**. The first expands to `lake clean selltc`, `lake build`, `lake env lean AxiomAudit.lean` and `lake env lean Main.lean`. All modules/root compile; all 51 axiom-audited declarations depend only on subsets of `propext`, `Classical.choice` and `Quot.sound`. Full output: `lean-verification.txt`, `lean-statements.txt`. No Lean sources, manifest or toolchain specification changed. The JSON adapter is elaborated, not newly subjected to the historical 575-case differential run in this revision.

## Python and non-timing reproducibility

```sh
.venv-publication/bin/python -B -m pytest -q -p no:cacheprovider tests
```

Result: **29 passed in 1.44s**, exit **0**.

The existing reproduction script was then executed with this exact read-only adaptation:

```python
from pathlib import Path
p = Path('audit/verify_experiment_reproduction.py').resolve()
s = p.read_text()
old = "(out/'reproduction_validation.json').write_text(json.dumps(summary,indent=2))"
assert s.count(old) == 1
s = s.replace(old, "print('Read-only reproduction summary:', json.dumps(summary,sort_keys=True))")
exec(compile(s, str(p), 'exec'), {'__name__': '__main__', '__file__': str(p)})
```

Run with `.venv-publication/bin/python -B`. Exit **0**; matches all 39 matrices, 1,200 non-timing outcomes and 90 scaling inputs/traces. All 13 original output files match the preserved earlier commit. The command changes no script or output file; no timing campaign, analysis regeneration or notebook execution was requested. `python-verification.txt` records complete command arguments and output, including the before/after hashes of 83 paths at that stage. Girard pagination was intentionally corrected later; every experimental file remains unchanged.

## Manuscript build and PDF checks

```sh
audit/toolchains/tectonic/tectonic --keep-logs --keep-intermediates SELLTCFULL.tex
pdfinfo SELLTCFULL.pdf
pdftoppm -scale-to 1500 -png SELLTCFULL.pdf audit/rendered-pages/revision-2026-09-24/page
```

Final build and rendering exit **0**. Native Tectonic 0.17.0 produces 27 letter pages; final log has no overfull/underfull boxes, LaTeX warnings, unresolved citations or duplicate labels. Four initial horizontal overflows were resolved by prose line wrapping. A subsequent `samepage` layout attempt kept the principal theorem together but produced an underfull vertical box; replacing it with `needspace` retained the complete theorem on page 15 without that warning. No experimental table or figure was changed to obtain the layout.

Bundled Python with `pypdf` extracted all pages and checked absence of `??`. It counted 18 abstract lines. Inline source/auxiliary checks found 52 unique labels, 63 reference uses, 16 cited bibliography entries and the preserved principal result numbers. PIL produced seven contact sheets from Poppler renders; these and the main-theorem page were inspected. Final page hashes are recorded separately from the first inspected pass so changed pages were not treated as previously reviewed.

The PDF operation marker ran successfully once with the bundled Node executable before manuscript authoring. Its arguments were `--operation-kind edit --expected-output-count 1 --output-format pdf`.

## Environment corrections, not hidden passing checks

- The first inventory command used the system Python 3.8 x86_64 interpreter. Its native Git child failed through incompatible `libxcrun`; the same inventory then succeeded under `.venv-publication/bin/python` (arm64). No artifact hashes were accepted from the failed attempt.
- `node` was absent from the shell PATH; the PDF marker succeeded using the explicit bundled Node path.
- An initial statement-audit command incorrectly prepended a repository-relative toolchain path from inside `lean4/`; it exited 127. The explicit absolute native toolchain path above corrected it, and the complete statement audit then exited 0.
- The staged whitespace check detected two blank PDF-extraction lines containing spaces. They were normalized before the remote push, the artifact manifest was refreshed, and the final complete revision diff passes. No PDF/source content changed.
- Publisher access restrictions and two Crossref 429 responses are disclosed with primary-source fallbacks in `coding-experiment-review.md`. No unsupported source metadata was invented.

## Remote update

After all verification and the English commit, the authorized dispatch uses:

```sh
GIT_TERMINAL_PROMPT=0 /usr/bin/git push origin codex/publication-audit
GIT_TERMINAL_PROMPT=0 /usr/bin/git ls-remote --heads origin codex/publication-audit
/usr/bin/git status --short --branch
```

The final task response reports the actual pushed commit and the result of comparing it with the remote. No force push, main merge, PR, release, archival upload or journal submission is part of this update.
