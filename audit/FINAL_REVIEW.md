# Final independent review and resolution record

Date: 23 September 2026. Scope: the reconstructed English manuscript and local artifact on `codex/publication-audit`, not the preserved baseline. This is a simulated interdisciplinary review performed by separate agent assignments and a coordinating integrator; it is not external peer review or a journal acceptance decision.

## Verdict

**No known blocking mathematical, formal-scope or experimental contradiction remains within the final stated claims.** The source compiles to a 23-page PDF, the current Lean root package builds without admitted results, the Python suite and notebook execute, and the reported numerical results match the retained CSVs. This technical verdict does not establish sufficient novelty or public artifact availability for LMCS. Those limitations are retained in [PUBLICATION_READINESS.md](../PUBLICATION_READINESS.md).

## Reviewer assignments and independence

| Reviewer | Scope and record | Independence |
|---|---|---|
| A: logic and formal methods | [REVIEW_A_LOGIC.md](REVIEW_A_LOGIC.md) | Fresh reviewer who did not author the repaired semantics or Lean library; inspected the actual statements/proofs, independently reran the axiom audit and checked source hashes. |
| B: coding theory | [REVIEW_B_CODING.md](REVIEW_B_CODING.md) | Fresh reviewer who did not author the manuscript or implementation; reviewed algebra, BEC/ML, stopping sets, complexity and result interpretation, and executed separate boundary/likelihood probes. |
| C: experiments and reproducibility | [REVIEW_C_EXPERIMENTS.md](REVIEW_C_EXPERIMENTS.md) | Reviewer independent of the Python/experiment author; regenerated every matrix and clean/corruption observation, audited repeated timings and reproduced aggregates. This reviewer authored the separate raw rewriting test model, so that model is not claimed to have an independent self-review. |

An earlier independent review of the coordinator's core mathematics is recorded in [SEMANTICS_REPAIR.md](SEMANTICS_REPAIR.md). The additional [mechanization scope cross-check](MECHANIZATION_SCOPE_CROSSCHECK.md) is explicitly limited to comparing canonical Lean representations with the paper; it is not a second independent review of its author's semantics fragment.

## Concrete objections and resolutions

| Issue and location | Severity | Resolution and recheck |
|---|---|---|
| Original exact endpoint discards Solve logs; weak context invariant allows duplicates and stale metadata (`lean4/SELLCert/Adequacy.lean`, original Rewriting; paper Section 6) | Blocking | Replaced by exact pending-incidence invariants, explicit trace indices and normalized logged endpoints. A inspected both directions for the same trace and arbitrary interleavings. Original counterexamples remain in the initial audit. |
| Original ML conclusion was `True`, separator completeness admitted, and failure soundness omitted forced-value agreement | Blocking | Genuine finite-field separation, completion-preservation and real-valued BEC maximization proofs compile; all 51 named results' transitive dependencies were inspected. A found no artificial assumption or vacuous substitute. |
| Zero-row solution was described as an empty vector despite q>0 (`paper/core.tex`, finite-field alternative) | Required mathematical correction | Changed to the q-dimensional zero vector; rechecked by the earlier mathematical reviewer and fresh B. |
| GE storage/operation accounting omitted q-dimensional output when m=0 (`paper/core.tex`, final cost paragraph) | Required boundary correction | Added q terms; fresh B checked zero-row and zero-column systems. |
| Hostile trace might be fully schema-scanned before the stated n+1 bound (`paper/core.tex`, checker definition/cost proof) | Required cost correction | Length cap precedes traversal. B used a list subclass that raises on iteration and confirmed both public checkers reject oversized traces without iteration. |
| Empty-trace Lean checker completeness could be read as every-prescribed-trace completeness (`paper/mechanization.tex`, formal report and Lean README) | Required scope clarification | Explicitly separated all-trace adequacy and soundness, arbitrary-residual witness equivalence, and empty-trace checker existence theorems. A reread and closed the objection. The stronger manuscript certificate theorem retains its full informal proof. |
| Global termination including Solve could be inferred from Lean normalization claims | Required scope clarification | Explicitly listed as manuscript-only; Lean propagation decrease/normalization/confluence remain accurately identified. A confirmed. |
| Historical `lean_environment.json`/`lean_source_inventory.json` appeared to conflict with current verification | Required provenance clarification | Formal report identifies these as baseline evidence; `lean_verification_summary.json` and clean-build/axiom outputs identify the repaired source. A checked all 13 current recorded hashes. |
| Reanalysis used live defaults rather than saved configuration (`publication_experiments.py`) | Major reproducibility | Analysis now uses the saved configuration for bootstrap seed/count and validates grid/raw hashes. Regression tests pass; C reproduced all summaries/intervals. |
| `--analyze-only` could bypass data-integrity checks | Major reproducibility | Validation and existing manifest hash checks precede analysis. C reviewed the correction. |
| “Atomic” checkpoint comment and hardcoded recovery total | Reproducibility/editorial | Removed unsupported atomicity wording; totals derive from validated trial counts. Raw measurements unchanged. |
| Internal `check_s` includes returned-word agreement assertion (`selltcfull_experiments.py`, pipeline wrapper) | Measurement-definition correction | Generated table says “Check ms”; prose distinguishes internal stage from standalone `trace_check_s`. Denominators and raw records were preserved. |
| Comparator caption could imply ten observations per family | Editorial denominator | Changed to three matrices per family and ten observations per matrix. |
| 100% clean completion might be mistaken for a new recovery guarantee | Optional B clarification, adopted | Results now state explicitly that the transmitted word guarantees clean compatibility; completion rate is implementation evidence. Counts and claims unchanged. |
| Long bibliography URL caused poor spacing; blank first-page class header caused two box warnings | Editorial/build | Verified and used Feldman's DOI, retained the unmodified LMCS class, and added a narrowly documented header-box compatibility patch preserving text-block geometry. Final build has no box, missing-reference or font warnings. |

## Executed final evidence

- **Lean:** clean root-package rebuild passes with Lean 4.14.0 and pinned Mathlib. All **51** named lemmas/theorems are covered by `AxiomAudit.lean`; only `propext`, `Classical.choice` and `Quot.sound` occur transitively. Statement audit and strict JSON runner type-check. See [formal verification report](LEAN_VERIFICATION_REPORT.md).
- **Differential checker:** **575/575** exact acceptance/output matches, comprising 369 accepted and 206 rejected cases. The interpreter and wrapper produce the same outputs. Native executable loading fails on this macOS host and is not represented as a passing runtime check.
- **Python:** **29 tests pass** in the final coordinator run; [saved output](evidence/python-final-tests.txt). The suite includes 5,054 brute-force-checked finite systems and the raw rewriting tests. C's separate independent oracle matched **64,151** acceptance decisions. B additionally checked **777** finite BEC likelihood cases.
- **Rewriting diagnostics:** 2,719 matrix/observation instances, 6,251 reachable contexts, 3,724 raw rewrite edges, 144 propagation diamonds and 4,889 exact operational traces are checked in the bounded test model. These are tests, not universal mechanized proofs about raw multisets.
- **Campaign:** 720 clean, 480 corruption and 90 scaling trials actually executed. C independently regenerated 39 matrices and 1,200 ordinary outcomes; the experiment workflow also reproduced all 90 scaling traces. Every expected algorithm/repetition identity and reported median was checked. All raw hashes and executed-source snapshot hashes match.
- **Notebook:** all **five** code cells executed in the experiment author's run and again in the coordinator's explicitly registered project kernel; [coordinator record](evidence/notebook-root-verification.txt). Reanalysis does not take a second timing campaign.
- **Article:** native Tectonic 0.17.0 builds the final English source with BibTeX/alphaurl and 16 verified references. All 23 rendered pages were visually inspected, including individual inspection of final bibliography changes. Final LaTeX has no unresolved citations/references or overfull/underfull boxes. See [PDF verification](PDF_VERIFICATION.md), [build evidence](evidence/manuscript-build.txt), and [final hashes](evidence/final-artifact-hashes.json).
- **Preservation:** original output files remain byte-identical to the archived baseline. No remote write, push, PR, release or submission was performed.

## Retained criticisms

The work is a narrowly scoped case study, not a new decoding algorithm or proof of SELL necessity. An end-to-end theorem from arbitrary serialized Python input to raw SELL derivability is absent and is not claimed. The matrix and observation are trusted inputs, trace validity is not internal execution attestation, and compatible corruption cannot be rejected by feasibility alone. Three matrices per condition limit statistical inference. A private repository is not a public archival artifact. The author's assessment of novelty, journal fit, public release and submission remains necessary; these criticisms have not been removed to obtain a favorable technical review.
