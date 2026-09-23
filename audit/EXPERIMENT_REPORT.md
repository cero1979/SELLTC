# Experimental repair and executed campaign report

Date: 2026-09-23. Initial-audit baseline: `f9beafa`. Original experimental files remain unchanged. All new measurements are in `publication_outputs/`; this is a declared new campaign, not a reproduction falsely attributed to the original parameters.

## Implementation and acceptance contracts

`selltcfull_experiments.py` is the authoritative implementation. The notebook imports it and `publication_experiments.py`; the duplicated `%%writefile` implementation has been removed.

The immutable `Graph` construction validates dimensions, integer incidence indices and duplicate edges, and creates both adjacency directions. Dense import/validation is explicitly outside the sparse-checker runtime. Graph generation/validation, dense conversion and kernel-basis construction are measured separately per matrix. The supplied graph and received word, the Python checker, Python/NumPy runtime and host are trusted. This is tested Python, not extracted or mechanically verified Python code.

The success checker rejects malformed certificate structure, out-of-range or noninteger indices, nonbinary or fractional bits, incorrect trace values, wrong residual dimensions and invalid parity. In particular, the audited `[2,2]` output defect is repaired. It validates each replay step using residual degree, residual syndrome and the XOR of unknown neighbor indices; then it checks the complete reconstructed word's parity. Received visible coordinates cannot be changed by a valid replay step or residual assignment. The failure checker validates the same replay and verifies the binary left-kernel witness and nonzero inner product with the residual syndrome. Both support valid partial traces, including the empty trace. An empty matrix encoded as `H=[]` uses `len(y)` as its number of columns at the public JSON boundary.

The independent direct verifier checks the final word's binary domain, visible-coordinate consistency and each parity equation. It does not replay the trace or call the producer, residual solver, or certificate checker. It establishes the same output membership and consistency properties for success, but not trace validity or impossibility. A valid trace does not attest which operations an untrusted producer actually executed.

On a validated adjacency representation, replay and each final verification branch take O(E+n+m+|T|) word operations; |T| is at most n. Matrix import, preprocessing and algebraic solving have separate costs. The GF(2) solver uses integer bitsets, fixed first-available pivots and exact row-operation tracking; it is not called sparse Gaussian elimination. A separate newly implemented dense replay checker provides a representation baseline on the same inputs and certificates. It is not an unchanged timing copy of the deleted original checker.

## Tests and reproducibility evidence

The whole repository Python test suite passed with **29 tests** in the recorded final verification at this stage (`audit/test_experiment_final.log`). These include the logic agent's tests, strict-domain regressions, rejection and valid-alternative trace cases, graph-generation checks, kernel sampling, timing denominators and saved-analysis-configuration handling.

The new solver was checked on **5,054** complete small binary matrix/RHS systems, covering every shape from 0-by-0 through 3-by-3, against exhaustive assignment enumeration. Success solutions and failure witnesses were checked directly. Exhaustive certificate/decoder tests also cover all received words on several small matrix shapes. These tests include no-variable systems, isolated or redundant checks, compatible determined/underdetermined systems and contradictions. They are finite executable evidence, not an arbitrary-size proof.

`generate_certificate_cases.py` regenerates **575** JSON differential cases: 369 accepted and 206 rejected by Python. `audit/adversarial_results.csv` records **24** named checks with expected and observed outcomes. It includes changes to the reconstructed word, trace value/order/check index, residual assignment, impossibility witness, duplicate steps, truncation, fractional values and nonbinary values. Correctly accepted transformations include commuting independent steps and truncating a trace while supplying a valid expanded residual assignment. Every named outcome matched its expectation. The independent Lean JSON runner then matched all 575 expected output objects exactly, with zero mismatches and exit status zero (`audit/evidence/lean_differential_comparison.json`). This is tested agreement on the corpus, not a refinement proof of Python.

`audit/verify_experiment_reproduction.py` reconstructed all **39 matrices**, all **1,200 decoding-trial non-timing outcomes**, and all **90 scaling inputs/traces** exactly from saved matrix/stream seeds. All 1,200 transmitted words in the decoding/corruption campaign were nonzero. The script also compared all **13 original output files** byte for byte against commit `f9beafa`; all were unchanged. Evidence: `audit/experiment_reproduction.log` and `publication_outputs/reproduction_validation.json`.

The full notebook executed successfully: all five code cells completed (`audit/notebook_execution.log`). On an existing completed output directory it validates the grid and raw checksums and regenerates every table and figure from those measurements. A fresh output path executes the declared measurements. No flag must be edited to regenerate the committed tables and figures.

## Declared and executed protocol

The configuration and running manifest were written before the first measurement. Measurement started at **2026-09-23 21:27:07 UTC**. Hardware was an Apple M3 Pro, Mac15,6, 11 reported CPU cores, 19,327,352,832 bytes of physical memory, macOS 27.0 arm64. The environment was Python 3.12.14, NumPy 2.3.5, pandas 2.2.3 and matplotlib 3.10.7. Testing/notebook packages and the later-required Jinja2 3.1.6 export dependency are pinned in `requirements-publication.txt`; the manifest records measurement and analysis environments separately.

- **Clean campaign:** 2 families × 4 blocklengths (128, 256, 512, 1024) × 3 independent matrices × 3 erasure probabilities (.30, .40, .50) × 10 channel trials = **720 trials**.
- **Corruption campaign:** the same family/matrix construction at n=256,512 × 3 matrices × epsilon=.40,.55 × nominal visible-flip probabilities .001,.01 × 10 trials = **480 trials**.
- **Separate checker scaling:** random-regular graphs at n=256,512,1024,2048,4096 × 3 independent matrices × 6 patterns at epsilon=.40 = **90 trials**. This experiment uses the all-zero codeword to avoid algebraic solving. It measures checker behavior, not recovery probability. Each checker performs one untimed validating/warmup call before five timed repetitions in randomized order.

The random-regular ensemble is a uniform socket pairing conditioned on no parallel edges. The second family is a capacity-constrained maximum-distance PEG variant: it chooses unreachable checks first, otherwise maximum graph distance, then minimum current degree, with seeded tie breaking and restart on dead end. This corrects the original distance-selection defect but does not claim that every published PEG variant has identical distribution.

For the decoding campaign, codewords are sampled uniformly from a deterministic kernel basis. Matrix, word, erasure, corruption and timing-order streams have explicit namespace labels. The seed is a 64-bit prefix of SHA-256 of a canonical JSON list containing the base seed and labels. NumPy PCG64 is used through `default_rng`. All **4,800 trial-purpose seeds** are distinct; no collision or accidental pairing was observed. Matrix seeds, matrix hashes and graph adjacency files are saved.

## Timing definitions and comparators

The five requested comparisons are peeling-only, GE-only, hybrid, certified hybrid and direct verification of a complete output. All algebraic comparators use the same exact elimination engine and pivot rule. Uncertified hybrid still constructs the same certificate; its difference from certified hybrid is execution of the checking stage. Direct verification has no failure-certificate analogue and is therefore absent for infeasible inputs.

There are also independently timed sparse replay and dense replay checks on the same certificate. Each decoding-trial function gets one untimed warmup, followed by three timed repetitions in a deterministic randomized order. There are **24,747** saved decoding/checking timing records and **1,350** separate scaling timing records. The actual certified repetition with median total time supplies the stage values, so stages and denominator definitions refer to one observed run, not an artificial combination of medians.

`total_s` is the producer's internal full wall interval. `check_s` is its internal check-stage interval, which includes the checker call and, for success, comparing the checker's reconstructed word with the producer's word. It therefore must be called **check-stage time**, not pure replay time. `trace_check_s` is the separate standalone sparse-checker measurement and is used for standalone-checker comparisons. The certified comparator's outer call time is recorded separately as `certified_s`.

Define D=`decode_s`=`total_s-check_s`, C=`check_s`, and total D+C. The relative overhead is C/D; the check-stage fraction is C/(D+C). `condition_summary.csv` reports both the mean of per-trial ratios and the ratio of mean times, with distinct column names. Neither is silently substituted for the other.

The stages are initialization, peeling, residual bit-row construction, elimination, final witness extraction/dispatch, back-substitution, other producer work, and checking. Row-operation tracking needed to construct a failure witness is part of elimination. The tiny witness stage on successful cases is dispatch/bookkeeping, not extraction of a failure vector. Other includes input parsing, word reconstruction and timing overhead. Graph generation/validation, dense conversion and kernel construction are excluded from per-input times and separately measured. No claim of negligible certification overhead is made: at epsilon=.40 across the fixed mixture, mean C/D was **1.231514**, and mean C/(D+C) was **0.521739**.

Memory uses `tracemalloc` peak incremental Python-tracked allocation on a separate invocation, not process RSS. Preexisting graph, dense matrix and certificate storage are excluded. NumPy allocations reported through its tracking hooks can contribute. Memory is measured on trial zero of each clean condition and each scaling matrix. Thus memory/time results are protocol-specific, and should not be presented as total decoder memory.

## Main observed results

| Quantity | Observed result |
|---|---:|
| Clean valid completions | 720/720 |
| Clean exact recovery | 562/720 = 78.0556% |
| Clean nonunique residual systems | 174/720 |
| Actual corrupted inputs | 251/480 |
| Corrupted inputs still admitting a completion | 100/251 |
| Incompatible corrupted inputs / accepted failure certificates | 151/251 |
| Generated certificates accepted | 1,200/1,200 |

At epsilon=.30, .40 and .50, exact recovery rates were respectively 238/240, 238/240 and 86/240. Uniqueness rates were 238/240, 237/240 and 71/240. All three conditions still had 240/240 compatible completions. Exact recovery in a nonunique instance is possible and distinct from uniqueness.

At epsilon=.40, every actually corrupted sampled input was incompatible (136 of 240 trials had flips). At epsilon=.55, 115 of 240 trials had flips and 100 of those remained compatible. This directly demonstrates why nominal corruption probability, realized corruption and algebraic inconsistency must be reported separately. An accepted completion under corruption need not be the transmitted word.

The table below gives descriptive log-log slopes across the five checker sizes. Percentile intervals resample the three independent matrix identities at each size, with 2,000 deterministic bootstrap replicates.

| Checker | Slope | 95% matrix-bootstrap interval |
|---|---:|---:|
| Sparse replay | 1.045791 | [1.032700, 1.061713] |
| Direct word verification | 1.005779 | [1.002871, 1.008460] |
| Dense replay | 1.582635 | [1.554521, 1.616569] |

These are finite-size measurements, not proofs of asymptotic complexity. They describe this machine, code and fixed epsilon. Three matrix realizations per size give limited ensemble uncertainty information; the intervals do not cover machine-to-machine or day-to-day timing variation.

At n=4096, mean median time was **4.546273 ms** for sparse replay, **2.965861 ms** for direct verification and **49.574264 ms** for dense replay. Mean tracked peak allocations were **192,459**, **73,768** and **5,216,347 bytes**, respectively. Direct checking was faster and used less tracked memory than replay. Replay's additional guarantee is validity of the declared trace, not a stronger codeword or ML guarantee and not proof of the producer's internal history.

## Generated artifacts and analysis integrity

The manuscript-facing files are generated from raw CSVs:

- `table_epsilon040.csv/.tex`: exact epsilon=.40 subset, 30 trials per family/size, with readable family labels and explicitly labeled check-stage time.
- `runtime_stages_epsilon040_ms.csv` and `runtime_stages_epsilon040.tex`: stages in milliseconds, equally pooled over the two declared families; 60 trials per n.
- `scaling_slopes.csv/.tex`: finite-size slopes and matrix-bootstrap intervals.
- `condition_summary.csv`, `matrix_cluster_intervals.csv`, `checker_time_memory_summary.csv`, `results.json`, `results.tex` and four PNG figures.
- `raw_clean.csv`, `raw_robustness.csv`, `raw_scaling.csv`, per-repetition timing CSVs, matrix metadata and saved adjacency files.

All four figures were visually inspected. Independent Reviewer C additionally reproduced the matrix/outcome and timing aggregations and checked 64,151 small-instance acceptance decisions; see `audit/REVIEW_C_EXPERIMENTS.md`. No original CSV or figure was edited. `analyze()` validates the complete trial grid and recorded raw hashes before analysis. Bootstrap settings and base seed come from the saved `declared_config.json`, not whatever live configuration a later user happens to set.

The measurement phase completed before two postprocessing failures: NumPy integer group keys were initially not JSON serializable for bootstrap seeding, then pandas LaTeX export revealed a missing Jinja2 dependency. Both were repaired after preserving the data. `--finalize-existing` validated the complete grid and finalized the existing measurements; nothing was selectively rerun or dropped. Exact source snapshots in `publication_outputs/source/` match the code hashes recorded before measurement. The current source additionally fixes empty-matrix JSON inference and analysis workflow issues; the manifest records its analysis identity separately. The replay verification confirms the updated checker reproduces every non-timing outcome.

## Reproduction commands

```sh
python3.12 -m venv .venv-publication
.venv-publication/bin/python -m pip install -r requirements-publication.txt
.venv-publication/bin/python -m pytest -q
.venv-publication/bin/python publication_experiments.py --output publication_outputs
.venv-publication/bin/python generate_certificate_cases.py
.venv-publication/bin/python audit/verify_experiment_reproduction.py
```

To collect new timings rather than analyze the preserved run, select a fresh output directory, e.g. `--output publication_outputs_new`. The standalone checker accepts one JSON object per line via `python selltcfull_experiments.py`. Objects have exactly `H`, `y`, `kind`, `trace`, `witness`; success witness entries follow the increasing residual-variable order, while failure witnesses have one bit per check.

## Remaining scientific limitations

This is a modest local campaign, not a code-family performance benchmark. Only three matrices per condition are sampled. The PEG construction includes prescribed capacities and is described as a variant. The direct verifier and checker share trusted graph validation and binary parsing, though they have independent verification algorithms. The algebraic comparisons deliberately share one solver and therefore are not an independent algebraic proof oracle; exhaustive small enumeration and the Lean comparison provide additional evidence. Python itself is not formally verified. Timing slopes, mutation tests and complete notebook execution do not establish arbitrary-size checker correctness. The all-zero scaling experiment must not be used to infer exact recovery. No result establishes that SELL provides faster verification than ordinary parity checking.
