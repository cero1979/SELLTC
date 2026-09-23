import SELLCert.PeelingState

/-! Canonical asynchronous contexts. K is functional and Q is a finite set for each
check, so each value/status/pending incidence has exact multiplicity. The rem degree
and syndrome are derived. `trace` is the external chronological event observer;
its multiset image corresponds to the unordered step atoms of the manuscript.
This is a SELL-style event semantics, not a formal SELL sequent calculus. -/
namespace SELLCert
open scoped BigOperators
variable {n m : ℕ}

@[ext] structure Context (n m : ℕ) where
  state : PeelingState n m
  pending : Fin m → Finset (Fin n)
  trace : List (StepTriple n m)

def encodeLogged (H : PCMatrix n m) (σ : PeelingState n m)
    (T : List (StepTriple n m)) : Context n m := ⟨σ, unknownNbrs H σ, T⟩

def encodeState (H : PCMatrix n m) (σ : PeelingState n m) : Context n m :=
  encodeLogged H σ []

def pendingSyndrome (H : PCMatrix n m) (C : Context n m) (j : Fin m) : Bit :=
  ∑ i, if i ∈ C.pending j then 0 else H j i * (C.state.K i).getD 0

/-- Every unknown incidence is pending; all pending incidences are graph edges.
Known incidences may still be pending: this is essential for arbitrary interleaving. -/
def WFContext (H : PCMatrix n m) (C : Context n m) : Prop :=
  ∀ j, unknownNbrs H C.state j ⊆ C.pending j ∧
    ∀ i ∈ C.pending j, H j i ≠ 0

lemma encode_wf (H : PCMatrix n m) (σ : PeelingState n m) (T : List (StepTriple n m)) :
    WFContext H (encodeLogged H σ T) := by
  intro j
  refine ⟨fun _ h => h, ?_⟩
  intro i hi
  exact (Finset.mem_filter.mp hi).2.1

def propagate (C : Context n m) (j : Fin m) (i : Fin n) : Context n m :=
  { C with pending := Function.update C.pending j ((C.pending j).erase i) }

def solve (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m) : Context n m :=
  ⟨applyStep H C.state stp,
   Function.update C.pending stp.j ((C.pending stp.j).erase stp.i), C.trace ++ [stp]⟩

def SolveEnabled (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m) : Prop :=
  C.pending stp.j = {stp.i} ∧ C.state.K stp.i = none ∧ stp.b = pendingSyndrome H C stp.j

lemma unknown_applyStep (H : PCMatrix n m) (σ : PeelingState n m)
    (stp : StepTriple n m) (j : Fin m) :
    unknownNbrs H (applyStep H σ stp) j = (unknownNbrs H σ j).erase stp.i := by
  ext i
  by_cases hi : i = stp.i
  · subst i; simp [unknownNbrs, applyStep]
  · simp [unknownNbrs, applyStep, hi, hi]

lemma pending_singleton_syndrome (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m)
    (hq : C.pending stp.j = {stp.i}) (hk : C.state.K stp.i = none) :
    pendingSyndrome H C stp.j = syndrome H C.state stp.j := by
  apply Finset.sum_congr rfl
  intro i _
  by_cases hi : i = stp.i
  · subst i; simp [hq, hk]
  · simp [hq, hi]

lemma solve_valid (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m)
    (hw : WFContext H C) (he : SolveEnabled H C stp) : ValidStep H C.state stp := by
  refine ⟨Finset.Subset.antisymm ?_ ?_, he.2.2.trans (pending_singleton_syndrome H C stp he.1 he.2.1)⟩
  · simpa [he.1] using (hw stp.j).1
  · rw [Finset.singleton_subset_iff]
    have hm : stp.i ∈ C.pending stp.j := by rw [he.1]; simp
    simp [unknownNbrs, (hw stp.j).2 stp.i hm, he.2.1]

lemma propagate_wf (H : PCMatrix n m) (C : Context n m) (j : Fin m) (i : Fin n)
    (b : Bit) (hk : C.state.K i = some b) (hw : WFContext H C) :
    WFContext H (propagate C j i) := by
  intro j'
  by_cases hj : j' = j
  · subst j'
    simp only [propagate, Function.update_same]
    constructor
    · intro k hku
      apply Finset.mem_erase.mpr
      refine ⟨?_, (hw j).1 hku⟩
      intro heq
      subst k
      have hn := (Finset.mem_filter.mp hku).2.2
      rw [hk] at hn
      contradiction
    · intro k hkp
      exact (hw j).2 k (Finset.mem_of_mem_erase hkp)
  · simpa [propagate, hj] using hw j'

lemma solve_wf (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m)
    (hw : WFContext H C) : WFContext H (solve H C stp) := by
  intro j
  constructor
  · intro i hi
    change i ∈ unknownNbrs H (applyStep H C.state stp) j at hi
    rw [unknown_applyStep] at hi
    obtain ⟨hne, hold⟩ := Finset.mem_erase.mp hi
    by_cases hj : j = stp.j
    · subst j
      simp only [solve, Function.update_same]
      exact Finset.mem_erase.mpr ⟨hne, (hw stp.j).1 hold⟩
    · simpa [solve, hj] using (hw j).1 hold
  · intro i hi
    by_cases hj : j = stp.j
    · subst j
      simp only [solve, Function.update_same] at hi
      exact (hw stp.j).2 i (Finset.mem_of_mem_erase hi)
    · apply (hw j).2 i
      simpa [solve, hj] using hi

/-- Derived rem fields perform the specified XOR update on Propagate. -/
lemma propagate_syndrome (H : PCMatrix n m) (C : Context n m) (j : Fin m) (i : Fin n)
    (b : Bit) (hp : i ∈ C.pending j) (hk : C.state.K i = some b) (hw : WFContext H C) :
    pendingSyndrome H (propagate C j i) j = pendingSyndrome H C j + b := by
  have he : H j i = 1 := bit_eq_one _ ((hw j).2 i hp)
  calc
    pendingSyndrome H (propagate C j i) j =
        ∑ k, ((if k ∈ C.pending j then 0 else H j k * (C.state.K k).getD 0) +
          if k = i then b else 0) := by
      apply Finset.sum_congr rfl
      intro k _
      by_cases hki : k = i
      · subst k; simp [propagate, hp, hk, he]
      · simp [propagate, hki]
    _ = pendingSyndrome H C j + b := by rw [Finset.sum_add_distrib]; simp [pendingSyndrome]

/-- Canonical normalized contexts have the operational syndrome at every check. -/
lemma encode_syndrome (H : PCMatrix n m) (σ : PeelingState n m)
    (T : List (StepTriple n m)) (j : Fin m) :
    pendingSyndrome H (encodeLogged H σ T) j = syndrome H σ j := by
  apply Finset.sum_congr rfl
  intro i _
  by_cases hi : σ.K i = none
  · simp [encodeLogged, unknownNbrs, hi]
  · simp [encodeLogged, unknownNbrs, hi]

/-- Erasing distinct or identical pending incidences commutes as a state update. -/
lemma propagate_commute (C : Context n m) (j k : Fin m) (i l : Fin n) :
    propagate (propagate C j i) k l = propagate (propagate C k l) j i := by
  apply Context.ext
  · rfl
  · funext r
    by_cases hj : r = j <;> by_cases hk : r = k
    · subst j; subst k; simp [propagate, Finset.erase_right_comm]
    · subst j; simp [propagate, hk, Ne.symm hk]
    · subst k; simp [propagate, hj, Ne.symm hj]
    · simp [propagate, hj, hk]
  · rfl

/-- Solve's selected rem becomes (0,0), as in the raw token rule. -/
lemma solve_selected_syndrome (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m)
    (hw : WFContext H C) (he : SolveEnabled H C stp) :
    pendingSyndrome H (solve H C stp) stp.j = 0 := by
  have hv := solve_valid H C stp hw he
  have hp : pendingSyndrome H (solve H C stp) stp.j =
      syndrome H (applyStep H C.state stp) stp.j := by
    simp [pendingSyndrome, solve, he.1, syndrome]
  rw [hp, applyStep_syndrome_update H C.state stp he.2.1,
    valid_edge H C.state stp hv, one_mul, ← hv.2, add_self_zmod2]

/-- Solve leaves every other rem syndrome unchanged until its pending value propagates. -/
lemma solve_other_syndrome (H : PCMatrix n m) (C : Context n m) (stp : StepTriple n m)
    (j : Fin m) (hj : j ≠ stp.j) (hw : WFContext H C) (he : SolveEnabled H C stp) :
    pendingSyndrome H (solve H C stp) j = pendingSyndrome H C j := by
  apply Finset.sum_congr rfl
  intro i _
  by_cases hi : i = stp.i
  · subst i
    by_cases hedge : H j stp.i = 0
    · simp [solve, hj, hedge]
    · have hp : stp.i ∈ C.pending j := (hw j).1 (by
        simp [unknownNbrs, hedge, he.2.1])
      simp [solve, hj, hp]
  · simp [solve, hj, applyStep, hi]

lemma applyStep_degree_update (H : PCMatrix n m) (σ : PeelingState n m)
    (stp : StepTriple n m) (hk : σ.K stp.i = none) (j : Fin m) :
    degree H (applyStep H σ stp) j = degree H σ j - (if H j stp.i ≠ 0 then 1 else 0) := by
  unfold degree
  rw [unknown_applyStep]
  by_cases he : H j stp.i = 0
  · have hn : stp.i ∉ unknownNbrs H σ j := by simp [unknownNbrs, he]
    simp [he, Finset.erase_eq_of_not_mem hn]
  · have hm : stp.i ∈ unknownNbrs H σ j := by simp [unknownNbrs, he, hk]
    simp [he, Finset.card_erase_of_mem hm]

end SELLCert
