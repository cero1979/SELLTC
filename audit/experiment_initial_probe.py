"""Read-only analysis of preserved original CSVs and original notebook algorithms.
Plot imports alone are stubbed because matplotlib is absent; numerical code is unmodified.
"""
from pathlib import Path
import sys, types, json, hashlib, itertools, platform
import numpy as np
import pandas as pd
root = Path(__file__).resolve().parents[1]
nb = json.loads((root/'SELLTCFULL_experiments.ipynb').read_text())
source = ''.join(nb['cells'][2]['source']).split('\n',1)[1]
plotstub=types.ModuleType('matplotlib');plotstub.pyplot=types.ModuleType('matplotlib.pyplot')
sys.modules['matplotlib']=plotstub;sys.modules['matplotlib.pyplot']=plotstub.pyplot
mod=types.ModuleType('original_notebook_algorithm');sys.modules[mod.__name__]=mod
exec(compile(source,'original_notebook_cell2','exec'),mod.__dict__)
clean=pd.read_csv(root/'SELLTCFULL_outputs/raw_clean.csv')
rob=pd.read_csv(root/'SELLTCFULL_outputs/raw_robustness.csv')
print('ENV',platform.platform(),sys.version.split()[0],'numpy',np.__version__,'pandas',pd.__version__)
print('ROWS',len(clean),len(rob),'clean groups',clean.groupby(['family','n','epsilon']).size().unique().tolist())
orig=pd.read_csv(root/'SELLTCFULL_outputs/table1_summary.csv')
pool=mod.summarize_table1(clean);correct=mod.summarize_table1(clean[clean.epsilon==.40])
print('TABLE EXACT MATCH ALL EPS',np.allclose(orig.select_dtypes('number'),pool.select_dtypes('number'),rtol=1e-12,atol=1e-12))
print('EPSILON .40 TABLE');print(correct.to_string(index=False))
print('POOLED TABLE');print(pool.to_string(index=False))
correct.to_csv(root/'audit/original_table_epsilon040_recomputed.csv',index=False)
print('RATIOS')
for (fam,n),d in clean.groupby(['family','n']):
 c=d.hybrid_checker_time_s;t=d.hybrid_time_s;q=t-c
 print(fam,n,'mean relative',float((c/q).mean()),'ratio mean relative',float(c.mean()/q.mean()),'mean fraction',float((c/t).mean()),'ratio mean fraction',float(c.mean()/t.mean()))
print('CHECKER SCALING')
for fam,d in mod.summarize_checker_scaling(clean).groupby('family'):
 slope,intercept=np.polyfit(np.log(d.n),np.log(d.checker_time_s),1)
 print(fam,'slope',slope,'5x size timing factor',float(d.checker_time_s.iloc[-1]/d.checker_time_s.iloc[0]))
runtimes=mod.summarize_runtime(clean)
print('CHECKER GREATER THAN RESIDUAL',int((runtimes.checker_time_s>runtimes.residual_time_s).sum()),'of',len(runtimes))
print('EPS .40 TIMES');print(runtimes[runtimes.epsilon==.4].to_string(index=False))
print('NONUNIQUE CLEAN',int((clean.residual_size>clean.rank_residual).sum()),'of',len(clean))
print(clean.assign(nonunique=clean.residual_size>clean.rank_residual,nullity=clean.residual_size-clean.rank_residual).groupby('epsilon')[['nonunique','nullity']].mean().to_string())
print('ORIGINAL SUMMARY AGREEMENT')
for stem,fun,df in [('success_summary',mod.summarize_success,clean),('runtime_summary',mod.summarize_runtime,clean),('checker_summary',mod.summarize_checker_scaling,clean),('robustness_summary',mod.summarize_robustness,rob)]:
 disk=pd.read_csv(root/'SELLTCFULL_outputs'/f'{stem}.csv');derived=fun(df)
 print(stem,np.allclose(disk.select_dtypes('number'),derived.select_dtypes('number'),rtol=1e-12,atol=1e-12))
print('ORIGINAL RETURN CONTRACT/MUTATION PROBES')
def probe(name,f):
 try: print(name,repr(f()))
 except Exception as e:print(name,'EXCEPTION',type(e).__name__,str(e))
H=np.array([[1,1]],dtype=np.uint8);y=np.array([-1,-1],dtype=np.int8)
probe('nonbinary rho [2,2]',lambda:mod.check_success_certificate(H,y,[],np.array([2,2])))
probe('fractional rho [.1,.1]',lambda:mod.check_success_certificate(H,y,[],np.array([.1,.1])))
probe('partial trace is allowed',lambda:mod.check_success_certificate(H,y,[],np.array([1,1])))
probe('bad rho length',lambda:mod.check_success_certificate(H,y,[],np.array([0])))
probe('scalar rho',lambda:mod.check_success_certificate(H,y,[],np.array(0)))
probe('truncated triple',lambda:mod.check_success_certificate(H,y,[(0,)],np.array([0,0])))
probe('bad index type',lambda:mod.check_success_certificate(H,y,[(0.0,0,0)],np.array([0])))
H2=np.array([[1,0],[1,1]],dtype=np.uint8);y2=np.array([-1,-1],dtype=np.int8)
st,tr,U=mod.peeling_decode(H2,y2)
print('dependent trace',tr)
probe('valid trace',lambda:mod.check_success_certificate(H2,y2,tr,np.zeros(0,dtype=np.uint8)))
probe('reversed dependent trace',lambda:mod.check_success_certificate(H2,y2,tr[::-1],np.zeros(0,dtype=np.uint8)))
probe('wrong trace bit',lambda:mod.check_success_certificate(H2,y2,[(0,0,1),(1,1,0)],np.zeros(0,dtype=np.uint8)))
probe('fractional trace bit',lambda:mod.check_success_certificate(H2,y2,[(0,0,.1),(1,1,0)],np.zeros(0,dtype=np.uint8)))
probe('out of range check',lambda:mod.check_success_certificate(H2,y2,[(2,0,0)],np.zeros(1,dtype=np.uint8)))
probe('truncated valid trace old rho',lambda:mod.check_success_certificate(H2,y2,tr[:1],np.zeros(0,dtype=np.uint8)))
H3=np.array([[1]],dtype=np.uint8);y3=np.array([1],dtype=np.int8)
probe('valid failure empty U',lambda:mod.check_failure_certificate(H3,y3,[],np.array([1])))
probe('zeroed failure witness',lambda:mod.check_failure_certificate(H3,y3,[],np.array([0])))
probe('nonbinary failure witness [3]',lambda:mod.check_failure_certificate(H3,y3,[],np.array([3])))
print('EXHAUSTIVE GF2 SOLVER')
count=0
for m in range(4):
 for n in range(4):
  if m*n>9:continue
  for vals in itertools.product((0,1),repeat=m*n):
   A=np.array(vals,dtype=np.uint8).reshape(m,n)
   candidates=np.array(list(itertools.product((0,1),repeat=n)),dtype=np.uint8).reshape(2**n,n)
   for bv in itertools.product((0,1),repeat=m):
    b=np.array(bv,dtype=np.uint8)
    solvable=any(np.array_equal(A@x%2,b) for x in candidates)
    for strategy in ('dense','sparse'):
     z=mod.gf2_solve(A,b,strategy)
     assert z.solvable==solvable,(A,b,strategy,z)
     if solvable:assert np.array_equal(A@z.solution%2,b)
     else:assert np.all(z.witness@A%2==0) and z.witness@b%2==1
     count+=1
print('GF2 exhaustive passed calls',count)
print('ROBUSTNESS ACTUAL FLIPS/COMPATIBILITY FROM STORED SEEDS')
records=[]
for row in rob.itertuples():
 yr=mod.simulate_bec_received_word(row.n,row.epsilon,row.delta,row.seed)
 flips=int((yr==1).sum())
 records.append((row.family,row.n,row.delta,flips,bool(row.ge_success),bool(row.hybrid_success_accept)))
r=pd.DataFrame(records,columns=['family','n','delta','actual_flips','compatible','accepted_success'])
print(r.assign(corrupted=r.actual_flips>0,corrupt_compatible=(r.actual_flips>0)&r.compatible).groupby('delta')[['corrupted','corrupt_compatible','accepted_success']].sum().to_string())
print('SEED COLLISIONS clean distinct',clean.seed.nunique(),'of',len(clean),'rob distinct',rob.seed.nunique(),'of',len(rob))
print('ROB delta 0/.0001 identical trial seeds',all(rob[rob.delta==0].seed.to_numpy()==rob[rob.delta==.0001].seed.to_numpy()))
print('MATRIX SEEDS',[(s.family,s.n,s.matrix_seed) for s in mod.CampaignConfig().family_specs()])
print('PEG NEIGHBOR SELECTION COUNTEREXAMPLE')
print('variable 0; check distances 1,3,5; candidates',mod._peg_candidate_checks([[0],[0,1],[1,2]],[[0,1],[1,2],[2]],0,{0}),'instead of deepest [2]')
print('COMPATIBLE CORRUPTION COUNTEREXAMPLE')
probe('H=[1,1], sent 00, corrupted y=[1,-1]',lambda:mod.run_hybrid_decoder(np.array([[1,1]],dtype=np.uint8),np.array([1,-1],dtype=np.int8))['decoded_word'].tolist())
