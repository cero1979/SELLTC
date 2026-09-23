#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec lake env lean --run Main.lean
