#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/test.sh
python scripts/render_waveforms.py
python scripts/build_report.py
cd latex
export TEXMFVAR=/tmp/alu-texmf-var
export TEXMFCONFIG=/tmp/alu-texmf-config
pdflatex -interaction=nonstopmode -halt-on-error report.tex > ../build/latex-pass1.log
pdflatex -interaction=nonstopmode -halt-on-error report.tex > ../build/latex-pass2.log
echo 'Report built: latex/report.pdf'
