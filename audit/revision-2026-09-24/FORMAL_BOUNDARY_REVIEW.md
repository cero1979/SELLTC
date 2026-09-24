# Formal boundary review — 24 September 2026

This review inspected all six `lean4/SELLCert/*.lean` modules, the library and audit entry points, `lean4/Main.lean`, both READMEs, `paper/mechanization.tex`, the raw semantics, and the Python state/replay/certificate implementations. No Lean or Python source was modified and no experimental data was regenerated.

## Representation map

| Correspondence | Exact scope and evidence |
| --- | --- |
| Admissible raw multiset **together with a declared history** `(M,T)` → canonical `(K,Q,T)` | The exact-multiplicity invariant determines `K`, each pending set, and each derived residual field. It requires the raw log to equal the multiset image `Log(T)`. This correspondence is a manuscript proof, not a Lean refinement. The raw multiset alone does not determine chronological order. |
| Canonical asynchronous Lean → canonical operational Lean | `Context` stores `K`, finite pending sets and an ordered observer; `WFContext` imposes unknown neighbors ⊆ pending neighbors ⊆ graph neighbors. `rewstar_sound`, `rewstar_wf` and `rewstar_observation` prove valid actual event traces, invariant preservation, replayed endpoint state and concatenated observer. |
| Operational trace → asynchronous canonical execution | `adequacy_one_step` lifts a permitted operational event from its normalized encoding. `adequacy_completeness` realizes every prescribed valid trace, with its exact event list and logged normalized endpoint. `thm_adequacy_complete` gives the same-trace existence equivalence. These are concrete LDPC declarations, not instances of a generic Lean transition-system theorem. |
| Canonical Lean checker ↔ Python cached checker and JSON adapter | Lean derives syndromes and degrees from `K`; Python `initialize_state` and `_apply` maintain cached syndrome, degree and unknown-index XOR arrays. The mathematical update equations are proved in Lean, but Python cache refinement, parsing and serialization are not. The historical 575-case corpus gives finite differential evidence, not universal program equivalence. It was not rerun or regenerated in this review. |

The new table in `paper/mechanization.tex` records these boundaries. The ordered observer is an external account of the declared execution; neither it nor a replayed certificate attests to a producer's historical execution.

## Exact declaration support

| Claim | Declaration and source |
| --- | --- |
| A permitted assignment agrees with every compatible codeword; replay preserves all compatible completions | `forced_value`, `trace_extends`, `PeelingState.lean:73,104` |
| Executable typed replay exactly matches valid traces and their fold | `replayFull_eq_some_iff`, `Checker.lean:25` |
| Arbitrary delayed propagation and Solve interleavings have valid actual traces | `rewstar_sound`, `Adequacy.lean:35`; initial-state specialization `adequacy_soundness:139` |
| Endpoint assignment and chronological observer match the actual indexed trace | `rewstar_observation`, `Adequacy.lean:61` |
| Pure propagation reaches a unique canonical normal form and its forks join | `propagation_normalization:85`, `propagation_normal_form_unique:160`, `propagation_confluence:173`, `Adequacy.lean` |
| Every prescribed valid operational trace has an exact logged normalized realization | `adequacy_completeness:130`, `thm_adequacy_complete:146`, `Adequacy.lean` |
| Accepted success and failure certificates are sound, including arbitrary valid partial traces | `thm_sound_success:62`, `thm_sound_failure:103`, `Soundness.lean` |
| Left-kernel separators exist exactly when the residual system is insoluble | `lem_unsat_witness_complete:25`, `residual_unsat_iff_witness:129`, `Soundness.lean` |
| A compatible word or initial inconsistency has an accepted certificate using the empty trace | `thm_complete_success:162`, `thm_complete_failure:150`, `Soundness.lean`; these named checker completeness theorems do not quantify over every prescribed partial trace. |
| Accepted words maximize a real closed-form BEC likelihood for `0 ≤ ε ≤ 1` | `bec_completion_maximizes:185`, `thm_ml:193`, `Soundness.lean`; product factorization and a probability-space construction are not mechanized. |

The raw token correspondence, label-erasure proposition, new abstract principle, global rewrite termination including Solve, stopping/nullity results, elimination implementation, sparse complexity and empirical claims remain outside the Lean proof scope. Propagation-only confluence must not be described as confluence of executions containing arbitrary Solve choices.

## Abstract-principle review

Forward simulation, an invariant, silent termination and uniqueness of silent normal forms do not alone imply completeness. For example, take one admissible raw state with no rewrite steps and one operational state with an observable self-loop labelled `a`. Silent normalization and uniqueness hold, and forward simulation is vacuous, but the operational trace `[a]` has no rewriting realization.

A valid abstraction must additionally assume local lifting of every allowed operational event from the corresponding normalized encoding, compatibility of projection/encoding/normalization, and preservation of the invariant used at successive steps. An exact history theorem also needs an explicit event observation with the stated concatenation law. In this concrete development the lifting premise is supplied by `adequacy_one_step`, rather than by forward simulation. The new abstract proposition and its instantiation argument are manuscript proofs; no generic abstraction claim may be attributed to the current Lean library.

## Fresh verification

From `lean4/`, the following command was run with the cached pinned native toolchain:

```sh
export PATH='/Users/cero/Downloads/Articulos/SELLTeoCod/SELLTCFULL_bundle/audit/toolchains/lean-4.14.0-darwin_aarch64/bin:/usr/bin:/bin:/usr/sbin:/sbin'
./verify.sh --clean > /tmp/selltc-revision-lean.log 2>&1
```

**Exit status: 0.** The script ran `lake clean selltc`, `lake build`, `lake env lean AxiomAudit.lean`, and `lake env lean Main.lean`. All six modules and the library root rebuilt successfully; the typed JSON entry point elaborated successfully. All **51** declarations printed by the axiom audit depend only on subsets of `propext`, `Classical.choice`, and `Quot.sound`. A source scan found no `sorry`, `admit`, `sorryAx`, project `axiom`, `native_decide`, `unsafe`, or `True` in the library and checker entry point.

The complete fresh build/axiom output was copied unchanged to [lean-verification.txt](lean-verification.txt). This verifies elaboration and axiom dependencies; it is not a fresh differential execution, performance run, or formal parser/Python refinement proof.
