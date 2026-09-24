import SELLCert.PeelingState

/-! Executable finite certificate checker. Trace replay recomputes residual data;
there is no assertion that this code has the sparse Python implementation's cost. -/
namespace SELLCert
open scoped BigOperators
variable {n m : ℕ}

def replayStep (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) :
    Option (PeelingState n m) :=
  if ValidStep H σ stp then some (applyStep H σ stp) else none

def replayFull (H : PCMatrix n m) (σ : PeelingState n m) :
    List (StepTriple n m) → Option (PeelingState n m)
  | [] => some σ
  | stp :: T => if ValidStep H σ stp then replayFull H (applyStep H σ stp) T else none

lemma validTrace_cons_iff (H : PCMatrix n m) (σ : PeelingState n m)
    (stp : StepTriple n m) (T : List (StepTriple n m)) :
    ValidTrace H σ (stp :: T) ↔ ValidStep H σ stp ∧ ValidTrace H (applyStep H σ stp) T := by
  constructor
  · intro h; cases h with | cons _ _ _ hv ht => exact ⟨hv, ht⟩
  · rintro ⟨hv, ht⟩; exact .cons σ stp T hv ht

lemma replayFull_eq_some_iff (H : PCMatrix n m) (σ τ : PeelingState n m)
    (T : List (StepTriple n m)) :
    replayFull H σ T = some τ ↔ ValidTrace H σ T ∧ τ = foldTrace H σ T := by
  induction T generalizing σ τ with
  | nil =>
      simp only [replayFull, Option.some.injEq, foldTrace, List.foldl_nil]
      constructor
      · intro h; exact ⟨.nil σ, h.symm⟩
      · exact fun h => h.2.symm
  | cons stp T ih =>
      by_cases hv : ValidStep H σ stp
      · simp [replayFull, hv, ih, validTrace_cons_iff, foldTrace]
      · simp [replayFull, hv, validTrace_cons_iff]

def assemble (σ : PeelingState n m) (ρ : Fin n → Bit) : Fin n → Bit :=
  fun i => (σ.K i).getD (ρ i)

lemma assemble_extends (σ : PeelingState n m) (ρ : Fin n → Bit) :
    Extends σ (assemble σ ρ) := by
  intro i b hb; simp [assemble, hb]

def ResidualParity (H : PCMatrix n m) (σ : PeelingState n m) (ρ : Fin n → Bit) : Prop :=
  ∀ j, (∑ i, H j i * (if σ.K i = none then ρ i else 0)) = syndrome H σ j

instance (H : PCMatrix n m) (σ : PeelingState n m) (ρ : Fin n → Bit) :
    Decidable (ResidualParity H σ ρ) := by unfold ResidualParity; infer_instance

def checkResidualParity (H : PCMatrix n m) (σ : PeelingState n m) (ρ : Fin n → Bit) : Bool :=
  decide (ResidualParity H σ ρ)

def checkChannel (y : ReceivedWord n) (x : Fin n → Bit) : Bool := decide (isConsistent y x)

def checkSuccess (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ρ : Fin n → Bit) : Option (Fin n → Bit) :=
  match replayFull H (initState H y) T with
  | none => none
  | some σ => if ResidualParity H σ ρ ∧ isConsistent y (assemble σ ρ)
      then some (assemble σ ρ) else none

def FailureWitness (H : PCMatrix n m) (σ : PeelingState n m) (ω : Fin m → Bit) : Prop :=
  (∀ i, σ.K i = none → (∑ j, ω j * H j i) = 0) ∧
    (∑ j, ω j * syndrome H σ j) = 1

instance (H : PCMatrix n m) (σ : PeelingState n m) (ω : Fin m → Bit) :
    Decidable (FailureWitness H σ ω) := by unfold FailureWitness; infer_instance

def checkFailure (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ω : Fin m → Bit) : Bool :=
  match replayFull H (initState H y) T with
  | none => false
  | some σ => decide (FailureWitness H σ ω)

end SELLCert
