# Publication repair implementation plan

Goal: produce a mathematically defensible English manuscript and reproducible artifact, with an explicit account of any remaining publication blockers.

Architecture: keep the operational peeling/certificate problem, replace the false canonical equality by a delayed-propagation simulation with explicit trace history, and keep independent certificate checking separate from production. A sparse Python checker implements the stated representation; finite Lean functions receive only precisely described mechanization claims.

Specification: user-supplied publication-audit prompt, implemented through the initial audit and the deliverables listed below. Work is authorized locally on `codex/publication-audit`; no remote publication, PR or submission.

## Constraints and review focus

- Preserve original manuscript, notebook, Lean files and output data in the baseline archive and retain original CSVs.
- No artificial axioms, admissions in claimed proofs, invented data, post-hoc seed selection or forced scaling models.
- All substantive theorem changes and excluded mechanization claims must be visible.
- Rejected certificates include invalid binary domains, out-of-range indices, malformed/truncated witnesses and traces. Valid commutations and valid partial traces remain acceptable.
- Arbitrary asynchronous interleavings must not emit invalid operational traces. Duplicate tokens must be excluded by construction or exact multiplicity invariants.
- Failure witnesses must work for zero-column/zero-row and redundant systems, and all compatible codewords must preserve forced assignments.
- Distinguish clean completion, unique recovery, exact recovery, corrupted compatibility, certificate validity and provenance.
- Every experimental figure/table must derive from checked-in raw data through a tested script; repeat timings are not independent matrices.

## Phase 1: initial audit and preservation

- [x] Compare authenticated remote and local Git heads; archive baseline and record hashes.
- [x] Audit theorem inventory, Lean source, all notebook code and output CSVs, Git history and documentation.
- [x] Execute regression probes on original code and attempt original clean compilation.
- [ ] Finish independent logical report, assemble INITIAL_AUDIT, and commit initial evidence before repairs.

## Phase 2: mathematical semantics and Lean

Files: `lean4/`, `paper/semantics.tex`, `audit/LEAN_VERIFICATION_REPORT.md`, `audit/SEMANTICS_REPAIR.md`, `tests/test_rewriting.py`.

- [ ] Present minimal lost-log and duplicate-token counterexamples in the repair record.
- [ ] Define pending sets Q_j with N(j) intersect U subset Q_j subset N(j), cardinality metadata, processed-incidence syndrome and ordered trace labels.
- [ ] Prove propagation stuttering, arbitrary-Solve soundness, invariant preservation, terminating/order-independent propagation normalization, and normalized logged completeness.
- [ ] Fix compiler/Lake configuration and pin mathlib. Prove replay correctness, success/failure soundness and separator completeness with real finite algebra.
- [ ] Replace True-valued ML with a genuine likelihood comparison if feasible; otherwise remove it from Lean's theorem claims and keep a complete manuscript proof.
- [ ] Compile each affected module and inspect theorem axiom dependencies. Compare executable Lean/Python acceptance if feasible; label finite testing accurately.
- [ ] Commit mathematics/formalization changes with exact verification evidence.

## Phase 3: Python and experimental reproduction

Files: `selltcfull_experiments.py`, dedicated support modules/tests as needed, `requirements.txt`, `SELLTCFULL_experiments.ipynb`, `publication_outputs/`, `audit/EXPERIMENT_REPORT.md`.

- [ ] Write regression tests for original nonbinary and malformed-certificate counterexamples, linear-system edge cases and permitted partial/commuting traces.
- [ ] Restore an authoritative module; implement validated adjacency and sparse replay; implement independent full-word verification.
- [ ] Use the same exact algebraic engine for GE-only and both hybrid comparators. Record all initialization, peeling, residual, elimination, extraction and check stages.
- [ ] Record a deterministic campaign configuration before running. Include independent matrices, random codewords, nullity/exact-recovery metrics, corruption compatibility, direct verification and separate memory/scaling sweeps.
- [ ] Execute the campaign, retain every outcome, regenerate figures/tables, and verify them directly from the CSVs. Original outputs remain unchanged.
- [ ] Execute notebook in a clean output path and commit code/data/tests together.

## Phase 4: manuscript and bibliography

Files: `SELLTCFULL.tex`, `SELLTCFULL.bib`, `paper/`, `SELLTCFULL.pdf`, `README.md`, `CHANGELOG_PUBLICATION.md`, `audit/NOVELTY_AND_LITERATURE.md`.

- [ ] Write complete corrected proofs and explicit examples; distinguish the SELL-inspired transition semantics from a deductive SELLF adequacy theorem.
- [ ] Explain ordinary rewriting, one ordinary exponential and two persistent labels without an unsupported necessity claim.
- [ ] State O(E+n+m) in its actual representation/model; give general bit-size bounds; compare direct validation with trace certification.
- [ ] Include only executed empirical results and accurately stated mechanization status. Verify bibliography against primary publications and current LMCS guidance.
- [ ] Use current LMCS class and alphaurl bibliography, compile with a working native TeX engine, resolve cross-references and inspect every rendered page.
- [ ] Update installation, testing, reproduction and limitation documentation, then commit.

## Phase 5: independent review and readiness

- [ ] Obtain distinct logic/formal-methods, coding-theory, and experiment/reproducibility reviews with concrete locations.
- [ ] Correct verified objections and rerun affected checks; retain unresolved objections.
- [ ] Write `audit/FINAL_REVIEW.md` and `PUBLICATION_READINESS.md`, state what is proved/mechanized/executed and what remains unresolved.
- [ ] Verify clean branch status and organized local commits; report artifacts and publication limitations without claiming journal readiness by default.
