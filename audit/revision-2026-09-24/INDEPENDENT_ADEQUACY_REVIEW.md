# Independent adequacy review — 24 September 2026

**Finding: no mathematical or formal-scope blockers found.** The abstract proposition has sufficient explicit assumptions, its proof establishes both stated directions and exact endpoints, and its LDPC instantiation does not assume the theorem it is used to explain.

The reviewer did not author the generic proposition, its proof, the instantiation, or the main manuscript narrative. The reviewer previously audited the Lean library and contributed its representation-boundary table. This review is independent of the abstract theorem's authorship. It reads the current `paper/semantics.tex`, `SELLTCFULL.tex`, `REVISION_REPORT.md`, `CLAIM_AUDIT.md`, and `ABSTRACT_ADEQUACY_NOTE.md`, checking the certificate cross-reference against `paper/core.tex` and the previously inspected Lean declarations. No manuscript or code changes and no additional Lean run were performed for this review.

## Abstract statement and proof

The four assumptions in `paper/semantics.tex:309–337` are sufficient:

- The canonical map is total on the stated operational states and multiset logs, with the required projection, log and silent-normality properties.
- Every permitted concrete transition preserves admissibility, so soundness applies to arbitrary interleavings rather than only the special executions constructed for completeness.
- Silent steps preserve both observations. Termination gives a normal descendant; the canonical-normal-state condition identifies every such descendant by its projection and log. This proves the exact normal form and silent confluence without assuming confluence of observable steps.
- Local lifting specifies both the label and the projected successor. This is stronger than merely requiring an outgoing event with the same label, and is the necessary distinction when operational transitions are nondeterministic.

The soundness induction (`semantics.tex:382–393`) appends the actual nonsilent label and one log occurrence at each observable step. It neither chooses a new order for the trace nor infers the trace from the endpoint log.

The completeness induction (`semantics.tex:395–412`) is correctly generalized to arbitrary admissible starting contexts. Its empty case normalizes the starting context. Its nonempty case normalizes, lifts the specified first operational step, and applies induction to the remaining path from the actual lifted successor. Invariant preservation and the single-occurrence log update supply the induction premises. The final multiset calculation and execution concatenation respectively establish the exact endpoint log and the exact ordered event list.

The result requires neither deterministic operational transitions nor confluence of the full concrete relation. It concerns finite specified paths; global termination of observable activity is not silently used. Canonical normalization is stronger than merely requiring each state to have some unique normal form, and the statement explicitly includes that stronger condition.

## LDPC instantiation and main theorem

The raw normalized encoding at `semantics.tex:415–437` is well-defined for a multiset log: replacing a representing list by a permutation leaves every raw token and multiplicity unchanged. Every finite multiset has such a representing list. This construction does not recover or attach a chronological history to the raw endpoint.

The four assumptions are discharged by the preceding definitions and lemmas. The local lifting argument is substantive: from `N(j) ∩ U = {i}` and `s(j) = b`, the normalized encoding contains the exact residual, pending and unknown tokens for the requested Solve. The Solve preservation lemma identifies its operational successor. Prior log atoms do not participate in enabledness. This argument appears before the main theorem, preventing a circular reliance on adequacy.

The main theorem and retained direct proof (`semantics.tex:447–500`) correctly cover unfinished propagations in the soundness direction and construct a normalized endpoint for the same prescribed trace in the completeness direction. The chosen fully propagating completeness witness imposes no scheduling restriction on the arbitrary executions quantified over by soundness. Empty and partial traces are explicit. The preservation lemmas retain exact token multiplicities, and no assumption of global input consistency is inserted.

The propagation-only confluence restriction is consistent throughout. Inconsistent instances may admit conflicting Solve choices, and the manuscript does not equate their assignments or traces. The normalization observer is the current operational state and raw log; it does not merge distinct observable outcomes.

## Cross-claims and trust boundaries

- The abstract, introduction and conclusion identify Theorem 6.10's exact trace correspondence while describing the abstraction as sufficient proof architecture, without an unsupported priority or universal-applicability claim.
- The event list is chronological execution data. Raw `Log(T)` is a multiset retaining multiplicities, and a raw endpoint alone is never claimed to determine chronological order. The raw-to-Lean map therefore requires a declared history or an explicitly relational correspondence.
- The certificate connection (`semantics.tex:510–519`) correctly invokes the residual bijection and binary linear algebra in addition to trace adequacy. Generic event-system hypotheses alone are not credited with success/failure certificate existence.
- The manuscript's certificate completeness for every prescribed valid partial trace remains distinct from Lean's named empty-trace checker-completeness theorems. Canonical Lean trace adequacy itself covers every valid prescribed trace.
- The abstract principle, raw representation bridge, SELL-label erasure and global Solve-inclusive termination are consistently treated as manuscript results. The Lean declarations remain concrete LDPC theorems, and no formal parser, serialization or Python cache-refinement theorem is asserted.
- The label-erasure interpretation retains its domain restrictions and does not become a SELL sequent-calculus equivalence, focused-proof adequacy result, or resource-representation minimality claim.
- Direct word checking and trace replay are correctly distinguished by the additional declared operational explanation, not a stronger final-word predicate or an attestation of producer history.

`REVISION_REPORT.md`, `CLAIM_AUDIT.md`, and `ABSTRACT_ADEQUACY_NOTE.md` agree on these scopes. At the time of review, revision-report section K explicitly awaits the final build/layout/preservation record; that is a documentation completion item for the coordinating agent, not a mathematical defect. This review does not independently certify the cited literature, numerical artifacts, or PDF layout, which have separate review and verification tasks.
