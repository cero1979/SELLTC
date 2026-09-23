import SELLCert.Rewriting
import SELLCert.Checker

/-! Trace-indexed adequacy for asynchronous SELL-style events. The index is data;
no ordered trace is extracted by eliminating a proof-irrelevant proposition. -/
namespace SELLCert
open scoped BigOperators
variable {n m : ℕ}

inductive RewStep (H : PCMatrix n m) :
    Context n m → List (StepTriple n m) → Context n m → Prop where
  | prop (C : Context n m) (j : Fin m) (i : Fin n) (b : Bit)
      (hp : i ∈ C.pending j) (hk : C.state.K i = some b) :
      RewStep H C [] (propagate C j i)
  | solv (C : Context n m) (stp : StepTriple n m) (he : SolveEnabled H C stp) :
      RewStep H C [stp] (solve H C stp)

inductive RewStar (H : PCMatrix n m) :
    Context n m → List (StepTriple n m) → Context n m → Prop where
  | refl (C : Context n m) : RewStar H C [] C
  | step {C D E : Context n m} {S T : List (StepTriple n m)}
      (hs : RewStep H C S D) (ht : RewStar H D T E) : RewStar H C (S ++ T) E

def extractedTrace {H : PCMatrix n m} {C D : Context n m} {T : List (StepTriple n m)}
    (_h : RewStar H C T D) : List (StepTriple n m) := T

lemma RewStar.trans {H : PCMatrix n m} {C D E : Context n m}
    {S T : List (StepTriple n m)} (h₁ : RewStar H C S D) (h₂ : RewStar H D T E) :
    RewStar H C (S ++ T) E := by
  induction h₁ with
  | refl => exact h₂
  | step hs ht ih => simpa [List.append_assoc] using RewStar.step hs (ih h₂)

/-- Soundness permits every interleaving admitted by the two local rules. -/
theorem rewstar_sound (H : PCMatrix n m) {C D : Context n m}
    {T : List (StepTriple n m)} (hder : RewStar H C T D) (hw : WFContext H C) :
    ValidTrace H C.state T := by
  revert hw
  induction hder with
  | refl C => intro _; exact .nil C.state
  | step hs ht ih =>
      intro hw
      cases hs with
      | prop j i b hp hk =>
          exact ih (propagate_wf H _ j i b hk hw)
      | solv stp he =>
          exact .cons _ stp _ (solve_valid H _ stp hw he) (ih (solve_wf H _ stp hw))

lemma rewstar_wf (H : PCMatrix n m) {C D : Context n m}
    {T : List (StepTriple n m)} (hder : RewStar H C T D) (hw : WFContext H C) :
    WFContext H D := by
  revert hw
  induction hder with
  | refl C => exact fun hw => hw
  | step hs ht ih =>
      intro hw
      cases hs with
      | prop j i b hp hk => exact ih (propagate_wf H _ j i b hk hw)
      | solv stp he => exact ih (solve_wf H _ stp hw)

lemma rewstar_observation (H : PCMatrix n m) {C D : Context n m}
    {T : List (StepTriple n m)} (hder : RewStar H C T D) :
    D.state = foldTrace H C.state T ∧ D.trace = C.trace ++ T := by
  induction hder with
  | refl C => simp [foldTrace]
  | step hs ht ih =>
      cases hs with
      | prop j i b hp hk => simpa [propagate] using ih
      | solv stp he => simpa [solve, foldTrace, List.append_assoc] using ih

def totalPending (C : Context n m) : ℕ := ∑ j, (C.pending j).card

lemma propagate_decreases (C : Context n m) (j : Fin m) (i : Fin n)
    (hp : i ∈ C.pending j) : totalPending (propagate C j i) < totalPending C := by
  apply Finset.sum_lt_sum
  · intro k _
    by_cases hk : k = j
    · subst k; simp [propagate, Finset.card_erase_le]
    · simp [propagate, hk]
  · refine ⟨j, Finset.mem_univ j, ?_⟩
    simpa [propagate] using Finset.card_erase_lt_of_mem hp

/-- Any well-formed asynchronous context normalizes by propagation alone.
The proof descends in the total number of pending incidences. -/
theorem propagation_normalization (H : PCMatrix n m) (C : Context n m)
    (hw : WFContext H C) : RewStar H C [] (encodeLogged H C.state C.trace) := by
  suffices ∀ k (C : Context n m), totalPending C = k → WFContext H C →
      RewStar H C [] (encodeLogged H C.state C.trace) from this _ C rfl hw
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
      intro C he hw
      by_cases hn : C.pending = unknownNbrs H C.state
      · have hc : C = encodeLogged H C.state C.trace := by
          cases C
          simp_all [encodeLogged]
        rw [← hc]
        exact .refl C
      · have hex : ∃ j, C.pending j ≠ unknownNbrs H C.state j := by
          by_contra h
          push_neg at h
          exact hn (funext h)
        obtain ⟨j, hj⟩ := hex
        have hss : unknownNbrs H C.state j ⊂ C.pending j :=
          Finset.ssubset_iff_subset_ne.mpr ⟨(hw j).1, Ne.symm hj⟩
        obtain ⟨i, hp, hu⟩ := Finset.exists_of_ssubset hss
        have hk : C.state.K i ≠ none := by
          intro hk
          exact hu (by simp [unknownNbrs, (hw j).2 i hp, hk])
        obtain ⟨b, hb⟩ : ∃ b, C.state.K i = some b := Option.ne_none_iff_exists'.mp hk
        have hd : totalPending (propagate C j i) < k := by
          rw [← he]; exact propagate_decreases C j i hp
        have ht := ih _ hd (propagate C j i) rfl (propagate_wf H C j i b hb hw)
        exact RewStar.step (.prop C j i b hp hb) ht

/-- Corrected one-step adequacy retains its Solve log and propagates every newly
known incidence before comparing with the normalized operational endpoint. -/
theorem adequacy_one_step (H : PCMatrix n m) (σ : PeelingState n m)
    (stp : StepTriple n m) (hv : ValidStep H σ stp) (L : List (StepTriple n m)) :
    RewStar H (encodeLogged H σ L) [stp]
      (encodeLogged H (applyStep H σ stp) (L ++ [stp])) := by
  have he : SolveEnabled H (encodeLogged H σ L) stp := by
    refine ⟨hv.1, valid_unknown H σ stp hv, ?_⟩
    rw [encode_syndrome]
    exact hv.2
  have hn := propagation_normalization H (solve H (encodeLogged H σ L) stp)
    (solve_wf H _ stp (encode_wf H σ L))
  simpa [solve, encodeLogged] using RewStar.step (.solv _ stp he) hn

theorem adequacy_completeness (H : PCMatrix n m) (σ : PeelingState n m)
    (T : List (StepTriple n m)) (hT : ValidTrace H σ T) (L : List (StepTriple n m)) :
    RewStar H (encodeLogged H σ L) T (encodeLogged H (foldTrace H σ T) (L ++ T)) := by
  induction hT generalizing L with
  | nil σ => simpa [foldTrace] using RewStar.refl (H := H) (encodeLogged H σ L)
  | cons σ stp T hv hT ih =>
      have h := (adequacy_one_step H σ stp hv L).trans (ih (L ++ [stp]))
      simpa [foldTrace, List.append_assoc] using h

theorem adequacy_soundness (H : PCMatrix n m) (y : ReceivedWord n)
    {C : Context n m} {T : List (StepTriple n m)}
    (hder : RewStar H (encodeState H (initState H y)) T C) :
    ValidTrace H (initState H y) (extractedTrace hder) :=
  rewstar_sound H hder (encode_wf H _ [])

/-- Both directions refer to the same explicit event trace T. -/
theorem thm_adequacy_complete (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) :
    ValidTrace H (initState H y) T ↔
      ∃ C, RewStar H (encodeState H (initState H y)) T C := by
  constructor
  · intro hT
    exact ⟨_, by simpa [encodeState] using adequacy_completeness H _ T hT []⟩
  · rintro ⟨C, hder⟩
    exact adequacy_soundness H y hder

def Normalized (H : PCMatrix n m) (C : Context n m) : Prop :=
  C.pending = unknownNbrs H C.state

/-- The normalized endpoint of any propagation-only derivation is unique. -/
theorem propagation_normal_form_unique (H : PCMatrix n m) {C D : Context n m}
    (hder : RewStar H C [] D) (hn : Normalized H D) :
    D = encodeLogged H C.state C.trace := by
  obtain ⟨hs, ht⟩ := rewstar_observation H hder
  have hs' : D.state = C.state := by simpa [foldTrace] using hs
  have ht' : D.trace = C.trace := by simpa using ht
  apply Context.ext
  · exact hs'
  · change D.pending = unknownNbrs H C.state
    exact hn.trans (congrArg (unknownNbrs H) hs')
  · exact ht'

/-- Arbitrary propagation orders join at the same canonical normal form. -/
theorem propagation_confluence (H : PCMatrix n m) {C D E : Context n m}
    (hw : WFContext H C) (hd : RewStar H C [] D) (he : RewStar H C [] E) :
    ∃ F, RewStar H D [] F ∧ RewStar H E [] F := by
  refine ⟨encodeLogged H C.state C.trace, ?_, ?_⟩
  · have hn := propagation_normalization H D (rewstar_wf H hd hw)
    obtain ⟨hs, ht⟩ := rewstar_observation H hd
    simpa [foldTrace, hs, ht] using hn
  · have hn := propagation_normalization H E (rewstar_wf H he hw)
    obtain ⟨hs, ht⟩ := rewstar_observation H he
    simpa [foldTrace, hs, ht] using hn

end SELLCert
