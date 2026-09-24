# Exact trace adequacy revision report

Date: 24 September 2026. Starting commit: `d277e952e256cabbac39c08af8a66f4b5f85a612`. Branch: `codex/publication-audit`.

## A. Executive summary

The revised paper centers on **Theorem 6.10: exact trace adequacy under delayed propagation**. Its soundness direction covers every asynchronous interleaving, including endpoints with pending known incidences; its completeness direction realizes each prescribed valid operational trace at its exact logged normal form. Residual algebra provides a compatible-completion or infeasibility certificate around this trace semantics.

The classical decoder, existing proofs, Lean development and recorded experiments are preserved. A new abstract proposition makes the proof architecture reusable by stating the additional local lifting and canonical-endpoint assumptions required for completeness. SELL provides the resource vocabulary; Proposition 6.12 positively identifies the differentiated persistent labels as operationally inessential here.

The full supplied specification, pre-edit inventory and hashes, plan, independent reviews and fresh verification records accompany this revision under `audit/revision-2026-09-24/` and `docs/superpowers/plans/2026-09-24-exact-trace-revision.md`.

## B. Section-by-section changes

| Part | Revision |
|---|---|
| Title | Centers exact trace adequacy, delayed propagation and residual certificates. |
| Abstract | Orders the problem, asynchronous difficulty, invariant, exact trace theorem, algebraic certificates and verification evidence; closes with label erasure. |
| Introduction | Distinguishes algorithm, certificate contract, asynchronous semantics and logical presentation. Previews `Q_j`, `D_j`, `p_j` and both delayed-residual equations; gives four contributions and identifies Theorem 6.10 explicitly. |
| Sections 2--4 | Existing mathematical statements and complete proofs retained. |
| Section 5 | Explains next to Proposition 5.1 that replay certifies a local operational explanation without strengthening the final-word predicate. |
| Section 6 | Adds a fully proved, named abstract principle and LDPC instantiation; explains the four ingredients before Theorem 6.10 and interprets its two directions after the proof. Reframes label erasure as an informative representation result. |
| Section 7 | Makes the raw-context/event-history, canonical Lean and Python boundaries explicit in a compact table. |
| Sections 8--9 | Preserve all empirical artifacts and values. Clarify what the whole-implementation comparison measures and the additional trace evidence obtained at measurable cost. |
| Related work | Acknowledges the closer prior BEC formalization of Affeldt et al. and gives a positive, cited-literature-relative contribution statement without priority language. |
| Conclusion | Starts with delayed propagation, normalization and exact trace adequacy; then certificates, mechanization, SELL's role and the retained limitations. |

### Title evaluation

The previous title accurately described the artifact but gave the SELL-style presentation more prominence than the principal theorem. Three alternatives were evaluated:

1. **Exact Trace Adequacy for LDPC Peeling: Delayed Propagation and Residual Certificates** (selected).
2. Asynchronous Trace Certification for Hybrid LDPC Decoding.
3. Delayed Propagation in Certified LDPC Decoding: An Operational Adequacy Theorem.

The selected title names the proved correspondence and both layers it connects, while keeping the classical algorithm identifiable. It is preferable to a SELL subtitle because Proposition 6.12 establishes that the differentiated labels are unnecessary for these rules. Author, affiliation and ORCID are unchanged.

## C. Mathematical changes

No original theorem, operational rule, certificate predicate or complete proof has been weakened. The change is a rigorous factorization of the adequacy argument plus explanatory prose. Definitions 6.1--6.2, Lemmas 6.4--6.7, Proposition 6.8, Theorem 6.10 and Propositions 6.11--6.12 retain their numbering.

The dependency audit distinguishes presentation order from logical dependence. Lemma 2.2 gives the residual bijection (Lemma 3.1), which supports success soundness and, with the finite-field alternative, failure soundness and certificate existence. The finite-execution adequacy theorem uses initialization, local invariant preservation/simulation, normalized enablement and propagation normalization; global termination is not a missing premise of that finite theorem. Proposition 6.8 additionally supports the maximal-execution discussion. Proposition 6.12 is an independent rule-by-rule representation correspondence, with invariant preservation needed for closure of the ordinary rewriting image; it is not derived from the stopping-set result.

The audit retains the exact multiset multiplicities and `N(j) ∩ U ⊆ Q_j ⊆ N(j)`. Propagation removes one delayed known incidence and stutters under projection. Solve requires an unknown singleton pending incidence at its forcing row, so it is a genuine degree-one step even when other rows lag. Propagation commutes and normalizes; competing Solve choices on inconsistent inputs are not claimed confluent. Empty unknown sets still require checking all residual equations.

## D. New abstract result

A named, unnumbered **Proposition (abstract adequacy principle)** precedes Theorem 6.10. It states invariant preservation, silent preservation of projection/log, event simulation, terminating canonical silent normalization and normalized local event lifting. It uses a multiset log observer and the separate ordered event sequence of an execution. Completeness quantifies over a specified operational path, so it does not assume event determinism in an arbitrary instance.

The proof gives both inductions in full. Forward simulation and unique silent normal forms alone cannot imply completeness: an operational system can have an event for which the concrete system has no transition. The new proposition therefore explicitly requires lifting and canonical normal-form alignment. This repairs the proposed abstract schema, not a defect in the pre-existing LDPC theorem, whose constructive completeness proof already supplies lifting.

The proposition organizes standard simulation reasoning; no general priority or new rewriting-theory claim is made. It is not newly mechanized. See [ABSTRACT_ADEQUACY_NOTE.md](ABSTRACT_ADEQUACY_NOTE.md) for hypotheses, proof dependencies and the LDPC instance.

## E. How Theorem 6.10 became central

The title, abstract, first introduction paragraph, contribution list, Section 6 opening, related-work synthesis and conclusion all identify exact trace adequacy as the paper's center. The theorem is explicitly marked as the principal theorem. Its original statement and full LDPC proof remain available rather than being replaced by an appeal to the abstraction.

The preceding paragraph collects initialization, silent stuttering, Solve simulation and terminating/confluent propagation normalization. The following interpretation distinguishes soundness for arbitrary interleavings from realization of each prescribed trace, explains the exact log and delayed endpoint, and retains empty/partial traces without maximality.

## F. How Proposition 6.12 was reframed

The full proposition and proof are retained. The result identifies a presentation choice that can be removed without changing the specified event-labelled behavior. Static reusable facts and learned reusable values have distinct intended roles, but their predicate symbols recover the partition after merging zones. Ordinary consume-and-recreate rewriting has the same sequential event behavior on the images of admissible contexts. The domain restrictions are retained; no correspondence on arbitrary malformed raw multisets is asserted.

## G. Revised role of SELL

SELL exposes reusable information versus consumable pending/residual resources. The invariant and local resource updates support certification. The two persistent labels organize access but add no operational expressive power to these two rules. No logical completeness, focused proof-search correspondence, SELLF adequacy or full-calculus equivalence is claimed.

## H. Direct checking versus replay

Both successful checking paths establish `Hx = 0` and visible-coordinate agreement. Replay additionally validates every declared assignment against the preceding degree-one operational state. It certifies a local explanation, not producer provenance or a stronger final-word predicate.

The same sparse asymptotic upper bound is retained. The data still show direct checking faster and using less additional tracked memory. The comparison concerns complete implementations, including their different state/representation work; it is not a controlled measurement of only the incremental cost of one validation instruction. Failure witnesses remain a separate infeasibility guarantee, which a direct word check does not supply.

## I. Formalization boundary

Raw multisets carry unordered log atoms. A chronological Lean observer therefore corresponds to a raw admissible context **together with an execution history**, not uniquely to the raw endpoint alone. The new scope table labels manuscript proofs, canonical mechanization, finite empirical cross-checks and unproved implementation/runtime connections separately.

The generic proposition, raw representation correspondence, label erasure, global termination including Solve, all-prescribed-trace certificate completeness, stopping/nullity and complexity statements remain manuscript results. Lean still proves canonical exact trace adequacy for each prescribed trace, certificate soundness, residual separator existence and named empty-trace checker completeness. No Python refinement, parser/serialization, compiler/runtime or timing verification has been added or implied. The previously recorded 575 differential comparisons remain historical test evidence and are not described as a newly rerun campaign.

## J. Bibliography

All 16 references are retained, with one metadata correction: Girard (1987) now uses journal pages 1--101 as explicitly recorded by the [publisher](https://www.sciencedirect.com/science/article/pii/0304397587900454) and its Crossref deposit. The author archive lists 1--102 for a restored version; that discrepancy is documented in the focused bibliography review rather than silently equating restored PDF length with journal pagination. The other 15 entries are unchanged. No reference was invented or added for the abstraction. The existing primary-source audit and the new focused review support their uses. The Affeldt--Garrigue--Saikawa comparison now acknowledges BEC sum-product termination and approximation invariants in addition to formal coding theory and extraction. The 2026 quantum-code preprints retain their distinct distance/optimality targets and preprint status. The positive gap statement is explicitly relative to cited developments, not an exhaustive novelty or priority certification.

## K. Build and verification

Fresh checks all completed successfully. Exact commands and environment corrections are recorded in [VERIFICATION_COMMANDS.md](audit/revision-2026-09-24/VERIFICATION_COMMANDS.md).

| Check | Result and evidence |
|---|---|
| Native Tectonic full build | Exit 0; **27 pages**, 18 rendered abstract lines; no undefined references/citations, duplicate labels, overfull/underfull boxes or LaTeX warnings in the final log. `manuscript-build.txt`, `pdf-info.txt`. |
| Reference/statement integrity | 52 unique labels, 63 reference uses, all 16 cited bibliography keys resolved; Theorem 6.10 and Proposition 6.12 numbering retained. All **18 original labelled lemma/proposition/theorem statement-and-proof blocks** are byte-identical. `integrity-checks.json`, `original-proof-preservation.json`. |
| Clean Lean verification | `./verify.sh --clean`, exit 0; all six modules/root rebuilt; checker entry point elaborated; all **51** audited declarations use only ordinary foundational axioms. `lean-verification.txt`. |
| Lean statement audit | `lake env lean StatementAudit.lean`, exit 0. `lean-statements.txt`. |
| Python regression suite | **29 passed**, exit 0. `python-verification.txt`. |
| Non-timing reproduction | **39 matrices, 1,200 clean/corruption outcomes and 90 scaling inputs/traces** matched; the only output-write statement was suppressed in memory. No new measurements or analysis artifacts were saved. `python-verification.txt`. |
| Preservation | **105 protected files** match the pre-edit SHA-256 snapshot, including all experiment artifacts, Lean sources/configuration, Python code/tests/notebook, requirements, class and baseline archive. The single bibliography metadata correction is intentional and outside this protected set. `integrity-checks.json`. |
| Mathematical review | Independent review found no blocker in the new proposition, complete proof, local lifting, multiset logs, nondeterministic paths or LDPC instance. `INDEPENDENT_ADEQUACY_REVIEW.md`. |
| PDF visual review | All 27 pages rendered and inspected; final changed pages rechecked after layout adjustment. Theorem 6.10 begins page 15 with its complete statement and proof. Figures and table data are unchanged and readable. `PDF_VERIFICATION.md`, contact sheets and page hashes. |

No proof source, experimental observation, timing, seed, generated figure or generated table was changed. The current source/output binding is `audit/revision-2026-09-24/final-artifact-hashes.json`; prior hash manifests retain their historical meaning.

## L. Unresolved issues and publication scope

The existing scientific and trust limitations remain. The abstract principle is not a new generic Lean library or evidence of a verified second application outside LDPC. Python is independent code, and the documented native Lean executable loading limitation on the audit host remains; interpreter execution and kernel compilation are separate matters. Finite tests and three matrices per condition do not prove universal implementation correctness or performance.

Journal novelty/fit, author approval, public archival release and submission remain outside this update. The user authorized committing and pushing this revision to the existing remote branch; no merge to `main`, new PR, release or submission is implied. Previous 23 September reports and hash snapshots remain historical evidence for commit `d277e95`; this revision supplies its own source/output binding.
