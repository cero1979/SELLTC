# Reviewer C: independent checker and experiment review

Date: 2026-09-23. This review was performed by the mathematical-semantics reviewer, independently of the author of the corrected Python implementation and experiment runner. The reviewer did not edit those implementations, raw CSVs, generated figures, or manuscript experiment prose. Observations were sent to their owners for correction. This report concerns the corrected campaign, not an endorsement of the preserved original results.

## Verdict and scope

No known blocking checker-soundness error, incorrect numerical denominator, missing trial, or contradiction between the reviewed experimental prose and the corrected data was found. The review identified reanalysis-integrity and wording defects, which were corrected and rechecked. The empirical results remain finite measurements of an independently written Python implementation: they are neither a proof of Python correctness nor a substitute for the mathematical or Lean theorems.

Files examined include `selltcfull_experiments.py`, `publication_experiments.py`, `tests/test_certificates.py`, `tests/test_experiments.py`, `paper/experiments.tex`, the executed-source snapshots, campaign configuration and manifest, all raw/repeated-timing CSVs, generated summaries and bootstrap intervals, and the named adversarial-case outcomes. Final notebook execution and integrated PDF visual inspection are outside this review and require their own evidence.

## Acceptance semantics and adversarial boundary

The sparse success checker validates the graph and received alphabet, caps trace length at n, rejects noninteger/Boolean indices and nonbinary values, replays only eligible unknown variables, requires an exact-length binary residual assignment, reconstructs the full word, and checks every original parity equation. Visible coordinates are preserved because replay assigns only currently unknown coordinates. Thus its full-word parity check implements the intended residual acceptance criterion without needing a separate redundant channel-consistency pass.

The degree and XOR-of-unknown-indices arrays are initialized from the validated graph and updated once per newly assigned variable. At degree one the index XOR identifies the actual unique unknown neighbor, including index zero. This makes the constant-time replay test faithful to the singleton condition. The graph constructor rejects duplicate edges and freezes consistent row/column adjacency. The per-input sparse complexity claim applies when this validated Graph is already available; passing a dense matrix to the public API additionally incurs conversion and validation.

The failure checker replays the same trace, validates an m-bit witness, accumulates its row combination only on remaining unknown columns, and checks the witness product with the residual syndrome is one. This is exactly the stated separator criterion. Degree-zero contradictions, zero unknown variables, zero rows, partial traces, and empty traces have coherent behavior. The producer no longer treats exhaustion of unknown variables as sufficient for success.

The direct verifier is independent of replay and residual state: it validates the candidate's binary domain, visible-coordinate agreement, and every row parity. The dense comparator is explicitly a timing baseline on a prevalidated dense binary matrix, not the public adversarial input checker. Unsigned byte matrix arithmetic followed by reduction modulo two preserves binary parity despite modular byte accumulation, since 256 is divisible by two.

The trust boundary does not cover arbitrary mutation of Python objects/runtime, forged trusted Graph internals, authenticated acquisition of H or y, or attestation that a producer actually followed its declared trace. The manuscript does not claim these properties. Alternative valid completions and reordered independent steps are correctly accepted; truncating a trace remains valid if the residual witness is adjusted accordingly.

## Executed verification

The reviewer independently ran:

```
.venv-publication/bin/python -m pytest -q -p no:cacheprovider tests/test_certificates.py tests/test_experiments.py
```

After the review corrections, **18 tests passed**. The suite includes exhaustive Gaussian solution/separator comparison with brute force on 5,054 small systems, exhaustive small-instance certificate outcomes, malformed-domain and trace mutations, empty-dimensional cases, dense/sparse agreement, graph-generation properties, timing identities, and saved-configuration analysis regressions.

The reviewer also executed separate read-only Python probes through standard input:

- An independent acceptance oracle enumerated every binary matrix and ternary received word for `(m,n)=(0,0),(0,2),(1,0),(1,1),(1,2),(2,1),(2,2)`, all in-range binary-labelled traces of length zero, one, or two, and all binary witnesses of the corresponding size. It recomputed unknown neighbors and parity from scratch, rather than using cached replay arrays. **64,151 success/failure decisions matched**, including invalid traces and trace lengths exceeding n.
- All **39 saved matrices** were regenerated exactly from their saved seeds with the declared construction and degree profile.
- All **1,200 clean/corruption observations** were regenerated from saved codeword, erasure, and corruption seeds. Their erasure/flip counts, producer status, trace length, residual size, rank, nullity, exact-recovery result, and certificate acceptance matched the recorded non-timing data. Sampled transmitted words passed direct parity verification.
- Every raw-file SHA-256 matched the manifest, and both archived executed-source files matched their measurement-start hashes. All saved matrix fingerprints matched their JSON adjacency files.
- The declared grid contained exactly 720 clean, 480 corruption, and 90 checker-scaling trials, 39 matrices, and 24,747 ordinary timing-repetition rows. The four trial stream seeds across clean/corruption trials gave 4,800 distinct values.
- For every trial, the reviewer checked the full algorithm-by-repetition identity set, not merely row counts; every timed repetition's order was a permutation of its intended comparators. Direct checking appeared only for success instances. The per-trial comparator fields equalled their recorded outer-time medians. Every stage decomposition came from the actual certified repetition with median internal total, and all additive stage fields matched that record.
- Every scaling trial had all three algorithms at all five repetitions, with the reported medians matching the repetitions.
- Every condition-summary cell, the epsilon 0.40/delta zero table, every matrix-cluster interval, and every finite-size scaling slope and bootstrap interval was independently recomputed and matched the generated CSVs.

These checks reproduce the non-timing outcomes and analysis, not the original wall-clock durations. The reviewer did not perform a second full timing campaign or infer that timings must reproduce exactly on another machine.

## Comparator fairness and statistical interpretation

GE-only and both hybrid modes use the same bitset elimination and row-transformation tracking implementation. Their different residual sizes reflect peeling rather than different algebra engines. The unverified hybrid still constructs a certificate; it is not a specially optimized witness-free producer. Peeling-only is incomplete, and direct verification presupposes a word and cannot certify infeasibility or trace validity. These distinctions are explicit in the manuscript and prevent interpreting verification latency as decoding latency.

The saved internal `check_s` interval includes the certificate checker and the producer/checker returned-word comparison. The separate `trace_check_s` measures the standalone invocation. The final table and prose identify the internal stage as “Check”, and state this inclusion. Outer medians and internal-stage medians are not silently equated.

The main epsilon-0.40 table uses 240 trials and excludes all other erasure probabilities. Each family/size row has 30 trials on three matrices. The mean per-trial relative ratio is approximately 1.231514 and the mean checker fraction is 0.521739. The corresponding ratios of pooled mean times are approximately 0.859 and 0.462. These are distinct estimands, computed with the intended denominators.

The clean campaign has **720 valid completions, 562 exact recoveries, and 546 unique completions**. All uniquely completable clean observations were recovered exactly; 174 residual systems were nonunique. Clean compatibility is guaranteed mathematically for correctly generated codewords and erasures; this 100% completion rate is a solver/checker observation, not evidence that the transmitted word was always recovered.

Among 480 corruption trials, **251 had a realized visible flip**, of which **151 were incompatible** and **100 remained compatible**. Thus 151/251 is a conditional detection fraction among actually corrupted inputs, whereas the corruption figure divides each bar by all 120 trials in that plotted condition. The manuscript distinguishes these denominators. It does not claim every visible corruption is detectable or that detection is globally monotone in flip probability.

The completion plot pools exactly 120 trials at each family/epsilon point across four equally represented blocklengths. The comparator plot pools 60 observations at each size across the two equally represented families. Checker-scaling timing points average 18 within-trial medians; memory points average only three profiled calls. Memory is incremental `tracemalloc` allocation, excluding preexisting inputs, not RSS or total memory footprint.

Matrices, not channel observations, are bootstrap clusters. With only three matrices per condition, the intervals have limited resolution and should remain descriptive. The scaling experiment uses a single construction, five finite blocklengths, and zero transmitted words; its slopes do not establish asymptotic complexity or ensemble-wide decoding behavior. The manuscript preserves the dense superlinear fit and direct-check speed/memory advantage rather than selecting favorable results.

## Findings, severity, and disposition

| Finding | Severity | Disposition |
|---|---|---|
| Reanalysis used live module CONFIG for bootstrap seed and replicate count instead of the saved run configuration; editing defaults could silently change old-run intervals. | Major reproducibility | Corrected: analysis loads `declared_config.json`; interval functions receive its configuration and an explicit seed base. A regression checks independence from modified live defaults. |
| `--analyze-only` bypassed declared-grid and raw-hash verification. | Major reproducibility | Corrected: `analyze` now validates the complete grid and existing manifest hashes before generating outputs. |
| The checkpoint comment claimed atomic writes although CSVs were written directly. | Editorial/operational | Corrected by removing the false atomicity claim. Interrupted incomplete directories must be preserved; completion requires grid validation. No promise of crash-atomic checkpoints remains. |
| Recovery metadata hardcoded 1,290 trials, which would be false for another configuration. | Editorial/reproducibility | Corrected: the total is derived from validated clean, corruption, and scaling counts. |
| Internal checker stage also contains returned-word agreement comparison; “Replay ms” could be mistaken for pure standalone checker time. | Major measurement definition | Corrected in generated caption/header and manuscript timing definitions. Existing measurements were preserved. |
| Comparator caption ambiguously placed ten observations “per family” instead of per matrix. | Editorial denominator | Corrected: three matrices per family and ten observations per matrix. |

The reviewer inspected the implemented corrections and reran the focused tests. These changes affect validation or analysis interpretation; the raw measurements remained unchanged.

## Remaining limits

There is no proof of Python implementation correctness or a compiler/runtime refinement theorem. Finite differential tests, including a future executable Lean comparison, cannot establish that universally. This review does not certify the hardware or the historical act of collecting a timestamp; it verifies preserved source/data consistency, exact trial coverage, deterministic outcome regeneration, and correct analysis of the recorded measurements. The final integrated notebook run, current analysis-source hash refresh, manuscript build, and visual QA must be recorded by their owning workflows before overall completion is claimed.
