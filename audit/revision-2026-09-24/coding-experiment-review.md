# Coding, experiment, and literature revision audit

Date: 24 September 2026. Scope: the requested conceptual revision of the English manuscript. The initial audit was read-only; after the coordinator completed the manuscript read and recorded the revision plan, this reviewer was authorized to edit only the direct/replay explanation in `paper/core.tex` and the prose in `paper/experiments.tex`, and to write this report and the verification log. No experiment source, test, notebook, figure, table, data, seed, matrix, or bibliography was changed by this reviewer.

## Findings and disposition

No coding-theory or experimental defect requiring a theorem repair, changed number, new measurement, or regenerated figure was identified. The existing proofs correctly distinguish compatible completion, unique completion and exact recovery, including inconsistent observations and degenerate dimensions. The prior independent report `audit/REVIEW_B_CODING.md` supplies the detailed algebraic analysis; the relevant statements were reread for this revision.

The substantive editorial findings are:

1. **Specify replay's additional predicate.** The existing phrase “operational explanation” was accurate but left the reader to reconstruct what it means. The cost section now says that each declared assignment is justified by a degree-one check in the preceding operational state. It explicitly separates this predicate from final-word correctness and from attestation of the producer's actual history.
2. **Make experiments answer the semantic question.** The experimental introduction now identifies the comparison as the cost of checking that declared explanation alongside direct final-word verification. The results retain direct checking's measured advantage and explain what additional evidence replay checks. The timing comparison concerns complete checker implementations, not an isolated measurement of one replay instruction.
3. **Acknowledge the closest formal BEC antecedent.** The primary Affeldt–Garrigue–Saikawa manuscript, Section 9.1, already formalizes BEC sum-product decoding as a terminating fixed-point computation with invariants. Section 9.2 addresses an extracted sum-product implementation for the BSC. This closer BEC antecedent should be named before distinguishing exact asynchronous event traces, propagation normalization and residual success/failure certificates. The coordinator owns the related-work revision. [Primary manuscript](https://staff.aist.go.jp/reynald.affeldt/documents/ecc.pdf).
4. **Avoid treating elementary simulation machinery as a new general theorem.** The four suggested conditions of silent stuttering, forward event simulation, silent termination and unique normal form do not alone imply operational-trace completeness. A lifting/enabling hypothesis is necessary. For example, a one-state concrete system with no transitions satisfies those four conditions, while its projection may have an operational successor with no concrete realization. This was sent to the coordinator before editing; the semantics reviewer owns the abstract proposition.

## Exact prose edits

In the paragraph following Proposition `prop:core-cost`, the final-word/trace comparison now reads:

> Replay additionally checks that every declared local assignment is justified by a degree-one check in the preceding operational state. It therefore certifies a local operational explanation, not a stronger final-word correctness predicate. This explanation concerns the supplied trace, not the producer's actual internal history.

The experimental opening now identifies the measured purpose: checking a declared operational explanation alongside direct final-word verification. Near the n=4096 comparison, the added text spells out degree-one justification and the preceding state, while retaining every timing, allocation, exponent and bootstrap interval. No proof, theorem statement, label, formula, figure or table was edited. A final textual assertion confirmed that all **10 core proof blocks** are byte-identical to the starting Git HEAD and every numerical token in the experiment section is unchanged.

## Direct checking versus replay: claim boundaries

| Claim | Support and status |
|---|---|
| Both success-checking methods establish parity and visible-coordinate agreement. | Mathematical contract and independent direct verifier; unchanged. |
| Replay additionally checks validity of the supplied chronological peeling sequence. | Operational step definition, replay checker and exact trace theorem; strengthened prose only. |
| Replay authenticates the producer's actual execution history. | Unsupported and expressly excluded. An independently constructed valid explanation may be accepted. |
| Empty and partial traces are allowed. | Retained. Their suitable residual witnesses still establish the corresponding success/failure status; replay is not required to be maximal. |
| Both sparse checking approaches admit O(n+m+E) word-operation upper bounds. | Incidence-count proof with validated adjacency and bounded certificate format; unchanged. This does not imply equal constants or measured latency. |
| Direct checking is faster in the reported separate scaling experiment. | Preserved: at n=4096, 2.966 ms direct versus 4.546 ms sparse replay; the corresponding tracked allocations are 72 versus 188 KiB. |
| Checking is negligible overhead. | Rejected by the retained evidence: mean per-trial C/D=1.232 and C/(D+C)=0.522 at epsilon .40. |
| The observed difference isolates the cost of validating the trace itself. | Not claimed. Implementations also differ in parsing, reconstructed state/word handling and allocation. The new prose explicitly refers to whole checkers. |
| Direct word verification certifies infeasibility. | Not claimed; failure uses a left-kernel witness. |

The experiment still uses the same row-transformation-tracking algebraic engine for GE-only and both hybrid pipelines. The hybrid without checking still constructs a certificate. The `check_s` stage contains the wrapper's producer/checker word comparison, while standalone `trace_check_s` does not. Those definitions, the internal/outer timer distinction and all averaging denominators remain intact.

## No-new-data requirement and verification

The complete current experiment implementation, runner, certificate tests, experiment tests, corpus generator, reproduction script and notebook cells were inspected. The four existing PNG figures were viewed directly; the generated TeX tables and their CSV sources were checked against the manuscript interpretation. The relevant README, publication-readiness report, source provenance, experiment repair/report documents, independent reviews, final review and mechanization-scope cross-check were read. Preserved baseline diagnostics were treated as historical evidence, not as descriptions of the current implementation.

The following existing verification ran successfully:

```text
.venv-publication/bin/python -B -m pytest -q -p no:cacheprovider tests
29 passed in 1.44s
```

The reproduction script was then executed from an **in-memory copy**, with `__file__` set to the original `audit/verify_experiment_reproduction.py` path. Exactly one statement was replaced: the final `reproduction_validation.json.write_text(...)` became a printed summary. The source file itself was unchanged. This preserves all verification assertions and prevents rewriting the existing evidence file.

The reproduction matched:

- all 39 matrices;
- all 1,200 clean/corruption non-timing outcomes, including status, erasure/flip counts, trace/residual sizes, rank, nullity and exact recovery;
- all 90 scaling inputs and trace/residual counts;
- all 13 original output files byte-for-byte against commit `f9beafa`.

No measurement campaign, `analyze()`, `run_campaign()`, figure rendering, table export, or notebook execution was invoked. Decoder functions internally read their clocks during the reproducibility assertions, but these incidental durations were neither used nor saved as replacement measurements.

SHA-256 snapshots before and after verification cover **83 protected files**: every file under `publication_outputs/` and `SELLTCFULL_outputs/`, plus the bibliography, two experiment modules, notebook and reproduction script. **Zero files changed during that verification.** The full commands, hashes, outputs and exit statuses are in `python-verification.txt` in this directory. The preserved results JSON hash is `cb948732f128771bdbfd53d4f59a6b7a85c64861d515ab2702649cef86490abc`; the bibliography hash at verification was `b4ce1a4600c5238bff5dfbe2233937b56a46d5b70bb61a73b0fa57186bda2777`. The coordinator subsequently authorized the single bibliographic pagination correction described below; it is a deliberate later editorial change, not a change to the experiment artifacts or a failure of the earlier preservation check.

## Audit of all 16 existing references

All entries were checked for identity, their role in the current claims, and available primary metadata/content. Fresh publisher-deposited Crossref queries succeeded for 11 of the 13 non-arXiv DOIs; Luby and Burshtein requests returned HTTP 429, for which author-hosted sources supplied the necessary evidence. Several publisher landing pages presented access challenges; this is disclosed rather than described as a full-text inspection. All 16 references are retained and no reference is added. The sole recommended bibliography correction is Girard's journal pagination; the coordinator owns that edit.

| Existing key | Primary evidence and permitted role | Assessment |
|---|---|---|
| `Gallager1962` | [Publisher DOI](https://doi.org/10.1109/TIT.1962.1057683); fresh deposited metadata confirms author/title, 1962, vol. 8(1), pp. 21–28. | LDPC origin/background. The historical IRE journal title is retained even though the current deposited container name is IEEE. Publisher full text encountered its JavaScript challenge. |
| `RichardsonUrbanke2008` | [Cambridge frontmatter](https://www.cambridge.org/core/books/abs/modern-coding-theory/frontmatter/F1304B645417CD0BBCFF27C5B49A8E6E) and fresh [DOI metadata](https://doi.org/10.1017/CBO9780511791338). | Standard coding/BEC reference; 2008 print year is correct, distinct from the later online publication date. |
| `LubyMitzenmacherShokrollahiSpielman2001` | [Spielman's author record](https://www.cs.yale.edu/homes/spielman/Research/erase.html) and [published paper](https://cs.yale.edu/homes/spielman/PAPERS/eraseIT.pdf). | Confirms all authors, 47(2), 569–584, February 2001, and sparse iterative erasure-recovery background. No theorem transfers automatically to the artifact's PEG variant. |
| `DiEtAl2002Stopping` | [Publisher DOI](https://doi.org/10.1109/TIT.2002.1003839) and fresh deposited metadata confirm authors, title, 48(6), 1570–1579, 2002. | Stopping-set priority retained. Direct publisher access challenged; the primary Burshtein paper also explicitly attributes the stopping-set obstruction. |
| `BurshteinMiller2004ML` | [Author-hosted published paper](https://www.eng.tau.ac.il/~burstyn/Publications/BEC_ML.pdf), especially Sections II–IV. | Iterative decoding, residual linear systems and algebraic methods for BEC ML decoding already exist. It blocks decoder/GE-combination novelty claims. Metadata agrees with the current 2004, 50(11), 2837–2844 entry. |
| `HuEleftheriouArnold2005PEG` | [Published paper](https://www.josephboutros.org/ldpc_vs_turbo/ldpc_Hu_ITjan05.pdf) and fresh deposited metadata. | PEG precedent verified; article starts partway down printed page 386, ends 398. The capacity-constrained implementation remains explicitly a variant. |
| `Girard1987` | [Publisher article record](https://www.sciencedirect.com/science/article/pii/0304397587900454) explicitly lists volume 50, issue 1, 1987, pages **1–101**; fresh [publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1016%2F0304-3975%2887%2990045-4) has `page="1-101"`. | **Correct the journal citation to 1–101.** The [author's archive metadata](https://girard.perso.math.cnrs.fr/Archives.html) instead says 1–102, and its restored PDF has 102 PDF pages. PDF page count does not establish journal pagination. The publisher's explicit article pagination is preferred. This metadata correction changes no scientific claim. |
| `Andreoli1992Focusing` | [Primary paper scan](https://www.cs.cmu.edu/~fp/courses/15816-s12/misc/andreoli92jlc.pdf) and fresh [DOI metadata](https://doi.org/10.1093/logcom/2.3.297). | Title/author, 2(3), 297–347, 1992 confirmed. Focusing background only; its theorem does not prove this encoding's logical adequacy. |
| `NigamMiller2009SELL` | [Author-hosted paper](https://nigam.info/docs/ppdp11-nigam.pdf), title page and abstract, and fresh [DOI metadata](https://doi.org/10.1145/1599410.1599427). | The paper is PPDP 2009 despite the PDF filename. It treats location-sensitive subexponentials and focused algorithmic specifications; those results cannot be borrowed for the two-rule operational system. |
| `Necula1997PCC` | [Author bibliography](https://people.eecs.berkeley.edu/~necula/papers.html), [author PCC description](https://people.eecs.berkeley.edu/~necula/pcc.html), and fresh [DOI metadata](https://doi.org/10.1145/263699.263712). | POPL 1997, pp. 106–119 and producer/checked-evidence precedent confirmed. BEC witnesses are not presented as PCC's full code-safety framework. |
| `FeldmanWainwrightKarger2005LP` | [Author-affiliated publication page](https://research.google/pubs/using-linear-programming-to-decode-binary-linear-codes/) and fresh [DOI metadata](https://doi.org/10.1109/TIT.2004.842696). | 51(3), 954–972, 2005 confirmed. LP relaxation/decoding optimality gives related context, with a different certificate property from BEC feasibility and local trace validity. |
| `AffeldtGarrigueSaikawa2020` | [Author-hosted paper](https://staff.aist.go.jp/reynald.affeldt/documents/ecc.pdf), Sections 9.1–9.2, and fresh [DOI metadata](https://doi.org/10.1007/s10817-019-09538-8). | 64(6), 1123–1164, 2020 confirmed. Prior BEC formalization must be acknowledged explicitly; extraction and its graph/channel qualifications should not be conflated with this paper's independent Python checker. |
| `McConnellEtAl2011` | [Author-affiliated institutional record](https://researchportalplus.anu.edu.au/en/publications/certifying-algorithms/) and fresh [DOI metadata](https://doi.org/10.1016/j.cosrev.2010.09.009). | Certifying algorithms and independent witness checking are established methodology. Journal issue date May 2011 is supported despite 2010 appearing in some online/institutional records. |
| `AlkassarEtAl2013` | [Author-deposited arXiv record](https://arxiv.org/abs/1301.7462). | Authors/title, January 2013 preprint and the VCC/Isabelle mathematical-witness/checker division confirmed. Citing the inspected preprint is legitimate; no guessed final publication metadata is needed. |
| `EhatammEtAl2026LeanQEC` | [Author-deposited arXiv v1 record](https://arxiv.org/abs/2605.16523v1). | All four authors, 15 May 2026 and title confirmed. Lean quantum-code distance certificates use a verified SAT reduction; this is a different target from classical BEC trace/feasibility certification. |
| `KrishnamoorthyEtAl2026CertifiedQ` | [Author-deposited arXiv v1 record](https://arxiv.org/abs/2608.25545v1). | All eleven authors, 26 August 2026 and title confirmed. The target is degenerate quantum ML decisions through partition-function comparisons, including statistical certificates; it does not supply this manuscript's operational trace theorem. |

The source audit verifies that the references are real and appropriately delimits their use; it is not a correctness review of all external proofs. All 16 entries and citation keys are retained. The other 15 entries are unchanged; the coordinator will apply only the publisher-supported Girard page-range correction.

## Conservative positioning and title recommendations

A focused search refreshed combinations of LDPC/peeling, asynchronous multiset rewriting, formal verification, subexponentials and trace certification. No closer exact-match source was identified in those results. That observation cannot support “first,” “unprecedented,” or a field-wide absence claim. General asynchronous simulation and normalization methods should not be described as newly invented merely because this application combines them.

Suggested positive gap statement for the coordinator:

> Relative to these lines of work, the question addressed here is the exact relation between an asynchronous peeling execution and its chronological operational trace. The delayed-incidence invariant and propagation normalization establish that relation for every admissible interleaving; the residual bijection then connects the same trace to independently checkable completion or infeasibility witnesses.

This positions the actual theorem without claiming an exhaustive literature exclusion or treating aggregation as novelty. The new abstract principle, if included, should be presented as a precise factoring of the proof architecture with an explicit lifting hypothesis, not as a newly discovered universal concurrency theorem.

Three title alternatives, supplied for the revision report rather than automatically applied:

1. **Delayed Propagation and Trace Adequacy in Hybrid LDPC Decoding** — preferred: names the obstruction and central theorem while retaining the residual-algebra setting.
2. **Exact Trace Certification for Asynchronous LDPC Peeling** — most focused on the principal result; residual certificates would need prominence in the abstract.
3. **Asynchronous Peeling and Algebraic Certificates for LDPC Decoding** — accessible and precise, with less emphasis on the adequacy theorem itself.

The current title is accurate, but its SELL subtitle emphasizes a presentation whose label distinction the paper proves inessential. A title centered on delayed propagation is preferable if the final abstract and introduction likewise make the exact trace theorem the organizing result.

## Remaining limits

No required coding or experiment correction remains in this review's scope. The Girard pagination discrepancy has an explicit editorial resolution: prefer the journal publisher's 1–101 range. The coordinator owns that bibliography edit, the revised title, integrated related work, final LaTeX/Lean build and visual QA; the semantics reviewer owns the abstract theorem work. Prior build records are not substituted for those fresh checks.
