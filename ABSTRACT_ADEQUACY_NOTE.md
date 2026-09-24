# Abstract delayed-propagation adequacy principle

Date: 2026-09-24. This note explains the named, unnumbered proposition added immediately before the principal LDPC theorem in `paper/semantics.tex`. It is a mathematical abstraction with a complete manuscript proof. It introduces no new Lean declaration, no new experimental result, and no claim of novelty for the general simulation argument.

## Statement and objects

The abstract concrete system has states `M`, an admissible subset `I`, silent transitions labelled `τ`, and observable transitions labelled by events in `A`. The operational system has states `S` and event-labelled transitions. Operational transitions may be nondeterministic; the theorem quantifies over a specified operational **path**, including its endpoint, rather than assuming that an event list alone determines a unique state.

Three maps are required on the appropriate domains:

- `π : I → S` observes the operational state.
- `ℓ : I → Multiset(A)` observes the retained log atoms.
- `Can : S × Multiset(A) → I` gives a canonical concrete representative of an operational state and log.

An execution's trace is its **ordered list of nonsilent event labels**. Its log is a finite multiset. The construction never attempts to recover chronological order from a multiset endpoint. This distinction is required for the raw LDPC contexts, which contain unordered `step` atoms.

The hypotheses are:

1. **Canonical representations.** `Can(σ,B)` is silent-normal, has projection `σ`, and has log `B`.
2. **Invariant preservation and local simulation.** Every concrete transition from `I` stays in `I`. Silent transitions preserve both `π` and `ℓ`. An `a`-labelled transition simulates an operational `a`-step between the endpoint projections and adds exactly one occurrence of `a` to the log.
3. **Terminating canonical normalization.** Silent reduction terminates on `I`, and every silent-normal admissible state `N` equals `Can(π(N),ℓ(N))`.
4. **Local lifting.** For every operational step `σ —a→ σ′` and every prior multiset log `B`, the state `Can(σ,B)` has an `a`-labelled concrete successor `P` with `π(P)=σ′`.

The conclusion first identifies the unique silent normal form as `Can(π(M),ℓ(M))`. Any two silent descendants have the same projection and log and therefore normalize to the same representative; this proves confluence for **silent reduction on admissible states only**.

For every finite concrete execution `M —T⇒* N` from `I`, the exact ordered list `T` labels an operational path from `π(M)` to `π(N)`, and `ℓ(N)=ℓ(M) ⊎ Log(T)`. Normalizing `N` reaches the canonical representative with precisely that final projection and accumulated log.

Conversely, any specified finite operational path from `π(M)` with labels `T` and endpoint `σ′` is realized from `M` by a concrete execution with the same ordered list and exact endpoint `Can(σ′,ℓ(M) ⊎ Log(T))`. This includes empty and partial paths and arbitrary admissible starting contexts. Initial silent normalization is allowed when the starting context is not canonical.

## Why the hypotheses cannot be silently dropped

**Forward simulation is not local lifting.** Consider two operational states with one event step `σ —a→ σ′`. Give the concrete system canonical states with the correct projections and logs, but no transitions at all. Silent stuttering and observable simulation hold vacuously; silent reduction terminates and has canonical normal forms. The operational step still has no concrete realization. Thus the four schematic assumptions in the editorial brief require the additional reverse, local lifting obligation before completeness follows.

**A unique normal form per state is not a canonical normal form for each observation.** Distinct silent-normal concrete states may have the same projection and log. Each can have a unique normal form, namely itself, without either being a chosen common representative. Condition 3 excludes that ambiguity. The proof therefore identifies the exact endpoint, rather than proving only existence of some normalized state.

**The lifted endpoint matters in a nondeterministic operational system.** It is insufficient to require merely an outgoing concrete transition with the right label. It must project to the prescribed successor `σ′`; otherwise a different successor of the same operational label could be realized while the requested path cannot.

**Log updates retain multiplicity.** Silent transitions must not modify the log, and an observable event must add exactly one occurrence. Set membership would not capture duplicated or lost events. An unordered log still cannot determine the order of its events, which is supplied separately by the labelled execution.

**All concrete successors must preserve the invariant.** Soundness concerns arbitrary permitted interleavings, not just a schedule selected by the proof. It cannot restrict preservation to the special normalized executions constructed for completeness.

## Complete proof architecture

The manuscript supplies three full arguments.

First, well-founded induction on silent reduction yields a silent-normal descendant of every admissible state. Silent stuttering preserves projection and log, and the canonical-normal-state hypothesis identifies every such descendant. This proves existence, uniqueness and silent confluence without appealing to an unstated Church–Rosser theorem or assuming confluence of observable transitions.

Second, induction on the length of a finite concrete execution proves soundness. A silent event leaves the operational path and log unchanged. An observable event appends exactly its label to the path and one occurrence to the log. The canonical normalization result then identifies the final normalized endpoint.

Third, induction on the length of the requested operational path proves completeness. The empty case normalizes the starting concrete state. The nonempty case first normalizes, lifts the first operational event using hypothesis 4, and applies induction to the remaining path from that successor. Concatenation retains the same event order, while the finite multiset calculation supplies the exact endpoint log. No assumption of an immediately propagating schedule is imposed on arbitrary executions by this construction; it is only one witness for the completeness direction.

## LDPC instantiation

Fix the supplied binary parity-check matrix `H`.

| Abstract object or condition | LDPC instance and justification |
|---|---|
| Concrete states and invariant | Raw contexts with the exact multiplicities of Definition 6.1; one unknown token or persistent value per variable, one residual token per row, one token per pending incidence, and the stated log multiset |
| Operational states and projection | Coherent peeling states and the projection of Definition 6.2 |
| Events | Peeling triples `(j,i,b)` |
| Silent relation | Propagate |
| Observable relation | Solve with its triple label |
| Log `ℓ` | The finite multiset of `step(j,i,b)` atoms |
| Canonical map | The normalized raw encoding with the given multiset log; equivalently `Enc_H(σ,T)` for any `T` with that multiset image |
| Condition 1 | Definition 6.2 and the pending-incidence invariant; normalized pending sets have no known incidence left to propagate |
| Condition 2 | Lemmas 6.5 and 6.6, including exact log updates and the operational projection of Solve |
| Condition 3 | Lemma 6.7; silent propagation removes precisely the delayed known incidences and reaches the exact encoding |
| Condition 4 | A valid operational step has `N(j) ∩ U={i}` and `s(j)=b`; the canonical context therefore contains the residual, pending, and unknown tokens enabling that precise Solve. Lemma 6.6 identifies its projected successor. The previous log does not affect enabledness. |
| Received-word initial state | Lemma 6.4 supplies the normalized empty-log encoding |

The map from a multiset log to the normalized raw encoding is well-defined because the encoding depends on a list only through its multiset image. Choosing a list representing the multiset does not add a chronological observer to the raw context.

Theorem 6.10 remains the principal numbered result. Its original statement and full direct proof are retained; its heading identifies it as the main theorem. The generic proposition is unnumbered and therefore does not shift Theorem 6.10 or Proposition 6.12. Its local lifting condition is verified explicitly **before** invoking Theorem 6.10, preventing a circular instantiation.

## Actual dependency map

The results form a directed dependency graph, rather than the single chain suggested in the editorial brief:

- Operational Definition 2.1 supports Lemma 2.2, which supports the residual bijection in Lemma 3.1.
- Lemma 3.1 and the certificate specification support success soundness, Theorem 3.3. Failure soundness/completeness, Theorem 3.6, additionally uses the finite-field alternative, Lemma 3.4. Proposition 3.5 concerns constructive row-operation witness extraction; the existential proof of Theorem 3.6 does not depend on that particular algorithm.
- Definitions 6.1–6.2 support initialization and the Propagate/Solve preservation lemmas, 6.4–6.6. The delayed-incidence invariant and Propagate preservation support normalization, Lemma 6.7.
- Proposition 6.8 uses invariant preservation and consumption of one pending token per event to prove global termination. It is not needed to prove Theorem 6.10 for finite executions. It does ensure that maximal executions cannot continue infinitely.
- Theorem 6.10 uses initialization, stuttering, Solve simulation, normalization, and the explicit local lifting fact. The abstract proposition factors this proof architecture; its generic proof depends on none of the LDPC lemmas.
- Proposition 6.11 uses preserved admissibility, normalization, and the enabledness of Solve whenever the normalized operational degree is one. Its interpretation as the endpoint of an exhausted run is consistent with global termination.
- Proposition 6.12 is a separate rule-by-rule representation comparison. Its ordinary-rewriting part uses invariant closure to stay in the specified image. It does **not** follow from the stopping-set proposition and is not a prerequisite of the adequacy theorem. Its translations preserve the observations and events used by that theorem.

The algebraic certificate layer is attached after trace adequacy: the emitted valid trace determines the operational residual, Lemma 3.1 identifies its compatible completions, and Theorems 3.3/3.6 justify the supplied success or infeasibility witness. None of those binary linear-algebra conclusions follows from the generic event-system assumptions alone.

## Mechanized and unmechanized parts

The new abstract proposition and its instantiation are proved in the manuscript, not added to Lean. Existing Lean declarations remain unchanged and retain their previous scope:

- `rewstar_sound` proves arbitrary-interleaving soundness for the canonical asynchronous representation.
- `rewstar_observation` proves the exact folded state and appended ordered observer.
- `adequacy_one_step` and `adequacy_completeness` implement the LDPC-specific local-lifting/normalization construction and retain the specified event list.
- `propagation_normalization`, `propagation_normal_form_unique`, and `propagation_confluence` establish the canonical silent-normalization results.

Raw multiset/canonical representation correspondence remains informal mathematics. The Lean context stores an ordered observer, whose multiset image corresponds to the raw log atoms. A raw context alone cannot reconstruct that observer; a diagram relating the representations must include execution history or describe the forgetful multiset map accurately.

The abstract result does not mechanize global Solve-inclusive termination, a SELL sequent calculus, label erasure, or Python refinement. The named checker-completeness theorems still construct empty-trace certificates; the stronger every-prescribed-valid-trace certificate theorem remains the manuscript's algebraic result. Parser, serializer, compiler/runtime behavior and timing evidence keep their existing boundaries.

## Reusability and limits

The proposition does not mention binary fields, parity equations, Tanner graphs or peeling. It applies to another asynchronous system if that system supplies an invariant, state projection, log observer, canonical representatives, the stipulated silent normalization, and **both** local simulation and local lifting. These are explicit verification obligations, not a claim that every propagation system satisfies them.

The principle is sufficient rather than necessary. For example, some systems permit operational steps to be lifted only by a longer concrete block, or have normalized states distinguished by additional hidden observations. Such systems would require a modified theorem; the current statement must not be applied to them without checking its hypotheses. No unrelated application, new expressiveness theorem, generic novelty claim, or result about full-system confluence is asserted.

Proposition 6.12 retains its mathematical statement and proof. Its revised interpretation is positive: the persistent zones expose the intended access discipline, while their event-preserving erasure identifies a distinction that this particular operational certification argument does not need. It does not prove that any broader class of resource-sensitive representations is minimal or that SELL logical calculi are equivalent.
