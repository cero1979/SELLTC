# Reviewer A: independent logic and formal-methods review

Review date: 2026-09-23. This reviewer did not author the repaired mathematical sections or Lean sources. The review read the final working-tree versions of `paper/core.tex`, `paper/semantics.tex`, `paper/mechanization.tex`, all six `lean4/SELLCert/*.lean` modules, the article's abstract/introduction/limitations, `lean4/README.md`, and `audit/LEAN_VERIFICATION_REPORT.md`. No mathematical or Lean source was edited by this reviewer.

## Assessment

No known blocking mathematical error remains in the inspected theorem statements and proofs under their now-explicit scope. The asynchronous adequacy theorem is substantive: it covers arbitrary interleavings, retains the specified chronological trace, and reaches the exact logged normalized endpoint. Its soundness direction is not an existence claim about an unrelated empty trace.

This finding does not establish novelty, journal suitability, universal Python correctness, or adequacy for a SELL deductive calculus. The positive assessment is of the particular operational specification, algebraic certificate contract, and stated Lean formalization. The remaining boundaries below are material to any submission or artifact description.

## Objections and disposition

| ID | Objection and concrete location | Status after review |
|---|---|---|
| A1 | `paper/mechanization.tex` originally called the group containing `thm_complete_success` and `thm_complete_failure` simply “Completeness of certificate formats.” In `lean4/SELLCert/Soundness.lean:150–175`, both checker-level statements explicitly use `T = []`. They do not individually prove existence after every prescribed valid partial trace, as `paper/core.tex:190–207` does informally. | **Corrected and rechecked.** The table now says “Residual and empty-trace certificate completeness” (`paper/mechanization.tex:59`), and lines 82–87 explicitly distinguish the general residual equivalence, empty-trace checker theorems, and stronger informal result. `LEAN_VERIFICATION_REPORT.md:133–138` and `lean4/README.md:35–39` now retain that distinction. This is a scope limitation, not a false empty-trace theorem. |
| A2 | The informal global termination proposition includes Solve events (`paper/semantics.tex:253–264`), whereas the source provides `propagate_decreases` and propagation normalization (`lean4/SELLCert/Adequacy.lean:71–114`), without a separate theorem of termination or an event-count bound for the full Solve/Propagate relation. | **Corrected and rechecked.** `paper/mechanization.tex:127–132` lists global rewrite termination including Solve as unmechanized, as do `LEAN_VERIFICATION_REPORT.md:263–268` and `lean4/README.md:67–72`. The informal decreasing-pending-token proof is valid. |
| A3 | Current verification evidence could be confused with preserved baseline evidence: `audit/evidence/lean_source_inventory.json` contains the old arbitrary-state sources and old hashes; `lean_environment.json` records the initial missing toolchain. | **Corrected and rechecked.** `LEAN_VERIFICATION_REPORT.md:3–7` now explicitly identifies both files as historical baseline snapshots and points to the current `lean_verification_summary.json`. This reviewer independently matched all 13 current recorded hashes against the working tree. |
| A4 | Replacing arbitrary raw multisets by functional knowledge and finite pending sets would silently evade duplicate-token and malformed-state obligations if advertised as the same fully mechanized raw syntax. | **Resolved by an explicit boundary.** Exact raw multiplicities are specified and maintained informally in `paper/semantics.tex:66–98,159–213`. The canonical Lean representation is declared at `lean4/SELLCert/Rewriting.lean:12–30`; `paper/mechanization.tex:19–28` explicitly states that the raw-token correspondence is not mechanized. |
| A5 | Distinct persistent labels might be advertised as necessary, or operational adequacy might be advertised as SELL/SELLF derivability adequacy. Neither follows from these rules. | **Resolved by narrowing and proving the actual claim.** `paper/semantics.tex:362–439` gives an event-preserving operational erasure result and excludes full logical-calculus equivalence. The abstract, introduction, related work and limitations retain that restriction. |

No source repair was demanded merely to expand the formalization beyond the disclosed scope. A1–A3 are closed as documentation corrections after re-reading the final manuscript, report and Lean README. Future summaries must preserve those distinctions.

## Mathematical checks

### Operational state, certificates and algebra

The local validity condition requires the actual unknown-neighbor set to be exactly `{i}`; neither an isolated variable nor a fabricated cached degree satisfies it. State coherence is immediate in the canonical representation and follows inductively for the cached mathematical equations (`paper/core.tex:18–61`; `PeelingState.lean:19–47,113–127`).

The preservation-of-completions lemma supplies the necessary direction for failure soundness. Every codeword compatible with the original observation must agree with every forced assignment; without this fact, incompatibility with the final residual alone would not exclude an original completion. It is proved in `paper/core.tex:38–61` and formally by `forced_value`, `applyStep_extends`, and `trace_extends` (`PeelingState.lean:73–111`). `thm_sound_failure` actually uses that chain (`Soundness.lean:103–115`).

The residual bijection is valid for every valid partial trace, including the empty trace and inputs with no compatible word (`paper/core.tex:93–107`). Filling and restriction are inverse after the forced-assignment argument. The success/failure alternative therefore quantifies over suitable witnesses, not all alleged witnesses (`core.tex:190–207`). Soundness also checks zero-degree rows, so eliminating every erasure does not itself imply acceptance.

The finite-field separator proof uses a linear functional on the column span, not positive-definite real inner-product reasoning in characteristic two (`core.tex:147–167`; `Soundness.lean:25–48`). The formal residual matrix pads known columns with zero, which is equivalent to restricting to unknown columns for these equations. `residual_unsat_iff_witness` (`Soundness.lean:128–146`) is a genuine general residual theorem. Its use of classical choice is an ordinary disclosed foundation for existence, not a verified Gaussian-elimination algorithm.

Zero rows, zero columns, redundant rows and zero dimensions are permitted. The finite-field alternative's `m=0` case has a solution; the inconsistent branch cannot arise. The row-operation witness argument remains valid when a residual has zero columns. The stated stopping-set argument is structural and does not confuse successful peeling with codeword acceptance. The nullity proof gives the correct number of compatible completions, rather than guaranteeing recovery of a particular transmitted word (`core.tex:63–84,169–188,209–224`).

The BEC claim uses a real likelihood inequality and explicitly includes incompatible competitors. For interior erasure probability, compatible words are exactly the maximizers when any compatible word exists; at endpoints an impossible observation can give every candidate likelihood zero. Neither the mathematical nor formal result asserts posterior conditioning on such an event. The Lean closed-form function is substantive, although equivalence to a coordinate-product probability model remains an informal derivation (`core.tex:226–257`; `Soundness.lean:177–200`).

### Arbitrary asynchronous behavior and exact logs

The key invariant is `N(j) ∩ U ⊆ Q_j ⊆ N(j)`. The inclusion allows a known value to remain pending at another check, while ensuring every unknown incidence is still represented. The stored syndrome sums known values outside `Q_j`; it need not equal the fully updated operational syndrome while propagation is unfinished (`semantics.tex:66–125`; `Rewriting.lean:23–30`). This is the appropriate invariant for arbitrary interleavings.

Propagate removes a known pending incidence only, preserves the assignment, and changes the stored syndrome by its bit. Solve requires a singleton pending set and a genuinely unknown variable. These conditions imply one actual unknown neighbor and the correct operational syndrome at the forcing check. At another adjacent check, the newly known variable remains pending, so that check's stored syndrome is unchanged until propagation. The raw proof explains all cases, and the formal `solve_valid`, invariant lemmas, and syndrome-update lemmas cover the canonical version (`semantics.tex:159–213`; `Rewriting.lean:57–178`).

Propagation termination and the unique normal form follow from deleting exactly the delayed known incidences. Same-row propagations commute because distinct enabled incidences leave each other enabled and XOR commutes; different rows modify different residuals. The formal confluence theorem concerns propagation-only derivations from a well-formed context. It does not claim confluence of conflicting Solve choices on an inconsistent input (`semantics.tex:218–271`; `Adequacy.lean:83–114,156–182`).

`RewStar H C T D` is explicitly indexed by the event list. `extractedTrace` returns that already available index; it does not recover computational order by eliminating a proof-irrelevant reachability proof (`Adequacy.lean:10–25`). The chronology is execution data, whereas raw `step` atoms form an unordered multiset. The manuscript explicitly separates these concepts (`semantics.tex:45–61`).

`rewstar_sound` has a well-formed initial-context hypothesis but no normalization or immediate-propagation hypothesis (`Adequacy.lean:34–47`). Its induction covers any allowed interleaving. `rewstar_wf` and `rewstar_observation` establish the endpoint invariant, folded state and exact appended observer. `adequacy_completeness` reaches `encodeLogged H (foldTrace H σ T) (L ++ T)` with the same specified event index `T`; `thm_adequacy_complete` uses the same universally quantified `T` on both sides (`Adequacy.lean:49–69,118–154`). The accumulated log is not lost in the endpoint.

### SELL-label erasure

The operational erasure proposition is valid on its stated image of contexts. Predicate symbols recover the distinction between edge and value facts; no rule tests a zone label or subexponential preorder. Replacing a persistent read by consumption followed by immediate recreation has the same sequential transition effect, because the value token is unique on admissible contexts (`semantics.tex:384–427`). Structural weakening and contraction are explicitly not extra transitions. This argument says nothing about simultaneous resource concurrency, a SELL sequent calculus, proof search, or focused proof equivalence, none of which should be inferred from the word “bisimulation.”

## Independent verification performed

This reviewer independently ran, from `lean4/`:

```sh
../audit/toolchains/lean-4.14.0-darwin_aarch64/bin/lake env \
  ../audit/toolchains/lean-4.14.0-darwin_aarch64/bin/lean AxiomAudit.lean
```

The command exited 0. All 51 named lemmas/theorems reported only `propext`, `Classical.choice`, and `Quot.sound` in their transitive dependencies (one declaration needed only `propext`). An independent source/audit-name comparison found 51 named source lemmas/theorems and 51 matching audit entries, with no missing or extra entry. All 13 source/configuration SHA-256 values in `evidence/lean_verification_summary.json` matched the current files. A targeted source scan found no actual admission, project axiom or unsafe implementation escape in the inspected sources; the ordinary words “admitting” and “admitted” occurred only in explanatory comments.

The clean project-build record and formal engineer's report were inspected. This reviewer did not delete caches or independently rebuild Mathlib; the independent axiom command used the project outputs checked by the recorded clean build. The 575-case differential comparison was inspected as evidence, not rerun or treated as universal refinement. No source compilation result, finite test suite, or hash is a substitute for reading the theorem statements.

## Remaining limitations relevant to publication

The main claim is a case-specific operational simulation and certificate specification. Peeling, stopping sets, residual elimination, left-kernel witnesses, rank/nullity, the BEC likelihood observation, and the certifying-producer/checker division are classical ingredients. The distinct SELL zones add organization but no demonstrated necessity or expressiveness in this model. Whether the remaining delayed-propagation theorem and artifact constitute a sufficient advance for the target journal remains an editorial/research judgment; this review does not establish priority or an exhaustive literature exclusion.

The formalization proves the typed checker and canonical event system. It does not mechanically verify the raw-multiset representation correspondence, SELL-label erasure, global Solve-inclusive termination, the general checker-completeness statement for every prescribed valid trace, stopping-set/nullity results, sparse asymptotic bounds, Gaussian-elimination code, JSON parser/adapter, Python caches or program, or measured statistics. Some of those are proved correctly in the manuscript, others are supported by separate finite tests. They must retain those respective evidence labels.

Acceptance certifies the supplied matrix/observation and declared trace. It does not authenticate the instance, attest to the producer's actual internal history, ensure unique completion, or guarantee detection of every visible corruption. The manuscript makes these distinctions explicitly (`core.tex:292–313`; article limitations). Within these boundaries, no additional logical blocker was identified by this independent review.
