# Lean verification report

Verified on 2026-09-23. This report concerns the repaired files in `lean4/`; the
original audit and preserved sources describe the pre-repair artifact.
`evidence/lean_source_inventory.json` and `evidence/lean_environment.json` are
historical baseline snapshots from 2026-09-20, not the current source/environment.
The current snapshot is `evidence/lean_verification_summary.json`.

## Result and exact scope

The complete default Lean library target builds from a clean **project** build
directory with Lean 4.14.0 and Mathlib v4.14.0. All 51 named library lemmas and
theorems were inspected with `#print axioms`. The union of their transitive axioms
is exactly `{propext, Classical.choice, Quot.sound}`. There is no project axiom,
`sorryAx`, admitted proof, `native_decide`, or vacuous `True` replacement in these
results. Source scanning also found no `sorry`, `admit`, `axiom`, `native_decide`,
or `unsafe` token in the six modules, root imports, or JSON runner.

This is a kernel-checked specification and typed certificate checker. It is **not**
a formal SELL/SELLF sequent calculus, a formal refinement of raw token multisets, a
verification of Python or its Gaussian elimination, a proof of the JSON adapter,
or a mechanization of implementation complexity. These limits are representation
and trust boundaries, not missing proofs hidden behind axioms.

Machine-readable summary and source SHA-256 hashes:
`evidence/lean_verification_summary.json`. Exact principal theorem signatures:
`evidence/lean_statement_audit.txt`. Complete transitive-axiom output:
`evidence/lean_axiom_audit.txt`.

## Versions and build evidence

- Host: macOS 27.0 arm64.
- Lean: `Lean (version 4.14.0, arm64-apple-darwin23.6.0, commit 410fab728470, Release)`.
- Lake: `Lake version 5.0.0-410fab7 (Lean version 4.14.0)`.
- Mathlib: `4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84` (tag `v4.14.0`).
- Compiler pin: `lean4/lean-toolchain`.
- All dependency commits: `lean4/lake-manifest.json`.
- `@[default_target] lean_lib SELLCert` imports every component; a bare build does
  not silently omit the library.

The audited host initially had no Lean/Lake/elan. An official Lean 4.14.0 archive
was downloaded locally, and the pinned dependencies and official Mathlib cache
were obtained. No global toolchain or system package installation was required.
The following environment was used before the commands below:

```sh
export PATH="/Users/cero/Downloads/Articulos/SELLTeoCod/SELLTCFULL_bundle/audit/toolchains/lean-4.14.0-darwin_aarch64/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd /Users/cero/Downloads/Articulos/SELLTeoCod/SELLTCFULL_bundle/lean4
```

| Command | Result | Evidence |
|---|---|---|
| `lake clean selltc` | Exit 0; only project outputs removed | `evidence/lean_clean.txt` |
| `lake build` | Exit 0; all six modules and root rebuilt, no warnings/errors | `evidence/lean_clean_build.txt` |
| `lake env lean AxiomAudit.lean` | Exit 0; 51 declarations; only ordinary foundational axioms | `evidence/lean_axiom_audit.txt` |
| `lake env lean StatementAudit.lean` | Exit 0; exact principal signatures printed | `evidence/lean_statement_audit.txt` |
| `lake env lean Main.lean` | Exit 0; JSON adapter type-checks | `evidence/lean_runner_compile.txt` |
| `lake env lean --run Main.lean < ../audit/differential_cases.jsonl` | Exit 0; 575 JSON outputs | `differential_lean_actual.jsonl`, `evidence/lean_differential_stderr.txt` |
| JSON-object comparison with Python's expected outputs | 575/575 exact matches; zero mismatches | `evidence/lean_differential_comparison.json` |

The clean build deliberately retains dependency caches. It rebuilds every project
source against the pinned imported library; this is not a claim that all of
Mathlib was rebuilt from source. `lean4/verify.sh --clean` reproduces the project
build, theorem axiom audit, and runner type check. `lean4/run_checker.sh` runs the
JSONL interface on an ordinary installation with `lake` on PATH.

### Environment failures, separated from source failures

1. `/usr/local/bin/zstd` and `/usr/local/bin/git` were x86_64 binaries on the arm64
   host. Native child execution failed. Native `/usr/bin/git` was used; local
   Python `zstandard` extracted the toolchain archive.
2. A Lean 4.14.0-linked native cache executable was rejected by the macOS 27 loader
   because its `__DATA_CONST` segment lacked `SG_READ_ONLY`. Its interpreter path
   (`lake env lean --run .lake/packages/mathlib/Cache/Main.lean get ...`) downloaded
   and unpacked 2493 required files successfully. This does not affect the Lean
   kernel check. The checker differential run also uses `lean --run`; no claim is
   made that the old-toolchain native checker binary was successfully executed on
   this OS. See `evidence/mathlib_cache.txt` and `evidence/mathlib_cache_interpreted.txt`.
3. Shallow dependency retrieval required the ProofWidgets release tag as well as
   its pinned commit to locate its release. The release was then obtained; this
   was a dependency setup issue, not a proof failure.

## Substantive theorem review

Compilation is not the sole justification for the claims: the statements and
proof dependencies were also read. `StatementAudit.lean` exposes their exact
quantifiers, premises and conclusions. The following mathematical content is
established for all finite dimensions, including zero dimensions.

### Operational state and replay

`PeelingState` stores only the partial assignment `K`. The functions `syndrome`,
`unknownNbrs`, and `degree` derive the residual data. `ValidStep` requires the
actual unknown-neighbor set of the specified check to be the singleton `{i}` and
requires the supplied value to equal that check's syndrome. In particular,
adjacency is no longer omitted.

`applyStep_syndrome_update` proves the incremental syndrome formula
`s'_j = s_j + H_ji b` when `K_i` is unknown; `applyStep_degree_update` proves the
corresponding edge-dependent decrement. Thus the canonical representation agrees
with the mathematical cached-update equations. It does not prove the correctness
of a separate mutable cache implementation.

`forced_value` proves that a valid step assigns `x_i=b` in every codeword extending
`K`. `applyStep_extends` and `trace_extends` preserve that agreement through the
whole valid trace. `replayFull_eq_some_iff` is an actual iff between executable
replay acceptance and the inductive `ValidTrace` predicate, including equality of
the returned state to `foldTrace`.

### Certificate soundness and completeness

- `thm_sound_success`: if `checkSuccess H y T ρ = some x`, then `H*x=0` and every
  visible bit of `y` agrees with `x`. The proof combines the known/unknown row
  decomposition with the residual parity check and explicit channel consistency.
- `thm_sound_failure`: if `checkFailure H y T ω = true`, no codeword is consistent
  with `y`. Replay correctness and `trace_extends` show that any supposed compatible
  codeword also extends the replayed state. The checked left-kernel and odd-syndrome
  conditions then contradict its parity equations.
- `lem_unsat_witness_sound`: `ωᵀA=0` and `ωᵀb=1` imply `Ax≠b` for every `x`.
- `lem_unsat_witness_complete`: if `Ax≠b` for every `x`, a row vector `ω` with both
  conditions exists. The proof separates `b` from the range of `A.mulVecLin` using
  `Submodule.exists_dual_map_eq_bot_of_nmem`, represents the functional by its
  values on coordinate vectors, and uses the fact that the only nonzero binary
  scalar is one. No positive-definite real inner-product argument is imported
  into characteristic two.
- `residual_unsat_iff_witness`: residual unsatisfiability is equivalent to the
  existence of the exact `FailureWitness` predicate tested by the checker.
- `thm_complete_failure`: every received word without a compatible codeword has
  an accepted failure certificate (the empty valid trace suffices).
- `thm_complete_success`: every compatible codeword is accepted with an empty
  trace and that completion as its residual assignment.

The two soundness theorems cover arbitrary accepted partial traces. The
checker-level completeness declarations `thm_complete_success` and
`thm_complete_failure` use empty traces; `residual_unsat_iff_witness` separately
covers every residual state. They do not verify extraction of a witness by
Python's row elimination or prove that the decoder internally followed the
submitted trace.

### Genuine BEC maximum likelihood

`becLikelihood ε y x` is an actual real-valued function. It is zero for inconsistent
`x`, and otherwise `ε^e * (1-ε)^k`, with the erasure and visible counts taken from
`y`. `bec_completion_maximizes` proves that a consistent completion maximizes this
likelihood over all candidate words for `0≤ε≤1`. `thm_ml` combines this inequality
with accepted-success soundness and explicitly quantifies over every competing
codeword. It contains neither the old axiom nor a `True` conclusion.

The closed interval includes endpoint cases where an observation may have zero
likelihood for every candidate. The theorem asserts a maximum, not positive
probability, uniqueness, posterior conditioning on an impossible event, or exact
recovery of the transmitted word. The likelihood's coordinate-product derivation
is mathematical manuscript content; no probability-space normalization theorem
is claimed for the Lean library.

### Asynchronous invariants, normalization, and adequacy

The original duplicate-permitting multiset record was replaced openly with a
canonical representation: functional `K`, finite pending sets `Q_j`, and an
external ordered log. A rem count is `|Q_j|`; its syndrome is the sum of known
contributions outside `Q_j`. The substantive invariant is

```
unknownNbrs H C.state j ⊆ C.pending j ⊆ neighbors H j.
```

Its right inclusion is written pointwise in Lean. Known incidences may remain
pending, so the invariant models intermediate, asynchronous states. Uniqueness of
known values and exact multiplicities are imposed by the representation. The
manuscript's correspondence from these canonical objects to well-formed raw token
multisets is not itself a mechanized isomorphism.

Propagate requires an actual pending incidence and a known value. Solve requires
`Q_j={i}`, an unknown `i`, and the value equal to the derived residual syndrome.
`propagate_wf`, `solve_wf`, and `solve_valid` establish preservation and local
operational soundness. Additional lemmas prove that the derived rem fields have
the stated token-rule updates: Propagate adds the known bit; Solve makes its
selected syndrome zero and leaves other syndromes unchanged until propagation.

`propagate_decreases` strictly decreases the total pending-incidence count.
`propagation_normalization` constructs a finite propagation-only derivation to
`encodeLogged H C.state C.trace`. `propagate_commute` proves commuting updates;
`propagation_normal_form_unique` and `propagation_confluence` prove order-independent
normalization for actual permitted derivations.

`RewStar H C T D` has **the event trace as explicit data in its index**. It is a
proposition, but `extractedTrace` simply returns that index. It does not pattern
match a non-singleton proof to produce data.

- `rewstar_sound` quantifies over every derivation from any well-formed context,
  with no requirement to propagate immediately after Solve. It proves that its
  actual event list `T` is a valid operational trace.
- `rewstar_observation` proves the endpoint state is `foldTrace` of those exact
  events and the endpoint observer is the previous observer followed by `T`.
- `adequacy_one_step` performs one Solve followed by normalization, retaining the
  emitted event.
- `adequacy_completeness` proves that every valid operational trace `T` from `σ`
  has a derivation from `encodeLogged H σ L` to
  `encodeLogged H (foldTrace H σ T) (L ++ T)` **with index exactly `T`**.
- `adequacy_soundness` specializes arbitrary-derivation soundness to the encoded
  received word.
- `thm_adequacy_complete` states an iff for the same `T`: validity from the initial
  state iff some event derivation with that trace exists. Its soundness direction
  is no longer the old vacuous existence of an unrelated empty trace.

The incorrect old exact endpoint and WF assertions were not retained under weaker
names. Their counterexamples are recorded in `LEAN_INITIAL.md`; the replacement
statements identify logs, canonicality and observation explicitly. No SELL proof
search, promotion rule or focused deductive adequacy theorem is claimed.

## Python comparison and trust boundary

The strict runner `Main.lean` parses the same JSONL schema as Python, checks
rectangular dimensions, binary integers, received symbols, trace dimensions and
indices, exact fields and witness length. It converts the sorted residual witness
to the total function expected by the typed checker. For a matrix with no rows it
infers the column count from the received word. Parsing or conversion failure
returns rejection.

The independently generated corpus has **575 cases**: **369 accepted** and
**206 rejected**, with **575 exact matches** of the JSON acceptance and word
objects. Inputs, expected results, and actual Lean results are respectively:

- `audit/differential_cases.jsonl`
- `audit/differential_expected.jsonl`
- `audit/differential_lean_actual.jsonl`

Case descriptions are in `audit/differential_case_index.csv`. The corpus includes
honest certificates, valid empty traces, mutated words/traces/witnesses, zero-check
cases and malformed inputs. These tests are evidence of agreement on the listed
cases, not a theorem of Python refinement. The parser, serializer, adapter,
interpreter/runtime and Python implementation are separate trust components.
The algebraic theorem trusts the supplied matrix and received word; it cannot
establish that an externally corrupted matrix is the intended code.

## Changes from the initially submitted formalization

- Added compiler pin, full manifest, default root build target, reusable verification
  scripts, explicit statement and axiom audits, and an executable JSONL interface.
- Corrected the invalid Lake package-name field and moved imports before module
  documentation (the original root failed Lean's import-order rule).
- Replaced five admissions, one artificial axiom and vacuous ML/adequacy content
  with proved substantive statements.
- Replaced malformed arbitrary cached states with canonical states and proved their
  incremental mathematical update equations.
- Replaced duplicate-permitting contexts with canonical pending sets and exact
  representation invariants; preserved genuine intermediate/asynchronous behavior.
- Replaced proof-to-data trace extraction by explicit trace-indexed reachability.
- Retained Solve logs in completeness endpoints; proved full arbitrary-interleaving
  soundness, propagation termination, normalization, commutation and confluence.
- Completed both certificate soundness proofs, failure-witness existence and
  checker-level certificate completeness, and a genuine BEC likelihood inequality.
- Rewrote the Lean README to state these results and their boundaries precisely.

Original `lake build` failed at the package configuration (String versus Name);
a diagnostic copy with only that field repaired then failed the original root's
import order. Logs are `evidence/lean_build_original.log` and
`evidence/lean_original_modules.txt`. These were source/configuration failures,
separate from dependency and native-loader issues. Original files remain preserved.

## Remaining scope limits

No unresolved admission or known false theorem remains in the claimed library.
The raw-token/canonical representation theorem, termination of arbitrary runs
including Solve (as distinct from the mechanized propagation-only normalization),
ordinary-exponential comparison, SELL-label erasure, stopping sets and residual-nullity
interpretation, Gaussian elimination implementation, sparse asymptotic analysis and statistics remain
mathematical or experimental manuscript results. Python-to-Lean refinement and
JSON-parser correctness are not proved. Native execution of binaries linked by
Lean 4.14.0 on the audited macOS 27 host remains an environment limitation; the
interpreter-based executable comparison and kernel verification both succeeded.
