/-!
# SELLCert.Basic

GF(2) arithmetic, Tanner graphs, and the fundamental codeword/consistency predicates.
We represent GF(2) as `ZMod 2` and use Mathlib's `Matrix` and `dotProduct` infrastructure.
-/

import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.DotProduct
import Mathlib.Algebra.BigOperators.Group.Finset

namespace SELLCert

open scoped Matrix BigOperators

variable {n m : ℕ}

/-! ### GF(2) arithmetic -/

/-- In GF(2), every element is its own additive inverse: x + x = 0. -/
@[simp]
lemma add_self_zmod2 (x : ZMod 2) : x + x = 0 := by decide

/-- In GF(2), 1 ≠ 0. -/
lemma one_ne_zero_zmod2 : (1 : ZMod 2) ≠ 0 := one_ne_zero

/-! ### Tanner graphs -/

/-- A parity-check matrix over GF(2). H j i = 1 iff check j is adjacent to variable i. -/
abbrev PCMatrix (n m : ℕ) := Matrix (Fin m) (Fin n) (ZMod 2)

/-- Received word on the BEC. `none` marks an erasure; `some b` is a known bit. -/
abbrev ReceivedWord (n : ℕ) := Fin n → Option (ZMod 2)

/-! ### Codeword conditions -/

/-- The j-th parity check: ∑ᵢ Hⱼᵢ · xᵢ over GF(2). -/
def parityBit (H : PCMatrix n m) (x : Fin n → ZMod 2) (j : Fin m) : ZMod 2 :=
  Matrix.dotProduct (H j) x

/-- x is a codeword: every parity check passes. -/
def isCW (H : PCMatrix n m) (x : Fin n → ZMod 2) : Prop :=
  H.mulVec x = 0

/-- x is consistent with the non-erased positions of y. -/
def isConsistent (y : ReceivedWord n) (x : Fin n → ZMod 2) : Prop :=
  ∀ (i : Fin n) (b : ZMod 2), y i = some b → x i = b

/-- `isCW` stated check-by-check via `parityBit`. -/
lemma isCW_iff_parityBit (H : PCMatrix n m) (x : Fin n → ZMod 2) :
    isCW H x ↔ ∀ j : Fin m, parityBit H x j = 0 := by
  simp [isCW, parityBit, Matrix.mulVec, Matrix.dotProduct, funext_iff]

/-- Helper: dot product of zero vector is zero. -/
@[simp]
lemma dotProduct_zero_left {α : Type*} [NonUnitalNonAssocSemiring α] [Fintype m]
    (v : Fin m → α) : Matrix.dotProduct 0 v = 0 := by
  simp [Matrix.dotProduct]

end SELLCert
