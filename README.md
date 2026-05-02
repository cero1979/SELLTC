# Certified Hybrid Decoding of Binary LDPC Codes over the BEC via SELL

This repository accompanies the paper:

> **Certified Hybrid Decoding of Binary LDPC Codes over the BEC via Subexponential Linear Logic (SELL)**

The paper proposes using Subexponential Linear Logic (SELL) as a formal
certification layer for a hybrid decoder that combines peeling (BEC-specific,
linear time) with Gaussian elimination over GF(2) (maximum-likelihood, used
only when peeling stalls). Every decoder invocation produces an independently
checkable certificate — either a *success certificate* witnessing that the
output is a codeword, or a *failure certificate* witnessing that the received
word is not in the code.

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

---

## Reproducing the experiments

### 1. Install dependencies

```bash
pip install numpy pandas matplotlib openpyxl
```

Required package versions:

| Package    | Minimum version |
|------------|-----------------|
| Python     | 3.10            |
| NumPy      | 1.24            |
| Pandas     | 1.5             |
| Matplotlib | 3.6             |

### 2. Run the smoke test (quick verification, ~30 seconds)

Open `SELLTCFULL_experiments.ipynb` in Jupyter and run all cells from top to
bottom. By default, `RUN_SMOKE = True` and `RUN_FULL = False`, so only the
smoke test runs.

The smoke test exercises the full pipeline with 2 code families, 2 erasure
rates, and 2 trials. It confirms that:

- Matrix generation, peeling, GE, and certificate checking all work.
- No false acceptances occur.
- Figures and summaries are exported without errors.

### 3. Run the full campaign (canonical reproduction)

In the notebook cell labelled **Full campaign**, set:

```python
RUN_FULL = True
```

Then re-run that cell.  The canonical configuration is:

| Parameter           | Value                                          |
|---------------------|------------------------------------------------|
| Degree profile      | $(d_v, d_c) = (3, 6)$, rate $\approx 1/2$     |
| Blocklengths        | $n \in \{1000, 2000, 5000\}$                   |
| Code families       | random regular + PEG, 3 blocklengths each      |
| Erasure rates       | $\epsilon \in \{0.34, 0.38, 0.40, 0.42, 0.44, 0.46, 0.50\}$ |
| Robustness levels   | $\delta \in \{0, 10^{-4}, 10^{-3}, 10^{-2}\}$ |
| Trials per point    | 100                                            |
| Base seed           | `20260427`                                     |

Total decoder calls: approximately 8,400.  Expected wall time: 20–60 minutes
depending on hardware, with most of the time spent at $n = 5000$.

After the campaign finishes, run the output-validation cell to verify that all
files are present and that the key theoretical invariants hold.

### 4. Compile the paper

From the repository root, run pdflatex twice (the second pass resolves
cross-references):

```bash
pdflatex SELLTCFULL.tex
pdflatex SELLTCFULL.tex
```

The LaTeX source uses `\IfFileExists` macros to include figures and Table 1
automatically when the output files are present. The paper compiles in both
states (with and without experimental outputs), showing placeholder boxes when
outputs are absent.

---

## Reproducibility

All random seeds are derived deterministically from a single integer,
`base_seed = 20260427`, recorded in `SELLTCFULL_outputs/manifest.json`.
Every code matrix, erasure pattern, and robustness perturbation is generated
from this seed via NumPy's seeded `default_rng`. No platform-specific
floating-point operations are used; the implementation relies solely on
integer GF(2) arithmetic.

A reviewer who runs the notebook with the same base seed and compatible NumPy
version will obtain numerically identical results.

---

## Theoretical guarantees verified by the experiment

The experiment is designed to confirm four predictions that follow from the
formal analysis in the paper:

1. **Clean-channel agreement**: on a noise-free BEC, the hybrid decoder always
   agrees with maximum-likelihood decoding, and no false acceptances occur.
2. **Hybrid gain**: the hybrid decoder strictly outperforms peeling alone in
   the transition region around the BEC threshold ($\epsilon^* \approx 0.4294$
   for rate-1/2 codes).
3. **Checker overhead**: certificate verification takes $O(|E| + n)$ time, and
   the observed checker-to-decode-time ratio decreases toward a small constant
   as $n$ grows.
4. **Robustness**: when the channel deviates from the pure BEC model, the
   failure certificate correctly identifies infeasible received words, and the
   false-acceptance rate remains zero.

---

## Citation

If you use this code or paper, please cite:

```
@article{selltc2025,
  title   = {Certified Hybrid Decoding of Binary LDPC Codes over the BEC
             via Subexponential Linear Logic (SELL)},
  year    = {2025},
}
```

---

## License

The code in this repository is released under the MIT License.
The accompanying paper (`SELLTCFULL.tex` and `SELLTCFULL.pdf`) is released
under CC BY 4.0.
