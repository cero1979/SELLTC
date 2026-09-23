import Lake
open Lake DSL

package selltc

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.14.0"

@[default_target]
lean_lib SELLCert where
  roots := #[`SELLCert]

lean_exe sellcert where
  root := `Main
