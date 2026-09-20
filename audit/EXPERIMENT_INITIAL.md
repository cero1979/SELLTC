# Initial experimental and implementation audit

Audit date: 2026-09-20. Baseline commit: `6bb47d9`. This report concerns the original notebook, original output files and empirical/complexity claims in the original manuscript. No existing implementation, manuscript, notebook or data was changed during this audit. Files under `audit/` contain only inspection copies, probes and newly derived audit evidence.

## Scope and reproducible evidence

All 14 notebook cells were inspected, including the complete 1,049-line embedded module. The following were inspected: every original CSV schema and grouped values; `manifest.json`; all summary-producing and plotting functions; relevant manuscript sections; README; deleted module in Git history; local and bundled Python environments. `audit/notebook_cell2_original.py` preserves the original notebook source including the `%%writefile` line. `audit/removed_module_original.py` is `git show HEAD^:selltcfull_experiments.py`. Removing the magic line from the notebook gives an exact line-for-line match with the deleted module.

Execute:

```sh
/Users/cero/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 audit/experiment_initial_probe.py > audit/experiment_initial_probe.log
```

The probe uses the unmodified original numerical algorithms. It substitutes an empty plotting import because matplotlib is unavailable in that runtime; it does not call plot functions. Outputs include exact table recomputation, runtime ratios, descriptive scaling fits, adversarial cases and exhaustive GF(2) solver tests. The correct original-data epsilon=0.40 aggregation is saved separately as `audit/original_table_epsilon040_recomputed.csv`; it does not replace original data.

Environment: bundled Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, macOS 27.0 arm64. Bundled matplotlib, IPython, Jupyter and SciPy were absent. The repository `.venv/bin/python3` is an x86_64 Mach-O executable; invoking it on this host fails with `bad CPU type in executable`. No lockfile or requirements file was found.

## Findings classified by severity

### E01 — Blocking: structural table describes a different experiment

`SELLTCFULL.tex` table caption says “100 trials at epsilon=0.40.” `summarize_table1` (embedded module lines 832–846) groups only by family, n, dv and dc. The full notebook passes all 4,200 clean rows, combining seven epsilons and 700 trials per family/size. Every numeric column of the committed table matches this pooled aggregation to floating-point tolerance (1e-12).

Examples:

| Family | n | Published mean trace | Correct at .40 | Published residual size | Correct at .40 |
|---|---:|---:|---:|---:|---:|
| PEG-style | 1000 | 261.551429 | 391.02 | 157.251429 | 9.05 |
| PEG-style | 2000 | 521.075714 | 789.52 | 318.925714 | 11.64 |
| PEG-style | 5000 | 1324.134286 | 2003.71 | 775.352857 | 0.00 |
| Random regular | 1000 | 256.417143 | 378.51 | 163.897143 | 23.27 |
| Random regular | 2000 | 531.875714 | 798.40 | 306.810000 | 0.00 |
| Random regular | 5000 | 1346.798571 | 2004.67 | 753.272857 | 0.00 |

Fix: filter explicitly or retain epsilon in grouping and publish separate conditions. Do not rewrite original CSVs.

### E02 — Blocking: empirical linear-scaling and timing claims contradict data

The Figure 3 caption claims seconds, log-log axes and a fitted slope near 1. The actual PNG and `plot_checker_scaling` show milliseconds on ordinary linear axes, without any fit. Descriptive least-squares log(time) versus log(n) fits of the three committed summary points yield:

| Family | Slope | Timing increase when n increases 5-fold |
|---|---:|---:|
| PEG-style | 1.786613 | 17.465783-fold |
| Random regular | 1.831602 | 18.801054-fold |

These three-point fits describe these measurements; they are not asymptotic complexity proofs and have no matrix-level replication. They plainly do not confirm linear scaling.

Figure 2 caption says epsilon=0.40 and checker consistently below residual solve. The plot actually includes the full epsilon grid. The checker exceeds residual solve in 19 of 42 grouped conditions, including all six conditions at epsilon=0.40:

| Family | n | Residual time (ms) | Checker time (ms) |
|---|---:|---:|---:|
| PEG-style | 1000 | 0.368060 | 2.490042 |
| PEG-style | 2000 | 0.645387 | 6.673921 |
| PEG-style | 5000 | 0.018159 | 35.626875 |
| Random regular | 1000 | 0.969766 | 2.451849 |
| Random regular | 2000 | 0.017799 | 6.882074 |
| Random regular | 5000 | 0.030642 | 38.811678 |

The Figure 4 caption describes dashed failure curves; both acceptance curves are solid in the plotting code. Regenerate figures and rewrite literal descriptions.

### E03 — Blocking: checker accepts values outside its mathematical output type

`check_success_certificate` converts witnesses with `astype` rather than validating canonical binary values. Reproduced:

```text
H = [[1,1]], y = [-1,-1], T = [], rho = [2,2]
returns (True, array([2,2], dtype=int8))
```

Thus the claimed Python output need not belong to F2^n. Fractional rho `[0.1,0.1]` and trace bit `0.1` are silently rounded to zero and accepted. A witness `[3]` is accepted for H=[[1]], y=[1], although the declared certificate type requires bits. Scalars and truncated trace tuples raise exceptions rather than reject. The caller contract currently neither enforces nor safely parses the declared types.

Fix: validate dimensionality, exact lengths, integer index types, binary values, bounds and trace integrity before state updates; return rejection for malformed certificates. Trusted inputs H and y also need a checked construction boundary. Optional precomputed adjacency is part of the trusted representation and must not be freely supplied inconsistently.

### E04 — Important: published runtime “overhead” has the wrong denominator

`run_hybrid_decoder` calls the wall interval including checker `decoder_time_s`. Stored `hybrid_time_s` is therefore total time. Stored `overhead_ratio` is `T_check/(T_total-T_check)` (relative extra time), but the table calls it checker/total.

These are different metrics. The pooled group statistics below show all four useful aggregations; averaging ratios is not taking ratios of means.

| Family | n | mean(check/decode) | mean(check)/mean(decode) | mean(check/total) | mean(check)/mean(total) |
|---|---:|---:|---:|---:|---:|
| PEG-style | 1000 | .634484 | .206473 | .322774 | .171138 |
| PEG-style | 2000 | .691310 | .158672 | .331781 | .136943 |
| PEG-style | 5000 | .765528 | .082252 | .343443 | .076000 |
| Random regular | 1000 | .621934 | .194144 | .315613 | .162580 |
| Random regular | 2000 | .725176 | .162698 | .343102 | .139931 |
| Random regular | 5000 | .790436 | .081130 | .351434 | .075042 |

Initialization is inside peeling time; dense residual construction falls between peeling and residual timing and is included only in total. Adjacency construction is performed per trial but excluded from reported decoder/checker timings. Witness extraction is bundled with elimination. None of these exclusions should be hidden in a new campaign.

### E05 — Important: implementation is dense despite sparse terminology

Source locations refer to the preserved module cell:

- `build_adjacency` lines 93–96 scans every dense row and column: O(mn) preprocessing.
- `initialize_state` lines 287–300 performs dense masked products and sums: O(mn).
- `residual_system_from_state` lines 303–307 allocates/copies an m by |U| dense array.
- Both checkers reconstruct dense residuals; success also computes the full dense `H @ x` (lines 475–481), costing O(mn) even after complete peeling.
- `gf2_solve` lines 365–431 holds dense A and an m by m row-operation matrix. `strategy='sparse'` changes only pivot/column heuristics; it is not sparse storage. Row/column-weight calculations add dense scans.

For the constant-degree family m=n/2 and |E|=3n, dense checker matrix work is quadratic in n. Its use of adjacency for incremental trace updates does not eliminate dense initialization/final validation. A linear graph algorithm can be implemented, but is not this implementation.

The abstract complexity statement also omits general input costs: both branches read y (n positions), state/witness rows (m positions, including isolated checks), and E edges. State a uniform O(E+n+m+|T|) word-RAM bound with a prevalidated adjacency representation; then under m=O(E+n), simplify to O(E+n). Trace triples cost O(log m + log n) bits, so success certificate size is O(|T|(log m+log n)+|U|), with an additional m bits for failure. The current O(n log n) simplification requires a relation between m and n. The tightness proof assumes its specific update algorithm is mandatory and does not establish the lower bound over all checkers. Direct full-word verification provides the same parity/channel guarantee without trace provenance at O(E+n+m).

### E06 — Important: comparisons confound algorithm and pivot heuristic

Manifest selects hybrid solver `sparse` and GE-only solver `dense`; this is the same elimination engine with different column order and pivot heuristics. Any difference combines peeling and heuristic effects. The campaign has only peeling, GE, and certified hybrid; there is no independently timed uncertified hybrid comparator or independent direct-word verifier. The `false_accept` oracle is another invocation of the same algebraic solver, so common-mode solver errors can escape this test.

Use identical algebraic engines/pivot policy for GE-only and both hybrids, time certification separately, and add direct verification with its guarantees explicitly distinguished.

### E07 — Important: robustness experiments do not test malformed certificates

All certificates are generated by the honest decoder. No original notebook cell corrupts certificates, despite the manuscript saying malformed certificates are rejected in notebook examples. The original false-accept metric records only agreement of certificate *status* with GE solvability; it neither checks returned-word domain nor independently validates the output.

Seed reconstruction of actual visible-bit flips gives:

| delta | Actually corrupted inputs | Corrupted but algebraically compatible | Accepted success |
|---:|---:|---:|---:|
| 0 | 0/600 | 0 | 600 |
| .0001 | 92/600 | 0 | 508 |
| .001 | 415/600 | 0 | 185 |
| .01 | 600/600 | 0 | 0 |

This campaign contains no corrupted-compatible example; positive success rates mostly mean no bit was flipped. Nevertheless such examples are easy and accepted correctly: H=[1 1], transmitted 00, received [1,erasure] after a visible flip admits output 11. Certificate acceptance cannot certify the originally transmitted word under corruptions. Record realized flip counts, compatibility and certificate validity separately.

### E08 — Important: success, ML completion and exact recovery are conflated

Every original trial transmits the all-zero word; the solver sets free variables to zero. All successful clean outputs can therefore equal the transmitted word even when uniqueness fails. Recorded residual size minus rank already shows 526/4,200 clean trials are nonunique; at epsilon=.50 the fraction is 515/600 = .858333 with mean nullity 27.378333. At epsilon=.46, 11/600 are nonunique, mean nullity .105. Thus 100% completion is not evidence of 100% unique recovery. Use random codewords sampled from the kernel, record exact recovery separately, and report nullity.

A valid partial trace is accepted intentionally by the algorithm: H=[1 1], both coordinates erased, empty trace, rho=[1,1] is valid. State explicitly that certification attests trace validity and a completion, not maximal peeling or the producer's internal execution history. Changing trace order is not always invalid: independent steps may commute, and a truncated trace with a correspondingly extended valid residual assignment remains valid.

### E09 — Important: replication and seed claims overstate evidence

There is one independently generated matrix per family/size (six matrices total). The 100 channel trials per condition are conditional trials on that fixed matrix, not independent matrix realizations. No hardware, exact package versions, timing protocol, warmup policy, matrix hashes, output hashes, timing repetitions or execution timestamp is stored in the manifest.

Matrix generation uses Python `random.Random`; channel generation uses NumPy `default_rng`. The notebook claims all randomness uses NumPy, which is false. Seed formulas collide: 4,200 clean rows have 3,500 distinct seeds because random_regular n=2000 and PEG-style n=1000 share matrix seed 20263427. Robustness has 1,500 distinct seeds across 2,400 rows; `round(1000*0.0001)=0` makes delta=0 and .0001 use identical erasure seeds. Such deliberate pairing could be useful but is neither declared nor consistently applied. Use documented stream identifiers, matrix identities and separate erasure/corruption generators.

The notebook's platform-independent “numerically identical results” promise is impossible for wall times. Even non-timing reproducibility requires exact Python and NumPy generator versions. The full campaign is 4,200+2,400=6,600 trials, each calling three decoder variants, not approximately 8,400 decoder calls as notebook text claims.

### E10 — Important: graph builder is PEG-inspired, not faithful PEG

`_peg_candidate_checks` traverses the entire connected component. When all checks are reachable it returns all non-excluded checks, not the farthest frontier. Concrete adjacency:

```text
var_to_checks = [[0],[0,1],[1,2]]
check_to_vars = [[0,1],[1,2],[2]]
variable=0, exclude={0}
```

Check distances are 1,3,5. The function returns [1,2], whereas a largest-distance choice is [2]. Label the original family PEG-inspired and avoid attributing standard PEG properties. A corrected generator requires direct distance tests and degree-profile checks.

### E11 — Important/editorial: reproducibility path exists but documentation is inaccurate

Commit `6bb47d9` removed standalone module and finalize script as redundant. README still lists both; direct import from a clean clone fails until notebook cell 2 runs. However, `%%writefile selltcfull_experiments.py` is present with the complete source; therefore **deletion alone does not prevent notebook reproduction**. Prefer a tracked authoritative module and a notebook that imports it, eliminating duplicate code and generated source.

No execution outputs are saved in the notebook. RUN_FULL defaults False; default Run All performs smoke work and reads pre-existing output files, so file-existence “validation” does not show a newly completed campaign. The manifest export precedes actual execution and overwrites the output-directory manifest even when a campaign is not run. New runs need separate run directories and completion metadata.

`export_table1_latex` declares 10 alignment columns (`llrrrrrrrr`) for a 13-column table. The committed LaTeX has 13 alignment columns (`llrrrrrrrrrrr`), so it was not obtained verbatim from this exporter. Both use unescaped underscored column names with `escape=False`, producing invalid ordinary LaTeX text without intervention. The figure includes are unconditional even though README says missing outputs give placeholders. The module uses Python 3.10 union type notation despite manuscript advertising 3.9+. SciPy is listed by the manuscript but never imported or required.

## Positive checks and limits

All committed numeric summary CSVs agree with the original raw CSVs under the actual aggregators. The table problem is a wrong condition/caption, not unexplained altered numeric data.

10,108 calls to the original GF(2) solver (both strategies; every 0..3 row by 0..3 column binary matrix and every RHS) agreed with exhaustive assignment enumeration. Returned solutions satisfy Ax=b; returned failure witnesses satisfy wA=0 and wb=1. This covers empty residuals, zero rows, redundant rows, determined and underdetermined systems. It is finite testing, not a proof for arbitrary dimensions.

Adversarial probes reject wrong bit, invalid check index, reversal of dependent trace, residual length mismatch and a zeroed failure witness. Type/domain and malformed-structure counterexamples above remain blocking implementation problems. No new timing campaign or figure regeneration is claimed in this initial audit.

## Proposed bounded repair and experimental campaign

1. Preserve baseline outputs and notebook as already done. Restore one tracked module; add dependency pins and a clean environment; make analysis derive figures/tables exclusively from raw run files.
2. Implement a validated adjacency graph, sparse replay using per-check degree, syndrome and XOR of unknown variable IDs; keep producer and checker separate. Implement direct sparse parity/channel checking independently. Keep a clearly named dense legacy reference for comparison. Reuse one exact elimination implementation and policy across GE and hybrids.
3. Add strict parsers and deterministic adversarial tests for bit/domain/shape/index/order/truncation modifications, including transformations that remain mathematically valid. Add exhaustive small linear-system and certificate checks against brute-force truth. A failed failure witness must not be confused with a proof of feasibility.
4. Pilot on 2 families × n in {128,256,512,1024} × 3 independent matrices × epsilon in {.30,.40,.50} × 10 channel trials (720 clean trials), plus 2 families × n in {256,512} × 3 matrices × epsilon in {.40,.55} × delta in {.001,.01} × 10 trials (480 robustness trials). This bounds dense elimination while including ambiguous completions and corrupted compatible systems. Add deterministic compatible-corruption cases regardless of random yield. Document the new seed and grid before running; it is a new campaign, not a replacement pretending to use the old parameters.
5. For each matrix, sample codewords via a precomputed kernel basis, record matrix rank/hash and trial stream IDs. Record initial erasures, actual flips, trace length, residual size/rank/nullity, exact recovery, direct validity, certificate outcome, failure-witness validity, all five comparator timings, stage timings and memory measurement method. Use repeated measurements after warmup with randomized comparator order. Distinguish graph preprocessing, which is amortized per matrix, from per-input initialization.
6. Use a separate checker scaling sweep on n in {256,512,1024,2048,4096}, 3 matrices per family and 10 trials at fixed epsilon, with repeated replay and direct checks. Compare dense and sparse checker on identical certificates. Report slopes with matrix-level bootstrap uncertainty as finite-size descriptions; do not force or proclaim an asymptotic law from fitted slopes.
7. Report conditional trial dispersion and matrix-level variability separately. Produce epsilon=.40 table through an explicit filter, both overhead definitions, relative versus ratio-of-means labels, units and actual comparator guarantees. Retain negative results, including direct checker speed advantage and exact-recovery failures in nonunique cases.

These are proposed settings, not executed results. If the pilot makes the algebraic campaign impractical, reduce trial count before execution and record the decision; do not discard runs selectively. Final claims must follow the completed data and the precise proven checker model.
