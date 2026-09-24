# Publication audit change log

Audit started 20 September 2026 and finalized after resumption on 23 September 2026. All manuscript, implementation and documentation changes are in English, on local branch `codex/publication-audit`. No push, pull request, release, arXiv posting or journal submission was performed.

## Preservation and initial diagnosis

- Confirmed that the supplied checkout matched the authenticated private GitHub origin at `6bb47d9781d813dff526e043c9d0ad35d37ed0a4`.
- Archived every tracked baseline artifact as `originals/baseline-6bb47d9.tar.gz`; preserved the old output directory, surrounding ZIP and earlier manuscript.
- Audited all original source, notebook cells, CSVs, Lean files, documentation and Git history before repair. Recorded mathematical counterexamples, compile/dependency failures, nonbinary false acceptance, misleading experimental summaries and novelty limitations.
- Committed that evidence before reconstruction (`f9beafa`). The audit remains historical evidence and is not rewritten to describe the repaired code as the baseline.

## Mathematical corrections

- Replaced the false log-free exact endpoint with an encoding that retains the accumulated log, an explicit chronological trace index, and normalized macrostep completeness for the same specified trace.
- Defined exact raw-token multiplicities and pending sets satisfying `N(j) ∩ U ⊆ Q_j ⊆ N(j)`. Derived actual operational degrees/syndromes separately from delayed rewrite metadata.
- Proved preservation, propagation stuttering, Solve validity under arbitrary interleavings, order-independent propagation normalization, global rewrite termination, soundness and full trace completeness. Included minimal lost-log and asynchronous examples.
- Made the SELL signature and operational interpretation explicit. Proved event-preserving erasure of the two persistent labels into an ordinary exponential zone and ordinary consume-and-recreate rewriting. Removed SELL necessity and unproved SELLF adequacy claims.
- Proved that every compatible original codeword extends every forced trace assignment, then established the residual bijection needed for failure soundness.
- Proved binary success soundness, left-kernel separation soundness/existence, row-transform witness extraction, and certificate existence for every valid partial trace. Covered zero rows/columns, empty residuals, redundant equations and degree-zero contradictions.
- Distinguished valid completion, maximum likelihood, uniqueness and transmitted-word recovery. Proved the BEC likelihood claim on `[0,1]` with explicit zero-probability endpoint qualifications.
- Replaced unsupported optimality claims with `O(n+m+E)` sparse word-RAM upper bounds, including initialization and early rejection of overlong traces. Separated dense conversion, producer elimination, checker cost and certificate bit size. Included the output-storage term for zero-row systems.
- Organized the substantive mathematics in local commit `493be72`.

## Lean reconstruction

- Fixed the Lake declaration, added an explicit Lean 4.14.0 toolchain and pinned dependency manifest, and made the library a real default build target.
- Rebuilt the formal state around a functional partial assignment with derived degree/syndrome. Canonical asynchronous contexts use finite pending sets and a chronological observer; malformed raw multisets remain outside this representation.
- Removed project admissions and the artificial `bec_equal_likelihood : True` axiom. Proved forced-value agreement, typed replay correctness, separator existence through genuine linear duality, success/failure soundness, residual witness equivalence and empty-trace checker completeness.
- Replaced vacuous ML with a real-valued closed-form BEC likelihood and an actual maximization theorem for `[0,1]`.
- Proved arbitrary-interleaving soundness, pending invariant preservation, propagation normalization/commutation/confluence, log-preserving completeness and same-trace equivalence.
- Added a strict executable JSON adapter and differential corpus. All 575 cases agree with Python on acceptance and accepted success words. On the audit host the Lean interpreter executes the runner; the native binary's macOS loader incompatibility is documented rather than concealed.
- Audited full theorem statements and transitive axiom dependencies; precise commands and output are in `audit/LEAN_VERIFICATION_REPORT.md`. No refinement of Python caches/parser, full raw-multiset encoding, SELL deductive calculus or Python Gaussian elimination is claimed.

## Python and experimental corrections

- Restored a single authoritative Python module instead of relying on notebook cell side effects. Enforced binary domains, integer index bounds, exact witness dimensions and the trace-length cap; malformed certificates fail closed.
- Added validated frozen adjacency, sparse cached replay and an independent full-word parity/channel verifier. Retained a dense replay comparator with an explicit prevalidated-input boundary.
- Used the same integer-bitset elimination engine and pivot rule across algebraic comparators. Separated per-input initialization, peeling, residual construction, elimination, final witness extraction, back substitution, other producer work and checking.
- Ran a new declared campaign: 720 clean trials and 480 corruption trials on 24 matrices, plus 90 checker-scaling trials on 15 other matrices. Preserved every original and new measurement. Saved deterministic stream seeds, actual matrices, source snapshots, raw hashes and environment information.
- Sampled random codewords for recovery experiments and measured residual nullity, uniqueness, exact recovery and realized visible corruption separately. Kept all-zero words only in the explicitly separate checker-scaling experiment.
- Corrected epsilon-0.40 filtering and distinguished the mean of overhead ratios from the ratio of mean times. Internal check-stage time includes the returned-word agreement assertion; standalone replay time is separate.
- Regenerated all paper figures/tables from raw data, including direct verification time/memory, stage costs, matrix-cluster uncertainty and unconstrained scaling fits. Retained negative evidence: direct checking is cheaper, some completions are nonunique, compatible corruption survives, and observed slopes are not exactly one.
- Fixed analysis-only NumPy scalar serialization and the missing Jinja2 dependency after measurements completed, without rerunning or dropping data. Archived the exact executed measurement source and identified the revised analysis source separately.
- Hardened reanalysis against live default-configuration changes and raw-data modification. Removed an inaccurate atomic-checkpoint claim. Executed the notebook and full regression suite, and independently regenerated matrices/outcomes.

## Article, literature and review

- Rewrote the English manuscript around a scoped logical specification and certifying-algorithm case study. Removed claims of a novel hybrid decoder, first formal LDPC treatment, universal linear empirical scaling, universal corruption detection and automatic exact recovery.
- Replaced the manual bibliography with verified BibTeX entries and primary references, including relevant 2026 quantum-coding preprints. Delimited their different certificate guarantees rather than asserting novelty from search absence.
- Used the current unmodified LMCS class, concise abstract, ORCID, alphaurl bibliography and native Tectonic build. Documented a narrow first-page header compatibility workaround that preserves the text-block geometry.
- Updated installation, proof scope, reproducibility, testing and build instructions. Removed duplicated inventory and references to absent files.
- Obtained independent logic/formal-methods, coding-theory and experiment/reproducibility reviews, with concrete objections and retained limitations. Final dispositions are in `audit/FINAL_REVIEW.md`; the scientific readiness decision is in `PUBLICATION_READINESS.md`.


## 24 September 2026: exact trace adequacy revision

- Repositioned the title, abstract, introduction, related work and conclusion around Theorem 6.10, delayed propagation and exact logged normalization.
- Added a fully proved abstract adequacy principle with invariant preservation, silent observers, canonical normalization and explicit local event lifting; kept the LDPC statement/proof and original theorem numbering.
- Preserved Proposition 6.12 and explained label erasure as an informative separation between resource-sensitive behavior and inessential differentiated persistent zones.
- Added a representation/evidence table that uses a raw context together with its declared event history, distinguishing informal proofs, canonical Lean results and finite Python comparisons.
- Clarified the local operational explanation obtained by trace replay, its equality with direct checking on final-word validity, and the retained direct-check performance advantage.
- Added the revision report, claim audit, abstraction note and dated verification/preservation evidence. Preserved prior audit records as historical snapshots.
- Corrected Girard (1987) journal pagination to 1--101 from the publisher record; retained all 16 references and documented the differing restored-version archive metadata.
