# Trace-Certified Hybrid LDPC Decoding

This research artifact accompanies **Trace-Certified Hybrid LDPC Decoding: A SELL-Style Operational Specification**. It connects classical BEC peeling and residual Gaussian elimination to independently checkable success/failure certificates and an asynchronous transition specification inspired by subexponential linear logic.

The central logical result relates **the same specified trace** in both directions: arbitrary admissible rewrite interleavings emit valid operational traces, and each valid operational trace has a derivation to its normalized endpoint with the accumulated log retained. Pending known incidences are represented explicitly. Two persistent SELL labels organize the specification but are not necessary for these rules; no SELLF sequent-calculus adequacy is claimed.

The manuscript proves success/failure soundness, certificate existence, residual equivalence, completion multiplicity, the BEC maximum-likelihood statement including endpoint qualifications, and sparse checking bounds. Direct word verification already establishes final parity and channel agreement; trace replay additionally checks a declared operational explanation. Neither implies that an untrusted producer internally followed that explanation, or that the completion is the transmitted word.

See [PUBLICATION_READINESS.md](PUBLICATION_READINESS.md) for the final scope and remaining publication limitations, and [CHANGELOG_PUBLICATION.md](CHANGELOG_PUBLICATION.md) for substantive repairs. The branch is `codex/publication-audit`. No submission or public release was made.

## Files

| Path | Purpose |
|---|---|
| `SELLTCFULL.tex`, `paper/*.tex`, `SELLTCFULL.bib` | English manuscript and bibliography |
| `SELLTCFULL.pdf` | Compiled manuscript |
| `lmcs.cls` | Unmodified LMCS class, downloaded 20 September 2026 |
| `lean4/` | Pinned Lean library, typed checker, executable adapter and verification documentation |
| `selltcfull_experiments.py` | Sparse checker, independent direct checker, dense comparator and decoder |
| `publication_experiments.py` | Declared campaign, validation and analysis |
| `generate_certificate_cases.py` | Adversarial and differential input cases |
| `SELLTCFULL_experiments.ipynb` | Executed reproducibility notebook |
| `requirements-publication.txt` | Pinned direct Python dependencies |
| `tests/` | Domain, algebra, checker, rewriting and experiment regression tests |
| `publication_outputs/` | New measurements, matrices, manifests, analysis, figures and measurement-source snapshots |
| `SELLTCFULL_outputs/` | Unchanged original experimental outputs; not the revised paper's evidence |
| `originals/baseline-6bb47d9.tar.gz` | Complete archive of every tracked baseline artifact |
| `audit/` | Initial audit, repair records, independent reviews and executed verification evidence |

## Python installation and tests

The executed environment was Python **3.12.14** on macOS arm64. Use a Python 3.12 installation:

```sh
python3.12 -m venv .venv-publication
.venv-publication/bin/python -m pip install -r requirements-publication.txt
.venv-publication/bin/python -m pytest tests -q
.venv-publication/bin/python generate_certificate_cases.py
```

Direct dependencies are NumPy 2.3.5, pandas 2.2.3, Matplotlib 3.10.7, pytest 8.4.2, nbclient 0.10.2, nbformat 5.10.4, ipykernel 6.30.1 and Jinja2 3.1.6. The run manifest records host and package information. Python is independently implemented and tested; it is **not formally verified or extracted from Lean**. A validated `Graph` with ordinary binary/erasure inputs is the sparse checker boundary. Malformed JSON and nonbinary values are rejected by the public certificate path.

## Regenerate analysis and rerun measurements

To rebuild tables and figures from the supplied raw data:

```sh
.venv-publication/bin/python publication_experiments.py --output publication_outputs --analyze-only
```

To run the declared campaign again, use a **new directory**:

```sh
.venv-publication/bin/python publication_experiments.py --output reproduction_outputs
```

The campaign comprises 720 clean trials and 480 corruption trials on 24 matrices, plus 90 checker-scaling trials on 15 independent matrices. Timings vary between runs and hosts. The configuration is saved before sampling. Matrix/channel/word/measurement streams have deterministically derived seeds. Repetitions on one matrix are not independent matrix realizations. The code refuses to overwrite an incomplete run silently; a completed run can regenerate analysis without taking new measurements.

The notebook regenerates every paper figure and table using the same module. Execute it from the repository root:

```sh
.venv-publication/bin/python -m ipykernel install --sys-prefix --name selltc-publication
.venv-publication/bin/python - <<'PY'
from pathlib import Path
import nbformat
from nbclient import NotebookClient
path = Path('SELLTCFULL_experiments.ipynb')
nb = nbformat.read(path, as_version=4)
NotebookClient(nb, timeout=600, kernel_name='selltc-publication',
               resources={'metadata': {'path': str(Path.cwd())}}).execute()
nbformat.write(nb, path)
PY
```

The notebook includes a clearly named output-directory setting. Use a fresh directory there to take new measurements instead of regenerating analysis from the supplied complete run. The old output directory is never used as a new campaign destination.

The published-in-this-artifact data show 720/720 valid clean completions but only 562/720 exact recoveries, with 174 nonunique residual systems. Of 251 actually corrupted inputs, 100 remained compatible and 151 produced accepted impossibility certificates. In the separate scaling experiment, direct word checking was faster and used less incremental tracked memory than trace replay. These are finite experimental observations, not universal performance or corruption-detection guarantees.

## Lean

Install Lean's `elan` toolchain manager, then run:

```sh
cd lean4
lake exe cache get
./verify.sh --clean
lake env lean StatementAudit.lean
```

`lean-toolchain` selects Lean 4.14.0. `lake-manifest.json` pins Mathlib and its dependencies; the Mathlib revision is `4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84`. Do not run `lake update` as part of reproduction, since it may change resolved dependencies. The default library target imports the proof modules. `./run_checker.sh` executes the JSON-lines checker via the Lean interpreter. The separately built native executable was rejected by the macOS 27 loader on the audit host, so native execution is not a reproduction prerequisite or a claimed passing check. See [lean4/README.md](lean4/README.md) and [audit/LEAN_VERIFICATION_REPORT.md](audit/LEAN_VERIFICATION_REPORT.md) for executable commands, actual theorem statements, axiom-dependency evidence and differential testing.

The formal state derives degree/syndrome from a partial assignment, whereas Python caches them. The Lean context is a canonical finite-set/event representation, not a mechanized quotient of arbitrary malformed multisets. Formal soundness applies to typed data; JSON parsing and runtime execution are separate trust boundaries. The raw-token correspondence, logical-label erasure, sparse complexity, Python Gaussian elimination and empirical claims are not presented as Lean theorems.

## Compile the paper

The final PDF was built with native **Tectonic 0.17.0** and the supplied LMCS class. From the repository root:

```sh
tectonic --keep-logs --keep-intermediates SELLTCFULL.tex
```

Tectonic runs BibTeX and the required reference-resolution passes, downloading its TeX dependencies on first use. The source uses `alphaurl` and DOI metadata, and includes the generated files under `publication_outputs/`. Regenerate those outputs before compiling after an analysis change. The source also provides the XeTeX hyperref driver explicitly because the class otherwise selects a pdfTeX driver under this Tectonic environment. A narrow preamble compatibility patch enlarges the class's empty first-page header boxes while keeping `headheight + headsep` fixed; it removes two class-origin box warnings without changing text-block geometry. The class file itself is unchanged. The installed x86_64 `pdflatex` on the audit host could not execute on arm64; it was not represented as a successful build.

## Limitations and preservation

This is a case study using classical decoding and certifying-algorithm ideas. The demonstrated contribution is a precise delayed-propagation invariant and trace correspondence, their scoped mechanization, and an auditable implementation study. These do not establish the necessity of subexponentials or sufficient novelty for acceptance at LMCS. Only three matrices per condition constrain ensemble inference. Memory measurements are incremental Python-tracked allocations, not process RSS. Timing slopes are descriptive finite-size fits.

The origin repository was private at the audit. Local reproducibility does not constitute public artifact availability or an archival DOI. Submission, licensing/release choices and scientific positioning require the author's review. The archive preserves the original manuscript, notebook, Lean code and outputs, including their documented defects. Consult [audit/SOURCE_PROVENANCE.md](audit/SOURCE_PROVENANCE.md) before comparing old and new results.
