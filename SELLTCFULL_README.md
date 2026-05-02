# SELLTCFULL artifact

This bundle contains the reproducibility package for the paper
"Certified Hybrid Decoding of Binary LDPC Codes over the BEC via Subexponential Linear Logic (SELL)".

## Files

- `SELLTCFULL.tex`: paper source, with complete experimental section.
- `lmcs.cls`: LMCS document class (required to compile the paper).
- `SELLTCFULL.pdf`: compiled PDF.
- `SELLTCFULL_experiments.ipynb`: self-contained notebook that generates all outputs.
- `selltcfull_experiments.py`: companion Python module used by the notebook.
- `SELLTCFULL_outputs/manifest.json`: canonical experiment configuration and seeds.
- `SELLTCFULL_outputs/fig{1,2,3,4}_*.png`: figures used in the paper (Figs. 1–4).
- `SELLTCFULL_outputs/table1_summary.tex`: LaTeX table included by the paper (Table 2).
- `SELLTCFULL_outputs/*.csv`: raw and summary data behind the figures and table.
- `lean4/`: Lean 4 mechanization of the main theorems.
- `finalize.sh`: convenience script to compile the paper after running the full campaign.

## Canonical full campaign

- Families: random regular and PEG
- Degree profile: (dv, dc) = (3, 6)
- Blocklengths: n in {1000, 2000, 5000}
- Clean-channel epsilon grid: {0.34, 0.38, 0.40, 0.42, 0.44, 0.46, 0.50}
- Robustness delta grid: {0, 1e-4, 1e-3, 1e-2}
- Default Monte Carlo budget: 100 trials per point

## Reproduction steps

1. Open `SELLTCFULL_experiments.ipynb`.
2. Run all cells (optionally run the smoke-test cell first to verify the environment).
3. Set `RUN_FULL = True` in the full-campaign cell when ready.
4. After the full campaign completes, run `bash finalize.sh` (or compile `SELLTCFULL.tex` directly).

The paper source will automatically include any generated figures and the LaTeX table export from `SELLTCFULL_outputs/`.