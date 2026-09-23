"""Regenerate every non-timing outcome from stored matrices and per-purpose seeds."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import numpy as np
import pandas as pd
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
import selltcfull_experiments as s
from publication_experiments import validate_campaign
out=root/'publication_outputs'
print('Complete grid:',validate_campaign(out))
metadata=pd.read_csv(out/'matrix_metadata.csv')
matrices={};bases={}
for row in metadata.itertuples():
    data=json.loads((out/'matrices'/f'{row.matrix_id}.json').read_text())
    graph=s.Graph(data['n'],tuple(tuple(v) for v in data['rows']))
    regenerated=s.generate_graph(row.family,row.n,3,6,int(row.matrix_seed))
    assert graph==regenerated,row.matrix_id
    matrices[row.matrix_id]=graph
    if row.matrix_id.startswith('campaign_'):bases[row.matrix_id]=s.kernel_basis(graph)
print('All',len(matrices),'matrices regenerated identically.')
raw=pd.concat([pd.read_csv(out/'raw_clean.csv'),pd.read_csv(out/'raw_robustness.csv')],ignore_index=True)
nonzero=0;exact=0
for row in raw.itertuples():
    g=matrices[row.matrix_id]
    x=s.sample_codeword(bases[row.matrix_id],g.n,np.random.default_rng(int(row.word_seed)))
    erased=np.random.default_rng(int(row.erasure_seed)).random(g.n)<row.epsilon
    flips=(np.random.default_rng(int(row.corruption_seed)).random(g.n)<row.delta)&~erased
    y=tuple(-1 if erased[i] else x[i]^int(flips[i]) for i in range(g.n))
    result=s.hybrid_decode(g,y,certify=True)
    assert result['accepted'] and result['kind']==row.kind
    assert int(erased.sum())==row.erasures and int(flips.sum())==row.flips
    for field in ('trace_len','residual_size','rank','nullity'):
        assert result[field]==getattr(row,field),(row.matrix_id,row.epsilon,row.delta,row.trial,field)
    assert (result['word']==x)==row.exact_recovery
    ge=s.hybrid_decode(g,y,peel=False)
    assert ge['kind']==result['kind']
    if result['kind']=='success':
        assert s.verify_word(g,y,result['word']) and s.verify_word(g,y,ge['word'])
    nonzero+=bool(any(x));exact+=bool(result['word']==x)
print('All',len(raw),'non-timing trial outcomes regenerated identically; transmitted nonzero words:',nonzero)
scale=pd.read_csv(out/'raw_scaling.csv')
for row in scale.itertuples():
    g=matrices[row.matrix_id]
    erased=np.random.default_rng(int(row.seed)).random(g.n)<row.epsilon
    y=tuple(-1 if erased[i] else 0 for i in range(g.n))
    state,trace=s.peeling_decode(g,y)
    assert len(trace)==row.trace_len and state.known.count(-1)==row.residual_size
    assert s.check_success_certificate(g,y,trace,[0]*row.residual_size)[0]
print('All',len(scale),'all-zero checker-scaling inputs/traces regenerated identically.')
original_files=subprocess.check_output(['git','ls-files','SELLTCFULL_outputs'],cwd=root,text=True).splitlines()
for name in original_files:
    baseline=subprocess.check_output(['git','show','f9beafa:'+name],cwd=root)
    assert (root/name).read_bytes()==baseline,name
print('All',len(original_files),'original output files unchanged byte-for-byte from f9beafa.')
summary=dict(matrix_reproductions=len(matrices),trial_reproductions=len(raw),scaling_reproductions=len(scale),nonzero_transmitted_words=nonzero,original_files_unchanged=len(original_files),all_checks_passed=True)
(out/'reproduction_validation.json').write_text(json.dumps(summary,indent=2))
