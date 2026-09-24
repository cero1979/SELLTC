# Initial Lean audit

Date: 2026-09-20. This audit describes the original source before repairs. Source hashes and declaration/import inventory are in `evidence/lean_source_inventory.json`. All six component modules and the root import file were read. The original tracked Lean files have not been changed.

## Initial environment and reproducibility

The host is macOS 27 arm64. Neither `lean`, `lake`, nor `elan` was initially on PATH. `lakefile.lean` selects mathlib tag `v4.14.0`, but there is no `lean-toolchain` and no `lake-manifest.json`. The README's bare `lake build` is therefore not reproducible on a clean machine without an externally chosen compiler. A local official Lean 4.14.0 binary is being obtained under the ignored audit toolchain directory; original sources are copied to `audit/build-original/lean4` so dependency setup does not modify tracked files. Environment observations are recorded in `evidence/lean_environment.json`.

## Source findings

All findings below are blocking unless explicitly marked important or editorial.

1. **Five explicit proof admissions.** `Soundness.lean:86` admits `lem_unsat_witness_complete`; `Soundness.lean:175` admits `thm_sound_failure`; `Adequacy.lean:85` admits `adequacy_one_step`; `Adequacy.lean:104` has another admission in `adequacy_completeness`; `Adequacy.lean:123` admits `adequacy_soundness`. A successful build permitting these would still not establish these theorems without `sorryAx`. Exact matches are saved in `evidence/lean_admissions_initial.txt`.
2. **ML is not expressed.** `bec_equal_likelihood` is an axiom whose conclusion is `True` (`Soundness.lean:187–194`). No erasure probability, probability value, comparison, maximum, or transition kernel appears in its type. The last conjunct of `thm_ml` is likewise `True`. Calling it a “genuine BEC axiom” or a mechanization of ML is false. It must be replaced by an actual finite-channel likelihood theorem or removed from the mechanized claim.
3. **Exact-state adequacy is false even on the smallest valid graph.** Let `n=m=1`, `H=[1]`, `y=[none]`, and take the valid step `(0,0,0)`. The initial context has `unk(0), pend(0,0), rem(0,1,0)` and no known value. Its only rewrite is Solve, which produces `known(0,0), rem(0,0,0), step(0,0,0)`. The encoded operational target has `known(0,0), rem(0,0,0)` with no `step`. No rule consumes a `step` atom. Thus the conclusion of `adequacy_one_step` and of completeness for this singleton trace is false. There is also a missing well-formedness premise for arbitrary `σ`.
4. **The advertised WF preservation statements are false.** `WFContext.wf_rem` requires a unique *pair of values occurring as a token*, not one occurrence; duplicate identical rem tokens are allowed. For `n=m=1`, `H=[1]`, let `P=[(0,0)]` and `L=[pend(0,0),rem(0,1,0),rem(0,1,0)]`. All four WF fields hold. Propagate removes one rem and the pend and adds `rem(0,0,0)`, leaving two different rem pairs and breaking both `wf_rem` and `wf_pend`. Separately, with `P=[]` and `L=[unk(0),unk(0),pend(0,0),rem(0,1,0)]`, WF holds but Solve leaves an unk token together with a known value, breaking `wf_var`. Consequently `propagate_wf` and `solve_wf` cannot be proved at these types without changing the invariant.
5. **Trace extraction uses proof elimination prohibited by Lean.** `RewStar` is declared in `Prop`, but `extractedTrace` pattern matches it to construct a `List` in `Type`. This nonsingleton inductive has no eliminator into Type. Moreover, two independent Solve orders can have the same start and final multiset, but different ordered traces: the relation's endpoints do not determine a trace. Use a trace-indexed relation in Prop or an explicit derivation datatype in Type.
6. **The combined adequacy soundness statement is vacuous.** Its second conjunct only says that whenever a context is reachable, *some* valid trace exists. The empty trace always exists. It does not connect the witness to the derivation, endpoint, or logs. The separate `adequacy_soundness` has the substantive intended claim, but the definition it depends on is invalid and the proof is admitted.
7. **The operational relation omits adjacency.** `ValidStep` states uniqueness as a one-way implication and never explicitly requires `H stp.j stp.i ≠ 0`. A malformed arbitrary state with degree one and no incident edge can satisfy the predicate. `replayStep` is stricter: it checks actual membership of the unique unknown-neighbor set. A degree invariant plus reachability can recover adjacency, but `adequacy_one_step` quantifies over arbitrary states with neither. Repair by expressing adjacency directly and proving stored-degree consistency.
8. **The existing invariant is inadequate for asynchronous contexts.** It says nothing about unique known values, unique unknowns, edge provenance, pending-incidence multiplicity, or syndrome meaning. After Solve, other adjacent checks retain pending incidences of a now-known variable. Such states cannot literally encode an operational state whose syndrome and degree have already been updated at every check. A strengthened asynchronous invariant and a normalized-state correspondence are required.
9. **Success soundness is unfinished even though its body contains no literal admission.** At `Soundness.lean:132–136`, residual parity has been substituted, but the connection between successful replay and `SyndromeInv` has not been established; `simp [add_self_zmod2]` cannot supply that semantic invariant. The channel proof also uses suspicious repeated quantifier elimination. Both must be diagnosed by compiling, not by counting admissions. The theorem's intended statement is mathematically sound for the defined checker and can be proved via replay correctness and syndrome preservation.
10. **Several elementary proof bodies are not credible compilations.** Examples include `by decide` for an open variable `x : ZMod 2`; `[Fintype m]` when `m : ℕ` in `dotProduct_zero_left`; a non-generalized list induction in `syndrome_invariant`; and use of a nonexistent `RewStar.step_of_refl` to turn a reflexive-transitive derivation into one step in adequacy completeness. The latter transformation is also mathematically invalid in general. Exact compiler findings follow below.

## Dependency and claim audit

The module dependency graph is `Basic → PeelingState → {Checker, Rewriting}`, `Checker → Soundness`, and `{Checker, Rewriting} → Adequacy`; the root imports all six. No completed module can be certified before its imports compile.

| Declaration | Intended substantive claim | Initial status |
|---|---|---|
| `isCW_iff_parityBit` | Matrix kernel membership iff every parity check is zero | Mathematically valid; compilation pending |
| `initState_syndrome_inv` | Initial cached syndrome equals the known contribution | Mathematically valid; compilation pending |
| `applyStep_syndrome_inv`, `syndrome_invariant` | Valid peeling updates preserve syndrome meaning | Mathematically valid; proof bodies need compilation/repair |
| `propagate_wf`, `solve_wf` | Rewriting preserves current `WFContext` | **False as stated**, explicit multiplicity counterexamples above |
| `lem_unsat_witness_sound` | Left-nullspace separator proves no solution | Mathematically valid; compilation pending |
| `lem_unsat_witness_complete` | Every inconsistent finite GF(2) system has a separator | Mathematically valid; explicitly admitted |
| `thm_sound_success` | Accepted output is a codeword consistent with received bits | Mathematically valid; replay-invariant proof missing |
| `thm_sound_failure` | Accepted failure witness excludes every consistent codeword | Mathematically valid; explicitly admitted; needs solution-preservation invariant, not only syndrome |
| `bec_equal_likelihood`, `thm_ml` | Supposed BEC ML optimality | ML proposition **not expressed**; axiom/True placeholder |
| `adequacy_one_step`, `adequacy_completeness` | Exact encoded endpoint reached | **False**, explicit one-edge counterexample |
| `adequacy_soundness` | Every rewrite derivation produces a valid operational trace | Plausible with reachable asynchronous invariant; current extraction ill-typed and proof admitted |
| `thm_adequacy_complete` | Combined directions | False first conjunct; second conjunct vacuous; transitive admission dependence |

`thm_ml` depends directly on `thm_sound_success` and the artificial axiom. `adequacy_completeness` depends on admitted `adequacy_one_step` and has another direct admission. `thm_adequacy_complete` depends on both adequacy directions. No root-level “fully proved” claim is justified by these sources.

## README and source-documentation corrections needed

- Root README calls `thm_sound_success` and `thm_ml` fully proved; false as mechanization claims.
- Lean README labels “Complete (1 admit)” as success; its alleged literal admit in success soundness is not actually in the body, which instead contains an unfinished argument.
- The BEC axiom description claims an equal-likelihood property that its type does not say.
- Adequacy module introduction calls completeness fully proved despite the helper admission, local admission, invalid extraction, and false endpoint.
- Root import module calls failure soundness complete while its proof is admitted, and lists stale identifier names.
- Estimates such as “~30/80/120/200 lines” are speculative and conceal substantive invariant changes. They are not evidence of proof feasibility.
- The README names `Subspace.orthogonal_orthogonal` as a “correct” API without a verified compilation. The claimed ordinary orthogonal-complement approach over GF(2) requires a bilinear-duality theorem; real inner-product positive-definiteness cannot be silently reused in characteristic two.

## Repair design, without weakening the intended results

1. Pin the compiler and dependency manifest; compile the elementary operational modules, add degree and agreement-with-solutions invariants, and prove replay soundness/completeness against the operational step predicate.
2. Prove success soundness using the residual/known decomposition of each row. Prove failure soundness using agreement of every consistent codeword with values forced by a valid trace, followed by the same decomposition and the separator identity.
3. Prove separator completeness with finite-dimensional linear dual separation (or verified Gaussian elimination), over the actual matrix map's range. Normalize a nonzero functional value in GF(2), and recover its coordinate row vector.
4. Replace insufficient WF with a pending-*set* / processed-incidence invariant, unique variable status and value, one rem token per check, exact degree count, and syndrome equal to the XOR of values on already processed incidences. Distinguish asynchronous and normalized contexts. Preserve explicit trace history in a trace-indexed derivation relation.
5. State adequacy as (i) each valid operational trace admits a derivation ending in the normalized encoded state plus its log multiset, with exactly the given trace labels, and (ii) every reachable rewrite derivation's labels form a valid operational trace. Prove local soundness for arbitrary interleavings, propagation normalization/termination and commutation, and macrostep completeness. This corrects false formulations openly and preserves both substantive directions.
6. Either formalize finite BEC likelihood as a product of per-coordinate factors (no full measure theory is necessary), with nonnegative erasure probability on `[0,1]`, and prove accepted outputs maximize it; or remove ML from Lean and retain a complete explicitly nonmechanized mathematical proof. Never retain the `True` placeholder.
7. Compare an executable Lean checker with Python over the same serialized finite cases. Differential tests establish agreement on tested inputs, not extraction/refinement or verification of Python. State this trust boundary explicitly.

## Compilation evidence

1. Original `lake build`, using official Lean 4.14.0 in a clean source copy, **exit 1**. Compiler: `Lean (version 4.14.0, arm64-apple-darwin23.6.0, commit 410fab728470, Release)`. Lake: `Lake version 5.0.0-410fab7 (Lean version 4.14.0)`. The first failure is a source configuration error: `lakefile.lean:7:10`, `"selltc" : String` is expected to have type `Lean.Name`. Thus the submitted project does not build even far enough to check its proofs. Full output: `evidence/lean_build_original.log`.

Commands (run from repository root unless stated):

```sh
curl -fL --retry 2 -o audit/toolchains/lean-4.14.0-darwin_aarch64.tar.zst https://github.com/leanprover/lean4/releases/download/v4.14.0/lean-4.14.0-darwin_aarch64.tar.zst
python3 -m pip install --target audit/toolchains/python-zstd zstandard
# Extract with zstandard.ZstdDecompressor().stream_reader and tarfile.open(mode="r|").
cp -R lean4 audit/build-original/
export PATH="$PWD/audit/toolchains/lean-4.14.0-darwin_aarch64/bin:$PATH"
cd audit/build-original/lean4
lean --version
lake --version
lake build
```

2. `tar --zstd` initially failed because `/usr/local/bin/zstd` is an x86_64 Mach-O binary not runnable in this arm64 process. Local Python `zstandard` extraction succeeded. This is an environment failure, separate from Lean source failures. Likewise native Lake's first dependency fetch failed because `/usr/local/bin/git` is x86_64. Native `/usr/bin/git` works; subsequent commands use `PATH="$LEAN_AUDIT_BIN:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"`. Dependency logs are in `evidence/lean_dependencies_original.log` and `evidence/lean_dependencies_native.log`.

3. In the **diagnostic copy only**, remove the erroneous `name := "selltc"` line, shallow-clone mathlib tag v4.14.0, and run `lake update`. The original tracked source remains untouched. Further module diagnostics after dependency retrieval will be added here; this intervention does not turn the failed original build into a passing build.

4. The checked-out mathlib tag resolves to `4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84`. Source inspection verifies that `Mathlib/LinearAlgebra/Dual.lean:739` **does** define `Submodule.exists_dual_map_eq_bot_of_nmem`; the README's claim that this was an erroneous preliminary API is itself erroneous. Its result is `∃ f : Dual R M, f x ≠ 0 ∧ p.map f = ⊥` given `x ∉ p` and freeness of the quotient, which supplies the intended separation route over a field.

The initial audit is complete as a source audit plus failed clean-build diagnosis. No statement is claimed kernel-verified. Dependency setup and deeper compiler diagnostics continue to support the repair phase.

