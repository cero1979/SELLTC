#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ "${1:-}" == "--clean" ]]; then
  lake clean selltc
fi
lake build
lake env lean AxiomAudit.lean
lake env lean Main.lean
