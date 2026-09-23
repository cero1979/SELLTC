# Verified finite specification and certificate checker

This library builds with **Lean 4.14.0** and **Mathlib v4.14.0**, pinned in
`lean-toolchain` and `lake-manifest.json` (Mathlib commit
`4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84`). The default `lake build` target
imports all six library modules. The last clean root-package build and dependency
inspection are recorded in [the verification report](../audit/LEAN_VERIFICATION_REPORT.md).

All 51 named library lemmas/theorems were checked with `#print axioms`. Their only
transitive assumptions are Lean's ordinary `propext`, `Classical.choice`, and
`Quot.sound`; some use fewer. No project axiom, admitted proof, `sorryAx`,
`native_decide`, or `True` substitute is used in these results.

## What is proved

| Property | Principal declaration |
|---|---|
| Every peeling assignment agrees with every compatible codeword | `forced_value`, `trace_extends` |
| Replay accepts exactly valid traces and returns their folded state | `replayFull_eq_some_iff` |
| Canonical syndrome/degree obey the usual incremental updates | `applyStep_syndrome_update`, `applyStep_degree_update` |
| Left-nullspace witnesses are sound and complete for finite GF(2) systems | `lem_unsat_witness_sound`, `lem_unsat_witness_complete` |
| Residual unsatisfiability iff a failure witness exists | `residual_unsat_iff_witness` |
| Accepted success gives a codeword consistent with the received symbols | `thm_sound_success` |
| Accepted failure excludes every consistent codeword | `thm_sound_failure` |
| Every compatible word can be certified; every impossible observation has a certificate | `thm_complete_success`, `thm_complete_failure` |
| Accepted success maximizes a real BEC likelihood for `0 ≤ ε ≤ 1` | `thm_ml` |
| Pending-set invariant preserved; every enabled Solve is operationally valid | `propagate_wf`, `solve_wf`, `solve_valid` |
| Derived rem syndromes perform the stated local XOR/Solve updates | `propagate_syndrome`, `solve_selected_syndrome`, `solve_other_syndrome` |
| Propagation terminates at a unique normal form and is confluent | `propagation_normalization`, `propagation_normal_form_unique`, `propagation_confluence` |
| Propagation updates commute | `propagate_commute` |
| Every permitted asynchronous interleaving has a valid ordered event trace | `rewstar_sound`, `adequacy_soundness` |
| Every prescribed operational trace reaches its normalized state with exactly that log | `adequacy_completeness` |
| Operational/event semantics coincide for the same trace | `thm_adequacy_complete` |

Operational/rewriting adequacy completeness covers every valid trace, maximal or
partial. Certificate soundness covers arbitrary accepted partial traces. The checker-level
completeness theorems use empty traces; residual-witness equivalence separately
covers every residual state. An empty trace is valid, and a complete residual
assignment or left-kernel witness can certify it. The ML theorem uses an actual real-valued likelihood, zero for inconsistent
words and `ε^e * (1-ε)^k` for consistent words, where `e` and `k` count erasures and
visible positions. It compares against all competing codewords, includes both
endpoint probabilities, and asserts neither unique recovery nor recovery of the
transmitted word.

## Representations and limits

`PeelingState` stores a partial assignment `K`. Syndrome and degree are computed
from it. This replaces the original arbitrary cached fields with canonical
states, and the update lemmas prove agreement with the mathematical cached-update
equations. It is not a verified refinement of the Python arrays.

`Context` stores a canonical state, finite pending sets `Q_j`, and an external
ordered event observer. Its invariant is
`unknownNbrs H K j ⊆ Q_j ⊆ neighbors H j`; its rem count and syndrome are derived.
Known incidences may remain pending, so arbitrary interleavings are modeled.
Functional values and finite sets enforce unique values and exact multiplicities
by representation. The manuscript proves the correspondence to well-formed raw
token multisets; that representation correspondence is not mechanized here.
The multiset image of the event observer gives the unordered log atoms.

`RewStar H C T D` is indexed by explicit trace data `T`. Completeness ends at
`encodeLogged` with the accumulated log; it never discards Solve events.
`extractedTrace` returns this explicit index, not information eliminated from a
proof-irrelevant reachability witness. This library formalizes a SELL-style event
system, **not a SELL/SELLF sequent calculus or a focusing theorem**.

The algebra proof constructs a separating linear functional; it does not verify
Python's Gaussian elimination implementation. Termination of arbitrary runs including Solve is proved in the manuscript; the
Lean termination theorem concerns propagation-only normalization. Neither sparse
time complexity, certificate bit size, nor experimental claims are mechanized. The BEC likelihood
is given in closed form; a probability-space construction and derivation of its
coordinate-product expression are outside the Lean library.

## Build and audit

Install `elan`/Lean using the official Lean distribution, then:

```sh
cd lean4
lake exe cache get
./verify.sh --clean
lake env lean StatementAudit.lean
```

`verify.sh --clean` runs `lake clean selltc`, retaining pinned dependency caches,
then rebuilds the complete root library, prints every named theorem's transitive
axioms, and type-checks the JSON runner. `StatementAudit.lean` prints exact
principal theorem signatures. `AxiomAudit.lean` lists all 51 named lemmas/theorems.

On the audited macOS 27 arm64 host, old `/usr/local/bin/git` and `zstd` binaries
were x86_64 and incompatible with native child processes. Put native `/usr/bin`
tools after the Lean toolchain directory in `PATH`. The Lean 4.14.0-linked cache
executable was also rejected by this OS loader (`SG_READ_ONLY` flag); its Lean
interpreter path succeeded:

```sh
lake build cache
lake env lean --run .lake/packages/mathlib/Cache/Main.lean get
```

These are environment issues, distinct from proof errors. The pinned dependencies
and all project proofs were successfully checked on the audited host.

## Executable checker and Python comparison

```sh
./run_checker.sh < ../audit/differential_cases.jsonl > actual.jsonl
```

The runner consumes one JSON object per line with exactly the keys `H`, `y`,
`kind`, `trace`, and `witness`. `H` is a rectangular binary matrix, `y` uses `-1`
for erasure and `0/1` for visible bits, and each trace entry is `[check,variable,bit]`.
`kind` is `success` or `failure`. A success witness is indexed by increasing
residual variable index after replay; a failure witness has one bit per row.
For `H=[]`, the column count is the length of `y`. Malformed data are rejected.
Outputs are `{"accepted": bool, "word": [bits] | null}`.

The recorded differential corpus has **575 cases, with 575 exact matches** to
Python's acceptance and reconstructed-word outputs (369 accepted, 206 rejected).
It includes malformed inputs, zero-check cases, partial traces, valid certificates
and corrupted certificates. This is finite differential testing, not a proof of
Python/Lean refinement. Parsing, serialization, the adapter, Lean execution and
Python remain outside the typed-checker soundness theorems. The tested command
uses `lean --run` to avoid the audited OS's native-loader incompatibility.

## Files

- `Basic.lean`: binary matrices and code/channel predicates.
- `PeelingState.lean`: canonical operational state, trace relation, solution preservation.
- `Checker.lean`: executable replay and success/failure conditions.
- `Soundness.lean`: certificate soundness/completeness, finite duality, BEC likelihood.
- `Rewriting.lean`: canonical asynchronous context and local invariant/update lemmas.
- `Adequacy.lean`: trace-indexed rewrites, normalization, confluence, adequacy.
- `Main.lean`: JSONL adapter and runner; no theorem verifies its parsing layer.

The original files and their false/admitted claims are retained in `../originals/`.
See [the initial audit](../audit/LEAN_INITIAL.md) for explicit counterexamples and
[the final Lean report](../audit/LEAN_VERIFICATION_REPORT.md) for commands/evidence.
