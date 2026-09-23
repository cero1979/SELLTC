import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.DotProduct
import Mathlib.Tactic

/-! Finite binary linear algebra. All channel and code predicates are explicit. -/
namespace SELLCert
open scoped BigOperators Matrix
variable {n m : ℕ}

abbrev Bit := ZMod 2
abbrev PCMatrix (n m : ℕ) := Matrix (Fin m) (Fin n) Bit
abbrev ReceivedWord (n : ℕ) := Fin n → Option Bit

@[simp] lemma add_self_zmod2 (x : Bit) : x + x = 0 := by
  have h : ∀ x : Bit, x + x = 0 := by decide
  exact h x

lemma bit_eq_one (x : Bit) (hx : x ≠ 0) : x = 1 := by
  have h : ∀ x : Bit, x = 0 ∨ x = 1 := by decide
  exact (h x).resolve_left hx

lemma bit_add_eq_zero (a b : Bit) (h : a + b = 0) : a = b := by
  have h' := congrArg (fun z : Bit => z + b) h
  simpa [add_assoc] using h'

def parityBit (H : PCMatrix n m) (x : Fin n → Bit) (j : Fin m) : Bit :=
  ∑ i, H j i * x i

def isCW (H : PCMatrix n m) (x : Fin n → Bit) : Prop := H.mulVec x = 0

def isConsistent (y : ReceivedWord n) (x : Fin n → Bit) : Prop :=
  ∀ i b, y i = some b → x i = b

lemma isCW_iff_parityBit (H : PCMatrix n m) (x : Fin n → Bit) :
    isCW H x ↔ ∀ j, parityBit H x j = 0 := by
  simp [isCW, parityBit, Matrix.mulVec, Matrix.dotProduct, funext_iff]

instance (y : ReceivedWord n) (x : Fin n → Bit) : Decidable (isConsistent y x) :=
  inferInstanceAs (Decidable (∀ i b, y i = some b → x i = b))

end SELLCert
