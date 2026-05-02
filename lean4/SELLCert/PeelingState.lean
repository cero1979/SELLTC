/-!
# SELLCert.PeelingState

Operational peeling decoder state, valid steps, peeling traces, and the
`syndrome_invariant` lemma (Lemma 4.9 in the paper: the `s` component always
equals the XOR of known-neighbor values).
-/

import SELLCert.Basic

namespace SELLCert

open scoped BigOperators

variable {n m : ℕ}

/-! ### State record -/

/-- The operational state of the peeling decoder. -/
structure PeelingState (n m : ℕ) where
  /-- Partial assignment: `K i = some b` means variable `i` has been decoded to `b`. -/
  K : Fin n → Option (ZMod 2)
  /-- Residual syndrome: `s j` = XOR of known-neighbor values of check `j`. -/
  s : Fin m → ZMod 2
  /-- Residual degree: `d j` = number of unresolved neighbors of check `j`. -/
  d : Fin m → ℕ

/-- A peeling step triple (j, i, b): check `j` forces variable `i` to value `b`. -/
structure StepTriple (n m : ℕ) where
  j : Fin m
  i : Fin n
  b : ZMod 2
  deriving DecidableEq

/-! ### Initialization -/

/-- Initialize the peeling state from received word `y` and parity-check matrix `H`. -/
def initState (H : PCMatrix n m) (y : ReceivedWord n) : PeelingState n m where
  K := y
  -- s₀(j) = ∑ᵢ H[j,i] · known_val(i), where unknown positions contribute 0
  s := fun j => ∑ i : Fin n, H j i * (y i).getD 0
  -- d₀(j) = |{i : H[j,i] ≠ 0 ∧ y i = none}|
  d := fun j => (Finset.univ.filter (fun i : Fin n => H j i ≠ 0 ∧ y i = none)).card

/-! ### Single step -/

/-- Apply one peeling step `stp` to state `σ`. No validity check here. -/
def applyStep (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) :
    PeelingState n m where
  K := fun i' => if i' = stp.i then some stp.b else σ.K i'
  s := fun j' => if H j' stp.i ≠ 0 then σ.s j' + stp.b else σ.s j'
  d := fun j' => if H j' stp.i ≠ 0 then σ.d j' - 1     else σ.d j'

/-- Logical predicate: `stp` is a valid peeling step in state `σ` under graph `H`. -/
def ValidStep (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) : Prop :=
  -- check j has exactly one unknown neighbor
  σ.d stp.j = 1 ∧
  -- variable i is currently unknown
  σ.K stp.i = none ∧
  -- i is the unique unknown neighbor of j
  (∀ i' : Fin n, H stp.j i' ≠ 0 → σ.K i' = none → i' = stp.i) ∧
  -- b equals the residual syndrome of j
  stp.b = σ.s stp.j

/-! ### Traces -/

/-- A list of triples forms a valid peeling trace starting from state `σ`. -/
inductive ValidTrace (H : PCMatrix n m) : PeelingState n m → List (StepTriple n m) → Prop where
  | nil  : ∀ σ, ValidTrace H σ []
  | cons : ∀ σ stp T,
      ValidStep H σ stp →
      ValidTrace H (applyStep H σ stp) T →
      ValidTrace H σ (stp :: T)

/-- Fold a trace over a starting state (unchecked). -/
def foldTrace (H : PCMatrix n m) (σ : PeelingState n m) (T : List (StepTriple n m)) :
    PeelingState n m :=
  T.foldl (applyStep H) σ

/-! ### Key invariant -/

/-- **Syndrome invariant** (Lemma 4.9 in paper):
For any state `σ` that satisfies the syndrome invariant, after applying any valid
peeling step the invariant is preserved.
The invariant is: `σ.s j = ∑ i, H j i * (σ.K i).getD 0` for all `j`. -/
def SyndromeInv (H : PCMatrix n m) (σ : PeelingState n m) : Prop :=
  ∀ j : Fin m, σ.s j = ∑ i : Fin n, H j i * (σ.K i).getD 0

/-- The initial state satisfies the syndrome invariant. -/
lemma initState_syndrome_inv (H : PCMatrix n m) (y : ReceivedWord n) :
    SyndromeInv H (initState H y) := by
  intro j
  simp [initState, SyndromeInv]

/-- A single valid step preserves the syndrome invariant. -/
lemma applyStep_syndrome_inv (H : PCMatrix n m) (σ : PeelingState n m)
    (stp : StepTriple n m) (hv : ValidStep H σ stp) (hinv : SyndromeInv H σ) :
    SyndromeInv H (applyStep H σ stp) := by
  intro j
  simp only [applyStep, SyndromeInv] at *
  -- The new K' satisfies: K' stp.i = some stp.b, K' i' = K i' for i' ≠ stp.i
  -- The new s'(j) = if H j stp.i ≠ 0 then σ.s j + stp.b else σ.s j
  -- We need: s'(j) = ∑ i, H j i * (K' i).getD 0
  -- Key facts from hv:
  have hKi : σ.K stp.i = none := hv.2.1
  -- ∑ i, H j i * (K' i).getD 0
  --   = ∑ i, H j i * (if i = stp.i then stp.b else (K i).getD 0)
  --   = H j stp.i * stp.b + ∑ i ≠ stp.i, H j i * (K i).getD 0
  -- Since (K stp.i).getD 0 = 0  (because K stp.i = none):
  --   = H j stp.i * stp.b + ∑ i, H j i * (K i).getD 0
  --   = H j stp.i * stp.b + σ.s j  (by IH = hinv j)
  -- The lhs (by definition of applyStep.s):
  --   = if H j stp.i ≠ 0 then σ.s j + stp.b else σ.s j
  -- Case H j stp.i = 0: both sides equal σ.s j ✓
  -- Case H j stp.i ≠ 0: lhs = σ.s j + stp.b,
  --   rhs = H j stp.i * stp.b + σ.s j = 1 * stp.b + σ.s j = stp.b + σ.s j ✓
  conv_rhs =>
    rw [show (fun i : Fin n => H j i * (if i = stp.i then some stp.b else σ.K i).getD 0)
          = (fun i => H j i * (if i = stp.i then stp.b else (σ.K i).getD 0)) from by
        ext i; simp [Option.getD]; split_ifs <;> simp]
  rw [show ∑ i : Fin n, H j i * (if i = stp.i then stp.b else (σ.K i).getD 0)
        = H j stp.i * stp.b + ∑ i : Fin n, H j i * (σ.K i).getD 0 from by
      rw [← Finset.add_sum_erase _ _ (Finset.mem_univ stp.i)]
      simp only [if_true, Finset.mem_erase, ne_eq]
      congr 1
      · simp
      · apply Finset.sum_congr rfl
        intro i hi
        simp [Finset.mem_erase] at hi
        simp [hi.1]]
  rw [← hinv j, show (σ.K stp.i).getD 0 = 0 from by simp [hKi]]
  simp only [mul_zero, Finset.sum_const_zero, add_zero] at *
  split_ifs with h
  · ring
  · -- H j stp.i = 0
    have : H j stp.i = 0 := by
      by_contra hc
      exact h hc
    simp [this]

/-- **Lemma 4.9**: the syndrome invariant holds for any reachable state. -/
theorem syndrome_invariant (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (hT : ValidTrace H (initState H y) T) :
    SyndromeInv H (foldTrace H (initState H y) T) := by
  induction T with
  | nil => exact initState_syndrome_inv H y
  | cons stp T ih =>
    simp only [foldTrace, List.foldl]
    cases hT with
    | cons σ stp' T' hv hT' =>
      apply ih
      · exact hT'

end SELLCert
