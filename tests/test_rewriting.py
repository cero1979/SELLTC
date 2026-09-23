"""Independent raw-multiset model and bounded audit of the manuscript semantics.

Run: python3 -m unittest discover -s tests -p 'test_rewriting.py' -v
No decoder or Lean implementation is imported. These are finite regression and
exhaustive checks, not a proof or a refinement of either implementation.
"""
from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations, product
import json
import unittest


@dataclass(frozen=True)
class Context:
    graph: tuple
    persistent: tuple
    linear: tuple


def context(graph, persistent=(), linear=()):
    return Context(tuple(tuple(row) for row in graph),
                   tuple(sorted(persistent)), tuple(sorted(linear)))


@dataclass(frozen=True, order=True)
class Event:
    kind: str
    j: int
    i: int
    b: int
    k: int
    p: int

    @property
    def label(self):
        return (self.j, self.i, self.b) if self.kind == 'solve' else None


def replace_tokens(tokens, removed, added):
    result = Counter(tokens)
    for token in removed:
        assert result[token] > 0
        result[token] -= 1
    result.update(added)
    return tuple(sorted(result.elements()))


def successors(ctx):
    """Exactly the original two raw rewrite rules; no invariant precondition."""
    present = set(ctx.linear)
    result = set()
    for atom in present:
        if atom[0] != 'rem':
            continue
        _, j, k, p = atom
        for pending in present:
            if pending[0] != 'pend' or pending[1] != j:
                continue
            i = pending[2]
            if k > 0:
                for variable, b in set(ctx.persistent):
                    if variable == i:
                        new = replace_tokens(ctx.linear, (pending, atom),
                                             (('rem', j, k - 1, p ^ b),))
                        result.add((Event('propagate', j, i, b, k, p),
                                    context(ctx.graph, ctx.persistent, new)))
            if k == 1 and ('unk', i) in present:
                new = replace_tokens(ctx.linear, (pending, atom, ('unk', i)),
                                     (('rem', j, 0, 0), ('step', j, i, p)))
                result.add((Event('solve', j, i, p, k, p),
                            context(ctx.graph, ctx.persistent + ((i, p),), new)))
    return sorted(result, key=lambda item: item[0])


def neighbors(graph, j):
    return frozenset(i for i, value in enumerate(graph[j]) if value)


def operational(graph, assignment):
    unknown = {i for i, bit in enumerate(assignment) if bit < 0}
    degree = tuple(len(neighbors(graph, j) & unknown) for j in range(len(graph)))
    syndrome = tuple(sum(assignment[i] for i in neighbors(graph, j)
                         if assignment[i] >= 0) % 2 for j in range(len(graph)))
    return tuple(assignment), syndrome, degree


def encode(graph, assignment, trace=()):
    _, syndrome, degree = operational(graph, assignment)
    known = tuple((i, b) for i, b in enumerate(assignment) if b >= 0)
    linear = [('unk', i) for i, b in enumerate(assignment) if b < 0]
    linear += [('rem', j, degree[j], syndrome[j]) for j in range(len(graph))]
    linear += [('pend', j, i) for j in range(len(graph))
               for i in neighbors(graph, j) if assignment[i] < 0]
    linear += [('step',) + stp for stp in trace]
    return context(graph, known, linear)


def invariant(ctx, n, trace):
    """Validate exact token multiplicity and every asynchronous invariant."""
    assignment = [-1] * n
    for i, b in ctx.persistent:
        assert 0 <= i < n and b in (0, 1)
        assert assignment[i] == -1, 'duplicate or contradictory known token'
        assignment[i] = b
    unknown = frozenset(i for i in range(n) if assignment[i] < 0)
    expected = Counter(('unk', i) for i in unknown)
    expected.update(('step',) + stp for stp in trace)
    delayed = []
    for j in range(len(ctx.graph)):
        pending = frozenset(atom[2] for atom in ctx.linear
                            if atom[0] == 'pend' and atom[1] == j)
        nbrs = neighbors(ctx.graph, j)
        assert nbrs & unknown <= pending <= nbrs
        p = sum(assignment[i] for i in nbrs - pending) % 2
        expected.update(('pend', j, i) for i in pending)
        expected.update((('rem', j, len(pending), p),))
        delayed.extend((j, i) for i in pending if assignment[i] >= 0)
    assert expected == Counter(ctx.linear), 'wrong multiplicities, syndrome, or logs'
    return tuple(assignment), tuple(delayed)


def replay(graph, received, trace):
    assignment = list(received)
    for j, i, bit in trace:
        assert 0 <= j < len(graph) and 0 <= i < len(assignment)
        assert {v for v in neighbors(graph, j) if assignment[v] < 0} == {i}
        assert bit == sum(assignment[v] for v in neighbors(graph, j)
                          if assignment[v] >= 0) % 2
        assignment[i] = bit
    return operational(graph, assignment)


def normalize(ctx, reverse=False):
    length = 0
    while True:
        enabled = [(event, nxt) for event, nxt in successors(ctx)
                   if event.kind == 'propagate']
        if not enabled:
            return ctx, length
        _, ctx = enabled[-1 if reverse else 0]
        length += 1


def fire(ctx, kind, j, i, b):
    matches = [(event, nxt) for event, nxt in successors(ctx)
               if (event.kind, event.j, event.i, event.b) == (kind, j, i, b)]
    assert len(matches) == 1
    return matches[0][1]


def realize(graph, received, trace):
    """Construct one Solve-plus-normalization witness of exactly this trace."""
    replay(graph, received, trace)
    current = encode(graph, received)
    recorded = []
    for j, i, b in trace:
        current = fire(current, 'solve', j, i, b)
        recorded.append((j, i, b))
        current, _ = normalize(current)
    return current, tuple(recorded)


def valid_traces(graph, assignment, prefix=()):
    """Independent operational enumerator, including all finite prefixes."""
    yield prefix
    for j in range(len(graph)):
        unresolved = [i for i in neighbors(graph, j) if assignment[i] < 0]
        if len(unresolved) == 1:
            i = unresolved[0]
            b = sum(assignment[v] for v in neighbors(graph, j)
                    if assignment[v] >= 0) % 2
            nxt = list(assignment)
            nxt[i] = b
            yield from valid_traces(graph, tuple(nxt), prefix + ((j, i, b),))


def flatten(ctx):
    """Forget the two persistent-zone labels and use ordinary typed tokens."""
    tokens = list(ctx.linear)
    tokens += [('val', i, b) for i, b in ctx.persistent]
    tokens += [('edge', j, i) for j in range(len(ctx.graph))
               for i in neighbors(ctx.graph, j)]
    return tuple(sorted(tokens))


def ordinary_successors(tokens):
    """Independent consume-and-recreate encoding of persistent lookup."""
    present = set(tokens)
    result = set()
    for atom in present:
        if atom[0] != 'rem':
            continue
        _, j, k, p = atom
        for pending in present:
            if pending[0] != 'pend' or pending[1] != j:
                continue
            i = pending[2]
            if k > 0:
                for b in (0, 1):
                    value = ('val', i, b)
                    if value in present:
                        nxt = replace_tokens(tokens, (value, pending, atom),
                                             (value, ('rem', j, k - 1, p ^ b)))
                        result.add((Event('propagate', j, i, b, k, p), nxt))
            if k == 1 and ('unk', i) in present:
                nxt = replace_tokens(tokens, (pending, atom, ('unk', i)),
                                     (('val', i, p), ('rem', j, 0, 0),
                                      ('step', j, i, p)))
                result.add((Event('solve', j, i, p, k, p), nxt))
    return result


def old_wf(ctx, n):
    """Literal weak original Lean membership/cardinality conditions."""
    for j in range(len(ctx.graph)):
        rem = {atom[2:] for atom in ctx.linear if atom[0] == 'rem' and atom[1] == j}
        if len(rem) != 1:
            return False
        k, _ = next(iter(rem))
        if sum(atom[0] == 'pend' and atom[1] == j for atom in ctx.linear) != k:
            return False
    for i in range(n):
        if (('unk', i) in ctx.linear) != (not any(v == i for v, _ in ctx.persistent)):
            return False
    return True


class RewritingRegression(unittest.TestCase):
    def test_empty_dimensions_and_isolated_variables(self):
        for graph, received in (((), ()), ((), (-1, 1)), (((), ()), ()),
                                (((0, 0),), (-1, 0))):
            ctx = encode(graph, received)
            assignment, delayed = invariant(ctx, len(received), ())
            self.assertEqual(assignment, received)
            self.assertEqual(delayed, ())
            self.assertEqual(successors(ctx), [])
            self.assertEqual(normalize(ctx), (ctx, 0))

    def test_lost_log_is_a_real_counterexample(self):
        initial = encode(((1,),), (-1,))
        after = fire(initial, 'solve', 0, 0, 0)
        self.assertNotEqual(after, encode(((1,),), (0,)))
        self.assertEqual(after, encode(((1,),), (0,), ((0, 0, 0),)))
        self.assertEqual(successors(after), [])

    def test_original_wf_allows_duplicate_rem_and_is_not_preserved(self):
        ctx = context(((1,),), ((0, 0),),
                      (('pend', 0, 0), ('rem', 0, 1, 0), ('rem', 0, 1, 0)))
        self.assertTrue(old_wf(ctx, 1))
        self.assertFalse(old_wf(fire(ctx, 'propagate', 0, 0, 0), 1))
        with self.assertRaises(AssertionError):
            invariant(ctx, 1, ())

    def test_original_wf_allows_duplicate_unknown(self):
        ctx = context(((1,),), (),
                      (('unk', 0), ('unk', 0), ('pend', 0, 0), ('rem', 0, 1, 0)))
        self.assertTrue(old_wf(ctx, 1))
        self.assertFalse(old_wf(fire(ctx, 'solve', 0, 0, 0), 1))

    def test_original_wf_allows_conflicting_knowledge(self):
        ctx = context(((1,),), ((0, 0), (0, 1)), (('rem', 0, 0, 0),))
        self.assertTrue(old_wf(ctx, 1))
        with self.assertRaises(AssertionError):
            invariant(ctx, 1, ())

    def test_missing_or_nonedge_pending_incidence_is_not_admissible(self):
        missing = context(((1, 1),), (),
                          (('unk', 0), ('unk', 1), ('pend', 0, 0), ('rem', 0, 1, 1)))
        nonedge = context(((0,),), (),
                          (('unk', 0), ('pend', 0, 0), ('rem', 0, 1, 0)))
        for ctx, received, triple in ((missing, (-1, -1), (0, 0, 1)),
                                      (nonedge, (-1,), (0, 0, 0))):
            self.assertTrue(old_wf(ctx, len(received)))
            self.assertTrue(successors(ctx))
            with self.assertRaises(AssertionError):
                invariant(ctx, len(received), ())
            with self.assertRaises(AssertionError):
                replay(ctx.graph, received, (triple,))

    def test_second_solve_can_precede_pending_propagations(self):
        graph = ((1, 0), (0, 1), (1, 1))
        ctx = fire(encode(graph, (-1, -1)), 'solve', 0, 0, 0)
        ctx = fire(ctx, 'solve', 1, 1, 0)
        trace = ((0, 0, 0), (1, 1, 0))
        known, delayed = invariant(ctx, 2, trace)
        self.assertEqual(known, (0, 0))
        self.assertEqual(len(delayed), 2)
        self.assertIn(('rem', 2, 2, 0), ctx.linear)
        self.assertEqual(normalize(ctx)[0], encode(graph, known, trace))
        self.assertEqual(normalize(ctx)[0], normalize(ctx, reverse=True)[0])

    def test_nonzero_stale_syndrome(self):
        graph = ((1, 1), (1, 1))
        ctx = fire(encode(graph, (-1, 1)), 'solve', 0, 0, 1)
        assignment, delayed = invariant(ctx, 2, ((0, 0, 1),))
        self.assertEqual(operational(graph, assignment)[1], (0, 0))
        self.assertIn(('rem', 1, 1, 1), ctx.linear)
        self.assertEqual(delayed, ((1, 0),))

    def test_terminal_multiset_does_not_determine_trace_order(self):
        graph = ((1, 0), (0, 1))
        a = ((0, 0, 0), (1, 1, 0))
        b = tuple(reversed(a))
        self.assertNotEqual(a, b)
        self.assertEqual(realize(graph, (-1, -1), a)[0],
                         realize(graph, (-1, -1), b)[0])

    def test_all_rules_are_not_globally_confluent_on_inconsistent_input(self):
        graph = ((1, 0), (1, 1))
        initial = encode(graph, (-1, 1))
        left = normalize(fire(initial, 'solve', 0, 0, 0))[0]
        right = normalize(fire(initial, 'solve', 1, 0, 1))[0]
        self.assertNotEqual(left, right)
        self.assertEqual(successors(left), [])
        self.assertEqual(successors(right), [])

    def test_exhaustive_small_instances(self):
        counts = Counter()
        dimensions = ((0, 0), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2))
        for n, m in dimensions:
            for flat in product((0, 1), repeat=n * m):
                graph = tuple(tuple(flat[j*n+i] for i in range(n)) for j in range(m))
                for received in product((-1, 0, 1), repeat=n):
                    counts['instances'] += 1
                    start = (encode(graph, received), ())
                    seen = {start}
                    todo = deque([start])
                    while todo:
                        ctx, trace = todo.popleft()
                        counts['reachable_contexts'] += 1
                        assignment, delayed = invariant(ctx, n, trace)
                        self.assertEqual(operational(graph, assignment), replay(graph, received, trace))
                        counts['delayed_contexts'] += bool(delayed)
                        normalized, length = normalize(ctx)
                        self.assertEqual(length, len(delayed))
                        self.assertEqual(normalized, encode(graph, assignment, trace))
                        self.assertEqual(normalized, normalize(ctx, reverse=True)[0])
                        outgoing = successors(ctx)
                        self.assertEqual({(e, flatten(nxt)) for e, nxt in outgoing},
                                         ordinary_successors(flatten(ctx)))
                        enabled_props = [e for e, _ in outgoing if e.kind == 'propagate']
                        for a, b in combinations(enabled_props, 2):
                            ab = fire(fire(ctx, a.kind, a.j, a.i, a.b), b.kind, b.j, b.i, b.b)
                            ba = fire(fire(ctx, b.kind, b.j, b.i, b.b), a.kind, a.j, a.i, a.b)
                            self.assertEqual(ab, ba)
                            counts['propagation_diamonds'] += 1
                        for event, nxt in outgoing:
                            counts['rewrite_edges'] += 1
                            counts[event.kind + '_edges'] += 1
                            new_trace = trace + ((event.label,) if event.label is not None else ())
                            pair = (nxt, new_trace)
                            if pair not in seen:
                                seen.add(pair)
                                todo.append(pair)
                    for trace in valid_traces(graph, received):
                        terminal, actual_trace = realize(graph, received, trace)
                        self.assertEqual(actual_trace, trace)
                        self.assertEqual(terminal, encode(graph, replay(graph, received, trace)[0], trace))
                        counts['operational_traces_realized'] += 1
        self.assertEqual(counts['instances'], 2719)
        self.assertEqual(counts['reachable_contexts'], 6251)
        self.assertEqual(counts['rewrite_edges'], 3724)
        print('\nSEMANTICS_COUNTS=' + json.dumps(dict(sorted(counts.items())), sort_keys=True), flush=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
