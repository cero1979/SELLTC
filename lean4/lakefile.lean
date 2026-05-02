-- lakefile.lean — Lake build configuration for the SELL certification Lean 4 formalization
-- This file will be completed once the Lean source files are written.

import Lake
open Lake DSL

package «selltc» where
  name := "selltc"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "master"

-- Planned modules (files not yet written):
-- lean_lib SELLCert
-- lean_lib PeelingState
-- lean_lib Rewriting
-- lean_lib Checker
-- lean_lib Soundness
-- lean_lib Adequacy
