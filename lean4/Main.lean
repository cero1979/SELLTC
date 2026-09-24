import SELLCert.Checker
import Lean

/-! JSONL interface for differential tests. The finite checker is verified; this
parser/serializer and the Lean runtime are part of the executable trust boundary. -/
open Lean SELLCert

private def rejected : Json := Json.mkObj [("accepted", toJson false), ("word", Json.null)]

private def parseBit (j : Json) : Except String Bit := do
  let i ← j.getInt?
  if i = 0 ∨ i = 1 then return (i.toNat : Bit) else throw "bit expected"

private def parseReceived (j : Json) : Except String (Option Bit) := do
  let i ← j.getInt?
  if i = -1 then return none
  else if i = 0 ∨ i = 1 then return some (i.toNat : Bit)
  else throw "received symbol expected"

private def parseStep (n m : Nat) (j : Json) : Except String (StepTriple n m) := do
  let a ← j.getArr?
  if a.size ≠ 3 then throw "triple expected"
  let row ← (a[0]!).getNat?
  let col ← (a[1]!).getNat?
  let bit ← parseBit a[2]!
  if hr : row < m then
    if hc : col < n then return ⟨⟨row, hr⟩, ⟨col, hc⟩, bit⟩
    else throw "column out of range"
  else throw "row out of range"

private def checkJson (doc : Json) : Except String Json := do
  let obj ← doc.getObj?
  let keys := obj.fold (fun ks k _ => k :: ks) ([] : List String)
  if keys.length ≠ 5 ∨ ¬keys.all (fun k => ["H", "y", "kind", "trace", "witness"].contains k) then
    throw "unexpected keys"
  let ys ← (← (← doc.getObjVal? "y").getArr?).mapM parseReceived
  let n := ys.size
  let rows ← (← (← doc.getObjVal? "H").getArr?).mapM fun row => do
    let cells ← row.getArr?
    if cells.size ≠ n then throw "matrix dimension"
    cells.mapM parseBit
  let m := rows.size
  let H : PCMatrix n m := fun j i => (rows[j.val]!).getD i.val 0
  let y : ReceivedWord n := fun i => ys[i.val]!
  let kind ← (← doc.getObjVal? "kind").getStr?
  if kind ≠ "success" ∧ kind ≠ "failure" then throw "certificate kind"
  let trace ← (← (← doc.getObjVal? "trace").getArr?).toList.mapM (parseStep n m)
  let witness ← (← (← doc.getObjVal? "witness").getArr?).mapM parseBit
  match replayFull H (initState H y) trace with
  | none => return rejected
  | some σ =>
      if kind = "success" then
        let unknowns := (List.finRange n).filter fun i => (σ.K i).isNone
        if witness.size ≠ unknowns.length then throw "residual assignment dimension"
        let pairs := unknowns.zip witness.toList
        let ρ : Fin n → Bit := fun i => (pairs.lookup i).getD 0
        match checkSuccess H y trace ρ with
        | none => return rejected
        | some x => return Json.mkObj [("accepted", toJson true),
            ("word", toJson ((List.finRange n).map fun i => (x i).val))]
      else
        if witness.size ≠ m then throw "witness dimension"
        let ω : Fin m → Bit := fun j => witness[j.val]!
        return Json.mkObj [("accepted", toJson (checkFailure H y trace ω)), ("word", Json.null)]

/-- Preserve the strict integer JSON domain: a scientific or decimal numeric token
is rejected even if the JSON number parser represents its value as an integer. -/
private def integerLexemes (s : String) : Bool := Id.run do
  let mut quoted := false
  let mut escaped := false
  for c in s.toList do
    if quoted then
      if escaped then escaped := false
      else if c == '\\' then escaped := true
      else if c == '"' then quoted := false
    else if c == '"' then quoted := true
    else if c == '.' || c == 'e' || c == 'E' then return false
  return true

private def processLine (s : String) : Json :=
  if integerLexemes s then
    match Json.parse s >>= checkJson with
    | .ok j => j
    | .error _ => rejected
  else rejected

private partial def runLines (input output : IO.FS.Stream) : IO Unit := do
  let line ← input.getLine
  if line.isEmpty then return
  output.putStrLn (processLine line).compress
  runLines input output

def main : IO Unit := do
  runLines (← IO.getStdin) (← IO.getStdout)
