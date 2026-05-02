/-!
# SELLCert — Lean 4 Mechanization of Certified Hybrid LDPC Decoding

This library formalizes the main results of the paper
*Certified Hybrid Decoding of Binary LDPC Codes over the BEC
via Subexponential Linear Logic*.

## Module structure

- `SELLCert.Basic`       — GF(2) arithmetic, Tanner graphs, codeword predicates
- `SELLCert.PeelingState`— Operational peeling state, valid steps, traces, replay
- `SELLCert.Rewriting`   — SELL atoms, context, (Propagate)/(Solve) rules, WF lemmas
- `SELLCert.Checker`     — Pure checker algorithms for success and failure certificates
- `SELLCert.Soundness`   — Soundness of success certificates (thm:sound),
                           soundness and completeness of failure certificates
                           (lem:unsat-witness-sound, lem:unsat-witness-complete)
- `SELLCert.Adequacy`    — Adequacy of the SELL-style specification (thm:adequacy-complete)

## Proof status

| Theorem               | File       | Status                                    |
|-----------------------|------------|-------------------------------------------|
| `isCW_iff`            | Basic      | Complete                                  |
| `syndrome_invariant`  | PeelingState | Complete (by induction on trace length) |
| `propagate_wf`        | Rewriting  | Complete                                  |
| `solve_wf`            | Rewriting  | Complete                                  |
| `thm_sound`           | Soundness  | Complete                                  |
| `lem_unsat_witness_sound`   | Soundness | Complete                            |
| `thm_sound_failure`   | Soundness  | Complete                                  |
| `thm_ml`              | Soundness  | Complete                                  |
| `lem_unsat_witness_complete` | Soundness | Admitted (double-dual over GF(2))  |
| `thm_adequacy_complete` | Adequacy | Admitted (induction structure written)    |
-/

import SELLCert.Basic
import SELLCert.PeelingState
import SELLCert.Rewriting
import SELLCert.Checker
import SELLCert.Soundness
import SELLCert.Adequacy
