# Exact trace adequacy editorial revision plan

**Goal:** Make the existing exact asynchronous trace correspondence the center of the English manuscript and push the verified revision to the existing remote branch.

**Architecture:** Preserve the certificate algebra, operational rules, Lean sources, and experimental artifacts. Add a fully proved abstract adequacy principle with explicit normalized-state lifting, then explain the existing LDPC theorem as its instance while retaining the detailed proof and numbering.

**Spec:** `audit/revision-2026-09-24/revision-specification.txt` (the user's supplied prompt).

## Constraints and review focus

- Preserve every experimental file, figure, table, seed, timing, count and interval byte-for-byte.
- Do not enlarge Lean claims: generic abstraction, raw representation bridge and label erasure remain manuscript proofs.
- Retain empty/partial traces, exact token multiplicities and logs, inconsistent-input behavior, and propagation-only confluence.
- A raw log multiset does not determine chronological order. Represent a raw context together with an event history when relating it to Lean's ordered observer.
- Completeness needs normalized event lifting in addition to forward simulation and silent normalization. State it explicitly and exhibit why omission fails.
- Direct checking proves the same final-word predicate; replay adds a declared local explanation, without producer-history attestation or a speed claim.
- Work continues on the already authorized `codex/publication-audit` branch. No main merge, new measurements, public release or submission is part of this revision.

## Inventory and dependency map

The tracked inventory and pre-edit SHA-256 values are recorded in `audit/revision-2026-09-24/`. The full manuscript consists of `SELLTCFULL.tex`, four `paper/*.tex` fragments, the generated experiment fragments and `SELLTCFULL.bib`; theorem environments are supplied by `lmcs.cls`. Figure/table generators are `publication_experiments.py` and its notebook; the independent producer/checkers are in `selltcfull_experiments.py`. Lean has six imported proof modules, a typed/JSON checker and statement/axiom audit entry points. Existing `audit/` reports describe the prior reconstruction and must remain historically identifiable.

Actual proof dependencies (not merely order of presentation):

1. Lemma 2.2 (state meaning/completion preservation) -> Lemma 3.1 (residual bijection) -> Theorem 3.3 (success soundness). Lemmas 3.1 and 3.4 (finite-field alternative) -> Theorem 3.6 (failure soundness and certificate existence for each specified trace). Proposition 3.5 supplies constructive extraction, not a premise needed for existence.
2. Definitions 6.1--6.2 and delayed-incidence identities -> initialization 6.4, propagation 6.5, Solve 6.6 and normalization 6.7. Lemmas 6.5--6.6 also yield Proposition 6.8 (global termination).
3. Lemmas 6.4--6.7 plus normalized local enablement -> Theorem 6.10. Proposition 6.8 is not required for the finite-execution correspondence; it supplies finiteness for maximal runs. Theorem 6.10, normalization/enablement and termination support Proposition 6.11's interpretation.
4. Proposition 6.12 is a separate rule-by-rule correspondence on its stated context classes, using invariant preservation for the ordinary rewriting image. It does not logically follow just from Proposition 6.11.

## Tasks

- [x] Read the complete manuscript and bibliography; inventory the repository, generated artifacts, Lean and prior evidence; obtain independent read-only mathematical, formalization and experimental/literature audits.
- [x] Revise abstract, introduction, related work, conclusion and title positioning in `SELLTCFULL.tex`; preview the pending-incidence equations and four contribution levels.
- [x] Add a named, unnumbered abstract proposition with complete proof before Theorem 6.10 in `paper/semantics.tex`. State invariant, observers, canonical normal form, forward simulation and normalized local lifting; retain the existing theorem/proof and Proposition 6.12 unchanged in meaning. Explain the four ingredients and both adequacy directions.
- [x] Clarify direct/replay interpretation in `paper/core.tex` and `paper/experiments.tex`; add a precise representation/scope table in `paper/mechanization.tex`.
- [x] Write `REVISION_REPORT.md` (A--L), `CLAIM_AUDIT.md` and `ABSTRACT_ADEQUACY_NOTE.md`; update README, readiness and changelog with a dated revision entry. Keep prior evidence historical and create a new current hash manifest.
- [x] Run the existing Python tests and non-timing reproduction checks without modifying recorded outputs; run a clean Lean build, axiom audit and statement audit. Record exact verification commands and exit codes.
- [x] Compile with cached native Tectonic, check references/citations/numbering/logs, render every page, inspect layout and repair any defects. Independently review the revised proof and claim boundaries.
- [x] Verify unchanged data/code/Lean hashes and a clean final diff; prepare the English commit and authorized `codex/publication-audit` push. The final task response records the actual remote SHA verification.

The user's explicit revision specification and push request authorize execution; no additional design approval is required. This is a manuscript revision, so validation uses proof review, existing tests, compilation and visual QA rather than implementation-mirroring new tests.


## Execution decisions and outcome

- Added the fully proved abstract proposition with multiset log observation and explicit local lifting; retained main result numbering and all 18 original result/proof blocks.
- Selected the title naming exact trace adequacy, delayed propagation and residual certificates; rationale and three alternatives are in the revision report.
- Corrected only Girard journal pagination (1--101, publisher record). All 16 references remain; this is the sole intentional departure from preserving the initial bibliography bytes.
- Used `needspace` to keep the main theorem statement together; class file and text-block geometry are unchanged.
- Fresh Lean/statement audits, 29 tests, non-timing reproduction, independent mathematical review and 27-page visual QA passed. No code/experimental changes or unresolved mathematical blockers were found.
