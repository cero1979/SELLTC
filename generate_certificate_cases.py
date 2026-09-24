"""Deterministic regression/differential corpus; no experiments are invented."""
from __future__ import annotations
import argparse
from copy import deepcopy
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
import selltcfull_experiments as s


def make_cases():
    cases=[];labels=[]
    for m,n in [(0,0),(1,1),(1,2),(2,2)]:
        for entries in itertools.product((0,1),repeat=m*n):
            H=np.array(entries,dtype=np.uint8).reshape(m,n)
            for y in itertools.product((-1,0,1),repeat=n):
                decoded=s.hybrid_decode(s.Graph.from_dense(H),y,certify=True)
                case=dict(H=H.tolist(),y=list(y),kind=decoded['kind'],trace=[list(t) for t in decoded['trace']],witness=list(decoded['witness']))
                cases.append(case);labels.append('honest')
                # Include adversarial witness edits even when they produce a different valid certificate.
                if case['witness']:
                    changed=deepcopy(case);changed['witness'][0]^=1
                    cases.append(changed);labels.append('witness_bit_flip')
                if case['trace']:
                    changed=deepcopy(case);changed['trace'][0][2]^=1
                    cases.append(changed);labels.append('trace_bit_flip')
                    changed=deepcopy(case);changed['trace']=changed['trace'][:-1]
                    cases.append(changed);labels.append('truncated_trace_same_witness')
                if case['kind']=='success':
                    changed=dict(H=H.tolist(),y=list(y),kind='success',trace=[],witness=[decoded['word'][i] for i,v in enumerate(y) if v==-1])
                    cases.append(changed);labels.append('valid_empty_trace')
    cases.extend([dict(H=[],y=[-1,1],kind='success',trace=[],witness=[0]),
                  dict(H=[],y=[-1,1],kind='failure',trace=[],witness=[])])
    labels.extend(['zero_checks_success','zero_checks_cannot_fail'])
    invalid=[None,{},dict(H=[[1]],y=[-1],kind='other',trace=[],witness=[0])]
    valid=dict(H=[[1]],y=[-1],kind='success',trace=[[0,0,0]],witness=[])
    for key,value in [('H',[[2]]),('H',[[1],[0,1]]),('y',[2]),('y',[]),('y',[[0]]),('trace',[[0]]),('trace',[[0,0,2]]),('trace',[[0,0,.1]]),('trace',[[0.,0,0]]),('trace',[[True,0,0]]),('trace',[[1,0,0]]),('trace',[[0,-1,0]]),('witness',[0]),('witness',None)]:
        invalid.append(dict(valid,**{key:value}))
    invalid.extend([dict(H=[[1,1]],y=[-1,-1],kind='success',trace=[],witness=v) for v in [[2,2],[.1,.1],['0','0'],[[0],[0]],None]])
    invalid.extend([dict(H=[[1]],y=[1],kind='failure',trace=[],witness=v) for v in [[3],[],[[1]],None]])
    for case in invalid:
        cases.append(case);labels.append('malformed_reject')
    return cases,labels


def named_adversarial_cases():
    base=dict(H=[[1,0],[1,1]],y=[-1,-1],kind='success',trace=[[0,0,0],[1,1,0]],witness=[])
    specifications=[('valid_complete',base,True)]
    def edit(name,expected=True,**kwargs):specifications.append((name,dict(base,**kwargs),expected))
    edit('changed_trace_value',False,trace=[[0,0,1],[1,1,0]])
    edit('dependent_steps_reversed',False,trace=base['trace'][::-1])
    edit('check_index_out_of_bounds',False,trace=[[2,0,0]])
    edit('variable_index_wrong',False,trace=[[0,1,0]])
    edit('duplicate_step',False,trace=base['trace']+[base['trace'][0]])
    edit('truncated_trace_without_residual',False,trace=base['trace'][:1])
    edit('truncated_trace_with_valid_residual',True,trace=base['trace'][:1],witness=[0])
    edit('empty_trace_with_valid_residual',True,trace=[],witness=[0,0])
    edit('residual_bit_changed',False,trace=[],witness=[1,0])
    edit('fractional_trace_bit',False,trace=[[0,0,.1],[1,1,0]])
    edit('truncated_step',False,trace=[[0]])
    edit('independent_steps_reversed',True,H=[[1,0],[0,1]],trace=base['trace'][::-1])
    edit('different_valid_completion',True,H=[[1,1]],trace=[],witness=[1,1])
    edit('nonbinary_residual',False,H=[[1,1]],trace=[],witness=[2,2])
    edit('compatible_visible_corruption',True,H=[[1,1]],y=[1,-1],trace=[],witness=[1])
    for name,w,expected in [('valid_impossibility',[1],True),('zeroed_impossibility',[0],False),('truncated_impossibility',[],False),('nonbinary_impossibility',[3],False)]:
        specifications.append((name,dict(H=[[1]],y=[1],kind='failure',trace=[],witness=w),expected))
    return specifications


def generate(output='audit'):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    cases,labels=make_cases();results=[]
    for case,label in zip(cases,labels):
        result=s.check_json(case)
        if label=='malformed_reject':assert not result['accepted']
        if result['accepted']:
            if case['kind']=='success':assert s.verify_word(case['H'],case['y'],result['word'])
            else:
                H=np.array(case['H'],dtype=np.uint8);y=case['y']
                assert not any(all(a==-1 or a==x[i] for i,a in enumerate(y)) and np.all(H@np.array(x,dtype=np.uint8)%2==0) for x in itertools.product((0,1),repeat=len(y)))
        results.append(result)
    (out/'differential_cases.jsonl').write_text(''.join(json.dumps(c,separators=(',',':'))+'\n' for c in cases))
    (out/'differential_expected.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in results))
    pd.DataFrame({'case':range(len(cases)),'category':labels,'accepted':[r['accepted'] for r in results]}).to_csv(out/'differential_case_index.csv',index=False)
    rows=[]
    for name,case,expected in named_adversarial_cases():
        result=s.check_json(case);assert result['accepted']==expected,(name,result,expected)
        rows.append(dict(case=name,expected_accept=expected,actual_accept=result['accepted'],input_json=json.dumps(case,separators=(',',':')),output_json=json.dumps(result,separators=(',',':'))))
    # The complete-word interface is tested independently of certificate parsing.
    for name,word,expected in [('valid_direct_word',[0,0],True),('word_bit_changed',[1,0],False),('visible_symbol_changed',[1,1],False),('nonbinary_word',[2,2],False)]:
        accepted=s.verify_word([[1,1]],[0,-1],word);assert accepted==expected
        rows.append(dict(case=name,expected_accept=expected,actual_accept=accepted,input_json=json.dumps({'H':[[1,1]],'y':[0,-1],'word':word}),output_json=json.dumps({'accepted':accepted})))
    pd.DataFrame(rows).to_csv(out/'adversarial_results.csv',index=False)
    summary={'differential_cases':len(cases),'accepted':sum(r['accepted'] for r in results),'rejected':sum(not r['accepted'] for r in results),'named_adversarial_cases':len(rows),'all_named_outcomes_expected':True}
    (out/'certificate_case_summary.json').write_text(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='audit');args=parser.parse_args();print(json.dumps(generate(args.output),indent=2))
