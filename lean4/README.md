# Lean 4 Mechanization Plan

This directory will contain a Lean 4 formalization of the main results from the paper
*Certified Hybrid Decoding of Binary LDPC Codes over the BEC via Subexponential Linear Logic*.

No Lean code has been written yet. This document records the formalization plan
so that progress can be tracked and contributions can be coordinated.

---

## Target theorems

| Label in paper | Description | Estimated effort |
|---|---|---|
| `thm:adequacy-complete` | Full adequacy of the SELL-style specification | 400–800 lines |
| `thm:sound` | Soundness of success certificates | 100–200 lines |
| `lem:unsat-witness-sound` | Soundness of failure certificates | 50–100 lines |
| `lem:unsat-witness-complete` | Completeness of failure certificates | 100–200 lines |

---

## Planned file structure

```
lean4/
  SELLCert.lean           -- Top-level imports and module summary
  PeelingState.lean       -- PeelingState record, WFMultiset, Step inductive
  Rewriting.lean          -- Propagate/Solve rules, ReflTransClosure, WF preservation
  Checker.lean            -- check_success / check_failure pure functions
  Soundness.lean          -- Theorems thm:sound, lem:unsat-witness-sound/complete
  Adequacy.lean           -- Theorem thm:adequacy-complete (completeness + soundness)
  lakefile.lean           -- Lake build file
```

---

## Core type encodings

### `PeelingState`
```lean
structure PeelingState where
  K    : Finmap (Fin n) (Fin 2)   -- partial assignment of erased positions
  s    : Fin n → Fin 2            -- received word (known positions)
  deg  : Fin m → ℕ               -- current degree of each check node
```

### `Atom`
Three atom kinds appear in the SELL multiset:
```lean
inductive Atom (n m : ℕ) where
  | Edge  : Fin n → Fin m → Atom n m    -- !^G: static edge
  | Known : Fin n → Fin 2 → Atom n m    -- !^K: known assignment
  | Check : Fin m → List (Fin n) → Atom n m  -- linear residual check (one-use)
```

### `WFMultiset`
```lean
structure WF (M : Multiset (Atom n m)) : Prop where
  wf1 : ...   -- each variable appears in at most one Known atom
  wf2 : ...   -- each Check atom's variable list is a subset of unknown variables
  wf3 : ...   -- Edge atoms are consistent with the Tanner graph H
```

### `Step`
```lean
inductive Step : Multiset (Atom n m) → Multiset (Atom n m) → Prop where
  | propagate : ...   -- fires when a check has degree one
  | solve     : ...   -- fires when all checks are resolved
```

---

## Adequacy proof plan

**Completeness** (`peeling_trace → derivation`):
- Induction on `|T|` (length of trace).
- Each step: show that the peeling step for variable `v` corresponds to
  one `Step.propagate` application followed by zero or more `Step.propagate`
  applications on neighboring checks.
- Key lemma: `propagate_commutes` — two `Step.propagate` applications on
  disjoint checks commute (proved by `Finmap.disjoint_update`).

**Soundness** (`derivation → peeling_trace`):
- Induction on `ReflTransClosure Step`.
- Base case: empty derivation = empty trace.
- Inductive step: peel off the first `Step.solve` (find it using
  `exists_solve_step`), identify the corresponding operational step,
  apply IH to the suffix.

---

## Mathlib dependencies

All of the following are already in Mathlib 4:

| Concept | Mathlib location |
|---|---|
| Finmap (partial maps) | `Mathlib.Data.Finmap` |
| Multiset operations | `Mathlib.Data.Multiset.Basic` |
| GF(2) arithmetic | `Mathlib.Algebra.Field.Basic` + `ZMod 2` |
| Sparse matrices over GF(2) | `Mathlib.LinearAlgebra.Matrix.DotProduct` |
| Finite-dim Hahn–Banach over finite field | `Mathlib.LinearAlgebra.Dual` |
| Reflexive-transitive closure | `Mathlib.Order.RelClasses` |

---

## Getting started with Lean 4

1. Install `elan` (the Lean version manager):
   ```bash
   curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
   ```
2. From the `lean4/` directory, run:
   ```bash
   lake update
   lake build
   ```
   The `lakefile.lean` (to be written) will declare the Mathlib dependency.

---

## Open questions

- The commutation lemma for `Step.propagate` is the most delicate part. The
  argument requires showing that two `Finmap.insert` operations on disjoint
  keys produce the same result regardless of order. This should follow from
  `Finmap.insert_insert_of_ne`.
- `lem:unsat-witness-complete` (completeness of failure certificates) uses
  the finite-dimensional Farkas lemma over GF(2). The precise Mathlib lemma
  to use is `Subspace.exists_dual_map_eq_bot_of_nmem`; confirm this is
  available in the target Mathlib version.
