#!/bin/bash
# finalize.sh — run this once the full campaign has completed.
# Usage: cd /Users/cero/Downloads/SELLTeoCod/SELLTCFULL_bundle && bash finalize.sh

set -e
cd "$(dirname "$0")"

PDFLATEX=/Library/TeX/texbin/pdflatex
OUTPUTS=SELLTCFULL_outputs

echo "=== Checking campaign outputs ==="
REQUIRED=(
    raw_clean.csv raw_robustness.csv
    success_summary.csv runtime_summary.csv
    checker_summary.csv robustness_summary.csv
    table1_summary.csv table1_summary.tex
    fig1_success_probability.png fig2_runtime_breakdown.png
    fig3_checker_scaling.png fig4_robustness.png
)
MISSING=0
for f in "${REQUIRED[@]}"; do
    if [ ! -f "$OUTPUTS/$f" ]; then
        echo "  MISSING: $OUTPUTS/$f"
        MISSING=1
    else
        echo "  OK: $OUTPUTS/$f"
    fi
done

if [ "$MISSING" -eq 1 ]; then
    echo ""
    echo "ERROR: Some campaign outputs are missing."
    echo "Wait for the full campaign to complete, then re-run this script."
    exit 1
fi

echo ""
echo "=== Compiling LaTeX (pass 1) ==="
$PDFLATEX -interaction=nonstopmode SELLTCFULL.tex > /tmp/latex1.log 2>&1
echo "=== Compiling LaTeX (pass 2 — resolves cross-references) ==="
$PDFLATEX -interaction=nonstopmode SELLTCFULL.tex > /tmp/latex2.log 2>&1
echo "PDF: $(grep 'Output written' /tmp/latex2.log)"

echo ""
echo "=== Pushing to GitHub ==="
git add SELLTCFULL_outputs/ SELLTCFULL.pdf
git commit -m "Add full campaign outputs (100 trials/point, n in {1000,2000,5000})"
git push origin main
echo "Done. Check https://github.com/cero1979/SELLTC"
