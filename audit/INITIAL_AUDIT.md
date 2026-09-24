# Initial publication audit

Date: 2026-09-20. Audited revision: `6bb47d9781d813dff526e043c9d0ad35d37ed0a4` (local checkout and authenticated GitHub `main` agree). Working branch: `codex/publication-audit`. All findings concern the preserved baseline, not a later repair. This report and its three specialist reports are the initial-audit gate required before reconstruction.

## Verdict

**The baseline is not ready for submission.** Its Lean exact-endpoint adequacy theorem is false, its context invariant does not support its preservation claims, its Lean project fails a clean build and contains admissions and a vacuous ML claim, and its Python checker accepts an output outside the declared binary domain. Experimental summaries disagree with their captions and do not support empirical linear scaling. These are scientific correctness issues, not only presentation defects.

No original results were deleted. `originals/baseline-6bb47d9.tar.gz` contains every tracked original artifact; the original output directory is retained unchanged. See [source provenance](SOURCE_PROVENANCE.md), [complete tracked inventory](evidence/baseline-inventory.txt), and [Git history](evidence/git-history.txt).

## Complete mathematical-result inventory and correspondence

| Baseline result | Statement assessment | Lean correspondence | Python correspondence / evidence |
|---|---|---|---|
| Stopping-set theorem, `thm:stopping` | Valid for maximal peeling with nonempty residual; distinguish contradiction from stall | No dedicated stopping-set theorem | `peeling_decode`; unknown-neighbor degrees |
| State-meaning lemma, `lem:state-meaning` | Correct induction for operational atomic updates | `initState_syndrome_inv`, `applyStep_syndrome_inv`, `syndrome_invariant`; source proof repair needed | `initialize_state`, `apply_peeling_step`, replay |
| Residual equivalence, `lem:residual-equivalence` | Correct for assignments extending K; does not alone connect all y-compatible words to K | No complete standalone bridge | `residual_system_from_state` |
| Success soundness, `thm:sound` | Mathematical argument correct with valid replay; implementation domain unchecked | `thm_sound_success` missing replay invariant; no passing build | `check_success_certificate` accepts nonbinary rho |
| Separator soundness, `lem:unsat-witness-sound` | Correct elementary finite-field identity | `lem_unsat_witness_sound`; compilation not established in baseline | `check_failure_certificate` |
| Separator completeness, `lem:unsat-witness-complete` | Correct finite-dimensional duality; classical result | Explicit admission | `gf2_solve`, exhaustive small-system probes |
| Row-reduction extraction, `prop:witness-extraction` | Correct; applies to zero rows and empty-column systems | Not mechanized | Row-operation witness matrix in `gf2_solve` |
| Failure soundness, `thm:unsat-certificate-sound` | Needs explicit forced-assignment preservation lemma to close y-to-K implication | `thm_sound_failure` admitted | Failure replay plus separator checking |
| BEC ML, `thm:ml` | Correct for interior epsilon as argued; endpoint statement needs clarification | Axiom and theorem conclude `True`, not ML | No probability model; compatible completion only |
| Checker complexity, `prop:checker-linear` | Sparse upper bound repairable to O(E+n+m); claimed universal optimality unjustified | Not mechanized | Baseline dense O(mn) initialization/final checking |
| Certificate size, `rem:cert-size` | Needs separate log m and log n and failure m bits | Not mechanized | Trace triples and residual/witness arrays |
| Propagate WF, `lem:propagate-wf` | False for baseline membership-only WF; invalid extracted-state interpretation | `propagate_wf` cannot prove stated type | Operational Python eagerly updates all neighbors, so different intermediate state model |
| Solve WF, `lem:solve-wf` | False for duplicate unknown/rem tokens and insufficient asynchronous invariant | `solve_wf` cannot prove stated type | Same distinction |
| Two-direction adequacy, `thm:adequacy-complete` | Exact canonical endpoint false; both directions need delayed-propagation semantics and trace labels | `adequacy_one_step`, `adequacy_completeness`, `adequacy_soundness` admitted; extractedTrace ill-typed; combined converse vacuous | Replay accepts an ordered operational trace, not a proof term |

Definitions audited include H, received word, K/U/s/d, operational initialization/update, ValidStep/ValidTrace, residual matrix and RHS, certificate formats, atoms/zones, Context, encodeState, propagate/solve, WFContext, RewStep/RewStar and extractedTrace. The full logical report gives minimal counterexamples and replacement invariants.

## Severity register

**Blocking**

- B1: exact encoded adequacy target loses an immutable step atom; H=[1], y=[erasure] is a counterexample.
- B2: duplicate tokens satisfy the existing WF predicate and violate both preservation claims; asynchronous residual metadata has a different meaning than operational metadata.
- B3: initial Lean build fails in lakefile; five admissions, artificial True axiom, invalid Prop-to-Type trace extraction, unfinished proof bodies and false completion claims.
- B4: Python accepts `rho=[2,2]` for H=[[1,1]], y=[-1,-1], yielding a nonbinary output; malformed inputs may raise exceptions.
- B5: published epsilon=.40 table actually pools seven epsilons; checker-scaling caption conflicts with measured slopes around 1.8.

**Major**

- M1: two persistent SELL labels are convenient, not proved essential; no SELLF adequacy is established.
- M2: dense implementation and claimed sparse complexity differ; time denominators and lower-bound claims are unjustified.
- M3: no direct-check comparator, mismatched GE pivot strategies, only six independent matrices, colliding random streams, and no proper malformed-certificate campaign.
- M4: all-zero transmission obscures ambiguity; 526/4200 clean records have nonunique completions. Corrupted-compatible cases are absent from original random robustness data.
- M5: original PEG-style builder is not the stated farthest-frontier PEG construction.
- M6: toolchain/lockfile absence, incompatible host executables, inaccurate README file lists, stale default notebook behavior and nonreproducible LaTeX exporter.
- M7: novelty is not established by combining known algorithms and certification; formal ECC and certifying-computation precedents must be treated accurately.
- M8: origin is private, so public artifact availability cannot yet be asserted.

**Editorial**

- E1: excessive abstract, repeated inventories and defensive commentary, speculative line counts for missing proofs.
- E2: manual bibliography and old LMCS class; current author instructions checked, see editorial report.

## Evidence and specialist reports

- [Logic and mathematical audit](LOGIC_INITIAL.md): all theorem dependencies, exact counterexamples, asynchronous semantics, SELL role.
- [Lean audit](LEAN_INITIAL.md): every module, direct/transitive admissions, invalid statements, toolchain evidence and clean-build failure.
- [Experimental audit](EXPERIMENT_INITIAL.md): source-line findings, recomputed statistics, 10,108 exhaustive solver probes, adversarial examples and campaign design.
- [Editorial/repository audit](EDITORIAL_INITIAL.md): other supplied manuscript, PDF inspection, documentation and current LMCS instructions.

The notebook embeds the deleted Python module with `%%writefile`; it can recreate it. The missing tracked module is a documentation/entry-point defect, not proof that notebook regeneration is impossible. Original numerical summary CSVs match their actual aggregators; no fabrication of raw data was established.

## Repair order and exit criteria

1. Replace false logical statements openly, strengthen delayed-propagation invariants, retain both soundness for arbitrary reachable interleavings and completeness modulo normalization and logs.
2. Repair and pin Lean; prove substantive claims where feasible, audit axioms, and separate mathematical proofs from uncompleted mechanization. No admission or artificial axiom may support a claimed verified result.
3. Validate certificate domains, implement sparse checking and an independent direct checker, establish regression/exhaustive tests and a documented new campaign before execution. Preserve old raw data.
4. Rebuild manuscript from corrected proofs and actually generated results, with checked literature and appropriately limited novelty.
5. Independently review logic, coding theory and reproducibility; repair verified objections; compile and visually inspect the final PDF; write an honest readiness report and organized local commits. No push, PR, public release or submission.

A repair is not completed merely by changing a label to “proved,” compiling through admitted theorems, hiding a negative result, or renaming a toy theorem as the intended result. Any remaining obstacle must be explicit in the final readiness report.
