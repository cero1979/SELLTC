"""Executable certification reference, not a mechanically verified Python program.

Trusted boundary: Graph construction validates binary incidence and freezes adjacency.
The sparse checker costs O(E+n+m+|T|) word operations on that representation.
Dense conversion/preprocessing and the integer-bitset GE engine are separate costs.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from numbers import Integral
from time import perf_counter
import json
import sys
from typing import Any
import numpy as np


def _integer(x: Any) -> bool:
    return isinstance(x, Integral) and not isinstance(x, (bool, np.bool_))


def _vector(value: Any, length: int, alphabet=(0, 1)) -> tuple[int, ...] | None:
    if not isinstance(value, (list, tuple, np.ndarray)):
        return None
    if isinstance(value, np.ndarray) and value.ndim != 1:
        return None
    if len(value) != length:
        return None
    if any(not _integer(v) or int(v) not in alphabet for v in value):
        return None
    return tuple(int(v) for v in value)


@dataclass(frozen=True)
class Graph:
    """Validated immutable binary incidence; rows may include isolated checks."""
    n: int
    rows: tuple[tuple[int, ...], ...]
    columns: tuple[tuple[int, ...], ...] = field(init=False, repr=False)

    def __post_init__(self):
        if not _integer(self.n) or self.n < 0:
            raise ValueError('n must be a nonnegative integer')
        if not isinstance(self.rows, (list, tuple)):
            raise ValueError('rows must be a finite sequence')
        cols = [[] for _ in range(self.n)]
        frozen = []
        for j, row in enumerate(self.rows):
            if not isinstance(row, (list, tuple)) or any(not _integer(i) or not 0 <= i < self.n for i in row):
                raise ValueError('invalid edge index')
            if len(set(row)) != len(row):
                raise ValueError('duplicate Tanner edge')
            row = tuple(sorted(int(i) for i in row))
            frozen.append(row)
            for i in row:
                cols[i].append(j)
        object.__setattr__(self, 'rows', tuple(frozen))
        object.__setattr__(self, 'columns', tuple(tuple(c) for c in cols))

    @property
    def m(self):
        return len(self.rows)

    @property
    def edge_count(self):
        return sum(map(len, self.rows))

    @classmethod
    def from_dense(cls, matrix):
        if not isinstance(matrix, (list, tuple, np.ndarray)):
            raise ValueError('matrix must be a two-dimensional binary array')
        if isinstance(matrix, np.ndarray):
            if matrix.ndim != 2:
                raise ValueError('matrix must have two dimensions')
            n = matrix.shape[1]
        else:
            n = len(matrix[0]) if len(matrix) and isinstance(matrix[0], (list, tuple, np.ndarray)) else 0
        rows = []
        for row in matrix:
            b = _vector(row, n)
            if b is None:
                raise ValueError('matrix must be rectangular and binary')
            rows.append(tuple(i for i, x in enumerate(b) if x))
        return cls(n, tuple(rows))

    def to_dense(self):
        out = np.zeros((self.m, self.n), dtype=np.uint8)
        for j, row in enumerate(self.rows):
            out[j, list(row)] = 1
        return out


def _graph(value, received=None):
    # JSON cannot encode a 0-by-n matrix's second dimension; y determines n.
    if isinstance(value, (list, tuple)) and not value and isinstance(received, (list, tuple, np.ndarray)):
        return Graph(len(received), ())
    return value if isinstance(value, Graph) else Graph.from_dense(value)


@dataclass
class State:
    known: list[int]
    syndrome: list[int]
    degree: list[int]
    unknown_xor: list[int]


def initialize_state(g: Graph, y: tuple[int, ...]) -> State:
    syndrome, degree, unknown_xor = [], [], []
    for row in g.rows:
        p = d = q = 0
        for i in row:
            if y[i] == -1:
                d += 1
                q ^= i
            else:
                p ^= y[i]
        syndrome.append(p)
        degree.append(d)
        unknown_xor.append(q)
    return State(list(y), syndrome, degree, unknown_xor)


def _apply(g: Graph, state: State, i: int, b: int):
    state.known[i] = b
    for j in g.columns[i]:
        state.syndrome[j] ^= b
        state.degree[j] -= 1
        state.unknown_xor[j] ^= i


def _parse_trace(trace, n, m):
    if not isinstance(trace, (list, tuple)) or len(trace) > n:
        return None
    result = []
    for triple in trace:
        if not isinstance(triple, (list, tuple)) or len(triple) != 3:
            return None
        j, i, b = triple
        if not all(_integer(v) for v in triple) or not (0 <= j < m and 0 <= i < n and b in (0, 1)):
            return None
        result.append((int(j), int(i), int(b)))
    return result


def _replay(g, y, trace):
    state = initialize_state(g, y)
    for j, i, b in trace:
        if state.degree[j] != 1 or state.unknown_xor[j] != i or state.known[i] != -1 or state.syndrome[j] != b:
            return None
        _apply(g, state, i, b)
    return state


def check_success_certificate(H, y, trace, rho):
    """Reject malformed evidence; allow any valid prefix, including the empty trace."""
    try:
        g = _graph(H, y)
        y = _vector(y, g.n, (-1, 0, 1))
        trace = _parse_trace(trace, g.n, g.m)
        if y is None or trace is None:
            return False, None
        state = _replay(g, y, trace)
        if state is None:
            return False, None
        unknown = [i for i, v in enumerate(state.known) if v == -1]
        rho = _vector(rho, len(unknown))
        if rho is None:
            return False, None
        word = state.known
        for i, b in zip(unknown, rho):
            word[i] = b
        # Check the residual equations directly over the original incidence.
        # Known assignments are fixed by y or a validated replay step.
        for j, row in enumerate(g.rows):
            parity = 0
            for i in row:
                parity ^= word[i]
            if parity:
                return False, None
        return True, tuple(word)
    except (ValueError, TypeError, IndexError, OverflowError):
        return False, None


def check_failure_certificate(H, y, trace, witness):
    try:
        g = _graph(H, y)
        y = _vector(y, g.n, (-1, 0, 1))
        trace = _parse_trace(trace, g.n, g.m)
        w = _vector(witness, g.m)
        if y is None or trace is None or w is None:
            return False
        state = _replay(g, y, trace)
        if state is None:
            return False
        parity = 0
        left = [0] * g.n
        for j, row in enumerate(g.rows):
            if w[j]:
                parity ^= state.syndrome[j]
                for i in row:
                    if state.known[i] == -1:
                        left[i] ^= 1
        return parity == 1 and not any(left)
    except (ValueError, TypeError, IndexError, OverflowError):
        return False


def verify_word(H, y, word):
    """Independent direct verifier: no replay, residual state or decoder calls."""
    try:
        g = _graph(H, y)
        y = _vector(y, g.n, (-1, 0, 1))
        x = _vector(word, g.n)
        if y is None or x is None:
            return False
        for i in range(g.n):
            if y[i] != -1 and y[i] != x[i]:
                return False
        for row in g.rows:
            value = 0
            for i in row:
                value ^= x[i]
            if value:
                return False
        return True
    except (ValueError, TypeError, IndexError, OverflowError):
        return False


def peeling_decode(g, y):
    g = _graph(g, y)
    y = _vector(y, g.n, (-1, 0, 1))
    if y is None:
        raise ValueError('invalid received word')
    state = initialize_state(g, y)
    trace = _peel(g, state)
    return state, trace


def _peel(g, state):
    queue = deque(j for j, d in enumerate(state.degree) if d == 1)
    trace = []
    while queue:
        j = queue.popleft()
        if state.degree[j] != 1:
            continue
        i, b = state.unknown_xor[j], state.syndrome[j]
        trace.append((j, i, b))
        _apply(g, state, i, b)
        for k in g.columns[i]:
            if state.degree[k] == 1:
                queue.append(k)
    return trace


def residual_system(g, state):
    unknown = [i for i, v in enumerate(state.known) if v == -1]
    position = {i: k for k, i in enumerate(unknown)}
    rows = []
    for neighbors in g.rows:
        row = 0
        for i in neighbors:
            if i in position:
                row |= 1 << position[i]
        rows.append(row)
    return rows, state.syndrome.copy(), unknown


@dataclass
class SolveResult:
    solvable: bool
    solution: tuple[int, ...] | None
    witness: tuple[int, ...] | None
    rank: int
    elimination_s: float
    witness_s: float
    backsub_s: float


def _eliminate(rows, rhs, n):
    """Fixed first-available pivot order for every comparator; exact bit arithmetic."""
    a, b = list(rows), list(rhs)
    transforms = [1 << j for j in range(len(a))]
    rank = 0
    pivots = []
    for col in range(n):
        pivot = next((r for r in range(rank, len(a)) if (a[r] >> col) & 1), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        b[rank], b[pivot] = b[pivot], b[rank]
        transforms[rank], transforms[pivot] = transforms[pivot], transforms[rank]
        for r in range(rank + 1, len(a)):
            if (a[r] >> col) & 1:
                a[r] ^= a[rank]
                b[r] ^= b[rank]
                transforms[r] ^= transforms[rank]
        pivots.append(col)
        rank += 1
        if rank == len(a):
            break
    return a, b, transforms, pivots


def solve_bitrows(rows, rhs, n):
    t0 = perf_counter()
    a, b, transforms, pivots = _eliminate(rows, rhs, n)
    contradiction = next((j for j in range(len(a)) if a[j] == 0 and b[j] == 1), None)
    elimination_s = perf_counter() - t0
    t0 = perf_counter()
    witness = None if contradiction is None else tuple((transforms[contradiction] >> j) & 1 for j in range(len(a)))
    witness_s = perf_counter() - t0
    t0 = perf_counter()
    solution = None
    if contradiction is None:
        x = 0
        for j in range(len(pivots) - 1, -1, -1):
            if b[j] ^ ((a[j] & x).bit_count() & 1):
                x |= 1 << pivots[j]
        solution = tuple((x >> i) & 1 for i in range(n))
    backsub_s = perf_counter() - t0
    return SolveResult(contradiction is None, solution, witness, len(pivots), elimination_s, witness_s, backsub_s)


def gf2_solve(A, b):
    g = _graph(A)
    rhs = _vector(b, g.m)
    if rhs is None:
        raise ValueError('invalid right-hand side')
    rows = [sum(1 << i for i in row) for row in g.rows]
    return solve_bitrows(rows, rhs, g.n)


def kernel_basis(g):
    rows = [sum(1 << i for i in row) for row in g.rows]
    a, _, _, pivots = _eliminate(rows, [0] * g.m, g.n)
    free = sorted(set(range(g.n)) - set(pivots))
    basis = []
    for col in free:
        x = 1 << col
        for j in range(len(pivots) - 1, -1, -1):
            if (a[j] & x).bit_count() & 1:
                x |= 1 << pivots[j]
        basis.append(x)
    return tuple(basis)


def sample_codeword(basis, n, rng):
    word = 0
    for v, use in zip(basis, rng.integers(0, 2, len(basis))):
        if use:
            word ^= v
    return tuple((word >> i) & 1 for i in range(n))


def hybrid_decode(H, y, certify=False, peel=True):
    """Untrusted producer; timing excludes once-per-matrix Graph construction."""
    g = _graph(H, y)
    tstart = perf_counter()
    y = _vector(y, g.n, (-1, 0, 1))
    if y is None:
        raise ValueError('invalid received word')
    t = perf_counter()
    state = initialize_state(g, y)
    init_s = perf_counter() - t
    t = perf_counter()
    trace = _peel(g, state) if peel else []
    peeling_s = perf_counter() - t
    t = perf_counter()
    rows, rhs, unknown = residual_system(g, state)
    residual_s = perf_counter() - t
    solution = solve_bitrows(rows, rhs, len(unknown))
    kind = 'success' if solution.solvable else 'failure'
    witness = solution.solution if solution.solvable else solution.witness
    word = None
    if solution.solvable:
        word = state.known.copy()
        for i, bit in zip(unknown, witness):
            word[i] = bit
        word = tuple(word)
    check_s = 0.
    accepted = None
    if certify:
        t = perf_counter()
        if kind == 'success':
            accepted, checked_word = check_success_certificate(g, y, trace, witness)
            if accepted and checked_word != word:
                raise AssertionError('producer and checker output differ')
        else:
            accepted = check_failure_certificate(g, y, trace, witness)
        check_s = perf_counter() - t
    total_s = perf_counter() - tstart
    decode_s = total_s - check_s
    return dict(kind=kind, trace=trace, witness=witness, word=word, accepted=accepted,
                trace_len=len(trace), residual_size=len(unknown), rank=solution.rank,
                nullity=len(unknown)-solution.rank, init_s=init_s, peeling_s=peeling_s,
                residual_s=residual_s, elimination_s=solution.elimination_s,
                witness_s=solution.witness_s, backsub_s=solution.backsub_s,
                check_s=check_s, total_s=total_s, decode_s=decode_s,
                relative_overhead=check_s/decode_s, check_fraction=check_s/total_s)


def peeling_only(g, y):
    t = perf_counter()
    state, trace = peeling_decode(g, y)
    return dict(total_s=perf_counter()-t, complete=(-1 not in state.known and not any(state.syndrome)), trace_len=len(trace))


def peg_candidates(var_rows, check_rows, variable, remaining):
    """Largest graph distance, preferring disconnected checks; capacity is explicit."""
    distance = {}
    seen_v = {variable}
    queue = deque([(variable, 0)])
    while queue:
        v, d = queue.popleft()
        for j in var_rows[v]:
            if j in distance:
                continue
            distance[j] = d + 1
            for w in check_rows[j]:
                if w not in seen_v:
                    seen_v.add(w)
                    queue.append((w, d + 2))
    available = [j for j in range(len(check_rows)) if remaining[j] > 0 and j not in var_rows[variable]]
    if not available:
        return []
    disconnected = [j for j in available if j not in distance]
    if disconnected:
        return disconnected
    farthest = max(distance[j] for j in available)
    return [j for j in available if distance[j] == farthest]


def generate_graph(family, n, dv, dc, seed):
    if n * dv % dc or dv > n * dv // dc or dc > n:
        raise ValueError('invalid regular degree profile')
    m = n * dv // dc
    rng = np.random.default_rng(seed)
    if family == 'random_regular':
        # Uniform socket permutation, rejecting non-simple pairings.
        checks = np.repeat(np.arange(m), dc)
        variables = np.repeat(np.arange(n), dv)
        for _ in range(10000):
            assignment = rng.permutation(variables)
            if len(np.unique(checks * n + assignment)) == n * dv:
                return Graph(n, tuple(tuple(int(i) for i in assignment[j*dc:(j+1)*dc]) for j in range(m)))
        raise RuntimeError('simple configuration-model sampling exhausted budget')
    if family != 'peg':
        raise ValueError('unsupported family')
    for _ in range(200):
        var_rows = [[] for _ in range(n)]
        check_rows = [[] for _ in range(m)]
        remaining = [dc] * m
        ok = True
        for variable in range(n):
            for _ in range(dv):
                candidates = peg_candidates(var_rows, check_rows, variable, remaining)
                if not candidates:
                    ok = False
                    break
                degree = min(len(check_rows[j]) for j in candidates)
                candidates = [j for j in candidates if len(check_rows[j]) == degree]
                j = int(rng.choice(candidates))
                var_rows[variable].append(j)
                check_rows[j].append(variable)
                remaining[j] -= 1
            if not ok:
                break
        if ok:
            return Graph(n, tuple(tuple(row) for row in check_rows))
    raise RuntimeError('capacity-constrained PEG sampling exhausted budget')


def dense_check_certificate(H, y, kind, trace, witness):
    """Dense replay baseline with strict parsing; retains O(mn) scans and products.

    H is a prevalidated dense binary matrix corresponding to the benchmark Graph.
    This does not invoke the sparse checker. It is a timing baseline, not verified code.
    """
    if not isinstance(H, np.ndarray) or H.ndim != 2:
        return False
    m, n = H.shape
    y = _vector(y, n, (-1, 0, 1))
    trace = _parse_trace(trace, n, m)
    if y is None or trace is None or kind not in ('success', 'failure'):
        return False
    known = np.array(y, dtype=np.int8)
    unknown = known == -1
    degree = H[:, unknown].sum(axis=1)
    rhs = (H[:, ~unknown] @ known[~unknown].astype(np.uint8)) % 2
    for j, i, b in trace:
        candidates = np.flatnonzero(H[j] & unknown)
        if degree[j] != 1 or len(candidates) != 1 or candidates[0] != i or rhs[j] != b:
            return False
        known[i] = b
        unknown[i] = False
        adjacent = np.flatnonzero(H[:, i])
        rhs[adjacent] ^= np.uint8(b)
        degree[adjacent] -= 1
    if kind == 'success':
        w = _vector(witness, int(unknown.sum()))
        if w is None:
            return False
        known[unknown] = w
        return bool(np.all(H @ known.astype(np.uint8) % 2 == 0))
    w = _vector(witness, m)
    if w is None:
        return False
    w = np.array(w, dtype=np.uint8)
    return bool(np.all(w @ H[:, unknown] % 2 == 0) and w @ rhs % 2 == 1)


def check_json(value):
    rejected = {'accepted': False, 'word': None}
    if not isinstance(value, dict) or set(value) != {'H', 'y', 'kind', 'trace', 'witness'}:
        return rejected
    if value['kind'] == 'success':
        accepted, word = check_success_certificate(value['H'], value['y'], value['trace'], value['witness'])
        return {'accepted': accepted, 'word': list(word) if word is not None else None}
    if value['kind'] == 'failure':
        return {'accepted': check_failure_certificate(value['H'], value['y'], value['trace'], value['witness']), 'word': None}
    return rejected


if __name__ == '__main__':
    for line in sys.stdin:
        try:
            result = check_json(json.loads(line))
        except (ValueError, TypeError):
            result = {'accepted': False, 'word': None}
        print(json.dumps(result), flush=True)
