import numpy as np
import pandas as pd
import pytest
import selltcfull_experiments as s


def test_generators_kernel_and_determinism():
    for family in ('random_regular','peg'):
        g=s.generate_graph(family,32,3,6,123)
        assert all(len(row)==6 for row in g.rows)
        assert all(len(row)==3 for row in g.columns)
        assert g==s.generate_graph(family,32,3,6,123)
        basis=s.kernel_basis(g)
        assert len(basis)==g.n-s.gf2_solve(g.to_dense(),[0]*g.m).rank
        words=[s.sample_codeword(basis,g.n,np.random.default_rng(k)) for k in range(10)]
        assert any(any(x) for x in words)
        assert all(s.verify_word(g,[-1]*g.n,x) for x in words)


def test_peg_distance_selects_farthest_available_check():
    assert s.peg_candidates([[0],[0,1],[1,2]],[[0,1],[1,2],[2]],0,[1,1,1])==[2]


def test_timing_metrics_are_consistent():
    g=s.Graph.from_dense([[1,1,0],[0,1,1]])
    r=s.hybrid_decode(g,[-1,-1,-1],certify=True)
    assert r['accepted']
    assert r['total_s']>=r['check_s']>0
    assert r['decode_s']==r['total_s']-r['check_s']
    assert r['relative_overhead']==r['check_s']/r['decode_s']
    assert r['check_fraction']==r['check_s']/r['total_s']
    stages=['init_s','peeling_s','residual_s','elimination_s','witness_s','backsub_s']
    assert all(r[k]>=0 for k in stages)
    assert sum(r[k] for k in stages)<=r['decode_s']


def test_table_filter_and_ratio_definitions():
    from publication_experiments import summarize_conditions
    df=pd.DataFrame([dict(family='test',n=8,matrix_id='a',epsilon=.4,delta=0,trial=i,decode_s=d,check_s=c,total_s=d+c,trace_len=1,residual_size=1,nullity=0,exact_recovery=True,accepted=True,kind='success',flips=0,compatible=True,direct_s=.01,ge_s=.3,hybrid_s=d,certified_s=d+c,peeling_only_s=.1,peeling_complete=True) for i,(d,c) in enumerate([(1.,1.),(9.,1.)])])
    row=summarize_conditions(df).iloc[0]
    assert row['relative_mean_ratio']==pytest.approx((1+1/9)/2)
    assert row['relative_ratio_means']==pytest.approx(.2)
    assert row['fraction_mean_ratio']==pytest.approx(.3)
    assert row['fraction_ratio_means']==pytest.approx(1/6)


def test_seed_scheme_accepts_numpy_group_keys_without_changing_seed():
    from publication_experiments import seed_for
    assert seed_for('bootstrap',np.int64(128),np.float64(.4))==seed_for('bootstrap',128,.4)


def test_campaign_validator_rejects_missing_measurements(tmp_path):
    import publication_experiments as p
    assert hasattr(p,'validate_campaign'), 'complete-grid validation must precede finalization'
    with pytest.raises((ValueError,FileNotFoundError)):
        p.validate_campaign(tmp_path)


def test_analysis_rejects_incomplete_output(tmp_path):
    import json
    import publication_experiments as p
    (tmp_path/'declared_config.json').write_text(json.dumps(p.CONFIG))
    with pytest.raises((ValueError,FileNotFoundError)):
        p.analyze(tmp_path)


def test_analysis_seed_can_use_saved_configuration():
    from publication_experiments import seed_for
    assert seed_for('analysis',base_seed=123)==seed_for('analysis',base_seed=123)
    assert seed_for('analysis',base_seed=123)!=seed_for('analysis',base_seed=124)


def test_scaling_analysis_uses_saved_config_despite_live_defaults(monkeypatch):
    import publication_experiments as p
    data=pd.DataFrame([dict(matrix_id=f'n{n}r{r}',n=n,sparse_s=n*(1+r*.1),direct_s=n*(.5+r*.1),dense_s=n*n*(1+r*.1)) for n in [16,32,64] for r in range(3)])
    saved=dict(p.CONFIG,bootstrap_replicates=20)
    before=p.scaling_summary(data,saved)
    monkeypatch.setitem(p.CONFIG,'base_seed',987654)
    monkeypatch.setitem(p.CONFIG,'bootstrap_replicates',5)
    after=p.scaling_summary(data,saved)
    pd.testing.assert_frame_equal(before,after)
