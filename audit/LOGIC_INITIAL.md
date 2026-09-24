# Initial mathematical and logical audit

Date: 2026-09-20. Scope: read-only examination of the original manuscript and all six Lean modules, with particular attention to `PeelingState.lean`, `Rewriting.lean`, and `Adequacy.lean`. Only this audit note was added by this reviewer. The proposed repair below is a mathematical design for the subsequent repair phase, not a claim that the repository already implements or mechanically proves it. Original source line numbers are used throughout. Compilation results belong to the independent Lean audit.

## Finding summary

The certificate architecture has valid mathematical foundations, but the original logical development is not publication-ready. The literal Lean completeness theorem is false, the stated multiset well-formedness preservation theorems are false on their quantified domain, and the manuscript's asynchronous soundness proof contains a substantive gap. These are not missing applications of library lemmas. A stronger invariant can preserve the intended two-clause semantics and establish soundness for arbitrary asynchronous executions; it is unnecessary to restrict executions to an artificially synchronized subset.

| ID | Severity | Finding and original evidence |
|---|---|---|
| L01 | Blocking | `solve` permanently adds a `step` atom, whereas `encodeState` has no logs. Exact endpoint `adequacy_one_step` and `adequacy_completeness` are false. `Rewriting.lean:60-73,91-100`; `Adequacy.lean:75-85,90-108`. |
| L02 | Blocking | `WFContext` states uniqueness of a *pair occurring by membership*, not multiplicity one of the corresponding token. Duplicate `rem` and `unk` atoms satisfy its premises and falsify the advertised preservation theorems. `Rewriting.lean:105-113,115-123,200-207`; manuscript lines 714-772. |
| L03 | Blocking | Well-formedness permits contradictory persistent values, missing or non-edge pending incidences, and arbitrary residual syndromes. Consequently state extraction is not well-defined on the stated domain and WF does not justify operational validity. Manuscript lines 728-731,870-873; `Rewriting.lean:105-113`. |
| L04 | Blocking | Intermediate rewriting states can contain known but unpropagated incidences. Their stored degrees and syndromes need not equal operational degrees and syndromes. The soundness proof incorrectly assumes the immediately following propagation block updates every neighbor. Manuscript lines 875-888. |
| L05 | Blocking | `extractedTrace` tries to compute an ordered list by eliminating a proof of a relation in `Prop`. Proof irrelevance loses the execution order; two different orders can have identical endpoints. `Adequacy.lean:43-67`. A trace-indexed relation or computational derivation object is required. |
| L06 | Major | `ValidStep` omits positive adjacency and accepts spurious steps on arbitrary malformed states; `adequacy_one_step` quantifies over all such states without an invariant. `PeelingState.lean:55-63`; `Adequacy.lean:75-77`. |
| L07 | Blocking | The final combined adequacy theorem weakens soundness to existence of *some* valid trace, which is satisfied by the empty trace independently of the derivation. Completeness also fails to assert that the requested trace is extracted. `Adequacy.lean:132-141`. |
| L08 | Major | Failure-certificate soundness needs the missing lemma that every completion of the original input extends every assignment forced by a valid trace. Residual equivalence alone fixes the enlarged assignment and does not prove this. Manuscript lines 557-570. |
| L09 | Major | The stopping-set theorem is true, but its full-decoding proof omits the direction that a stopping subset of the initial erasure set can never lose a variable. Manuscript lines 221-236. |
| L10 | Blocking | SELL necessity is unsupported and false for the stated transition system: both persistent zones can be merged, and persistence can be encoded by ordinary consume-and-recreate rewriting. The graph zone is not consulted by either rule. Manuscript lines 101-103,668-689,901-902. |
| L11 | Blocking | The ML formalization concludes `True`, and its named probability axiom also concludes `True`; neither expresses likelihood or maximization. `Soundness.lean:187-212`; contrary claims at manuscript lines 950-981. |
| L12 | Major | Complexity omits input dimensions and overclaims lower bounds; certificate bit size silently assumes a relationship between m and n. Manuscript lines 607-625. |
| L13 | Major | The producer returns success immediately whenever no erasures remain, even if a degree-zero row has syndrome one. Its certificate is then rejected by the checker. Manuscript lines 302-304. |
| L14 | Major | Robustness prose confuses consistency with recovery of the transmitted word, uses an incorrect quantifier for witness completeness, and asserts monotonic corruption detection without justification. Manuscript lines 913-915,935. |
| L15 | Editorial | Fixed theorem/definition numbers in the Lean discussion and comments have drifted; proof-status prose and line estimates are not evidence of mechanization. Manuscript lines 942-995,999-1079. |

## Complete manuscript result inventory and source correspondence

The mathematical claims below exhaust the theorem, lemma, and proposition environments. Remarks with substantive mathematical claims are listed separately.

| Manuscript result | Lines | Mathematical assessment | Lean counterpart in original source |
|---|---:|---|---|
| Peeling stalls iff a stopping set remains (`thm:stopping`) | 221-237 | The local equivalence is correct. The full-erasure-removal characterization is correct, but one direction of its proof is missing; see L09. “Fully decodes” must mean removes erasures, or assume a compatible received word. | No theorem about stopping sets found. |
| Meaning of the state components (`lem:state-meaning`) | 375-406 | Correct informal induction for both degree and syndrome. | `SyndromeInv`, `initState_syndrome_inv`, `applyStep_syndrome_inv`, `syndrome_invariant`; no degree invariant counterpart. Original proof scripts require independent compilation. |
| Residual equivalence (`lem:residual-equivalence`) | 408-435 | Correct for assignments extending the current K. Does not by itself show every completion of original y extends K. | No theorem with this name or equivalent general completion-preservation statement found. |
| Success soundness (`thm:sound`) | 442-467 | Correct informal proof for the specified checker, including partial valid traces. | `thm_sound_success`, `Soundness.lean:99-143`; purported syndrome bridge is absent. It must not be called mechanically complete on source inspection alone. |
| Infeasibility witness soundness | 476-495 | Correct elementary linear-algebra argument, including zero residual variables. | `lem_unsat_witness_sound`, `Soundness.lean:54-64`. Compiler/dependency status is separate. |
| Infeasibility witness completeness | 497-522 | Correct finite-dimensional argument using the nondegenerate coordinate pairing. | `lem_unsat_witness_complete`, `Soundness.lean:76-86`, explicitly admitted. |
| Witness extraction from row reduction | 524-551 | Correct. Invertibility of the row-operation matrix supports equivalence of systems; the displayed witness identity itself needs only the stated transformed row. | No extraction algorithm or theorem found. |
| Failure-certificate soundness | 557-570 | True, but proof misses forced-assignment preservation (L08). | `thm_sound_failure`, `Soundness.lean:149-175`, explicitly admitted. |
| Accepted completions are ML | 573-592 | Correct for 0 < epsilon < 1. The theorem should state the domain used in its proof, or treat endpoints using nonnegative rather than strictly positive likelihood. | `thm_ml` has no ML conclusion; `bec_equal_likelihood` has no likelihood equation. |
| Checker linear complexity | 607-621 | Sparse abstract implementation can achieve O(n+m+|E|); the two displayed dimension-omitting bounds need additional assumptions. Claimed universal tightness is not proved. | No cost semantics or complexity proof found. |
| Propagate preservation | 736-755 | False on the stated multiset WF domain because multiplicities are unrestricted. Correct under the stronger invariant below. | `propagate_wf`, `Rewriting.lean:116-198`, attempts a false theorem. |
| Solve preservation | 757-773 | False on the stated multiset WF domain, including duplicate unknown tokens. Correct under the stronger invariant below. | `solve_wf`, `Rewriting.lean:201-277`, attempts a false theorem. |
| Adequacy | 793-893 | The manuscript's existential normalized-endpoint completeness is repairable and the arbitrary-derivation trace soundness claim is true with a stronger invariant. The supplied proof is insufficient. Literal Lean exact-endpoint completeness is false. | `adequacy_one_step`, `adequacy_completeness`, `adequacy_soundness`, `thm_adequacy_complete`; multiple admissions and structural errors. |

Additional claims: certificate size (623-626), “SELL is essential” (101-103), focusing/SELLF packaging (895-898), persistent knowledge ensures all propagation is complete (902), corruption guarantees (913-935), and the complete-mechanization descriptions (942-995). None of the source files defines a SELL sequent calculus, subexponential preorder, focusing discipline, or calculus-level adequacy theorem.

Definitions map as follows. A parity-check matrix is `PCMatrix` over `ZMod 2`; channel consistency and code membership are `isConsistent` and `isCW` (`Basic.lean:31-48`). `PeelingState` stores K, s, d (`PeelingState.lean:20-26`), with U derived from K. `initState`, `applyStep`, and `ValidTrace` occur at lines 38-43,48-52,68-73. The trace triple is `StepTriple` (29-33). The residual assignment is a function on U in the paper, but a total `Fin n -> ZMod 2` whose values at known positions are ignored in Lean (`Checker.lean:53-56,72-79`). `Context` stores the matrix G, a persistent multiset P, and a linear multiset L (`Rewriting.lean:49-55`), rather than an actual proof-theoretic context. `Atom.edge` and `Atom.known` are constructors, but the actual static graph and knowledge are represented separately as G and P. `RewStep` carries an H parameter that its constructors never consult (`Adequacy.lean:43-52`). `checkSuccess` and `checkFailure` express certificate checks, but no theorem in this original bundle establishes correspondence with the independent Python implementation. This last point requires the implementation audit, not an inference from similar names.

## Explicit counterexamples

### C1: smallest log obstruction to exact endpoint adequacy

Let n=m=1, H=[1], and y=(erasure). Then sigma has K empty, d(1)=1, s(1)=0. The valid operational step is (1,1,0). Its initial encoding contains

```
P = empty
L = {unk(1), pend(1,1), rem(1,1,0)}.
```

The only possible first rewrite is Solve. It produces

```
P = {(1,0)}
L = {rem(1,0,0), step(1,1,0)}.
```

The target `encodeState H (applyStep H sigma stp)` instead has L={rem(1,0,0)}. Neither rule removes a step atom. No nonempty derivation can reach the target, and the empty derivation does not change K. Thus the exact theorem is false even from a legitimate initial state. More generally, the step-token count is monotone and increases by one at every Solve, whereas every `encodeState` has step-token count zero.

This does **not** refute the manuscript's separately stated existential endpoint theorem, which allows a context carrying logs and extracts its state while ignoring logs. It refutes the claimed correspondence between that theorem and the Lean statement.

### C2: duplicate rem tokens falsify propagate preservation

Use n=m=1, H=[1], P={(1,0)} and

```
L = {pend(1,1), rem(1,1,0), rem(1,1,0)}.
```

All original `WFContext` fields hold. There is exactly one *pair* (k,p) whose rem atom occurs, namely (1,0); no unknown token coexists with the known value; the pending-token count is one. Propagate erases only one copy of `rem(1,1,0)` and leaves

```
L' = {rem(1,1,0), rem(1,0,0)}.
```

Now two different rem pairs occur, and the residual old rem also has the wrong pending count. Therefore `propagate_wf` is mathematically false as quantified. The same multiplicity ambiguity is present in the manuscript's membership-based WF1.

### C3: duplicate unknown tokens falsify solve preservation

Use n=m=1, H=[1], P empty and

```
L = {unk(1), unk(1), pend(1,1), rem(1,1,0)}.
```

Again original WF holds. Solve erases one unknown token, adds known(1,0), and leaves the other unknown token. The resulting variable is both known and unknown, contradicting `wf_var`. The theorem's explicit conclusion that `unk(1)` is absent is also false.

### C4: WF does not define a partial assignment or a valid residual

With n=m=1, P={(1,0),(1,1)} and L={rem(1,0,0)}, the original WF fields hold. The manuscript's requirement “K(1)=b iff val(1,b) occurs” assigns two different values to K(1), so state extraction is not a function.

Even restricting token multiplicities and known values is insufficient. Let H=[1 1], K empty and L={unk(1),unk(2),pend(1,1),rem(1,1,1)}. WF holds and Solve can resolve variable 1 to 1, although the actual check has two unknown neighbors. The predicate neither demands a pending token for every unknown edge nor gives the syndrome any semantic meaning. No claim that arbitrary WF contexts represent operational states is justified.

### C5: arbitrary `ValidStep` need not be a graph step

Let H=[0], K(1)=none, d(1)=1, s(1)=0. `PeelingState` permits this inconsistent record. `ValidStep H sigma (1,1,0)` holds: its universal uniqueness implication is vacuous because the row has no edges. Nevertheless `encodeState` has no pend token, and no rewrite is possible. Adding logs to the target alone therefore does not fix `adequacy_one_step`. Require a degree invariant or strengthen `ValidStep` to assert that the unknown-neighbor set is exactly {i}; for a general one-step theorem require both degree and syndrome invariants.

### C6: reachable asynchronous state is not its operational encoding

Take H=[[1],[1]], y=(erasure), and solve variable 1 at the first check. Its value is now known, but before propagation the second check retains `pend(2,1), rem(2,1,0)`. Its stored degree is 1; its operational number of unknown neighbors is 0.

For a simultaneous syndrome discrepancy on a compatible input, take H=[[1,1],[1,1]], y=(erasure,1). Solve variable 1 at check 1 with value 1. Before propagation, check 2 stores `rem(2,1,1)`, although the operational state has d(2)=0 and s(2)=1 XOR 1=0.

Consequently simply deleting logs does not turn every intermediate context into `encodeState` of the replayed state. Normalization or an observational projection is also necessary.

### C7: the next solve may precede unfinished propagation

Take

```
H = [[1,0], [0,1], [1,1]], y=(erasure,erasure).
```

Solve (1,1,0), then immediately solve (2,2,0). Both are legal rewrites and form a valid operational trace. The propagation block after the first solve is empty. Check 3 still contains both pending incidences and `rem(3,2,0)`, while the replayed operational state after the two solves has degree zero everywhere. This explicitly falsifies the manuscript's claim at lines 887-888 that the maximal immediate propagation block already puts the suffix at the checker-updated encoding. It does not falsify trace soundness; the strengthened invariant below proves that theorem without this assumption.

### C8: proof-irrelevant reachability cannot carry chronological trace extraction

Let H be the 2-by-2 identity matrix and erase both variables. Solve first variable 1 then variable 2, or first variable 2 then variable 1. Both derivations have the same initial context and exactly the same final multisets of assignments, rem atoms, and step atoms. Their chronological traces differ. Since proofs of `RewStar H initial final : Prop` are proof-irrelevant, a function on that proposition cannot compute the two different lists. This is a representation error independent of tactics or missing lemmas.

### C9: degree-zero inconsistency and compatible corruption

For H=[1], y=(1), the hybrid pseudocode reaches U empty immediately and returns success x=(1), but its success checker rejects because s(1)=1. The correct residual problem has zero columns and right-hand side 1; omega=(1) is an infeasibility witness. The producer must verify zero-degree constraints before reporting success or route all cases through residual algebra.

For H=[1 1], transmitted word (0,0), and corrupted received word (1,erasure), the completion (1,1) has valid parity and agrees with every visible input. It has a valid success certificate although it is not the transmitted word. Thus “never silently accepts a wrong codeword” cannot mean exact recovery under corrupted inputs. It can mean only soundness relative to the supplied H and y.

## Proposed nontrivial adequacy repair

### Semantic objects and invariant

Keep the original two rewrite rules, including their step-log output. Separate the operational state from its asynchronous realization. For a partial assignment K write U for its unknown coordinates and N(j) for the actual neighbors of check j. Let Q_j be a finite set of **pending incidences**, including unknown neighbors and possibly known neighbors whose value has not yet been propagated.

An admissible asynchronous context has the following exact structure:

1. G=H; P is exactly the graph of the partial function K, with one value token per known variable.
2. L has exactly one `unk(i)` for i in U, no other unknown tokens, exactly one `pend(j,i)` for i in Q_j, and exactly one `rem(j,|Q_j|,p_j)` per row.
3. `N(j) intersect U` is a subset of Q_j, and Q_j is a subset of N(j). In particular no unknown incidence has already disappeared and no non-edge incidence exists.
4. `p_j = XOR {K(i) : i in N(j) minus Q_j}`. Every value in this sum is defined, by item 3.
5. The remaining linear atoms are precisely the multiset of logged triples from the chosen derivation history T. They do not determine the order of T; chronological order belongs to the derivation or to an explicit trace index.

These are exact multiplicity statements, not membership-based uniqueness. The context can equivalently be represented by finite data (K,Q,p,logs), provided an explicit encoding into the original multiset syntax is given and shown to commute with both rules. Such a representation change must not silently discard the multiset adequacy claim.

Define the operational projection pi(M) from its unique K and the actual graph H:

```
d_op(j) = |N(j) intersect U|
s_op(j) = XOR {K(i) : i in N(j) intersect dom(K)}.
```

If D_j=Q_j intersect dom(K) denotes delayed known incidences, the invariant implies

```
stored_degree(j) = d_op(j) + |D_j|
s_op(j) = stored_syndrome(j) XOR XOR {K(i) : i in D_j}.
```

Thus the stored state is not asserted to be operational while D_j is nonempty. A context is **propagation-normalized** when every D_j is empty. Exactly then its non-log part is `encodeState H (pi(M))`.

### Preservation and local simulation argument

The initial encoding is admissible: Q_j=N(j) intersect U, and the initialization syndrome is the XOR of exactly the neighbors outside Q_j. All token multiplicities are one and the initial log is empty.

For Propagate at (j,i), i belongs to Q_j and is known with a unique value b. The rule replaces Q_j by Q_j minus {i}. It removes no unknown incidence. The outside set N(j) minus Q_j gains precisely i, so its XOR changes by b, exactly as the rule updates p_j. Its cardinality decreases by one, exactly as the rem degree update. All other rows and K remain unchanged. Thus the invariant is preserved and the operational projection does not change. Propagate is a stuttering step of the operational simulation.

For Solve at (j,i,p), `rem(j,1,p)` and the unique pending structure imply Q_j={i}. The unknown token means i is unknown. Since every unknown neighbor must lie in Q_j and i is a genuine neighbor, `N(j) intersect U={i}`. All other neighbors are known and outside Q_j; therefore the stored p is exactly the operational syndrome s_op(j). Hence (j,i,p) is a valid operational peeling step.

After Solve, assign K(i)=p and remove i from U. At the forcing row Q_j becomes empty and the XOR outside Q_j becomes p XOR p=0, matching `rem(j,0,0)`. At any other adjacent row, i was unknown and therefore still belongs to its pending set; it stays pending but is now known, so the sum over neighbors outside its pending set is unchanged. At nonadjacent rows nothing changes. Exactly one unknown token is consumed, one persistent value is added, and one log atom is created. This proves preservation and simulation of one true operational step even when previous assignments still have unpropagated incidences elsewhere.

### Propagation normalization and commutation argument

With K fixed, the number `sum_j |Q_j intersect dom(K)|` decreases by one at each Propagate, is a nonnegative integer, and is positive precisely when a propagation is available. Every propagation-only maximal continuation therefore terminates after exactly this many steps. Its final pending sets are forced to be Q_j intersect U=N(j) intersect U, and its final syndromes are forced by the invariant to be s_op(j). Thus the normalized context is unique, including its unchanged log multiset.

For two propagations at different checks the updated fields are disjoint. For two distinct pending incidences of the same check, both remain enabled after either order: the initial pending degree is at least two. Both orders remove the same two incidences, decrement the degree by two, and XOR the same two known bits. Associativity and commutativity of XOR give the same result. Token uniqueness excludes a second consumption of the same incidence. This proves the required diamond property directly and also explains the unique normal form.

All rewrite derivations are finite: the number of unknown tokens plus pending tokens strictly decreases at each rule (by one for Propagate, by two for Solve). Pure propagation normalization needs no fairness assumption. A derivation that merely stops early need not be normalized; a maximal derivation is normalized and has either no unknowns or a nonempty stopping residual.

### Correct theorem statement and proof plan

Write `Enc_H(sigma,T)` for `encodeState H sigma` plus the multiset of step-log atoms for T. The logs record occurrences, while T records order. Use either a derivation object in `Type`, with a well-defined chronological `trace(D)`, or a proposition `Derives H M T M'` whose trace is an explicit index. A relation in `Prop` with only endpoint indices is insufficient.

For H, received y, and its initial state sigma_0, the corrected theorem should assert:

**Soundness for arbitrary interleavings.** Every finite derivation D from `Enc_H(sigma_0,[])` has a trace T valid from sigma_0. Its endpoint M satisfies the asynchronous invariant, pi(M) is exactly the operational state obtained by replaying T, and propagation normalization of M is exactly `Enc_H(replay(T),T)`.

**Completeness with the requested trace.** For every valid operational trace T from sigma_0, there exists a derivation D whose chronological trace is exactly T and whose endpoint is exactly `Enc_H(replay(T),T)`.

Soundness follows by induction on the rewrite derivation using the local simulation above. The base projection is sigma_0. A Propagate preserves K and hence pi and contributes no trace entry. A Solve is a valid operational step with the claimed value, changes pi by the operational `applyStep`, and appends precisely its triple to T. The invariant and log equation follow simultaneously. Normalization is the preceding unique-normal-form argument.

Completeness follows by induction on T, maintaining the exact normalized endpoint. For a valid next triple (j,i,b), its encoding contains `unk(i)`, `pend(j,i)`, and `rem(j,1,b)`, so Solve applies. Then propagate the newly known i to every other adjacent check. Such a pending incidence exists because i was unknown at the normalized start; its count is positive. Each is consumed exactly once. The resulting context is propagation-normalized, its projection is the operational updated state, and its log is the old log plus exactly this step. This establishes the exact endpoint `Enc_H` and exact requested chronological trace. Concatenation of these macrotransitions realizes the full trace.

This theorem is substantive: it proves that unrestricted asynchronous rule schedules cannot emit an invalid operational trace, establishes a precise relationship between cached residuals and operational residuals, and realizes each specified operational trace without changing its order. It does not use trivial existence of an empty trace, discard the log problem, or identify unnormalized contexts with operational states.

### Bounded independent check of the proposed invariant

A read-only Python enumeration was executed during this audit; it did not edit source code or generate manuscript results. It enumerated every binary matrix and every ternary received word for dimension pairs (0,0), (1,1), (1,2), (2,1), (2,2), (2,3), (3,1), and (3,2), then all reachable asynchronous configurations including their chronological traces. Result:

```
instances: 2719
reachable contexts including trace history: 6251
rewrite edges: 3724
Solve edges: 2218
Propagate edges: 1506
contexts with delayed known incidences: 1362
PASS: invariant, validity of every chronological trace, and normalization equations.
```

This is bounded diagnostic evidence, not a substitute for the mathematical argument or Lean verification. The enumeration represented exact pending sets, so it intentionally does not validate the original defective WF predicate on arbitrary multisets.

## Other mathematical corrections required

### Completion preservation, certificates, and stopping sets

For a fixed codeword x consistent with the original y, induct on a valid trace. Initially x extends K_0. At a step forcing i at j, every neighbor of j except i is known and already agrees with x. The parity equation for x therefore forces `x_i = XOR(known neighbors) = s(j) = b`. Thus x extends the enlarged K. This lemma proves every original completion survives replay; conversely any completion extending the enlarged K is consistent with original y because known coordinates are never overwritten. Consequently the residual solutions after any valid partial trace are in bijection with the original compatible codewords, via reconstruction. This supplies the missing step in failure soundness and makes certificate completeness precise.

Partial valid traces are intentionally safe: T may be empty or stop before peeling stalls. The residual witness must still cover all remaining unknown variables. A success certificate attests that an assignment exists and that the declared trace is valid; it does not prove the producer actually followed that trace internally, recover the transmitted word in a nonunique instance, or prove uniqueness. If the residual system is compatible, the number of completions is `2^(|U|-rank(H_U))`; it is unique exactly when that nullity is zero.

For the omitted stopping-set direction, let S be a nonempty stopping subset of U_0. If S is contained in the current U, a peeling step cannot remove i in S: its forcing check would then have at least two neighbors in S, contradicting residual degree one. Hence S stays contained in U throughout every run, and full erasure removal is impossible. Together with the proof already present, this establishes the biconditional.

Witness completeness is existential: an inconsistent residual admits **some** accepted omega; it does not make every supplied omega valid. For instance omega=0 fails `omega^T r=1` on every input. The prose at line 915 must use the existential quantifier.

### ML, computational cost, and threat scope

A finite BEC model needs no unproved axiom: define the one-coordinate transition probability as epsilon for erasure, 1-epsilon for agreement, and zero for disagreement, and take the finite product. Under 0 <= epsilon <= 1 every factor is nonnegative. A consistent codeword has the common likelihood `epsilon^e (1-epsilon)^(n-e)`; an inconsistent one has zero. Thus a consistent codeword maximizes likelihood, including endpoint cases where the common likelihood is zero for an impossible observation. If the paper uses strict positivity, state 0 < epsilon < 1 instead. The Lean formalization must actually compare these likelihoods, or omit its ML claim explicitly.

With bidirectional adjacency lists, valid-trace replay and sparse parity/witness verification admit O(n+m+|E|) word operations. Initialization reads y and row data, so failure checking cannot generally omit n; checking all zero-degree rows means success checking cannot generally omit m. Simplification to O(n+|E|) is possible with a stated bound on m, and O(|E|+m) for failure also needs to account for n. No complexity result has been proved for the dense function/matrix Lean representation or Python implementation by this argument. State a word-RAM representation, preprocessing policy, and treatment of malformed certificates. A final assignment alone is directly checkable in the same sparse asymptotic time and avoids replay overhead; the extra trace buys trace validity, not a stronger parity certificate.

In general, a trace of t entries has `O(t(log(m+1)+log(n+1)+1))` bits, plus |U| assignment bits for success or m witness bits for failure. Replacing both logarithms by log n needs an explicit relation such as m polynomially bounded by n. An Omega(|E|) universal lower bound does not follow merely from the fact that this particular algorithm updates every adjacent check.

Soundness is relative to the supplied matrix and received word and to correct execution of the checker. A corrupted H changes the code being checked; no authentication or recovery of the intended matrix is provided. Some visible-bit corruptions retain a compatible codeword. Detection probability need not increase monotonically with the corruption probability: for the length-two parity code and no erasures, independent flips are inconsistent with probability `2 delta (1-delta)`, which decreases after delta=1/2 and is zero at delta=1. The empirical claim at line 935 needs to be restricted to the actual measured conditions.

## Exact role of SELL

The present theorem is about a two-rule multiset transition system. In that system S and K both have unrestricted reuse, and no rule tests a label ordering or a difference in structural permissions. Relabel both persistent zones by a single ordinary exponential; the operational transitions are identical. In fact the static graph zone is not consulted at all: adjacency is enforced only by the intended pending-incidence invariant. Merely storing `ctx.G=H` does not make a malformed pending token correspond to an edge.

Ordinary multiset rewriting can also preserve a value token explicitly:

```
val(i,b) + pend(j,i) + rem(j,k,p)
  -> val(i,b) + rem(j,k-1,p XOR b).
```

This consumes and recreates the same information and has the same sequential transitions. No semantic copying of bits or one-use graph corruption is necessary. Distinct subexponential zones provide a useful specification discipline and organizational distinction, but necessity or extra expressive power has not been demonstrated here. Persistence also does not force propagation to occur before another rule; C7 is a reachable counterexample.

For an actual SELL embedding, specify the signature (labels, preorder, unbounded subset), formula grammar, reusable program context, quantification or ground-instantiation convention, and arithmetic interpretation of k-1 and XOR. Then define a deductive calculus and prove the embedding if calculus-level adequacy is claimed. Until then use “SELL-style multiset rewriting with persistent zones,” and explicitly distinguish the operational theorem from any SELLF or focused-proof theorem. The paper's main identity can be retained honestly without asserting that the two subexponentials are mathematically necessary.

## Recommended repair order

1. Finish the repository-wide initial audit and preserve the original artifacts before implementing changes.
2. Correct the operational validity predicate and prove degree, syndrome, known-value extension, and completion-preservation invariants.
3. Replace WF by the exact asynchronous invariant; replace proof-irrelevant trace extraction by explicit event/trace data; repair adequacy using log-extended endpoints and propagation normalization.
4. Prove certificate soundness/completeness with the actual checker specification and give its trust boundary. Either implement the real finite BEC likelihood theorem or report ML as informal only.
5. Correct zero-variable residual handling, complexity statements, and corruption interpretation; verify the concrete implementation separately.
6. Reposition the contribution as a precise SELL-style specification and trace-certification architecture. Claim no calculus-level SELLF adequacy or necessity of the two zones without a separate proof.

No source theorem has been repaired by this audit note. Publication readiness remains blocked until the false statements, invalid proof representation, implementation issues, and mechanization claims are corrected and independently verified.
