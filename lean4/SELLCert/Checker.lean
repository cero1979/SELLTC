/-!
# SELLCert.Checker

Pure checker algorithms for success and failure certificates (Algorithm 2 in the paper).

- `checkSuccess H y T ρ` — replay trace `T` from `y`, then verify that `ρ` satisfies
  every residual parity equation and is consistent with the channel. Returns `some x`
  on acceptance or `none` on rejection.
- `checkFailure H y T ω` — replay trace `T` from `y`, then verify that the witness
  `ω` certifies infeasibility of the residual system. Returns `true` on acceptance.
-/

import SELLCert.PeelingState

namespace SELLCert

open scoped BigOperators

variable {n m : ℕ}

/-! ### Checker output -/

/-- Result of the success checker: either an accepted codeword or a rejection report. -/
inductive CheckResult (n : ℕ) where
  | accept      : (Fin n → ZMod 2) → CheckResult n  -- accepted codeword
  | rejectTrace : CheckResult n                       -- invalid trace step
  | rejectParity : Fin m → CheckResult n              -- parity check failed for check j
  | rejectChannel : Fin n → CheckResult n             -- channel consistency violated

/-! ### Trace replay -/

/-- Attempt to replay one step of the trace; returns the updated state or `none`. -/
def replayStep (H : PCMatrix n m) (σ : PeelingState n m) (stp : StepTriple n m) :
    Option (PeelingState n m) :=
  -- check that stp.i is the unique unknown neighbor of stp.j
  let unknNbrs := Finset.univ.filter (fun i' : Fin n => H stp.j i' ≠ 0 ∧ σ.K i' = none)
  if h : σ.d stp.j = 1 ∧ stp.i ∈ unknNbrs ∧ unknNbrs.card = 1 ∧ stp.b = σ.s stp.j
  then some (applyStep H σ stp)
  else none

/-- Replay a full trace, returning the final state or `none` if any step is invalid. -/
def replayFull (H : PCMatrix n m) (σ₀ : PeelingState n m) :
    List (StepTriple n m) → Option (PeelingState n m)
  | []        => some σ₀
  | stp :: T  => do
      let σ' ← replayStep H σ₀ stp
      replayFull H σ' T

/-! ### Success checker -/

/-- Check all residual parity equations: for each check j,
    ∑_{i ∈ U} H[j,i] · ρ(i) = s(j). -/
def checkResidualParity (H : PCMatrix n m) (σ : PeelingState n m)
    (ρ : Fin n → ZMod 2) : Bool :=
  Finset.univ.all fun j : Fin m =>
    (∑ i : Fin n, H j i * (if σ.K i = none then ρ i else 0)) == σ.s j

/-- Check channel consistency: for all non-erased i, the output x satisfies x i = y i. -/
def checkChannel (y : ReceivedWord n) (x : Fin n → ZMod 2) : Bool :=
  Finset.univ.all fun i : Fin n =>
    match y i with
    | none   => true
    | some b => x i == b

/-- **Success checker** (Algorithm 2, success branch).
    Given parity-check matrix H, received word y, peeling trace T, and
    residual assignment ρ, replays T from the initial state and verifies:
    1. each trace step is valid;
    2. ρ satisfies all residual parity equations;
    3. the assembled codeword is consistent with y.
    Returns `some x` on acceptance, `none` on any check failure. -/
def checkSuccess (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ρ : Fin n → ZMod 2) :
    Option (Fin n → ZMod 2) := do
  let σ ← replayFull H (initState H y) T
  guard (checkResidualParity H σ ρ)
  let x : Fin n → ZMod 2 := fun i => (σ.K i).getD (ρ i)
  guard (checkChannel y x)
  pure x

/-! ### Failure checker -/

/-- **Failure checker** (Algorithm 2, failure branch).
    Verifies that ω is an infeasibility witness for the residual system after replaying T:
    1. each trace step is valid;
    2. ω^T H_U = 0 (ω is in the left null space of the residual matrix);
    3. ω^T r = 1 (ω separates the RHS from the column space).
    Returns `true` on acceptance. -/
def checkFailure (H : PCMatrix n m) (y : ReceivedWord n)
    (T : List (StepTriple n m)) (ω : Fin m → ZMod 2) : Bool :=
  match replayFull H (initState H y) T with
  | none   => false
  | some σ =>
    -- check ω^T H_U = 0: for each unknown column i, ∑_j ω_j * H_j_i = 0
    let check1 : Bool := Finset.univ.all fun i : Fin n =>
      if σ.K i = none
      then (∑ j : Fin m, ω j * H j i) == (0 : ZMod 2)
      else true
    -- check ω^T r = 1: ∑_j ω_j * s(j) = 1
    let check2 : Bool := (∑ j : Fin m, ω j * σ.s j) == (1 : ZMod 2)
    check1 && check2

end SELLCert
