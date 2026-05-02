-- lakefile.lean — Lake build configuration for the SELL certification Lean 4 formalization

import Lake
open Lake DSL

package «selltc» where
  name := "selltc"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.14.0"

lean_lib «SELLCert» where
  roots := #[`SELLCert]
