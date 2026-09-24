import SELLCert.Checker
import Mathlib.LinearAlgebra.Dual
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Data.Real.Basic

namespace SELLCert
open scoped BigOperators Matrix
variable {n m : ℕ}

def innerProd (ω b : Fin m → Bit) : Bit := Matrix.dotProduct ω b

lemma inner_mulVec (ω : Fin m → Bit) (A : PCMatrix n m) (x : Fin n → Bit) :
    innerProd ω (A.mulVec x) = innerProd (Matrix.vecMul ω A) x :=
  Matrix.dotProduct_mulVec ω A x

theorem lem_unsat_witness_sound (A : PCMatrix n m) (b ω : Fin m → Bit)
    (h1 : Matrix.vecMul ω A = 0) (h2 : innerProd ω b = 1) :
    ∀ x : Fin n → Bit, A.mulVec x ≠ b := by
  intro x hx
  have h : innerProd ω b = 0 := by rw [← hx, inner_mulVec, h1]; simp [innerProd]
  rw [h2] at h
  exact one_ne_zero h

/-- Finite-dimensional separation supplies a genuine left-nullspace witness. -/
theorem lem_unsat_witness_complete (A : PCMatrix n m) (b : Fin m → Bit)
    (hno : ∀ x : Fin n → Bit, A.mulVec x ≠ b) :
    ∃ ω : Fin m → Bit, Matrix.vecMul ω A = 0 ∧ innerProd ω b = 1 := by
  classical
  let p : Submodule Bit (Fin m → Bit) := LinearMap.range A.mulVecLin
  have hn : b ∉ p := by
    rintro ⟨x, hx⟩
    exact hno x hx
  obtain ⟨f, hfb, hf⟩ := Submodule.exists_dual_map_eq_bot_of_nmem hn inferInstance
  let ω : Fin m → Bit := fun j => f (fun k => if j = k then 1 else 0)
  have hrep (v : Fin m → Bit) : f v = innerProd ω v := by
    simpa [innerProd, Matrix.dotProduct, ω, smul_eq_mul, mul_comm] using
      LinearMap.pi_apply_eq_sum_univ f v
  have hz (x : Fin n → Bit) : f (A.mulVec x) = 0 := by
    have hm : f (A.mulVec x) ∈ p.map f := ⟨A.mulVec x, ⟨x, rfl⟩, rfl⟩
    rw [hf] at hm
    exact hm
  refine ⟨ω, ?_, bit_eq_one _ (by rw [← hrep]; exact hfb)⟩
  apply Matrix.dotProduct_eq_zero
  intro x
  rw [← Matrix.dotProduct_mulVec]
  change innerProd ω (A.mulVec x) = 0
  rw [← hrep]
  exact hz x

lemma residual_sound (H : PCMatrix n m) (σ : PeelingState n m) (ρ : Fin n → Bit)
    (hp : ResidualParity H σ ρ) : isCW H (assemble σ ρ) := by
  apply (isCW_iff_parityBit H _).mpr
  intro j
  rw [row_decomposition H σ _ (assemble_extends σ ρ)]
  have he : (∑ i, H j i * (if σ.K i = none then assemble σ ρ i else 0)) =
      ∑ i, H j i * (if σ.K i = none then ρ i else 0) := by
    apply Finset.sum_congr rfl
    intro i _
    cases h : σ.K i <;> simp [assemble, h]
  rw [he, hp j, add_self_zmod2]

theorem thm_sound_success (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ρ x : Fin n → Bit)
    (hcheck : checkSuccess H y T ρ = some x) : isCW H x ∧ isConsistent y x := by
  cases hr : replayFull H (initState H y) T with
  | none => simp [checkSuccess, hr] at hcheck
  | some σ =>
      by_cases hp : ResidualParity H σ ρ ∧ isConsistent y (assemble σ ρ)
      · have hx : assemble σ ρ = x := by simpa [checkSuccess, hr, hp] using hcheck
        rw [← hx]
        exact ⟨residual_sound H σ ρ hp.1, hp.2⟩
      · simp [checkSuccess, hr, hp] at hcheck

lemma failure_excludes_extension (H : PCMatrix n m) (σ : PeelingState n m)
    (ω : Fin m → Bit) (hw : FailureWitness H σ ω)
    (x : Fin n → Bit) (hcw : isCW H x) (hx : Extends σ x) : False := by
  have hr (j : Fin m) : syndrome H σ j =
      ∑ i, H j i * (if σ.K i = none then x i else 0) := by
    have he := row_decomposition H σ x hx j
    rw [(isCW_iff_parityBit H x).mp hcw j] at he
    exact bit_add_eq_zero _ _ he.symm
  have hz : (∑ j, ω j * syndrome H σ j) = 0 := by
    calc
      (∑ j, ω j * syndrome H σ j) =
          ∑ i, (∑ j, ω j * H j i) * (if σ.K i = none then x i else 0) := by
        simp_rw [hr, Finset.mul_sum]
        rw [Finset.sum_comm]
        apply Finset.sum_congr rfl
        intro i _
        rw [Finset.sum_mul]
        apply Finset.sum_congr rfl
        intro j _
        ring
      _ = 0 := by
        apply Finset.sum_eq_zero
        intro i _
        by_cases hi : σ.K i = none
        · simp [hi, hw.1 i hi]
        · simp [hi]
  rw [hw.2] at hz
  exact one_ne_zero hz

theorem thm_sound_failure (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ω : Fin m → Bit)
    (hcheck : checkFailure H y T ω = true) :
    ∀ x : Fin n → Bit, ¬ (isCW H x ∧ isConsistent y x) := by
  cases hr : replayFull H (initState H y) T with
  | none => simp [checkFailure, hr] at hcheck
  | some σ =>
      have hw : FailureWitness H σ ω := by simpa [checkFailure, hr] using hcheck
      obtain ⟨hT, hσ⟩ := (replayFull_eq_some_iff H _ _ T).mp hr
      intro x ⟨hcw, hcon⟩
      apply failure_excludes_extension H σ ω hw x hcw
      rw [hσ]
      exact trace_extends H _ T hT x hcw hcon

def residualMatrix (H : PCMatrix n m) (σ : PeelingState n m) : PCMatrix n m :=
  fun j i => if σ.K i = none then H j i else 0

lemma residual_mulVec (H : PCMatrix n m) (σ : PeelingState n m) (ρ : Fin n → Bit)
    (j : Fin m) : (residualMatrix H σ).mulVec ρ j =
      ∑ i, H j i * (if σ.K i = none then ρ i else 0) := by
  simp only [Matrix.mulVec, Matrix.dotProduct]
  apply Finset.sum_congr rfl
  intro i _
  by_cases hi : σ.K i = none <;> simp [residualMatrix, hi]

/-- Full completeness of residual witnesses, including empty and singular systems. -/
theorem residual_unsat_iff_witness (H : PCMatrix n m) (σ : PeelingState n m) :
    (¬ ∃ ρ, ResidualParity H σ ρ) ↔ ∃ ω, FailureWitness H σ ω := by
  constructor
  · intro hno
    have ha : ∀ ρ, (residualMatrix H σ).mulVec ρ ≠ syndrome H σ := by
      intro ρ he
      apply hno
      refine ⟨ρ, ?_⟩
      intro j
      rw [← residual_mulVec H σ ρ j, he]
    obtain ⟨ω, hω, hb⟩ := lem_unsat_witness_complete (residualMatrix H σ) (syndrome H σ) ha
    refine ⟨ω, ?_, hb⟩
    intro i hi
    have hz := congrFun hω i
    simpa [Matrix.vecMul, Matrix.dotProduct, residualMatrix, hi] using hz
  · rintro ⟨ω, hw⟩ ⟨ρ, hp⟩
    exact failure_excludes_extension H σ ω hw (assemble σ ρ)
      (residual_sound H σ ρ hp) (assemble_extends σ ρ)

/-- If no consistent codeword exists, the checker accepts an impossibility
certificate. A valid empty peeling trace suffices; no maximal-peeling premise is needed. -/
theorem thm_complete_failure (H : PCMatrix n m) (y : ReceivedWord n)
    (hno : ¬ ∃ x, isCW H x ∧ isConsistent y x) :
    ∃ ω, checkFailure H y [] ω = true := by
  have hr : ¬ ∃ ρ, ResidualParity H (initState H y) ρ := by
    rintro ⟨ρ, hp⟩
    apply hno
    exact ⟨assemble (initState H y) ρ, residual_sound H _ ρ hp,
      assemble_extends (initState H y) ρ⟩
  obtain ⟨ω, hw⟩ := (residual_unsat_iff_witness H _).mp hr
  exact ⟨ω, by simp [checkFailure, replayFull, hw]⟩

/-- Every compatible codeword is accepted with an empty trace and that completion. -/
theorem thm_complete_success (H : PCMatrix n m) (y : ReceivedWord n)
    (x : Fin n → Bit) (hcw : isCW H x) (hcon : isConsistent y x) :
    checkSuccess H y [] x = some x := by
  have ha : assemble (initState H y) x = x := by
    funext i
    cases hy : y i with
    | none => simp [assemble, initState, hy]
    | some b => simp [assemble, initState, hy, hcon i b hy]
  have hr : ResidualParity H (initState H y) x := by
    intro j
    have he := row_decomposition H (initState H y) x hcon j
    rw [(isCW_iff_parityBit H x).mp hcw j] at he
    exact (bit_add_eq_zero _ _ he.symm).symm
  simp [checkSuccess, replayFull, hr, ha, hcon]

/-- The finite memoryless BEC transition likelihood. It includes inconsistent candidates. -/
def becLikelihood (ε : ℝ) (y : ReceivedWord n) (x : Fin n → Bit) : ℝ :=
  if isConsistent y x then
    ε ^ (Finset.univ.filter (fun i => y i = none)).card *
      (1 - ε) ^ (Finset.univ.filter (fun i => (y i).isSome)).card
  else 0

/-- Maximization holds on the entire closed interval, including zero-probability events. -/
theorem bec_completion_maximizes (ε : ℝ) (hε0 : 0 ≤ ε) (hε1 : ε ≤ 1)
    (y : ReceivedWord n) (x : Fin n → Bit) (hx : isConsistent y x)
    (x' : Fin n → Bit) : becLikelihood ε y x' ≤ becLikelihood ε y x := by
  by_cases hx' : isConsistent y x'
  · simp [becLikelihood, hx, hx']
  · simp only [becLikelihood, if_pos hx, if_neg hx']
    exact mul_nonneg (pow_nonneg hε0 _) (pow_nonneg (sub_nonneg.mpr hε1) _)

theorem thm_ml (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ρ x : Fin n → Bit)
    (hcheck : checkSuccess H y T ρ = some x)
    (ε : ℝ) (hε0 : 0 ≤ ε) (hε1 : ε ≤ 1) :
    isCW H x ∧ isConsistent y x ∧
      ∀ x', isCW H x' → becLikelihood ε y x' ≤ becLikelihood ε y x := by
  obtain ⟨hcw, hcon⟩ := thm_sound_success H y T ρ x hcheck
  exact ⟨hcw, hcon, fun x' _ => bec_completion_maximizes ε hε0 hε1 y x hcon x'⟩

end SELLCert
