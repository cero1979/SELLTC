"""First regression, run against the preserved baseline before repair."""
import importlib.util
from pathlib import Path
import sys
import numpy as np


def test_original_rejects_nonbinary_certificate():
    path = Path(__file__).resolve().parents[1] / 'audit/removed_module_original.py'
    spec = importlib.util.spec_from_file_location('baseline_experiment', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    accepted, _ = mod.check_success_certificate(
        np.array([[1, 1]], dtype=np.uint8), np.array([-1, -1]), [], np.array([2, 2]))
    assert not accepted, 'nonbinary witness must be rejected'
