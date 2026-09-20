# Editorial and repository initial audit

Audit date: 2026-09-20. Baseline: `6bb47d9781d813dff526e043c9d0ad35d37ed0a4`.

## Provenance and inventory

The authenticated GitHub connector confirms that the supplied folder is the current `main` revision of the private origin. The source archive and checksums are recorded in `SOURCE_PROVENANCE.md`; every tracked file is listed in `evidence/baseline-inventory.txt`. The surrounding `logic_reader_adjusted2_layout.tex` is an earlier 63 KB article-format manuscript with an experimental plan, while the tracked 93 KB LMCS manuscript adds the experiments and Lean claims. Both surrounding files and the original ZIP are preserved unchanged. The tracked manuscript is the reconstruction target.

The baseline PDF has 29 letter-size pages, was produced on 2026-05-02, and displays the same title/author as the source. Its first page was rendered and inspected. The abstract substantially exceeds LMCS's recommended 20 lines. Clean baseline compilation with installed `pdflatex` could not start: its executable is x86_64 while this host is arm64 (`bad CPU type in executable`). This is an environment failure, not a LaTeX finding. An isolated arm64 Tectonic 0.17.0 compiler is being used for the subsequent reproducibility check.

## Verified issues

| Severity | Location | Finding / required correction |
|---|---|---|
| Blocking | Abstract; contributions; Section 9; READMEs | Lean success/ML and invariant-completion claims contradict source. The artifact is not a verified checker merely because some bodies lack literal admissions. |
| Blocking | Section 6, adequacy | Logged endpoints, multiplicities and delayed propagation invalidate the presented proof; see `LOGIC_INITIAL.md`. |
| Major | Introduction, paragraphs on SELL necessity | Ordinary rewriting can read a fact by consuming and reproducing it, and ordinary `!` can hold both persistent predicates. Two labels are organizational, not necessary for these rules. |
| Major | Failure-soundness proof | Must establish that *every* compatible codeword extends each forced trace assignment, not just invoke a residual equivalence for an already fixed partial assignment. |
| Major | Complexity proposition | Both branches must include input initialization and trace replay: `O(n+m+|E|)` with adjacency lists and word-size indices. Dense conversion costs `Theta(mn)`; isolated checks/variables cannot be ignored. The claimed universal lower bound does not follow from this implementation's updates. |
| Major | Certificate-size remark | General trace cost is `O(t(log(m+1)+log(n+1)+1))`, plus residual/failure bits. `O(n log n)` assumes `m` polynomial in `n`; it does not “match” an `O(n)` bit output bound. |
| Major | ML theorem | State epsilon's domain explicitly, handle endpoints or restrict to `(0,1)`, and distinguish likelihood maximization, uniqueness, exact recovery and posterior inference. The BSC remark about “different consistent completions” is misleading for an unerased observation. |
| Major | Implementation documentation | Deleted module is still listed as present; notebook actually regenerates it with `%%writefile`. `finalize.sh` is also listed but absent. Root README repeats the repository inventory. |
| Major | Section 10 figures/table | Captions assert empirical linearity and the wrong aggregation condition; original data are preserved and numerical discrepancies documented independently. |
| Major | Novelty | Classical hybrid decoding, algebraic separators, certifying algorithms and formal ECC libraries predate this work. A SELL label by itself establishes neither necessity nor novelty. |
| Editorial | Abstract; repetitive remarks | Remove speculative line-count estimates for missing proofs and repeated defensive explanations of triviality. Give exact theorem and implementation scope. |
| Editorial | References | LMCS currently requests BibTeX with alphaurl (or equivalent), DOI where available, and the current class. Baseline uses a manual bibliography and no DOI metadata. |
| Major | Artifact access | Origin is private. Public reproducibility cannot be claimed before the author explicitly authorizes artifact release; no release is authorized now. |

## Current LMCS requirements (checked against official pages)

LMCS covers logic-related theoretical and practical computer science, including verification, formalized mathematics and semantics. This supports topical relevance; it does not establish sufficient scientific novelty. Its author guidance requires English, normally at most 50 pages, an introductory section, and a concise abstract normally no longer than 20 lines. Submission requires a prior arXiv/CoRR posting including TeX sources and cs.LO classification; no submission or posting is performed in this task. See [author information](https://lmcs.episciences.org/page/authors-information) and [purpose](https://lmcs.episciences.org/page/purpose).

For final production LMCS specifies its current class, BibTeX/alphaurl or an equivalent setup, ORCIDs, consistent references, no changed default font and no overfull boxes. It encourages DOI references and durable artifact hosting. See [LaTeX style](https://lmcs.episciences.org/page/authors-latex-style). The current class is downloaded only to `audit/evidence/lmcs-current.cls` for comparison at this audit stage. These formatting changes cannot repair an insufficient contribution.
