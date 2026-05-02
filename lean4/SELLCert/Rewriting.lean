/-!
# SELLCert.Rewriting

SELL-style multiset rewriting for phase I (peeling decoding).

We define:
- `Atom n m` — the six atom kinds used in the SELL encoding
- `Context n m` — a tripartite context with !^S, !^K, and linear zones
- `encodeState` — encode a `PeelingState` as a `Context`
- `propagate`, `solve` — the two rewriting rules as context transformers
- `WFContext` — the well-formedness predicate
- `propagate_wf`, `solve_wf` — preservation lemmas (Lemmas 5.3 and 5.4 in paper)

The rewriting rules are:

  **(Propagate)**: !^K val(i,b) ⊗ pend(j,i) ⊗ rem(j,k,p) ⊸ rem(j,k-1,p+b)

  **(Solve)**:     rem(j,1,p) ⊗ pend(j,i) ⊗ unk(i)
                     ⊸ !^K val(i,p) ⊗ step(j,i,p) ⊗ rem(j,0,0)
-/

import SELLCert.PeelingState

namespace SELLCert

variable {n m : ℕ}

/-! ### Atoms -/

/-- The six atom kinds in the SELL encoding. -/
inductive Atom (n m : ℕ) where
  /-- `!^S edge(j,i)` — static Tanner edge (S zone; weakening and contraction available). -/
  | edge  : Fin m → Fin n → Atom n m
  /-- `!^K val(i,b)` — persistent decoded value (K zone; weakening and contraction available). -/
  | known : Fin n → ZMod 2 → Atom n m
  /-- `unk(i)` — variable `i` not yet resolved (linear zone, one-use). -/
  | unk   : Fin n → Atom n m
  /-- `pend(j,i)` — variable `i` is a pending unknown of check `j` (linear zone). -/
  | pend  : Fin m → Fin n → Atom n m
  /-- `rem(j,k,p)` — check `j` has `k` remaining unknowns and residual syndrome `p` (linear zone). -/
  | rem   : Fin m → ℕ → ZMod 2 → Atom n m
  /-- `step(j,i,b)` — log atom recording that variable `i` was resolved to `b` via check `j`. -/
  | step  : Fin m → Fin n → ZMod 2 → Atom n m
  deriving DecidableEq, Repr

/-! ### Context (tripartite) -/

/-- A SELL context with the three zones from the paper. -/
structure Context (n m : ℕ) where
  /-- !^S zone: static Tanner graph (never consumed). -/
  G : PCMatrix n m
  /-- !^K zone: persistent known assignments (can be reused). -/
  P : Multiset (Fin n × ZMod 2)
  /-- Linear zone: one-use atoms (unk, pend, rem, step). -/
  L : Multiset (Atom n m)

/-! ### State encoding -/

/-- Encode a peeling state `σ` as a SELL context under graph `H`. -/
def encodeState (H : PCMatrix n m) (σ : PeelingState n m) : Context n m where
  G := H
  -- K zone: one (i, b) entry for each resolved variable
  P := (Finset.univ.filter (fun i : Fin n => (σ.K i).isSome)).val.map
         (fun i => (i, (σ.K i).getD 0))
  -- Linear zone: unk atoms + rem atoms + pend atoms
  L :=  -- unk(i) for each unknown variable
        (Finset.univ.filter (fun i : Fin n => σ.K i = none)).val.map (Atom.unk) ++
        -- rem(j, d(j), s(j)) for each check
        (Finset.univ : Finset (Fin m)).val.map (fun j => Atom.rem j (σ.d j) (σ.s j)) ++
        -- pend(j, i) for each (j, i) edge where i is still unknown
        ((Finset.univ : Finset (Fin m × Fin n)).filter
           (fun p => H p.1 p.2 ≠ 0 ∧ σ.K p.2 = none)).val.map
          (fun p => Atom.pend p.1 p.2)

/-! ### Rewriting rules -/

/-- **(Propagate)**: consume `pend(j,i)` and `rem(j,k,p)`, produce `rem(j,k-1,p+b)`.
    Preconditions: the atoms are present in the linear zone and `(i,b) ∈ P`. -/
def propagate (ctx : Context n m) (j : Fin m) (i : Fin n) (b : ZMod 2)
    (k : ℕ) (p : ZMod 2) (hk : 0 < k)
    (hpend  : Atom.pend j i ∈ ctx.L)
    (hrem   : Atom.rem j k p ∈ ctx.L)
    (hknown : (i, b) ∈ ctx.P) : Context n m where
  G := ctx.G
  P := ctx.P                            -- K zone: unchanged
  L := (ctx.L.erase (Atom.pend j i)).erase (Atom.rem j k p) |>.cons
         (Atom.rem j (k - 1) (p + b))  -- linear zone: updated

/-- **(Solve)**: consume `rem(j,1,p)`, `pend(j,i)`, `unk(i)`;
    produce `(i,p)` in K zone, `step(j,i,p)` and `rem(j,0,0)` in linear zone. -/
def solve (ctx : Context n m) (j : Fin m) (i : Fin n) (p : ZMod 2)
    (hrem  : Atom.rem j 1 p ∈ ctx.L)
    (hpend : Atom.pend j i ∈ ctx.L)
    (hunk  : Atom.unk i ∈ ctx.L) : Context n m where
  G := ctx.G
  P := ctx.P.cons (i, p)                             -- K zone: add new assignment
  L := ((ctx.L.erase (Atom.rem j 1 p)).erase
           (Atom.pend j i)).erase (Atom.unk i)
         |>.cons (Atom.rem j 0 0)
         |>.cons (Atom.step j i p)

/-! ### Well-formedness -/

/-- Well-formedness of a context: it correctly encodes some peeling state. -/
structure WFContext (H : PCMatrix n m) (ctx : Context n m) : Prop where
  wf_graph : ctx.G = H
  /-- Each check `j` has exactly one `rem(j,·,·)` atom in `L`. -/
  wf_rem   : ∀ j : Fin m, ∃! kp : ℕ × ZMod 2, Atom.rem j kp.1 kp.2 ∈ ctx.L
  /-- Each variable is either `unk` (in L) or `known` (in P), not both. -/
  wf_var   : ∀ i : Fin n, (Atom.unk i ∈ ctx.L) ↔ (∀ b : ZMod 2, (i, b) ∉ ctx.P)
  /-- The number of `pend(j,·)` atoms equals the `k` in `rem(j,k,·)`. -/
  wf_pend  : ∀ j : Fin m, ∀ k p, Atom.rem j k p ∈ ctx.L →
             (ctx.L.filter (fun a => ∃ i, a = Atom.pend j i)).card = k

/-- **Lemma 5.3**: `propagate` preserves well-formedness. -/
theorem propagate_wf (H : PCMatrix n m) (ctx : Context n m)
    (j : Fin m) (i : Fin n) (b : ZMod 2) (k : ℕ) (p : ZMod 2)
    (hk : 0 < k)
    (hpend  : Atom.pend j i ∈ ctx.L)
    (hrem   : Atom.rem j k p ∈ ctx.L)
    (hknown : (i, b) ∈ ctx.P)
    (hwf : WFContext H ctx) :
    WFContext H (propagate ctx j i b k p hk hpend hrem hknown) := by
  constructor
  · -- graph unchanged
    exact hwf.wf_graph
  · -- each check still has a unique rem atom
    intro j'
    by_cases hj : j' = j
    · subst hj
      refine ⟨⟨k - 1, p + b⟩, ?_, ?_⟩
      · simp [propagate, Multiset.mem_cons, Multiset.mem_erase_of_ne]
      · intro ⟨k'', p''⟩ hk''
        -- the old rem(j,k,p) is erased; only rem(j,k-1,p+b) remains for j
        simp only [propagate] at hk''
        simp only [Multiset.mem_cons, Multiset.mem_erase] at hk''
        obtain h | h := hk''
        · exact Prod.mk.inj h
        · have := hwf.wf_rem j
          obtain ⟨⟨k₀, p₀⟩, hmem, huniq⟩ := this
          have heq := huniq ⟨k, p⟩ hrem
          have heq2 := huniq ⟨k'', p''⟩ (by
            rcases h with ⟨hne, hmem'⟩
            exact hmem')
          simp at heq heq2
          omega
    · -- j' ≠ j: rem(j', ·, ·) is unaffected
      have hwfj' := hwf.wf_rem j'
      obtain ⟨⟨k'', p''⟩, hmem, huniq⟩ := hwfj'
      refine ⟨⟨k'', p''⟩, ?_, ?_⟩
      · simp [propagate, Multiset.mem_cons]
        right
        constructor
        · intro heq; exact hj (Atom.rem.inj heq).1
        constructor
        · intro heq; exact hj (Atom.rem.inj heq).1
        · exact hmem
      · intro ⟨k₃, p₃⟩ h3
        simp only [propagate, Multiset.mem_cons, Multiset.mem_erase] at h3
        rcases h3 with h3 | ⟨hne1, hne2, h3⟩
        · have := Atom.rem.inj h3; simp at this; exact absurd this.1 hj
        · exact huniq ⟨k₃, p₃⟩ h3
  · -- var status: unk ↔ not in P — K zone unchanged, L zone: pend/rem changed but not unk
    intro i'
    simp [propagate, WFContext.wf_var]
    constructor
    · intro h b hb
      have := (hwf.wf_var i').mp h
      exact this b (by simpa using hb)
    · intro h
      apply (hwf.wf_var i').mpr
      intro b hb
      exact h b (by simpa using hb)
  · -- pend count matches k in rem — after propagate, pend(j,i) is removed and rem(j,k,p)
    -- becomes rem(j,k-1,p+b), so count for j decreases by 1 ✓
    intro j' k' p' hrem'
    simp only [propagate] at hrem' ⊢
    by_cases hj : j' = j
    · subst hj
      simp only [Multiset.mem_cons, Multiset.mem_erase] at hrem'
      rcases hrem' with h | ⟨_, _, h⟩
      · obtain ⟨rfl, rfl⟩ : k' = k - 1 ∧ p' = p + b := by
          have := Atom.rem.inj h; exact ⟨this.2.1, this.2.2⟩
        have hcount := hwf.wf_pend j k p hrem
        simp [Multiset.filter_erase, Multiset.card_erase_of_mem]
        omega
      · have hcount := hwf.wf_pend j k' p' h
        simp [Multiset.filter_erase, Multiset.card_erase_of_mem]
        omega
    · simp only [Multiset.mem_cons, Multiset.mem_erase] at hrem'
      rcases hrem' with h | ⟨hne1, hne2, h⟩
      · exact absurd (Atom.rem.inj h).1 hj
      · have hcount := hwf.wf_pend j' k' p' h
        simp only [Multiset.filter_cons, Multiset.filter_erase]
        -- pend(j, i) is removed; pend(j', ·) atoms for j' ≠ j are unaffected
        simp [show ∀ i'', (∃ i''', Atom.pend j i'' = Atom.pend j' i''') ↔ j = j' from by
          intro i''; simp [Atom.pend.injEq]; tauto]
        simp [hj, hcount]

/-- **Lemma 5.4**: `solve` preserves well-formedness. -/
theorem solve_wf (H : PCMatrix n m) (ctx : Context n m)
    (j : Fin m) (i : Fin n) (p : ZMod 2)
    (hrem  : Atom.rem j 1 p ∈ ctx.L)
    (hpend : Atom.pend j i ∈ ctx.L)
    (hunk  : Atom.unk i ∈ ctx.L)
    (hwf : WFContext H ctx) :
    WFContext H (solve ctx j i p hrem hpend hunk) := by
  constructor
  · exact hwf.wf_graph
  · -- rem uniqueness: rem(j,·,·) is replaced by rem(j,0,0)
    intro j'
    by_cases hj : j' = j
    · subst hj
      refine ⟨⟨0, 0⟩, ?_, ?_⟩
      · simp [solve, Multiset.mem_cons]
      · intro ⟨k'', p''⟩ hk''
        simp only [solve, Multiset.mem_cons, Multiset.mem_erase] at hk''
        rcases hk'' with h | ⟨_, _, ⟨_, h⟩⟩
        · simp [Atom.rem.injEq] at h
        · have := (hwf.wf_rem j).choose_spec.2 ⟨k'', p''⟩ (by
            rcases h with ⟨_, h⟩; exact h)
          exact this
    · have := hwf.wf_rem j'
      obtain ⟨⟨k'', p''⟩, hmem, huniq⟩ := this
      refine ⟨⟨k'', p''⟩, ?_, ?_⟩
      · simp [solve, Multiset.mem_cons]
        right; refine ⟨?_, ?_, ?_, ?_, hmem⟩
        all_goals (intro h; exact hj (Atom.rem.inj h).1)
      · intro ⟨k₃, p₃⟩ h3
        simp only [solve, Multiset.mem_cons, Multiset.mem_erase] at h3
        rcases h3 with h | ⟨_, _, ⟨_, h⟩⟩
        · exact absurd (Atom.rem.inj h).1 hj
        · exact huniq ⟨k₃, p₃⟩ h
  · -- var status: unk(i) is consumed, (i,p) added to P
    intro i'
    simp only [solve]
    constructor
    · intro h
      -- unk(i) was erased; if i' = i then unk(i') was removed → contradiction
      by_cases hi : i' = i
      · subst hi
        simp [Multiset.mem_erase_of_mem] at h
      · -- i' ≠ i: unk(i') status unchanged, P unchanged for (i',·)
        have := (hwf.wf_var i').mp (by
          simp [Multiset.mem_erase] at h
          exact h.2.2)
        intro b hb
        simp [Multiset.mem_cons] at hb
        rcases hb with ⟨rfl, rfl⟩ | hb
        · exact absurd rfl hi
        · exact this b hb
    · intro h
      -- unk(i') must not be in the erased linear zone
      by_cases hi : i' = i
      · subst hi
        exfalso
        have : (i, p) ∈ Multiset.cons (i, p) ctx.P := Multiset.mem_cons_self _ _
        exact h p this
      · have hunk_i' : Atom.unk i' ∈ ctx.L := by
          apply (hwf.wf_var i').mpr
          intro b hb
          exact h b (Multiset.mem_cons_of_mem _ hb)
        simp [Multiset.mem_erase_of_ne (by intro h; exact hi (Atom.unk.inj h)),
              Multiset.mem_erase_of_ne (by intro h; exact hi (by simp [Atom.pend.injEq] at h)),
              hunk_i']
  · -- pend count: rem(j,1,p) → rem(j,0,0), and pend(j,i) is consumed
    intro j' k' p' hrem'
    simp only [solve, Multiset.mem_cons, Multiset.mem_erase] at hrem'
    rcases hrem' with h | ⟨_, _, ⟨_, h⟩⟩
    · obtain ⟨rfl, rfl, rfl⟩ : j' = j ∧ k' = 0 ∧ p' = 0 := by
        simp [Atom.rem.injEq] at h; exact ⟨h.1, h.2.1, h.2.2⟩
      have hcount := hwf.wf_pend j 1 p hrem
      simp [Multiset.filter_erase, Multiset.card_erase_of_mem, hcount]
    · have hcount := hwf.wf_pend j' k' p' h
      simp only [solve]
      simp [Multiset.filter_erase, Multiset.card_erase_of_mem]
      exact hcount

end SELLCert
