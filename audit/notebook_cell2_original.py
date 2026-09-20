%%writefile selltcfull_experiments.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import json
import random
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ERASURE = np.int8(-1)


@dataclass
class PeelingState:
    """State of the phase-I peeling decoder."""
    known: np.ndarray
    unknown_mask: np.ndarray
    rhs: np.ndarray
    degree: np.ndarray


@dataclass
class GF2SolveResult:
    """Outcome of Gaussian elimination over GF(2)."""
    solvable: bool
    solution: Optional[np.ndarray]
    witness: Optional[np.ndarray]
    rank: int
    column_order: np.ndarray


@dataclass
class FamilySpec:
    """Code family specification used by the experiment runner."""
    family: str
    n: int
    dv: int
    dc: int
    matrix_seed: int


@dataclass
class CampaignConfig:
    """
    Canonical experiment configuration faithful to Section 8 of the paper.

    The paper fixes the blocklength set and the robustness grid, while leaving
    the exact epsilon grid and trial count within a reasonable range. We choose
    an explicit epsilon grid centered around the classical rate-1/2 (3,6) BEC
    transition region, and set the default trial count to the lower edge of the
    paper's 100-500 Monte Carlo range so the campaign remains practical.
    """
    dv: int = 3
    dc: int = 6
    blocklengths: Tuple[int, ...] = (1000, 2000, 5000)
    epsilons: Tuple[float, ...] = (0.34, 0.38, 0.40, 0.42, 0.44, 0.46, 0.50)
    robustness_deltas: Tuple[float, ...] = (0.0, 1e-4, 1e-3, 1e-2)
    clean_trials: int = 100
    robustness_trials: int = 100
    hybrid_solver: str = "sparse"
    ge_solver: str = "dense"
    base_seed: int = 20260427

    def family_specs(self) -> List[FamilySpec]:
        specs: List[FamilySpec] = []
        for family_name, family_offset in (("random_regular", 1000), ("peg", 2000)):
            for n in self.blocklengths:
                specs.append(
                    FamilySpec(
                        family=family_name,
                        n=n,
                        dv=self.dv,
                        dc=self.dc,
                        matrix_seed=self.base_seed + family_offset + n,
                    )
                )
        return specs


def make_output_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_adjacency(H: np.ndarray) -> Tuple[List[List[int]], List[List[int]]]:
    check_to_vars = [np.flatnonzero(H[j]).tolist() for j in range(H.shape[0])]
    var_to_checks = [np.flatnonzero(H[:, i]).tolist() for i in range(H.shape[1])]
    return check_to_vars, var_to_checks


def generate_random_regular_ldpc(
    n: int,
    dv: int,
    dc: int,
    seed: int = 0,
    max_tries: int = 200,
) -> np.ndarray:
    """
    Build a simple random regular parity-check matrix with column weight dv
    and row weight dc.
    """
    if (n * dv) % dc != 0:
        raise ValueError("n * dv must be divisible by dc")
    rng = random.Random(seed)
    m = (n * dv) // dc

    for _ in range(max_tries):
        H = np.zeros((m, n), dtype=np.uint8)
        remaining = [dc] * m
        variables = list(range(n))
        rng.shuffle(variables)
        ok = True

        for v in variables:
            for _edge in range(dv):
                candidates = [c for c in range(m) if remaining[c] > 0 and H[c, v] == 0]
                if not candidates:
                    ok = False
                    break
                weights = [remaining[c] for c in candidates]
                total_weight = float(sum(weights))
                target = rng.uniform(0.0, total_weight)
                accum = 0.0
                chosen = candidates[-1]
                for c, weight in zip(candidates, weights):
                    accum += weight
                    if target <= accum:
                        chosen = c
                        break
                H[chosen, v] = 1
                remaining[chosen] -= 1
            if not ok:
                break

        if ok and all(value == 0 for value in remaining):
            return H

    raise RuntimeError("Could not construct a random regular LDPC matrix with the requested parameters.")


def _peg_candidate_checks(
    var_to_checks: List[List[int]],
    check_to_vars: List[List[int]],
    variable: int,
    exclude: set[int],
) -> List[int]:
    """
    PEG helper: prefer checks that remain far from the current variable in the
    partially built Tanner graph.
    """
    m = len(check_to_vars)
    visited_vars = {variable}
    visited_checks: set[int] = set()
    frontier_vars = {variable}

    while frontier_vars:
        frontier_checks: set[int] = set()
        for v in frontier_vars:
            for c in var_to_checks[v]:
                if c not in visited_checks:
                    frontier_checks.add(c)

        if not frontier_checks:
            break

        visited_checks |= frontier_checks
        next_vars: set[int] = set()
        for c in frontier_checks:
            for v in check_to_vars[c]:
                if v not in visited_vars:
                    next_vars.add(v)

        if not next_vars:
            break

        visited_vars |= next_vars
        frontier_vars = next_vars

    farthest = [c for c in range(m) if c not in visited_checks and c not in exclude]
    return farthest or [c for c in range(m) if c not in exclude]


def generate_peg_ldpc(
    n: int,
    dv: int,
    dc: int,
    seed: int = 0,
    max_tries: int = 50,
) -> np.ndarray:
    """
    Build a regular PEG-style parity-check matrix with the same degree profile.
    """
    if (n * dv) % dc != 0:
        raise ValueError("n * dv must be divisible by dc")
    root_rng = random.Random(seed)
    m = (n * dv) // dc

    for _ in range(max_tries):
        rng = random.Random(root_rng.randint(0, 10**9))
        check_to_vars: List[List[int]] = [[] for _ in range(m)]
        var_to_checks: List[List[int]] = [[] for _ in range(n)]
        remaining = [dc] * m
        ok = True

        for variable in range(n):
            for edge_slot in range(dv):
                exclude = set(var_to_checks[variable])
                if edge_slot == 0:
                    candidates = [c for c in range(m) if remaining[c] > 0 and c not in exclude]
                else:
                    candidates = [
                        c
                        for c in _peg_candidate_checks(var_to_checks, check_to_vars, variable, exclude)
                        if remaining[c] > 0 and c not in exclude
                    ]
                    if not candidates:
                        candidates = [c for c in range(m) if remaining[c] > 0 and c not in exclude]

                if not candidates:
                    ok = False
                    break

                min_degree = min(len(check_to_vars[c]) for c in candidates)
                best = [c for c in candidates if len(check_to_vars[c]) == min_degree]
                chosen = rng.choice(best)

                check_to_vars[chosen].append(variable)
                var_to_checks[variable].append(chosen)
                remaining[chosen] -= 1

            if not ok:
                break

        if ok and all(value == 0 for value in remaining):
            H = np.zeros((m, n), dtype=np.uint8)
            for c, variables in enumerate(check_to_vars):
                H[c, variables] = 1
            return H

    raise RuntimeError("Could not construct a PEG LDPC matrix with the requested parameters.")


def load_optional_public_matrix(path: str | Path) -> np.ndarray:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".npy":
        return np.load(path).astype(np.uint8)
    if suffix == ".csv":
        return np.loadtxt(path, delimiter=",", dtype=np.uint8)
    if suffix == ".txt":
        return np.loadtxt(path, dtype=np.uint8)
    raise ValueError("Supported matrix formats are .npy, .csv, and .txt.")


def simulate_bec_received_word(
    n: int,
    epsilon: float,
    delta: float = 0.0,
    seed: int = 0,
    transmitted: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Generate a received word on the BEC, then optionally corrupt visible bits.
    """
    rng = np.random.default_rng(seed)
    x = np.zeros(n, dtype=np.int8) if transmitted is None else transmitted.astype(np.int8).copy()
    y = x.copy()
    erasures = rng.random(n) < epsilon
    y[erasures] = ERASURE

    if delta > 0.0:
        visible_positions = np.flatnonzero(~erasures)
        flips = rng.random(visible_positions.size) < delta
        y[visible_positions[flips]] ^= 1

    return y


def initialize_state(H: np.ndarray, y: np.ndarray) -> PeelingState:
    known = y.copy().astype(np.int8)
    unknown_mask = known == ERASURE
    if np.any(~unknown_mask):
        rhs = (H[:, ~unknown_mask] @ known[~unknown_mask].astype(np.uint8)) % 2
    else:
        rhs = np.zeros(H.shape[0], dtype=np.uint8)
    degree = H[:, unknown_mask].sum(axis=1).astype(np.int32)
    return PeelingState(
        known=known,
        unknown_mask=unknown_mask,
        rhs=rhs.astype(np.uint8),
        degree=degree,
    )


def residual_system_from_state(H: np.ndarray, state: PeelingState) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    U = np.flatnonzero(state.unknown_mask)
    HU = H[:, U].astype(np.uint8)
    r = state.rhs.astype(np.uint8).copy()
    return HU, r, U


def peeling_decode(
    H: np.ndarray,
    y: np.ndarray,
    check_to_vars: Optional[List[List[int]]] = None,
    var_to_checks: Optional[List[List[int]]] = None,
) -> Tuple[PeelingState, List[Tuple[int, int, int]], np.ndarray]:
    if check_to_vars is None or var_to_checks is None:
        check_to_vars, var_to_checks = build_adjacency(H)

    state = initialize_state(H, y)
    trace: List[Tuple[int, int, int]] = []
    queue = [j for j in range(H.shape[0]) if state.degree[j] == 1]
    in_queue = np.zeros(H.shape[0], dtype=bool)
    for j in queue:
        in_queue[j] = True

    while queue:
        j = queue.pop()
        in_queue[j] = False

        if state.degree[j] != 1:
            continue

        unknowns = [i for i in check_to_vars[j] if state.unknown_mask[i]]
        if len(unknowns) != 1:
            continue

        i = unknowns[0]
        b = int(state.rhs[j])
        trace.append((j, i, b))

        state.known[i] = np.int8(b)
        state.unknown_mask[i] = False

        for check in var_to_checks[i]:
            if state.degree[check] <= 0:
                continue
            state.rhs[check] ^= np.uint8(b)
            state.degree[check] -= 1
            if state.degree[check] == 1 and not in_queue[check]:
                queue.append(check)
                in_queue[check] = True

    return state, trace, np.flatnonzero(state.unknown_mask)


def order_columns(A: np.ndarray, strategy: str = "dense") -> np.ndarray:
    if strategy == "dense":
        return np.arange(A.shape[1])
    if strategy == "sparse":
        weights = A.sum(axis=0)
        return np.argsort(weights, kind="stable")
    raise ValueError(f"Unsupported column-ordering strategy: {strategy}")


def gf2_solve(A: np.ndarray, b: np.ndarray, strategy: str = "dense") -> GF2SolveResult:
    """
    Solve Ax = b over GF(2) and, when inconsistent, extract a failure witness.
    """
    A = A.copy().astype(np.uint8)
    b = b.copy().astype(np.uint8)
    m, n = A.shape

    if n == 0:
        if np.all(b == 0):
            return GF2SolveResult(True, np.zeros(0, dtype=np.uint8), None, 0, np.arange(0))
        witness = np.zeros(m, dtype=np.uint8)
        witness[int(np.flatnonzero(b)[0])] = 1
        return GF2SolveResult(False, None, witness, 0, np.arange(0))

    order = order_columns(A, strategy)
    A = A[:, order]
    U = np.eye(m, dtype=np.uint8)
    row = 0
    pivots: List[Tuple[int, int]] = []

    for col in range(n):
        pivot_candidates = np.where(A[row:, col] == 1)[0]
        if pivot_candidates.size == 0:
            continue

        if strategy == "sparse":
            actual_rows = row + pivot_candidates
            row_weights = A[actual_rows].sum(axis=1)
            pivot_row = int(actual_rows[np.argmin(row_weights)])
        else:
            pivot_row = row + int(pivot_candidates[0])

        if pivot_row != row:
            A[[row, pivot_row]] = A[[pivot_row, row]]
            b[[row, pivot_row]] = b[[pivot_row, row]]
            U[[row, pivot_row]] = U[[pivot_row, row]]

        elimination_mask = A[:, col].astype(bool)
        elimination_mask[row] = False
        if np.any(elimination_mask):
            A[elimination_mask] ^= A[row]
            b[elimination_mask] ^= b[row]
            U[elimination_mask] ^= U[row]

        pivots.append((row, col))
        row += 1
        if row == m:
            break

    rank = len(pivots)
    inconsistent_rows = np.where((A.sum(axis=1) == 0) & (b == 1))[0]
    if inconsistent_rows.size > 0:
        witness = U[int(inconsistent_rows[0])].copy()
        return GF2SolveResult(False, None, witness, rank, order)

    x = np.zeros(n, dtype=np.uint8)
    for r, col in reversed(pivots):
        later_cols = np.flatnonzero(A[r, col + 1 :]) + col + 1
        rhs = b[r]
        if later_cols.size > 0:
            rhs ^= np.bitwise_xor.reduce(A[r, later_cols] & x[later_cols])
        x[col] = rhs

    x_original_order = np.zeros(n, dtype=np.uint8)
    x_original_order[order] = x
    return GF2SolveResult(True, x_original_order, None, rank, order)


def check_success_certificate(
    H: np.ndarray,
    y: np.ndarray,
    trace: Sequence[Tuple[int, int, int]],
    rho: np.ndarray,
    check_to_vars: Optional[List[List[int]]] = None,
    var_to_checks: Optional[List[List[int]]] = None,
) -> Tuple[bool, Optional[np.ndarray]]:
    if check_to_vars is None or var_to_checks is None:
        check_to_vars, var_to_checks = build_adjacency(H)

    state = initialize_state(H, y)

    for j, i, b in trace:
        if j < 0 or j >= H.shape[0] or i < 0 or i >= H.shape[1]:
            return False, None
        if state.degree[j] != 1:
            return False, None

        unknowns = [v for v in check_to_vars[j] if state.unknown_mask[v]]
        if len(unknowns) != 1 or unknowns[0] != i:
            return False, None
        if int(state.rhs[j]) != int(b):
            return False, None

        state.known[i] = np.int8(b)
        state.unknown_mask[i] = False
        for check in var_to_checks[i]:
            if state.degree[check] <= 0:
                continue
            state.rhs[check] ^= np.uint8(b)
            state.degree[check] -= 1

    HU, r, U = residual_system_from_state(H, state)
    if rho.shape[0] != U.shape[0]:
        return False, None

    lhs = (HU @ rho.astype(np.uint8)) % 2
    if not np.array_equal(lhs.astype(np.uint8), r.astype(np.uint8)):
        return False, None

    x = state.known.copy()
    x[U] = rho.astype(np.int8)
    visible = y != ERASURE
    if not np.array_equal(x[visible], y[visible]):
        return False, None
    if not np.all((H @ x.astype(np.uint8)) % 2 == 0):
        return False, None
    return True, x.astype(np.int8)


def check_failure_certificate(
    H: np.ndarray,
    y: np.ndarray,
    trace: Sequence[Tuple[int, int, int]],
    witness: np.ndarray,
    check_to_vars: Optional[List[List[int]]] = None,
    var_to_checks: Optional[List[List[int]]] = None,
) -> bool:
    if check_to_vars is None or var_to_checks is None:
        check_to_vars, var_to_checks = build_adjacency(H)

    state = initialize_state(H, y)

    for j, i, b in trace:
        if j < 0 or j >= H.shape[0] or i < 0 or i >= H.shape[1]:
            return False
        if state.degree[j] != 1:
            return False

        unknowns = [v for v in check_to_vars[j] if state.unknown_mask[v]]
        if len(unknowns) != 1 or unknowns[0] != i:
            return False
        if int(state.rhs[j]) != int(b):
            return False

        state.known[i] = np.int8(b)
        state.unknown_mask[i] = False
        for check in var_to_checks[i]:
            if state.degree[check] <= 0:
                continue
            state.rhs[check] ^= np.uint8(b)
            state.degree[check] -= 1

    HU, r, _ = residual_system_from_state(H, state)
    w = witness.astype(np.uint8)
    if w.shape[0] != HU.shape[0]:
        return False
    left = (w @ HU) % 2 if HU.size > 0 else np.zeros(HU.shape[1], dtype=np.uint8)
    right = int((w @ r) % 2)
    return np.all(left == 0) and right == 1


def run_hybrid_decoder(
    H: np.ndarray,
    y: np.ndarray,
    solver_strategy: str = "sparse",
    check_to_vars: Optional[List[List[int]]] = None,
    var_to_checks: Optional[List[List[int]]] = None,
) -> Dict[str, Any]:
    if check_to_vars is None or var_to_checks is None:
        check_to_vars, var_to_checks = build_adjacency(H)

    wall_t0 = time.perf_counter()

    peel_t0 = time.perf_counter()
    state, trace, _ = peeling_decode(H, y, check_to_vars, var_to_checks)
    peel_t1 = time.perf_counter()

    HU, r, U = residual_system_from_state(H, state)

    residual_t0 = time.perf_counter()
    solve = gf2_solve(HU, r, strategy=solver_strategy)
    residual_t1 = time.perf_counter()

    if solve.solvable:
        status = "success"
        rho = solve.solution
        witness = None
    else:
        status = "failure"
        rho = None
        witness = solve.witness

    check_t0 = time.perf_counter()
    if status == "success":
        accepted, decoded_word = check_success_certificate(H, y, trace, rho, check_to_vars, var_to_checks)
        checker_outcome = "success" if accepted else "reject"
    else:
        accepted = check_failure_certificate(H, y, trace, witness, check_to_vars, var_to_checks)
        decoded_word = None
        checker_outcome = "failure" if accepted else "reject"
    check_t1 = time.perf_counter()

    wall_t1 = time.perf_counter()
    density = float(HU.mean()) if HU.size > 0 else 0.0
    decoder_time = wall_t1 - wall_t0
    checker_time = check_t1 - check_t0

    return {
        "trace": trace,
        "rho": rho,
        "witness": witness,
        "status": status,
        "checker_outcome": checker_outcome,
        "accepted": bool(accepted),
        "decoded_word": decoded_word,
        "peeling_time_s": peel_t1 - peel_t0,
        "residual_time_s": residual_t1 - residual_t0,
        "checker_time_s": checker_time,
        "decoder_time_s": decoder_time,
        "overhead_ratio": checker_time / max(decoder_time - checker_time, 1e-12),
        "trace_len": len(trace),
        "residual_size": int(U.size),
        "rank_residual": int(solve.rank),
        "density_residual": density,
    }


def run_peeling_only(
    H: np.ndarray,
    y: np.ndarray,
    check_to_vars: Optional[List[List[int]]] = None,
    var_to_checks: Optional[List[List[int]]] = None,
) -> Dict[str, Any]:
    if check_to_vars is None or var_to_checks is None:
        check_to_vars, var_to_checks = build_adjacency(H)

    t0 = time.perf_counter()
    state, trace, U = peeling_decode(H, y, check_to_vars, var_to_checks)
    t1 = time.perf_counter()

    success = bool(U.size == 0 and np.all(state.rhs == 0))
    return {
        "success": success,
        "time_s": t1 - t0,
        "trace_len": len(trace),
        "residual_size": int(U.size),
    }


def run_ge_only(H: np.ndarray, y: np.ndarray, solver_strategy: str = "dense") -> Dict[str, Any]:
    t0 = time.perf_counter()
    state = initialize_state(H, y)
    HU, r, U = residual_system_from_state(H, state)
    solve = gf2_solve(HU, r, strategy=solver_strategy)
    t1 = time.perf_counter()
    return {
        "solvable": bool(solve.solvable),
        "time_s": t1 - t0,
        "rank_residual": int(solve.rank),
        "residual_size": int(U.size),
        "solution": solve.solution,
        "witness": solve.witness,
    }


def build_family_matrix(
    family: str,
    n: int,
    dv: int,
    dc: int,
    seed: int,
    public_matrix_path: Optional[str | Path] = None,
) -> np.ndarray:
    if family == "random_regular":
        return generate_random_regular_ldpc(n=n, dv=dv, dc=dc, seed=seed)
    if family == "peg":
        return generate_peg_ldpc(n=n, dv=dv, dc=dc, seed=seed)
    if family == "public_optional":
        if public_matrix_path is None:
            raise ValueError("public_matrix_path must be provided for family='public_optional'.")
        return load_optional_public_matrix(public_matrix_path)
    raise ValueError(f"Unknown family: {family}")


def run_single_trial(
    H: np.ndarray,
    family: str,
    n: int,
    dv: int,
    dc: int,
    epsilon: float,
    delta: float,
    trial: int,
    seed: int,
    hybrid_solver: str = "sparse",
    ge_solver: str = "dense",
) -> Dict[str, Any]:
    check_to_vars, var_to_checks = build_adjacency(H)
    y = simulate_bec_received_word(n=n, epsilon=epsilon, delta=delta, seed=seed)

    peeling = run_peeling_only(H, y, check_to_vars, var_to_checks)
    ge = run_ge_only(H, y, ge_solver)
    hybrid = run_hybrid_decoder(H, y, hybrid_solver, check_to_vars, var_to_checks)

    hybrid_success_accept = hybrid["accepted"] and hybrid["checker_outcome"] == "success"
    hybrid_failure_accept = hybrid["accepted"] and hybrid["checker_outcome"] == "failure"
    false_accept = (
        (hybrid_success_accept and not ge["solvable"])
        or (hybrid_failure_accept and ge["solvable"])
    )

    return {
        "family": family,
        "n": n,
        "dv": dv,
        "dc": dc,
        "epsilon": epsilon,
        "delta": delta,
        "trial": trial,
        "seed": seed,
        "peeling_success": peeling["success"],
        "peeling_time_s": peeling["time_s"],
        "ge_success": ge["solvable"],
        "ge_time_s": ge["time_s"],
        "hybrid_success_accept": hybrid_success_accept,
        "hybrid_failure_accept": hybrid_failure_accept,
        "hybrid_checker_accept": hybrid["accepted"],
        "hybrid_checker_outcome": hybrid["checker_outcome"],
        "hybrid_time_s": hybrid["decoder_time_s"],
        "hybrid_peeling_time_s": hybrid["peeling_time_s"],
        "hybrid_residual_time_s": hybrid["residual_time_s"],
        "hybrid_checker_time_s": hybrid["checker_time_s"],
        "overhead_ratio": hybrid["overhead_ratio"],
        "trace_len": hybrid["trace_len"],
        "residual_size": hybrid["residual_size"],
        "rank_residual": hybrid["rank_residual"],
        "density_residual": hybrid["density_residual"],
        "false_accept": bool(false_accept),
    }


def run_experiment_grid(
    family_specs: Sequence[Dict[str, Any] | FamilySpec],
    epsilons: Sequence[float],
    trials: int,
    delta: float = 0.0,
    base_seed: int = 1234,
    hybrid_solver: str = "sparse",
    ge_solver: str = "dense",
    public_matrix_path: Optional[str | Path] = None,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for spec in family_specs:
        if isinstance(spec, FamilySpec):
            spec = asdict(spec)
        family = str(spec["family"])
        n = int(spec["n"])
        dv = int(spec["dv"])
        dc = int(spec["dc"])
        matrix_seed = int(spec.get("matrix_seed", base_seed + n))

        H = build_family_matrix(
            family=family,
            n=n,
            dv=dv,
            dc=dc,
            seed=matrix_seed,
            public_matrix_path=public_matrix_path,
        )

        for epsilon in epsilons:
            for trial in range(trials):
                seed = base_seed + 100_000 * matrix_seed + 1_000 * int(round(1000 * epsilon)) + trial
                rows.append(
                    run_single_trial(
                        H=H,
                        family=family,
                        n=n,
                        dv=dv,
                        dc=dc,
                        epsilon=float(epsilon),
                        delta=float(delta),
                        trial=trial,
                        seed=seed,
                        hybrid_solver=hybrid_solver,
                        ge_solver=ge_solver,
                    )
                )

    return pd.DataFrame(rows)


def run_robustness_grid(
    family_specs: Sequence[Dict[str, Any] | FamilySpec],
    epsilon: float,
    deltas: Sequence[float],
    trials: int,
    base_seed: int = 2026,
    hybrid_solver: str = "sparse",
    ge_solver: str = "dense",
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for spec in family_specs:
        if isinstance(spec, FamilySpec):
            spec = asdict(spec)
        family = str(spec["family"])
        n = int(spec["n"])
        dv = int(spec["dv"])
        dc = int(spec["dc"])
        matrix_seed = int(spec.get("matrix_seed", base_seed + n))

        H = build_family_matrix(
            family=family,
            n=n,
            dv=dv,
            dc=dc,
            seed=matrix_seed,
        )

        for delta in deltas:
            for trial in range(trials):
                seed = base_seed + 100_000 * matrix_seed + 10_000 * int(round(1000 * delta)) + trial
                rows.append(
                    run_single_trial(
                        H=H,
                        family=family,
                        n=n,
                        dv=dv,
                        dc=dc,
                        epsilon=float(epsilon),
                        delta=float(delta),
                        trial=trial,
                        seed=seed,
                        hybrid_solver=hybrid_solver,
                        ge_solver=ge_solver,
                    )
                )

    return pd.DataFrame(rows)


def summarize_success(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["family", "n", "epsilon"], as_index=False)
        .agg(
            peeling_success=("peeling_success", "mean"),
            hybrid_success_accept=("hybrid_success_accept", "mean"),
            ge_success=("ge_success", "mean"),
            trials=("trial", "nunique"),
        )
    )


def summarize_runtime(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["family", "n", "epsilon"], as_index=False)
        .agg(
            peeling_time_s=("hybrid_peeling_time_s", "mean"),
            residual_time_s=("hybrid_residual_time_s", "mean"),
            checker_time_s=("hybrid_checker_time_s", "mean"),
            hybrid_time_s=("hybrid_time_s", "mean"),
            overhead_ratio=("overhead_ratio", "mean"),
        )
    )


def summarize_table1(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["family", "n", "dv", "dc"], as_index=False)
        .agg(
            mean_trace_len=("trace_len", "mean"),
            mean_residual_size=("residual_size", "mean"),
            mean_rank_residual=("rank_residual", "mean"),
            mean_density_residual=("density_residual", "mean"),
            mean_peeling_time_ms=("hybrid_peeling_time_s", lambda s: 1000.0 * s.mean()),
            mean_residual_time_ms=("hybrid_residual_time_s", lambda s: 1000.0 * s.mean()),
            mean_checker_time_ms=("hybrid_checker_time_s", lambda s: 1000.0 * s.mean()),
            mean_hybrid_time_ms=("hybrid_time_s", lambda s: 1000.0 * s.mean()),
            mean_overhead_ratio=("overhead_ratio", "mean"),
        )
    )


def summarize_checker_scaling(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["family", "n"], as_index=False)
        .agg(checker_time_s=("hybrid_checker_time_s", "mean"))
    )


def summarize_robustness(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["family", "n", "delta"], as_index=False)
        .agg(
            accepted_success=("hybrid_success_accept", "mean"),
            accepted_failure=("hybrid_failure_accept", "mean"),
            false_accept_rate=("false_accept", "mean"),
        )
    )


def save_dataframe(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        df.to_csv(path, index=False)
    elif path.suffix.lower() == ".xlsx":
        df.to_excel(path, index=False)
    else:
        raise ValueError("Supported tabular export formats are .csv and .xlsx.")
    return path


def export_table1_latex(table_df: pd.DataFrame, path: str | Path) -> Path:
    """
    Export the summary table in a format directly consumable by the paper.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pretty = table_df.copy()
    pretty["family"] = pretty["family"].map(
        {
            "random_regular": "Random regular",
            "peg": "PEG",
            "public_optional": "Public matrix",
        }
    ).fillna(pretty["family"])

    latex = pretty.to_latex(
        index=False,
        float_format=lambda x: f"{x:.3f}",
        column_format="llrrrrrrrr",
        escape=False,
    )
    path.write_text(latex, encoding="utf-8")
    return path


def export_manifest(config: CampaignConfig, out_dir: str | Path) -> Path:
    out_dir = make_output_dir(out_dir)
    manifest = {
        "campaign": asdict(config),
        "families": [asdict(spec) for spec in config.family_specs()],
    }
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def plot_success_probability(summary_df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    for (family, n), group in summary_df.groupby(["family", "n"]):
        group = group.sort_values("epsilon")
        prefix = f"{family}, n={n}"
        ax.plot(group["epsilon"], group["peeling_success"], marker="o", label=f"{prefix} - peeling")
        ax.plot(group["epsilon"], group["hybrid_success_accept"], marker="s", label=f"{prefix} - hybrid")
        ax.plot(group["epsilon"], group["ge_success"], marker="^", label=f"{prefix} - GE-only")

    ax.set_xlabel("Erasure probability $\\epsilon$")
    ax.set_ylabel("Success probability")
    ax.set_title("Figure 1. Success probability versus $\\epsilon$")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_runtime_breakdown(
    runtime_df: pd.DataFrame,
    path: str | Path,
    family: Optional[str] = None,
    n: Optional[int] = None,
) -> Path:
    data = runtime_df.copy()
    if family is not None:
        data = data[data["family"] == family]
    if n is not None:
        data = data[data["n"] == n]

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    for (fam, blocklength), group in data.groupby(["family", "n"]):
        group = group.sort_values("epsilon")
        prefix = f"{fam}, n={blocklength}"
        ax.plot(group["epsilon"], 1000.0 * group["peeling_time_s"], marker="o", label=f"{prefix} - peeling")
        ax.plot(group["epsilon"], 1000.0 * group["residual_time_s"], marker="s", label=f"{prefix} - residual GE")
        ax.plot(group["epsilon"], 1000.0 * group["checker_time_s"], marker="^", label=f"{prefix} - checker")

    ax.set_xlabel("Erasure probability $\\epsilon$")
    ax.set_ylabel("Mean runtime (ms)")
    ax.set_title("Figure 2. Runtime breakdown versus $\\epsilon$")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_checker_scaling(scale_df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for family, group in scale_df.groupby("family"):
        group = group.sort_values("n")
        ax.plot(group["n"], 1000.0 * group["checker_time_s"], marker="o", label=family)

    ax.set_xlabel("Blocklength $n$")
    ax.set_ylabel("Mean checker time (ms)")
    ax.set_title("Figure 3. Checker time versus blocklength")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_robustness(robust_df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    for (family, n), group in robust_df.groupby(["family", "n"]):
        group = group.sort_values("delta")
        prefix = f"{family}, n={n}"
        ax.plot(group["delta"], group["accepted_success"], marker="o", label=f"{prefix} - accepted success")
        ax.plot(group["delta"], group["accepted_failure"], marker="s", label=f"{prefix} - accepted failure")

    ax.set_xlabel("Corruption rate $\\delta$")
    ax.set_ylabel("Acceptance rate")
    ax.set_title("Figure 4. Robustness under BEC violations")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def narrative_summary(success_df: pd.DataFrame, runtime_df: pd.DataFrame, robustness_df: pd.DataFrame) -> str:
    """
    Produce a compact narrative summary after a campaign has run.
    """
    hybrid_gain = float(success_df["hybrid_success_accept"].mean() - success_df["peeling_success"].mean())
    mean_checker_ms = float(1000.0 * runtime_df["checker_time_s"].mean())
    mean_residual_ms = float(1000.0 * runtime_df["residual_time_s"].mean())
    mean_overhead = float(runtime_df["overhead_ratio"].mean())
    max_false_accept = float(robustness_df["false_accept_rate"].max())

    return (
        f"Across the executed campaign, the hybrid decoder improved the mean success rate over "
        f"peeling-only by {hybrid_gain:.3f}. The checker remained lightweight on average "
        f"({mean_checker_ms:.3f} ms) compared with the residual algebraic phase "
        f"({mean_residual_ms:.3f} ms), with a mean overhead ratio of {mean_overhead:.3f}. "
        f"The maximum observed false-acceptance rate was {max_false_accept:.3f}."
    )


def save_figure_bundle(
    success_df: pd.DataFrame,
    runtime_df: pd.DataFrame,
    checker_df: pd.DataFrame,
    robustness_df: pd.DataFrame,
    out_dir: str | Path,
) -> Dict[str, Path]:
    out_dir = make_output_dir(out_dir)
    paths = {
        "fig1": plot_success_probability(success_df, out_dir / "fig1_success_probability.png"),
        "fig2": plot_runtime_breakdown(runtime_df, out_dir / "fig2_runtime_breakdown.png"),
        "fig3": plot_checker_scaling(checker_df, out_dir / "fig3_checker_scaling.png"),
        "fig4": plot_robustness(robustness_df, out_dir / "fig4_robustness.png"),
    }
    return paths
