import SELLCert.Basic

/-! Canonical operational states. Syndrome and degree are computed from K, rather
than separately cached fields. This avoids admitting inconsistent arbitrary states;
it does not certify the cached arrays of an independently optimized implementation. -/
namespace SELLCert
open scoped BigOperators
variable {n m : ℕ}

structure PeelingState (n m : ℕ) where
  K : ReceivedWord n

structure StepTriple (n m : ℕ) where
  j : Fin m
  i : Fin n
  b : Bit
  deriving DecidableEq

def unknownNbrs (H : PCMatrix n m) (σ : PeelingState n m) (j : Fin m) : Finset (Fin n) :=
  Finset.univ.filter (fun i => H j i ≠ 0 ∧ σ.K i = none)

def syndrome (H : PCMatrix n m) (σ : PeelingState n m) (j : Fin m) : Bit :=
  ∑ i, H j i * (σ.K i).getD 0

def degree (H : PCMatrix n m) (σ : PeelingState n m) (j : Fin m) : ℕ :=
  (unknownNbrs H σ j).card

def initState (_H : PCMatrix n m) (y : ReceivedWord n) : PeelingState n m := ⟨y⟩

def applyStep (_H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) :
    PeelingState n m := ⟨Function.update σ.K stp.i (some stp.b)⟩

def ValidStep (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) : Prop :=
  unknownNbrs H σ stp.j = {stp.i} ∧ stp.b = syndrome H σ stp.j

instance (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) :
    Decidable (ValidStep H σ stp) := by unfold ValidStep; infer_instance

lemma valid_unknown (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m)
    (hv : ValidStep H σ stp) : σ.K stp.i = none := by
  have hm : stp.i ∈ unknownNbrs H σ stp.j := by rw [hv.1]; simp
  exact (Finset.mem_filter.mp hm).2.2

lemma valid_edge (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m)
    (hv : ValidStep H σ stp) : H stp.j stp.i = 1 := by
  have hm : stp.i ∈ unknownNbrs H σ stp.j := by rw [hv.1]; simp
  exact bit_eq_one _ (Finset.mem_filter.mp hm).2.1

inductive ValidTrace (H : PCMatrix n m) : PeelingState n m → List (StepTriple n m) → Prop where
  | nil : ∀ σ, ValidTrace H σ []
  | cons : ∀ σ stp T, ValidStep H σ stp → ValidTrace H (applyStep H σ stp) T →
      ValidTrace H σ (stp :: T)

def foldTrace (H : PCMatrix n m) (σ : PeelingState n m) (T : List (StepTriple n m)) :
    PeelingState n m := T.foldl (applyStep H) σ

/-- Every known assignment agrees with the candidate x. -/
def Extends (σ : PeelingState n m) (x : Fin n → Bit) : Prop :=
  ∀ i b, σ.K i = some b → x i = b

/-- Known and unknown contributions partition each parity equation. -/
lemma row_decomposition (H : PCMatrix n m) (σ : PeelingState n m) (x : Fin n → Bit)
    (hx : Extends σ x) (j : Fin m) :
    parityBit H x j = syndrome H σ j +
      ∑ i, H j i * (if σ.K i = none then x i else 0) := by
  rw [syndrome, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  cases h : σ.K i with
  | none => simp [h]
  | some b => simp [h, hx i b h]

lemma forced_value (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m)
    (hv : ValidStep H σ stp) (x : Fin n → Bit) (hcw : isCW H x)
    (hx : Extends σ x) : x stp.i = stp.b := by
  have hrow := row_decomposition H σ x hx stp.j
  have hsum : (∑ i, H stp.j i * (if σ.K i = none then x i else 0)) = x stp.i := by
    rw [Finset.sum_eq_single stp.i]
    · simp [valid_unknown H σ stp hv, valid_edge H σ stp hv]
    · intro i _ hi
      by_cases he : H stp.j i = 0
      · simp [he]
      · have hn : σ.K i ≠ none := by
          intro hk
          have hm : i ∈ unknownNbrs H σ stp.j := by simp [unknownNbrs, he, hk]
          rw [hv.1] at hm
          exact hi (Finset.mem_singleton.mp hm)
        simp [hn]
    · simp
  rw [hsum, (isCW_iff_parityBit H x).mp hcw stp.j] at hrow
  exact (bit_add_eq_zero _ _ hrow.symm).symm.trans hv.2.symm

lemma applyStep_extends (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m)
    (hv : ValidStep H σ stp) (x : Fin n → Bit) (hcw : isCW H x)
    (hx : Extends σ x) : Extends (applyStep H σ stp) x := by
  intro i b hb
  by_cases hi : i = stp.i
  · subst i
    simp [applyStep] at hb
    subst b
    exact forced_value H σ stp hv x hcw hx
  · exact hx i b (by simpa [applyStep, hi] using hb)

lemma trace_extends (H : PCMatrix n m) (σ : PeelingState n m)
    (T : List (StepTriple n m)) (hT : ValidTrace H σ T)
    (x : Fin n → Bit) (hcw : isCW H x) (hx : Extends σ x) :
    Extends (foldTrace H σ T) x := by
  induction hT with
  | nil σ => exact hx
  | cons σ stp T hv hT ih =>
      exact ih (applyStep_extends H σ stp hv x hcw hx)

/-- The canonical syndrome agrees with the incremental XOR update on every row. -/
lemma applyStep_syndrome_update (H : PCMatrix n m) (σ : PeelingState n m)
    (stp : StepTriple n m) (hk : σ.K stp.i = none) (j : Fin m) :
    syndrome H (applyStep H σ stp) j = syndrome H σ j + H j stp.i * stp.b := by
  calc
    syndrome H (applyStep H σ stp) j =
        ∑ k, (H j k * (σ.K k).getD 0 + if k = stp.i then H j stp.i * stp.b else 0) := by
      apply Finset.sum_congr rfl
      intro k _
      by_cases hki : k = stp.i
      · subst k; simp [applyStep, hk]
      · simp [applyStep, hki]
    _ = syndrome H σ j + H j stp.i * stp.b := by
      rw [Finset.sum_add_distrib]
      simp [syndrome]

end SELLCert
