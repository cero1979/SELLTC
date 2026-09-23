# SELL-style semantics repair and independent mathematical review

Date: 2026-09-23. The repository-wide initial audit was completed and committed before this repair phase. This report covers `paper/semantics.tex` and the independent raw-multiset diagnostic model in `tests/test_rewriting.py`. It does not report Lean compilation or decoder experiments; those have separate reports.

## Mathematical repair delivered

The manuscript fragment replaces the invalid literal log-free adequacy claim and the weak well-formedness predicate with a precise theorem for the original two asynchronous operational rules. It establishes the following statements with full informal proofs:

1. **Exact context invariant.** Known assignments form a partial function represented by exactly one value token per known variable. Unknown, pending, and residual tokens have specified multiplicities. Pending sets satisfy `N(j) ∩ U ⊆ Q_j ⊆ N(j)`. The stored residual is the XOR of known neighbors outside `Q_j`; thus delayed known incidences are explicitly allowed.
2. **Operational projection.** Its degree and syndrome are derived from the current assignment and actual matrix. The difference from cached rewrite data is explicit: `|Q_j| = d(j) + |D_j|` and `s(j) = p_j XOR XOR(K on D_j)`, where `D_j` contains known pending neighbors.
3. **Propagation stuttering.** A Propagate event preserves the invariant and operational projection. It consumes precisely one delayed known incidence.
4. **Solve soundness under arbitrary interleavings.** Its unique pending incidence and unknown token force the actual unknown-neighbor set to be a singleton. The cached residual at this check equals the operational syndrome, even if other checks still have delayed known incidences. The event simulates exactly one valid operational step.
5. **Normalization and propagation confluence.** The number of delayed known incidences strictly decreases. Propagations at distinct rows commute; propagations at distinct incidences of one row commute by XOR associativity/commutativity. Every maximal propagation-only continuation has the same exact endpoint, including unchanged logs. No confluence of arbitrary Solve choices is claimed.
6. **Global rewrite termination.** Every event consumes one pending token and creates none. Execution length is bounded by the initial number of pending incidences; Solve count is also bounded by the initial number of unknowns.
7. **Exact trace adequacy.** Every finite asynchronous execution from the initial context emits a valid operational trace, and its normalized endpoint is the replayed state encoded together with the trace's log multiset. Conversely every specified valid operational trace, including a partial or empty trace, has a derivation with exactly that chronological trace and exactly that logged normalized endpoint.
8. **Maximal executions.** A maximal rewrite execution is propagation-normalized and leaves either no unknowns or a nonempty stopping set. Empty unknown set alone does not imply a zero syndrome.
9. **Operational label erasure.** For these two rules, merging S and K into one ordinary persistent zone preserves events in both directions. On admissible contexts, ordinary multiset rewriting that consumes and recreates a value token has the same event-labelled transitions. This is a strong bisimulation for the specified operational systems, not an equivalence of full logical calculi.

The fragment includes the one-variable lost-log counterexample and a three-check example in which two Solve events occur before their shared check receives either propagation. These demonstrate why the previous endpoint equation and synchronized-block soundness proof were inadequate.

The logical vocabulary specifies a possible signature with labels S and K, a discrete preorder, and both labels unbounded; the static zone also holds the reusable program. The index domains and successor/XOR interpretation are stated. The text explicitly limits its theorem to operational multiset rewriting and makes no focused SELL/SELLF adequacy claim. References to Girard, Nigam--Miller, and Andreoli use the bibliography verified by the coordinating audit.

## Relationship to the original claim and to Lean

This is not a restriction to conveniently synchronized executions: soundness quantifies over every derivation of the original two raw rules from an initial encoding, including executions that end before propagation is complete. Synchronization is used only to construct a witness for completeness.

The ordered trace is carried by execution events or an explicit trace index. The endpoint's log multiset cannot reconstruct its order. Consequently the theorem never extracts computational trace data from an endpoint-only reachability proof in `Prop`.

The Lean agent has reported a canonical representation using assignment K, finite pending sets Q, and a residual syndrome derived from processed known neighbors. This excludes malformed cached records and duplicate tokens by construction. Such a representation is mathematically equivalent to the admissible multiset contexts described here, but the completed mechanization report must state exactly which representation relation, normalization result, and log correspondence are proved in Lean. This report does not claim that an informal representation argument has been mechanically checked. In particular, proofs about canonical records must not be described as proofs over every arbitrary raw multiset or as a SELL calculus formalization.

## Executed independent checks

Command, run from the bundle root:

```
python3 -m unittest discover -s tests -p 'test_rewriting.py' -v
```

All **11 tests passed**. The saved output is `audit/evidence/semantics-tests.txt`.

The model executes the raw multiset rules directly: it removes only one occurrence of every linear premise, retains persistent values on lookup, and appends a log atom for every Solve. Its transition generator does not assume the invariant. The invariant and operational replay functions then independently check reachable contexts.

The exhaustive component covers every binary matrix and every received word over `{erasure,0,1}` for dimension pairs `(n,m) = (0,0),(1,1),(1,2),(2,1),(2,2),(2,3),(3,1),(3,2)`. It reports:

| Quantity | Count |
|---|---:|
| Matrix/received-word instances | 2,719 |
| Reachable contexts including chronological trace history | 6,251 |
| Rewrite edges | 3,724 |
| Solve edges | 2,218 |
| Propagate edges | 1,506 |
| Contexts with delayed known incidences | 1,362 |
| Checked propagation diamonds | 144 |
| Operational traces realized with exact labels and endpoint | 4,889 |

For every reachable context, the tests compare the projection with independent replay, verify exact normalization and normalization length, compare different propagation orders, check enabled propagation diamonds, and compare persistent rewriting with the independent ordinary consume-and-recreate rules. Separately, an operational trace enumerator realizes every valid finite trace in the bounded instances; this also checks completeness for partial traces.

Named tests preserve the original negative examples: duplicate residual tokens falsify weak WF preservation; duplicate unknown tokens survive Solve; conflicting known values, missing pending edges, and non-edge pending atoms pass the old weak predicate but fail the new invariant. Other tests cover nonzero delayed syndromes, the lost log, two different chronological traces with identical terminal multisets, absence of global confluence on inconsistent inputs, empty dimensions, and isolated variables.

These finite checks are independent diagnostic evidence. They are not a substitute for the universal proof and do not establish a refinement of Python or Lean implementations.

## Independent Reviewer B: coding theory and certificate proof review

The semantics reviewer separately read the complete `paper/core.tex` without editing it. Its mathematical structure corrects the original failure-soundness gap: the known-value extension lemma is proved first, and residual equivalence is a bijection with all original compatible codewords. The finite-field alternative, Gaussian witness extraction, existential certificate completeness for every valid partial trace, rank--nullity multiplicity statement, and finite BEC likelihood argument are sound at the informal mathematical level. Endpoint erasure probabilities are handled by nonnegative likelihood rather than an unjustified positivity argument. The trust boundary properly distinguishes compatible completion, transmitted-word recovery, and attestation of a producer's internal actions.

Three concrete corrections were reported to the coordinator (original review locations):

- `paper/core.tex:164`: for m=0 and q>0, a solution is the q-dimensional zero vector, not an empty vector. This was an explicit dimension-zero wording error.
- `paper/core.tex:378-381`: the storage bound must include the q-bit output when m=0, or explicitly exclude input/output storage. A bound `O(q + m(q+m))` covers it.
- `paper/core.tex:113-116,341-343`: enforce the trace-length cap before validating every triple, or validate while streaming. Otherwise an arbitrarily long schema-valid hostile trace could be scanned before the claimed n+1-entry bound applies.

The coordinator corrected all three findings, and the reviewer reread the affected passages to confirm the q-dimensional zero vector, the explicit trace-length cap, and the storage bound including q. The scope of this review is the stated mathematics and cost model, not a claim that the implementation follows it without separate tests or refinement evidence.

## Verification limits and integration

Standalone LaTeX syntax verification completed successfully with native Tectonic (exit 0, six pages), including bibliography resolution. The final LaTeX log contains no undefined-reference, overfull-box, or underfull-box warning. Evidence is recorded in `audit/evidence/semantics-latex.txt`; Tectonic separately warns that the temporary wrapper inputs this workspace's absolute paths. The manuscript coordinator performs the final integrated LMCS build and PDF visual review. The temporary article-class wrapper uses the same mathematical macros and theorem environments but is not a replacement for the final manuscript PDF.

No known mathematical blocker remains in the corrected semantics fragment after the independent coordinating review. Publication readiness nevertheless depends on the final Lean statements and dependency audit, the concrete checker and experimental validation, integrated cross-references/layout, and the complete final review. Neither the bounded tests nor an isolated LaTeX build certifies those separate deliverables.
