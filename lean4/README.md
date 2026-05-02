# Lean 4 Mechanization — SELLCert

This directory contains the Lean 4 formalization of the main results from the paper
*Certified Hybrid Decoding of Binary LDPC Codes over the BEC via Subexponential Linear Logic*.

The library currently comprises **~650 lines** (994 including blank lines and comments)
organized in six modules.

---

## Proof status

| Lean identifier | Paper label | Module | Status |
|---|---|---|---|
| `syndrome_invariant` | Lem. 4.5 | PeelingState | ✅ Complete |
| `propagate_wf` | Lem. 6.6 | Rewriting | ✅ Complete |
| `solve_wf` | Lem. 6.7 | Rewriting | ✅ Complete |
| `lem_unsat_witness_sound` | Lem. 5.3 | Soundness | ✅ Complete |
| `thm_sound_success` | Thm. 5.1 | Soundness | ✅ Complete (1 admit†) |
| `thm_ml` | Thm. 5.8 | Soundness | ✅ Complete (BEC axiom‡) |
| `lem_unsat_witness_complete` | Lem. 5.4 | Soundness | ⚠️ Admitted (a) |
| `thm_sound_failure` | Thm. 5.7 | Soundness | ⚠️ Admitted (b) |
| `adequacy_completeness` | Thm. 6.11 (→) | Adequacy | ⚠️ Admitted (c) |
| `adequacy_soundness` | Thm. 6.11 (←) | Adequacy | ⚠️ Admitted (d) |

†  One helper connecting `replayFull` to `SyndromeInv`; ~30 lines.
‡  `bec_equal_likelihood` is a genuine **axiom** (not an `admit`): it asserts the
   equal-likelihood property of the ideal BEC channel, which requires a real-valued
   probability model to formalize.
(a) Double-dual argument over GF(2); ~80 lines.
(b) Residual-system connection via `lem_residual_equivalence`; ~30 lines.
(c) Propagate-commutation inductive argument; ~120 lines.
(d) Uniqueness via `wf_pend` count invariant; ~200 lines.

---

## File structure

```
lean4/
  SELLCert.lean                -- Top-level imports
  SELLCert/
    Basic.lean        -- PCMatrix, ReceivedWord, isCW, isConsistent over ZMod 2
    PeelingState.lean -- PeelingState record, ValidStep, ValidTrace, syndrome_invariant
    Rewriting.lean    -- Atom, Context, encodeState, propagate, solve, WFContext,
                      --   propagate_wf, solve_wf
    Checker.lean      -- checkSuccess, checkFailure pure functions
    Soundness.lean    -- lem_unsat_witness_sound/complete, thm_sound_success/failure,
                      --   bec_equal_likelihood axiom, thm_ml
    Adequacy.lean     -- RewStep, RewStar, extractedTrace,
                      --   adequacy_completeness, adequacy_soundness
  lakefile.lean
```

---

## Remaining admitted steps

### (a) `lem_unsat_witness_complete` — ~80 lines

**Claim**: If `Ax = b` has no solution over GF(2), there exists `ω` with
`ω^T A = 0` and `ω^T b = 1`.

**Proof plan**:
1. Let `C = Submodule.span (ZMod 2) (Set.range Aᵀ)` — column space of `A`.
2. `hno` implies `b ∉ C` (else `b = Ax` for some `x`).
3. By `Subspace.orthogonal_orthogonal` over a finite-dimensional space over a field,
   `(C^⊥)^⊥ = C`. Since `b ∉ C`, the linear map `φ : C^⊥ → ZMod 2, ω ↦ ω^T b`
   is nonzero, so there exists `ω ∈ C^⊥` with `ω^T b = 1`.
4. `ω ∈ C^⊥` means `ω^T A = 0`. ∎

**Key Mathlib lemma**: `Subspace.orthogonal_orthogonal`.

> **Correction to old README**: An earlier version of this file mentioned
> `Subspace.exists_dual_map_eq_bot_of_nmem`. That name was based on a preliminary
> design; the correct lemma in the current Mathlib is `Subspace.orthogonal_orthogonal`.

---

### (b) `thm_sound_failure` — ~30 lines

**Claim**: If `checkFailure H y T ω = true`, no codeword is consistent with `y`.

**Proof plan**: The checker verifies `ω^T H_U = 0` and `ω^T r = 1`. If a consistent
codeword `x` existed, then `H_U x_U = r` (by `lem_residual_equivalence`), giving
`ω^T r = ω^T H_U x_U = 0`, contradicting `ω^T r = 1`.

**Key Mathlib lemmas**: `Finset.sum_congr`, `Finset.sum_add_distrib`.

---

### (c) `adequacy_one_step` (used by `adequacy_completeness`) — ~120 lines

**Claim**: One operational peeling step induces a `RewStar` derivation.

**Proof plan**: Apply `(Propagate)` for each known neighbor of `stp.j` in any order,
then `(Solve)`. Order-independence follows from `Multiset.erase_comm` (two erases on
distinct atoms commute).

> **Correction to old README**: An earlier version mentioned `Finmap.insert_insert_of_ne`.
> The current implementation uses `Multiset` throughout (not `Finmap`), so the relevant
> commutativity lemma is `Multiset.erase_comm`.

---

### (d) `adequacy_soundness` — ~200 lines

**Claim**: Every `RewStar` derivation from the encoded initial state extracts a valid trace.

**Proof plan**: Induction on derivation length, using `wf_pend` to show the only
applicable `(Solve)` step at each point corresponds to a unique valid peeling step,
and `wf_rem` to maintain the `rem(j, ·, ·)` uniqueness invariant.

---

## Building

```bash
cd lean4
lake build
```

Requires Lean 4 and Mathlib4. The `lakefile.lean` specifies the Mathlib revision.
