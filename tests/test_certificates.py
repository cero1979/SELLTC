import itertools
import json
import numpy as np
import pytest
import selltcfull_experiments as s


def bits(n):
    return itertools.product((0, 1), repeat=n)


def test_strict_binary_regression():
    h = [[1, 1]]
    for rho in ([2, 2], [.1, .1], ['0', '0'], np.array(0), [[0], [0]], [0], None):
        assert s.check_success_certificate(h, [-1, -1], [], rho) == (False, None)
    for trace in ([(0,)], [(0, 0, .1)], [(0.0, 0, 0)], [(True, 0, 0)], None):
        assert s.check_success_certificate([[1]], [-1], trace, []) == (False, None)
    assert not s.check_failure_certificate([[1]], [1], [], [3])


def test_invalid_public_inputs_and_immutable_graph():
    for h in ([[2]], [[.0]], [[1], [0, 1]], np.ones((1, 1, 1)), None):
        assert s.check_success_certificate(h, [-1], [], [0]) == (False, None)
    for y in ([2], [-2], [.0], [], [[0]], None):
        assert not s.check_success_certificate([[1]], y, [], [0])[0]
    g=s.Graph.from_dense([[1,0],[1,1]])
    with pytest.raises((ValueError, TypeError)):
        s.Graph(2, ((0,0),))
    with pytest.raises((AttributeError, TypeError)):
        g.n=3
    assert g.edge_count == 3


def test_trace_mutations_and_valid_alternatives():
    h=[[1,0],[1,1]];y=[-1,-1];trace=[(0,0,0),(1,1,0)]
    assert s.check_success_certificate(h,y,trace,[]) == (True,(0,0))
    for bad in (trace[::-1], [(0,0,1),(1,1,0)], [(2,0,0)], [(0,1,0)], trace+[trace[0]]):
        assert not s.check_success_certificate(h,y,bad,[])[0]
    assert not s.check_success_certificate(h,y,trace[:1],[])[0]
    assert s.check_success_certificate(h,y,trace[:1],[0])[0]
    assert s.check_success_certificate(h,y,[],[0,0])[0]
    independent=[[1,0],[0,1]]
    assert s.check_success_certificate(independent,y,trace[::-1],[])[0]
    assert s.check_success_certificate([[1,1]],y,[],[1,1]) == (True,(1,1))
    assert not s.check_success_certificate([[1,1]],y,[],[1,0])[0]
    assert not s.verify_word([[1,1]],[0,-1],[1,1])


def test_failure_edge_cases_and_compatible_corruption():
    assert s.check_failure_certificate([[1]],[1],[],[1])
    assert not s.check_failure_certificate([[1]],[1],[],[0])
    assert not s.check_failure_certificate([[1]],[1],[],[])
    assert not s.check_failure_certificate([[1]],[-1],[],[1])
    assert s.check_success_certificate([[1,1]],[1,-1],[],[1])==(True,(1,1))
    assert s.verify_word(s.Graph(0,((),)),[],[])
    assert s.check_success_certificate(s.Graph(0,((),)),[],[],[])==(True,())
    assert not s.check_failure_certificate(s.Graph(0,((),)),[],[],[1])


def test_exhaustive_small_system_solver_and_checkers():
    # Includes zero variables/rows, redundancy and all consistent/inconsistent RHSs.
    count=0
    for m in range(4):
        for n in range(4):
            for entries in bits(m*n):
                a=np.array(entries,dtype=np.uint8).reshape(m,n)
                for rhs in bits(m):
                    valid=[x for x in bits(n) if np.array_equal(a@np.array(x,dtype=np.uint8)%2,rhs)]
                    out=s.gf2_solve(a,rhs)
                    assert out.solvable == bool(valid)
                    if valid:
                        assert tuple(out.solution) in valid
                    else:
                        w=np.array(out.witness,dtype=np.uint8)
                        assert np.all(w@a%2==0)
                        assert int(w@np.array(rhs,dtype=np.uint8)%2)==1
                    count+=1
    assert count==5054


def test_exhaustive_certificate_acceptance_truth():
    for m,n in [(0,2),(1,2),(2,2),(2,3)]:
        for entries in bits(m*n):
            a=np.array(entries,dtype=np.uint8).reshape(m,n)
            g=s.Graph.from_dense(a)
            for y in itertools.product((-1,0,1),repeat=n):
                completions=[x for x in bits(n) if all(v==-1 or v==x[i] for i,v in enumerate(y)) and np.all(a@np.array(x,dtype=np.uint8)%2==0)]
                out=s.hybrid_decode(g,y,certify=True)
                assert out['accepted']
                assert (out['kind']=='success')==bool(completions)
                if completions:
                    assert tuple(out['word']) in completions
                    assert s.verify_word(g,y,out['word'])
                else:
                    assert s.check_failure_certificate(g,y,out['trace'],out['witness'])
                erased=[i for i,v in enumerate(y) if v==-1]
                for rho in bits(len(erased)):
                    ok,x=s.check_success_certificate(g,y,[],rho)
                    assert ok==(x in completions if ok else any(tuple(rho)==tuple(z[i] for i in erased) for z in completions))
                for w in bits(m):
                    ok=s.check_failure_certificate(g,y,[],w)
                    if ok:assert not completions


def test_json_boundary():
    case={'H':[[1,1]],'y':[-1,-1],'kind':'success','trace':[],'witness':[0,0]}
    assert s.check_json(case)=={'accepted':True,'word':[0,0]}
    for value in (None,{},dict(case,kind='x'),dict(case,witness=[2,2]),dict(case,trace=[[0]])):
        assert s.check_json(value)=={'accepted':False,'word':None}


def test_dense_sparse_same_certificate():
    a=np.array([[1,0,1],[0,1,1]],dtype=np.uint8);g=s.Graph.from_dense(a)
    for y in itertools.product((-1,0,1),repeat=3):
        r=s.hybrid_decode(g,y,certify=True)
        assert s.dense_check_certificate(a,y,r['kind'],r['trace'],r['witness'])==r['accepted']


def test_json_empty_matrix_keeps_received_dimension():
    case=dict(H=[],y=[-1,1],kind='success',trace=[],witness=[0])
    assert s.check_json(case)=={'accepted':True,'word':[0,1]}
    assert s.check_json(dict(case,kind='failure',witness=[]))=={'accepted':False,'word':None}
