# Reviewer B: independent coding-theory and interpretation review

Date: 2026-09-23. This is a fresh review of the final English manuscript, performed independently of its authoring and the earlier checker/experiment review. No manuscript, implementation, or data files were changed. The only authored deliverable is this report.

## Verdict and scope

**No blocking mathematical error or unsupported experimental conclusion was found in the reviewed coding-theory scope.** The proofs supply the necessary forced-assignment argument, residual bijection, success/failure soundness, and existence of exactly one certificate status. Degenerate dimensions, inconsistent observations, endpoint channel probabilities, and nonunique completion are treated correctly. The complexity statement is explicitly about a validated sparse representation and a word-RAM; it is not presented as an unconditional Python or hostile-byte-stream bound.

The principal sources reviewed in full were `paper/core.tex`, `paper/experiments.tex`, and `SELLTCFULL.tex`. I also examined the generated result text/tables, `publication_outputs/results.json`, the relevant CSV summaries and raw outcome fields, and the checker/solver/graph-generator/timing portions of `selltcfull_experiments.py` and `publication_experiments.py` where needed to assess the manuscript's claims. I read `audit/REVIEW_C_EXPERIMENTS.md` to identify its distinct reproduction scope; I did not merely adopt its mathematical verdict or repeat its full campaign.

This review does not assess the rewriting/SELL proofs, Lean coverage, bibliography completeness, final PDF layout, notebook execution, or publication-release access. Those are separate review responsibilities. It does not prove Python correctness or reproduce historical wall-clock measurements.

## Mathematical objections examined and disposition

| Topic and source location | Independent assessment | Status |
|---|---|---|
| Forced assignments: `paper/core.tex:38–61` | The induction first preserves the exact known-sum and unknown-degree meanings, then uses the witnessing parity equation to force the newly assigned bit in every compatible codeword. Inconsistency makes the completion-preservation assertion vacuous without invalidating state coherence. No assumption of successful decoding is smuggled into the proof. | Pass |
| Residual bijection: `paper/core.tex:86–107` | Filling a residual solution gives all original parities, and completion preservation gives the converse even for a nonmaximal trace. Restriction and filling are explicit inverse maps. The claim concerns the original visible symbols, not merely agreement with an arbitrarily extended assignment. | Pass |
| Success contract: `paper/core.tex:109–145` | Binary domains, index bounds, witness length and replay validity precede acceptance. An empty unknown set still leaves all original rows to check. The result is a compatible codeword, with no unsupported exact-recovery conclusion. | Pass |
| Finite-field alternative and Gaussian separator: `paper/core.tex:147–207` | The column-space functional construction proves existence; the product contradiction proves exclusivity. Recording elementary row operations supplies the actual left-kernel witness. The echelon argument establishes that an inconsistent system produces a zero coefficient row with right-hand side one. Redundant equations and zero columns do not require full row rank. | Pass |
| Zero dimensions: `paper/core.tex:165–166`, `179–187`, `379–383` | With zero rows, the zero vector is in **F₂^q**, so its dimension remains q. With zero columns, the empty assignment solves exactly the zero right-hand side; otherwise a nonzero right-hand-side coordinate supplies a separator. The dense-construction bound contains the necessary standalone q term for returning a q-bit solution when m=0. | Pass; previous concerns independently rechecked |
| Stopping sets on inconsistent inputs: `paper/core.tex:63–84` | The first-removed-member proof is structural and does not assume a compatible codeword. Maximality refers to availability of degree-one steps, not early termination on a contradictory degree-zero row. The text expressly separates erasure removal from acceptance and preserves degree-zero contradictions. | Pass |
| Multiplicity and exact recovery: `paper/core.tex:209–224` | The affine-kernel parameterization gives exactly 2^(|U|−rank) solutions. Clean-channel truth is one of them; uniqueness forces recovery, but success alone does not. The later nonunique exact recoveries are consistent with this statement. | Pass |
| BEC endpoints and impossible observations: `paper/core.tex:226–257` | The product definition resolves ε=0, ε=1, and empty-coordinate cases. A compatible word remains an ML maximizer even when every likelihood is zero. The equality between maximizers and compatible words is restricted to an interior ε and existing completion, and no posterior on a null event is claimed. | Pass |
| Corruption and trust: `paper/core.tex:283–313` | The explicit `(1,*)` example shows valid acceptance of a word different from the transmitted word. The certificate authenticates neither the supplied matrix nor the actual producer history. Rejection of one alleged failure witness is not misrepresented as evidence of satisfiability. | Pass |

The certificate completeness theorem is correctly an existence assertion for a suitable witness after **every valid finite trace**, including the empty trace. It does not claim that arbitrary purported witnesses pass or that exactly one witness exists.

## Representation and cost review

`paper/core.tex:315–365` distinguishes dense preprocessing from checking on validated row and column adjacency. Retaining the m term is necessary for arbitrarily many isolated checks and is done explicitly. The unknown-index XOR is a valid singleton identifier once the degree is one, including a zero-based index of zero. Each replayed variable is newly assigned; summing its adjacency visits over the trace visits at most all graph incidences once. Initialization and the success or separator products use another constant number of passes. This justifies the stated O(n+m+|E|) upper bound and storage on the declared word-RAM.

The length cap at `paper/core.tex:114–118` and `343–345` is present before unrestricted trace processing. The executable `_parse_trace` at `selltcfull_experiments.py:133–144` rejects a list/tuple longer than n before iterating over entries. The mathematical text also explicitly excludes the bytes already consumed by a parser that materializes unbounded hostile input. Thus the cap does not silently turn a JSON parser into a streaming bounded-time parser.

The trace-bit formula at `paper/core.tex:367–377` pays for both check and variable indices and separates the binary witness from the trace. The text acknowledges that index operations are not constant-time in a bit-complexity model; the abstract word-RAM bound must continue to be read with that qualification. A full word is already a sufficient n-bit success witness for parity and visible-coordinate agreement, and the manuscript appropriately says the trace adds an explanation rather than stronger final-word validity.

The dense elimination bound at `paper/core.tex:379–387` is a conservative elementary-bit-operation bound for the stated straightforward dense array algorithm, including the m transformation columns, initialization, pivot searches and the returned q-coordinate solution. It does not claim that the measured Python integer-bitset engine realizes that exact dense cost. Recording transformations may be expensive; no universal hybrid speedup is inferred.

## Scientific interpretation of experiments

The manuscript treats the decoding and linear algebra as classical (`SELLTCFULL.tex:68–73`, `108–117`) and locates the claimed case-specific work in the operational correspondence (`81–90`, `130–139`). Aggregating familiar decoding, certification and proof-assistant ingredients is not itself asserted as novelty. Assessing the correctness or novelty of the rewriting theorem is Reviewer A's separate task.

The experimental comparison is scientifically qualified in the relevant places:

- `paper/experiments.tex:44–76` uses the same elimination engine with row-transform tracking across GE-only and hybrid pipelines. It says that the unchecked hybrid still constructs a certificate; the comparison isolates checker execution rather than a hypothetical witness-free producer. It distinguishes standalone checking, the wrapper's returned-word comparison, and internal versus outer timers.
- `paper/experiments.tex:98–143` separates compatible completion, exact recovery, uniqueness, and peeling completion. All 546 unique clean observations were recovered; the extra 16 exact recoveries are chance matches in nonunique systems. Pooling across the four sizes is declared and is not called a threshold estimate.
- `paper/experiments.tex:148–191` treats direct word checking as verification of an already available candidate, not competing decoding latency. The observed sparse/dense difference is an implementation result on the stated finite graphs and host. The dense baseline's scans are not used to disprove the abstract sparse bound. The sparse fitted exponent above one and direct checker's lower cost are retained.
- `paper/experiments.tex:78–112`, `167–191` identifies the separate all-zero-word checker workload, excludes recovery inference, describes incremental tracked allocations rather than total memory, and states that the bootstrap has only three matrix clusters per size/condition. Its narrow finite-size intervals are not promoted to ensemble-wide or asymptotic claims.
- `paper/experiments.tex:193–212` uses the correct corruption denominator: 251 actually corrupted observations out of 480, of which 151 are incompatible and 100 remain compatible. The figure's bars instead divide by all 120 trials in each displayed condition, explicitly stated. No universal detection claim or monotonicity theorem is inferred.
- `SELLTCFULL.tex:168–185` preserves these limits in the conclusion rather than withdrawing them after reporting favorable measurements.

**Optional editorial clarification, not a blocker:** Near `paper/experiments.tex:115–122`, one sentence could explicitly say that clean-channel compatibility is guaranteed by the transmitted codeword, so 100% valid completion primarily checks implementation behavior on those trials and is not an independent recovery-performance theorem. This already follows from the theory and from the clean/recovery distinction, so no correction is required for mathematical validity.

## Fresh checks executed by Reviewer B

A read-only Python probe, run with `.venv-publication/bin/python`, completed with exit code zero. It directly checked:

1. Zero-row Gaussian systems with q in {0,1,4}, requiring a returned solution of exactly q coordinates; zero-column systems with right-hand sides `()`, `(0)`, `(1)`, `(0,1)` and `(1,1)`, checking solution existence or the witness dot product.
2. An inconsistent received word whose maximal peel nevertheless removes every erasure, followed by accepted failure certification.
3. A degree-zero contradiction coexisting with a nonempty stopping residual, again producing an accepted failure certificate.
4. The compatible-corruption example, which returns the valid but wrong transmitted-word candidate `(1,1)`.
5. Oversized traces represented by a list subclass whose iterator raises if touched. Both public certificate checkers rejected these traces without iterating their entries.
6. All one-row binary parity-check codes through blocklength three, every ternary observation and ε in {0,0.4,1}: **777 likelihood cases** satisfied the manuscript's ML assertions, including the empty-coordinate case.
7. Fresh direct aggregation of raw outcome CSVs: **720** accepted clean successes, **562** exact recoveries, **546** unique completions, **zero** unique-but-inexact completions and **16** nonunique exact recoveries; **480** corruption trials, **229** with no realized flip, **251** with a flip, **100** corrupted-compatible and **151** corrupted-incompatible observations.

These small checks are supporting evidence, not substitutes for the proofs. I did not rerun Reviewer C's full matrix regeneration, 1,200-observation reproduction or timing campaign.

## Reviewed source identities

SHA-256 at review completion:

| File | SHA-256 |
|---|---|
| `paper/core.tex` | `08c8a01fc2d415e3a056368e038b158ed881db28aaae8d49c9ddfc1770966133` |
| `paper/experiments.tex` | `a0dff69d0293b4f02c6c8651206c9703cb4a82f7cf1db2f87779bea8845a8ce1` |
| `SELLTCFULL.tex` | `4faf3799a550f30a30aa59a3e69a6dd14081f27362555a8287693eabc37f37ef` |
| `publication_outputs/results.json` | `cb948732f128771bdbfd53d4f59a6b7a85c64861d515ab2702649cef86490abc` |

There are no unresolved required changes in this review's scope. The optional wording improvement above does not change the claims, numbers or interpretation.
