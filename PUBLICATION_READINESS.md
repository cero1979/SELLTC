# Publication readiness

Assessment date: **23 September 2026**. Repository: `cero1979/SELLTC`. Local branch: `codex/publication-audit`.

## Decision

**The authorized local audit and reconstruction are complete. The artifact is technically coherent and ready for the author's scientific review; it is not declared ready for immediate LMCS submission.** No known blocking defect remains within the revised mathematical claims, accurately scoped mechanization and recorded experimental evidence. Sufficient novelty for an international journal is not established by compilation, testing or this simulated review, and the private origin has not been publicly archived.

The final deliverable is a **23-page English manuscript** (`SELLTCFULL.tex`, `paper/`, `SELLTCFULL.bib`, `SELLTCFULL.pdf`), a repaired Lean library, a tested Python implementation and executed notebook, regenerated data/figures, original artifacts preserved intact, and auditable review/build records. No push, PR, release, arXiv posting or journal submission was performed.

## Mathematical results established

The manuscript supplies complete proofs of:

1. Coherent peeling state updates and preservation of every original compatible completion by every valid partial trace.
2. Stopping-set characterization, with structural exhaustion distinguished from parity consistency on corrupted inputs.
3. A bijection between residual solutions and all original compatible codewords; nullity and uniqueness consequences.
4. Success-certificate soundness and left-kernel failure soundness/completeness, including zero-dimensional, redundant and degree-zero cases. For every specified valid partial trace, one certificate status has an acceptable witness.
5. Gaussian row-transformation witness extraction, including why inconsistent echelon systems expose a contradictory row.
6. Genuine BEC maximum-likelihood completion for erasure probabilities in `[0,1]`, with zero-probability endpoint and exact-recovery qualifications.
7. Exact raw-token invariants with delayed known incidences; propagation stuttering and commutation; Solve validity under arbitrary interleavings; normalization, rewrite termination and maximal-run behavior.
8. Soundness and completeness for the **same chronological trace**, with the accumulated log retained at the normalized endpoint.
9. Event-preserving erasure of the two persistent subexponential labels, and translation to ordinary consume-and-recreate rewriting on admissible contexts.
10. Sparse `O(n+m+E)` checker upper bounds in the stated word-RAM/adjacency model, separate dense/producer costs and bit-size bounds. No unsupported universal optimality is claimed.

## What Lean establishes

Lean **4.14.0**, pinned Mathlib commit **`4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84`**, builds the complete root library. All **51 named lemmas/theorems** have inspected transitive axiom output limited to ordinary Lean foundations (`propext`, `Classical.choice`, `Quot.sound`). No project admission, `sorryAx`, artificial axiom, `native_decide` shortcut or `True` replacement supports the claims.

Mechanized results include forced assignment agreement, typed replay correctness, update equations, real linear-algebraic separator existence, success/failure soundness, residual witness equivalence, **empty-trace checker completeness**, real-valued BEC likelihood maximization, pending-set preservation, propagation normalization/confluence, arbitrary-interleaving adequacy soundness and exact logged completeness for every operational trace.

This scope is precise: canonical contexts enforce token uniqueness through functions/finite sets. The raw-multiset representation bridge and SELL-label erasure are informal proofs. Global rewrite termination including Solve, stopping-set/nullity results, the all-prescribed-trace checker-completeness theorem, Gaussian-elimination implementation, complexity/bit-size bounds and experimental claims are not presented as complete Lean theorems. The BEC formalization uses the closed-form likelihood; its coordinate-product interpretation is proved in the manuscript. No SELL/SELLF deductive calculus is formalized.

Lean and Python agreed on **575 differential cases** (369 accepted, 206 rejected), including returned success words. This is finite test evidence, not a refinement proof for Python or JSON parsing. The executed Lean path is `lake env lean --run Main.lean` / `run_checker.sh`: the native binary builds but cannot load under the audited macOS 27 runtime. This platform limitation remains documented; it does not invalidate the kernel-checked proofs or the successful interpreter run.

Full commands, statements, dependencies and source hashes: [LEAN_VERIFICATION_REPORT.md](audit/LEAN_VERIFICATION_REPORT.md).

## Experiments actually executed

| Component | Executed scope |
|---|---|
| Clean BEC | 720 trials, two constructions, four sizes, three matrices per family/size, three erasure probabilities, ten observations per matrix/condition |
| Visible corruption | 480 trials on the declared subset of matrices, two erasure probabilities and two flip probabilities |
| Independent checker scaling | 90 trials on 15 other regular matrices, five sizes through n=4096, six observations per matrix |
| Repeated timing | One warmup and three randomized repetitions per ordinary operation; one validation call and five repetitions per scaling operation |
| Memory | Separate incremental Python-tracked allocations, excluding preexisting inputs; not RSS |
| Reproduction | All 39 matrices, 1,200 clean/corruption outcomes and 90 scaling traces regenerated; tables, uncertainty summaries and figures rebuilt from retained raw CSVs |
| Notebook and tests | All five code cells executed; final full suite **29 passed** |

The data give **720/720** valid clean completions, **562/720** exact recoveries and **546/720** unique completions; 174 systems were nonunique. Of 480 corruption trials, 251 realized a visible flip: **151** were incompatible and **100** remained compatible. All generated success/failure certificates passed their respective checks.

At n=4096, separate mean checker times were approximately **4.546 ms sparse replay**, **2.966 ms direct checking** and **49.574 ms dense replay**. Direct verification also used less incremental tracked memory. The fitted sparse exponent was **1.046**, direct **1.006**, dense **1.583**; intervals and finite-size qualifications are reported. These measurements support no universal speedup, asymptotic inference or universal corruption detection.

The internal checker fraction at epsilon 0.40 was a mean per-trial **0.522**, while the mean per-trial checker/decode ratio was **1.232**. The ratios of pooled mean times were instead **0.462** and **0.859**. Definitions, stage accounting and the wrapper's returned-word comparison are explicit. The eight-row epsilon table uses only epsilon 0.40 and delta zero. Timing observations remain the original executed values; analysis failures were repaired without dropping or recollecting measurements.

See [EXPERIMENT_REPORT.md](audit/EXPERIMENT_REPORT.md), [Reviewer C](audit/REVIEW_C_EXPERIMENTS.md), and `publication_outputs/manifest.json` for protocol, source provenance, raw hashes and exact reproduction commands.

## Novelty and scientific limits

The defensible contribution is the explicit delayed-propagation invariant, exact trace/log correspondence, scoped formalization and critical checker-cost case study. Classical hybrid decoding, stopping sets, finite-field alternatives, certifying algorithms and formal error-correcting-code libraries are prior work. Recent 2026 quantum-coding preprints also preclude treating “Lean plus coding certificates” as a novelty claim by itself.

The differentiated SELL zones are convenient, not necessary for these operational rules. No new expressiveness separation, focusing theorem or SELLF adequacy is claimed. The literature review verifies 16 cited sources and compares their guarantees; it cannot prove priority by absence of an identical search result. The author must assess whether this case-specific contribution is sufficiently substantial for LMCS, or whether a broader generalization/application or a differently positioned venue is warranted. This is a scientific decision, not a defect hidden behind passing tests.

Python and the experimental harness are independently tested implementations, not extracted verified code. The trusted matrix/observation may differ from the physical communication instance; certificates do not authenticate them. A valid trace attests to permissible steps, not a producer's historical internal actions. Three matrices per condition give limited ensemble evidence, and all measurements concern the recorded constructions, finite sizes and host.

## Publication actions still outside this task

- **Author review of the scientific contribution and final text.** The simulated reviews identify no known blocking error within the scoped claims; they are not external peer review or an acceptance guarantee.
- **Public artifact preparation if submission is pursued.** The origin was private at audit time. A durable archive/DOI and suitable release/license choices have not been authorized or created. Local reproducibility is not public availability.
- **Actual submission prerequisites.** The official [LMCS author guidance](https://lmcs.episciences.org/page/authors-information) requires prior CoRR/arXiv posting with TeX sources and cs.LO before journal submission; [style guidance](https://lmcs.episciences.org/page/authors-latex-style) encourages durable artifact references. The checked [policies](https://lmcs.episciences.org/page/policies) require original work and appropriate disclosure of any prior conference version. No assertion about the author's unpublished submission history is made. These are recorded prerequisites, not actions taken here.

## Build, visual verification and preservation

Native **Tectonic 0.17.0** compiled the final source with the current unmodified LMCS class, alphaurl bibliography and 16 verified references. The final LaTeX log has no undefined citations/references, font warnings or overfull/underfull boxes. The 23-page PDF was rendered and visually inspected throughout; final source/output hashes bind it to the supplied inputs. A narrowly documented first-page header workaround preserves the text-block geometry; it does not alter the class file or replace the default font. See [PDF_VERIFICATION.md](audit/PDF_VERIFICATION.md).

All original tracked artifacts remain in `originals/baseline-6bb47d9.tar.gz`; all 13 original output files remain byte-identical. Commits separate initial audit, mathematical repair, Lean repair, experiments, and final article/review integration. [FINAL_REVIEW.md](audit/FINAL_REVIEW.md) records independent objections and their dispositions. [CHANGELOG_PUBLICATION.md](CHANGELOG_PUBLICATION.md) describes the substantive changes. Reproduction instructions are in [README.md](README.md).
