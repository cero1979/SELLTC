# Mechanization scope cross-check (not an independent semantics review)

Date: 2026-09-23. This document is a cross-domain check of `paper/mechanization.tex` against the corrected Lean declarations. Its author also wrote `paper/semantics.tex`, so it must **not** be counted as an independent Reviewer A evaluation of that semantics section. The coordinator will obtain a fresh independent logic review. No Lean source was edited by this reviewer.

## Statement-level assessment

The corrected adequacy is substantive and does not silently replace the requested property by existence of an arbitrary or empty trace.

- `PeelingState.lean:10-34` stores only the partial assignment and derives syndrome, degree, and actual unknown-neighbor sets. `ValidStep` requires equality with the singleton `{stp.i}` and the true syndrome. Positive adjacency and unknown status are consequences, avoiding the original vacuous uniqueness predicate.
- `Rewriting.lean:12-30` stores canonical assignment, finite pending sets, and an ordered observer. `WFContext` requires every unknown edge to remain pending and every pending incidence to be a genuine edge. Pending known incidences are permitted.
- `pendingSyndrome` is derived from known neighbors outside the pending set. `SolveEnabled` requires a singleton pending set, unknown status, and this derived value. Together with WF this implies a genuine operational step (`solve_valid`). `propagate_syndrome`, `solve_selected_syndrome`, and `solve_other_syndrome` substantiate the correspondence with the stored-residual raw rules rather than merely assigning the intended meaning by name.
- `Adequacy.lean:10-25` indexes both one-event and multievent relations by explicit lists. `extractedTrace` returns the explicit data index; it does not eliminate endpoint-only reachability proofs into computational lists.
- `rewstar_sound` accepts any well-formed starting context and every rule interleaving. It does not require all propagation to finish before the next Solve.
- `rewstar_observation` states that the endpoint assignment is precisely the fold of the actual event trace and that its observer is exactly the previous observer appended with that same trace.
- `propagation_normalization` constructs an empty-observation derivation to the normalized encoding. `propagation_normal_form_unique` and `propagation_confluence` concern propagation-only derivations, which cannot contain a Solve event because Solve contributes a nonempty singleton list.
- `adequacy_one_step` and `adequacy_completeness` retain the log and end at `encodeLogged` of the actual updated/folded state. Completeness keeps the requested trace T exactly.
- `thm_adequacy_complete` is an equivalence for the same universally quantified T. Its reverse implication is not the original vacuous existence of some valid trace.

No mathematical weakening or unproved side condition was identified in those statements. The ordered observer contains more information than the raw endpoint log multiset, and the manuscript correctly says that its multiset image, rather than the list itself, corresponds to raw step atoms.

## Certificate and probability scope

`Checker.lean` defines finite typed replay and explicit residual/witness predicates. `replayFull_eq_some_iff` relates actual replay to both validity and the folded endpoint. `thm_sound_success` proves code membership and consistency of the returned word. `thm_sound_failure` uses trace-preservation of every compatible completion, which supplies the missing connection from the original input to the residual.

`lem_unsat_witness_complete` proves a real separating row vector by linear duality; it is not a new probability or algebra axiom. `residual_unsat_iff_witness` supplies general residual witness completeness. The named certificate-completeness lemmas `thm_complete_success` and `thm_complete_failure` currently construct **empty-trace** certificates. This is enough to establish global existence of an accepted certificate, but it is not by itself a mechanized statement that every prescribed valid partial trace admits the corresponding status certificate. The latter general statement is proved informally in `paper/core.tex`; the final status report must preserve this distinction unless the Lean statement is subsequently strengthened.

`becLikelihood` is genuinely real-valued, equals the closed-form BEC likelihood on compatible words, and is zero on incompatible words. `bec_completion_maximizes` compares it with every candidate for the closed interval 0 <= epsilon <= 1; `thm_ml` quantifies over all competing codewords and states the actual likelihood inequality. There is no vacuous `True` conclusion. The coordinate-product factorization and its interpretation as a channel model remain informal, as the manuscript explicitly discloses.

## Representation and implementation boundaries

The manuscript correctly separates the canonical Lean representation from arbitrary raw multisets. Token multiplicities, functional knowledge, and cached residual coherence are enforced by representation. A proof about this canonical state is not a proof that an arbitrary duplicate-containing multiset is well formed, and it does not verify Python's cached arrays. The raw-token representation argument and operational label-erasure theorem remain informal mathematical results.

The typed success witness is a total function on all variable indices; the Python format serializes only residual coordinates. The finite-index Lean inputs also presuppose successful parsing and conversion. Any executable adapter and differential tests must be reported separately. Neither these tests nor the typed mathematical checker establishes a compiler/runtime refinement theorem for the Python implementation.

The Lean normalization proof descends on total pending incidences for Propagate and proves propagation confluence/unique normal form. The full raw rewriting termination bound, including Solve events, is proved in the manuscript but is not expressed as a separate global termination theorem in the inspected Lean source. No claim of full rewriting confluence is present or justified.

## Verification status and required final addendum

This is a statement/source scope check, not a replacement for the Lean agent's compilation and transitive-axiom audit. A source scan of the inspected core modules found no `sorry`, `admit`, project `axiom`, or `unsafe` declaration. Absence from source text alone does not establish the dependencies of compiled theorems; the separate verification report must contain fresh build and `#print axioms` evidence.

At review time the executable JSON adapter and differential-run audit were still being finalized. Consequently the sentence in the mechanization section describing finite Lean/Python comparisons is contingent on the subsequent successful run and recorded outcomes. The final review must add the executable build, the precise corpus size and comparison result, and any adapter limitations; this document does not certify an unexecuted comparison.

No statement-level blocker was found in the corrected canonical adequacy or soundness declarations. The fresh independent logic reviewer must still inspect the manuscript proofs, and the final artifact review must confirm the completed build, axioms, adapter and differential evidence before treating the mechanization section as finalized.

## Coordinator's completion addendum

The contingent checks above subsequently completed: the clean root-package build passed, all 51 named results were audited for transitive axioms, and the interpreted executable matched Python on all 575 cases (369 accepts, 206 rejects), including returned success words. Native executable loading remains a documented macOS limitation. The fresh independent [Reviewer A report](REVIEW_A_LOGIC.md) is complete and closes the statement-scope/provenance objections. See [FINAL_REVIEW.md](FINAL_REVIEW.md) and [LEAN_VERIFICATION_REPORT.md](LEAN_VERIFICATION_REPORT.md) for the final evidence; the preceding paragraphs preserve the earlier cross-check's actual scope.
