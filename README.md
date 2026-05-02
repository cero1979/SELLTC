# Certified Hybrid Decoding of Binary LDPC Codes over the BEC via SELL

This repository accompanies the paper:

> **Certified Hybrid Decoding of Binary LDPC Codes over the BEC via Subexponential Linear Logic (SELL)**

The paper develops a proof-theoretic certification layer for a hybrid LDPC decoder that combines BEC peeling (phase I) with Gaussian elimination over GF(2) (phase II). Every decoder invocation produces an independently checkable certificate — either a *success certificate* witnessing that the output is a valid codeword consistent with the received word, or a *failure certificate* witnessing infeasibility of the residual linear system. The checker runs in time *O(|E| + n)*, linear in the Tanner graph.

The central formal results are:

- **Adequacy** (Theorem thm:adequacy-complete): the SELL-style multiset-rewriting specification induces exactly the same executions as the operational peeling decoder.
- **Soundness of success certificates** (Theorem thm:sound): any certificate accepted by the checker witnesses a valid maximum-likelihood decoding.
- **Soundness and completeness of failure certificates** (Lemmas lem:unsat-witness-sound and lem:unsat-witness-complete): the failure witness is both necessary and sufficient to detect infeasibility.

The paper includes a Lean 4 mechanization roadmap (Section 8) identifying the exact types, lemmas, and tactic patterns needed to formalize all four results in Lean 4 / Mathlib. Mechanization is the primary near-term goal for follow-up work.

---

## Repository structure

```
SELLTCFULL.tex                  Main paper (LaTeX source)
SELLTCFULL.pdf                  Compiled paper
SELLTCFULL_experiments.ipynb    Reference implementation notebook
selltcfull_experiments.py       Python module: checker + decoder reference implementation
lean4/                          Lean 4 mechanization plan and skeleton (see below)
SELLTCFULL_outputs/             Supplementary experimental data
    manifest.json               Configuration and seeds used for the data
    raw_clean.csv               Per-trial results on the clean BEC
    raw_robustness.csv          Per-trial results with BEC violations
    success_summary.csv         Grouped success rates
    runtime_summary.csv         Grouped runtime breakdown
    checker_summary.csv         Checker scaling vs. blocklength
    robustness_summary.csv      Grouped robustness statistics
    table1_summary.csv          Structural statistics table
    table1_summary.tex          LaTeX export of Table 1
    fig*.png                    Figures (supplementary; not the paper's primary claim)
```

---

## Lean 4 mechanization plan

The `lean4/` directory contains a formalization plan for the four main theorems using Lean 4 and Mathlib. See [lean4/README.md](lean4/README.md) for the full roadmap, including:

- Type encodings for `PeelingState`, `WFMultiset`, and `Step`.
- The two-direction proof plan for the adequacy theorem (`adequacy_completeness`, `adequacy_soundness`).
- Mathlib dependencies and estimated effort per theorem.

No Lean code has been written yet; the directory contains the plan and skeleton as a starting point.

---

## Python reference implementation

`selltcfull_experiments.py` provides a pure Python implementation of the certified hybrid decoder. Its purpose is to allow the certificate format and checker algorithm to be inspected and executed without a proof assistant.

Key functions traceable to paper definitions:

| Function | Paper reference |
|---|---|
| `peeling_decode(H, y)` | Phase I; returns trace T and partial assignment K |
| `gf2_solve(A, b)` | Phase II; returns ρ (solution) or ω (infeasibility witness) |
| `check_success_certificate(H, y, T, rho)` | Algorithm 1 (success branch) |
| `check_failure_certificate(H, y, T, omega)` | Algorithm 1 (failure branch) |
| `run_hybrid_decoder(H, y)` | Full pipeline |

### Running the notebook

```bash
pip install numpy pandas matplotlib
jupyter notebook SELLTCFULL_experiments.ipynb
```

The notebook demonstrates the checker on small examples and verifies that false-acceptance rate is zero on the test instances.

---

## Supplementary experimental data

The `SELLTCFULL_outputs/` directory contains results from a Monte Carlo campaign run on two LDPC code families (random regular and PEG) at three blocklengths (n ∈ {1000, 2000, 5000}). This data is provided as supplementary material so that readers can inspect the checker's behavior; it does not constitute the paper's primary evidence. All seeds are recorded in `manifest.json`.

---

## Compiling the paper

```bash
pdflatex SELLTCFULL.tex
pdflatex SELLTCFULL.tex
```

Requires TeX Live 2020 or later with standard packages. The paper compiles without the experimental outputs present.

---

## Citation

```bibtex
@article{selltcfull2026,
  title   = {Certified Hybrid Decoding of Binary {LDPC} Codes over the {BEC}
             via Subexponential Linear Logic},
  note    = {Manuscript; Lean~4 mechanization in progress}
}
```

---

## Repository structure

```
SELLTCFULL.tex                  Main paper (LaTeX source)
SELLTCFULL.pdf                  Compiled paper
SELLTCFULL_experiments.ipynb    Reproducibility notebook (run this to regenerate all figures/tables)
selltcfull_experiments.py       Python module with all experiment logic
SELLTCFULL_outputs/             Output directory (created by the notebook)
    manifest.json               Canonical configuration and seeds
    raw_clean.csv               Per-trial results on the clean BEC
    raw_robustness.csv          Per-trial results with BEC violations
    success_summary.csv         Grouped success rates
    runtime_summary.csv         Grouped runtime breakdown
    checker_summary.csv         Checker scaling vs. blocklength
    robustness_summary.csv      Grouped robustness statistics
    table1_summary.csv          Structural statistics table
    table1_summary.tex          LaTeX export of Table 1
    fig1_success_probability.png  Figure 1 — success probability across epsilon
    fig2_runtime_breakdown.png    Figure 2 — runtime breakdown by stage
    fig3_checker_scaling.png      Figure 3 — checker overhead vs. blocklength
    fig4_robustness.png           Figure 4 — robustness to BEC violations
```

