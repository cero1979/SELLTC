"""Declared, bounded experiment runner; all paper outputs derive from raw CSVs.

Run `python publication_experiments.py --output publication_outputs`.
An existing completed directory is analyzed, never silently overwritten. Use a fresh
--output directory for a new timing run. No files in SELLTCFULL_outputs are touched.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter
import tracemalloc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import selltcfull_experiments as s


CONFIG = {
    'protocol_version': 1,
    'base_seed': 20260920,
    'families': ['random_regular', 'peg'], 'dv': 3, 'dc': 6,
    'blocklengths': [128, 256, 512, 1024], 'matrix_replicates': 3,
    'epsilons': [.30, .40, .50], 'clean_trials_per_matrix_condition': 10,
    'robustness_blocklengths': [256, 512], 'robustness_epsilons': [.40, .55],
    'deltas': [.001, .01], 'robustness_trials_per_matrix_condition': 10,
    'timing_repetitions': 3, 'warmup_runs_per_trial': 1,
    'scaling_family': 'random_regular',
    'scaling_blocklengths': [256, 512, 1024, 2048, 4096],
    'scaling_matrix_replicates': 3, 'scaling_trials_per_matrix': 6,
    'scaling_epsilon': .40, 'scaling_timing_repetitions': 5,
    'bootstrap_replicates': 2000,
    'notes': [
        'New campaign, not a rerun pretending to use the original parameters.',
        '720 clean and 480 robustness trials; one code matrix per family/size/replicate reused across conditions.',
        '90 checker-scaling trials; independent matrices from decoding campaign and all-zero words (checker-focused, no recovery inference).',
        'Random codewords sampled uniformly from a precomputed kernel basis for clean and robustness trials.',
        'Regular matrices use uniform socket permutations conditioned on simplicity.',
        'PEG variant uses maximum graph distance, then minimum check degree, with prescribed check-capacity constraint and restart on dead end.',
        'GE-only and both hybrids use identical integer-bitset first-available-pivot elimination with row-transform tracking.',
        'Uncertified hybrid still constructs the same certificate but does not execute the checker.',
        'Graph validation, matrix generation, dense conversion and kernel-basis construction are measured once per matrix, outside per-input times.',
        'Per-input initialization is measured inside each decode; timing repetition order is randomized deterministically.',
        'Stage values use the certified repetition whose total time is the median, preserving exact denominators.',
        'Direct verification applies only to success outputs; it cannot certify infeasibility or trace validity.',
        'Separate sparse/dense replay timings use the same certificate and are randomized with other comparators.',
        'Memory is tracemalloc Python-tracked peak incremental allocation, not RSS; measured separately on trial 0 of every clean condition and scaling trial 0.',
        'Three matrices per condition limit ensemble inference; intervals bootstrap matrices, not pooled channel observations.',
    ]
}


def seed_for(*labels, base_seed=None):
    labels = [v.item() if isinstance(v, np.generic) else v for v in labels]
    payload = json.dumps([CONFIG['base_seed'] if base_seed is None else base_seed, *labels], separators=(',', ':')).encode()
    return int.from_bytes(sha256(payload).digest()[:8], 'little')


def _sha_file(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def environment():
    info = {'python': sys.version, 'platform': platform.platform(), 'machine': platform.machine(),
            'processor': platform.processor(), 'cpu_count': os.cpu_count(),
            'clock': 'time.perf_counter',
            'packages': {p: importlib.metadata.version(p) for p in ['numpy','pandas','matplotlib','pytest','nbclient','nbformat','ipykernel']}}
    for key, command in [('hardware_model',['sysctl','-n','hw.model']), ('cpu_brand',['sysctl','-n','machdep.cpu.brand_string']), ('memory_bytes',['sysctl','-n','hw.memsize'])]:
        try:
            info[key] = subprocess.check_output(command,text=True,stderr=subprocess.DEVNULL).strip()
        except (FileNotFoundError,subprocess.CalledProcessError):
            info[key] = 'unavailable'
    return info


def _check(g, y, result):
    if result['kind']=='success':
        return s.check_success_certificate(g,y,result['trace'],result['witness'])[0]
    return s.check_failure_certificate(g,y,result['trace'],result['witness'])


def peak_allocation(function):
    tracemalloc.start()
    function()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def matrix_record(family,n,rep,namespace='campaign'):
    seed=seed_for(namespace,'matrix',family,n,rep)
    t=perf_counter();g=s.generate_graph(family,n,CONFIG['dv'],CONFIG['dc'],seed);generation_s=perf_counter()-t
    t=perf_counter();dense=g.to_dense();dense_s=perf_counter()-t
    t=perf_counter();basis=s.kernel_basis(g) if namespace=='campaign' else ();basis_s=perf_counter()-t
    encoded=json.dumps({'n':g.n,'rows':g.rows},separators=(',',':'))
    identity=f'{namespace}_{family}_n{n}_r{rep}'
    meta=dict(matrix_id=identity,family=family,n=n,m=g.m,edges=g.edge_count,matrix_rep=rep,
              matrix_seed=seed,matrix_sha256=sha256(encoded.encode()).hexdigest(),
              generation_validation_s=generation_s,dense_conversion_s=dense_s,kernel_basis_s=basis_s,
              kernel_dimension=len(basis) if namespace=='campaign' else None)
    return g,dense,basis,meta,encoded


def run_trial(g,dense,basis,meta,epsilon,delta,trial):
    labels=[meta['matrix_id'],epsilon,delta,trial]
    seeds={name:seed_for(*labels,name) for name in ['word','erasure','corruption','order']}
    x=s.sample_codeword(basis,g.n,np.random.default_rng(seeds['word']))
    erased=np.random.default_rng(seeds['erasure']).random(g.n)<epsilon
    flips=(np.random.default_rng(seeds['corruption']).random(g.n)<delta)&~erased
    y=tuple(-1 if erased[i] else x[i]^int(flips[i]) for i in range(g.n))
    certificate=s.hybrid_decode(g,y,certify=True)
    assert certificate['accepted']
    compatible=certificate['kind']=='success'
    assert s.hybrid_decode(g,y,peel=False)['kind']==certificate['kind']
    if compatible:
        assert s.verify_word(g,y,certificate['word'])
    # Each function includes its own input/state initialization where applicable.
    functions={
        'peeling_only':lambda:s.peeling_only(g,y),
        'ge':lambda:s.hybrid_decode(g,y,peel=False),
        'hybrid':lambda:s.hybrid_decode(g,y),
        'certified':lambda:s.hybrid_decode(g,y,certify=True),
        'trace_check':lambda:_check(g,y,certificate),
        'dense_check':lambda:s.dense_check_certificate(dense,y,certificate['kind'],certificate['trace'],certificate['witness']),
    }
    if compatible:
        functions['direct']=lambda:s.verify_word(g,y,certificate['word'])
    for _ in range(CONFIG['warmup_runs_per_trial']):
        for function in functions.values():
            function()
    timings=defaultdict(list);outputs=defaultdict(list);raw=[]
    rng=np.random.default_rng(seeds['order'])
    for rep in range(CONFIG['timing_repetitions']):
        for order,name in enumerate(rng.permutation(list(functions))):
            name=str(name)
            t=perf_counter();answer=functions[name]();elapsed=perf_counter()-t
            if name in ('trace_check','dense_check','direct'):
                assert answer
            timings[name].append(elapsed);outputs[name].append(answer)
            record=dict(matrix_id=meta['matrix_id'],epsilon=epsilon,delta=delta,trial=trial,repetition=rep,order=order,algorithm=name,elapsed_s=elapsed)
            if name=='certified':
                record.update({k:answer[k] for k in ('init_s','peeling_s','residual_s','elimination_s','witness_s','backsub_s','check_s','decode_s','total_s')})
            raw.append(record)
    # Select an actual median-total repetition, preserving additivity of its stages.
    cert=sorted(outputs['certified'],key=lambda z:z['total_s'])[len(outputs['certified'])//2]
    row={k:v for k,v in meta.items() if k in ('matrix_id','family','n','m','edges','matrix_rep','matrix_seed','matrix_sha256')}
    row.update(epsilon=epsilon,delta=delta,trial=trial,**{f'{k}_seed':v for k,v in seeds.items()},
               erasures=int(erased.sum()),flips=int(flips.sum()),compatible=compatible,
               kind=cert['kind'],accepted=cert['accepted'],trace_len=cert['trace_len'],residual_size=cert['residual_size'],
               rank=cert['rank'],nullity=cert['nullity'],exact_recovery=compatible and cert['word']==x,
               unique_completion=compatible and cert['nullity']==0,
               peeling_complete=outputs['peeling_only'][0]['complete'],
               direct_valid=bool(compatible and s.verify_word(g,y,cert['word'])))
    row.update({k:cert[k] for k in ('init_s','peeling_s','residual_s','elimination_s','witness_s','backsub_s','check_s','decode_s','total_s','relative_overhead','check_fraction')})
    row['other_decode_s']=row['decode_s']-sum(row[k] for k in ('init_s','peeling_s','residual_s','elimination_s','witness_s','backsub_s'))
    for name in ['peeling_only','ge','hybrid','certified','trace_check','dense_check','direct']:
        row[f'{name}_s']=float(np.median(timings[name])) if timings[name] else np.nan
    row.update(trace_peak_bytes=np.nan,dense_peak_bytes=np.nan,direct_peak_bytes=np.nan)
    if trial==0 and delta==0:
        row['trace_peak_bytes']=peak_allocation(functions['trace_check'])
        row['dense_peak_bytes']=peak_allocation(functions['dense_check'])
        if compatible:row['direct_peak_bytes']=peak_allocation(functions['direct'])
    return row,raw


def run_scaling_trial(g,dense,meta,trial):
    seed=seed_for('scaling',meta['matrix_id'],trial,'erasure')
    erased=np.random.default_rng(seed).random(g.n)<CONFIG['scaling_epsilon']
    y=tuple(-1 if erased[i] else 0 for i in range(g.n))
    state,trace=s.peeling_decode(g,y)
    rho=tuple(0 for v in state.known if v==-1)
    word=(0,)*g.n
    functions={'sparse':lambda:s.check_success_certificate(g,y,trace,rho)[0],
               'direct':lambda:s.verify_word(g,y,word),
               'dense':lambda:s.dense_check_certificate(dense,y,'success',trace,rho)}
    for function in functions.values():assert function()
    timings=defaultdict(list);raw=[]
    rng=np.random.default_rng(seed_for('scaling',meta['matrix_id'],trial,'order'))
    for rep in range(CONFIG['scaling_timing_repetitions']):
        for order,name in enumerate(rng.permutation(list(functions))):
            name=str(name)
            t=perf_counter();accepted=functions[name]();elapsed=perf_counter()-t
            assert accepted
            timings[name].append(elapsed)
            raw.append(dict(matrix_id=meta['matrix_id'],n=g.n,trial=trial,repetition=rep,order=order,algorithm=name,elapsed_s=elapsed))
    row=dict(matrix_id=meta['matrix_id'],n=g.n,m=g.m,edges=g.edge_count,matrix_rep=meta['matrix_rep'],trial=trial,seed=seed,
             epsilon=CONFIG['scaling_epsilon'],trace_len=len(trace),residual_size=len(rho))
    for name in functions:
        row[f'{name}_s']=float(np.median(timings[name]))
        row[f'{name}_peak_bytes']=peak_allocation(functions[name]) if trial==0 else np.nan
    return row,raw


def summarize_conditions(df):
    rows=[]
    for (family,n,epsilon,delta),g in df.groupby(['family','n','epsilon','delta'],sort=True):
        rows.append(dict(family=family,n=n,epsilon=epsilon,delta=delta,trials=len(g),matrices=g.matrix_id.nunique(),
                         completion_rate=float((g.kind=='success').mean()),acceptance_rate=float(g.accepted.mean()),
                         peeling_completion_rate=float(g.peeling_complete.mean()),exact_recovery_rate=float(g.exact_recovery.mean()),
                         unique_rate=float(((g.kind=='success')&(g.nullity==0)).mean()),mean_nullity=float(g.nullity.mean()),
                         trace_len=float(g.trace_len.mean()),residual_size=float(g.residual_size.mean()),
                         actually_corrupted=int((g.flips>0).sum()),corrupted_compatible=int(((g.flips>0)&g.compatible).sum()),
                         incompatible=int((~g.compatible).sum()),
                         decode_ms=1000*g.decode_s.mean(),check_ms=1000*g.check_s.mean(),total_ms=1000*g.total_s.mean(),
                         direct_ms=1000*g.direct_s.mean(),ge_ms=1000*g.ge_s.mean(),hybrid_ms=1000*g.hybrid_s.mean(),
                         certified_ms=1000*g.certified_s.mean(),peeling_only_ms=1000*g.peeling_only_s.mean(),
                         relative_mean_ratio=float((g.check_s/g.decode_s).mean()),relative_ratio_means=float(g.check_s.mean()/g.decode_s.mean()),
                         fraction_mean_ratio=float((g.check_s/g.total_s).mean()),fraction_ratio_means=float(g.check_s.mean()/g.total_s.mean())))
    return pd.DataFrame(rows)


def cluster_intervals(df, config=None):
    config=CONFIG if config is None else config
    rows=[]
    for key,g in df.groupby(['family','n','epsilon','delta']):
        for metric in ['exact_recovery','compatible','trace_check_s','direct_s','ge_s','certified_s']:
            clusters=g.groupby('matrix_id')[metric].mean().dropna().to_numpy(dtype=float)
            if not len(clusters):continue
            rng=np.random.default_rng(seed_for('bootstrap',*key,metric,base_seed=config['base_seed']))
            samples=rng.choice(clusters,(config['bootstrap_replicates'],len(clusters)),replace=True).mean(axis=1)
            rows.append(dict(family=key[0],n=key[1],epsilon=key[2],delta=key[3],metric=metric,matrices=len(clusters),
                             estimate=float(clusters.mean()),matrix_sd=float(clusters.std(ddof=1)) if len(clusters)>1 else np.nan,
                             lower95=float(np.quantile(samples,.025)),upper95=float(np.quantile(samples,.975))))
    return pd.DataFrame(rows)


def scaling_summary(df, config=None):
    config=CONFIG if config is None else config
    means=df.groupby(['matrix_id','n'])[['sparse_s','direct_s','dense_s']].mean().reset_index()
    results=[]
    sizes=sorted(means.n.unique())
    for metric in ['sparse_s','direct_s','dense_s']:
        arrays=[means[means.n==n][metric].to_numpy() for n in sizes]
        slope=float(np.polyfit(np.log(sizes),np.log([a.mean() for a in arrays]),1)[0])
        rng=np.random.default_rng(seed_for('scaling-bootstrap',metric,base_seed=config['base_seed']))
        bootstrap=[]
        for _ in range(config['bootstrap_replicates']):
            sampled=[rng.choice(a,len(a),replace=True).mean() for a in arrays]
            bootstrap.append(float(np.polyfit(np.log(sizes),np.log(sampled),1)[0]))
        results.append(dict(algorithm=metric.removesuffix('_s'),slope=slope,lower95=float(np.quantile(bootstrap,.025)),upper95=float(np.quantile(bootstrap,.975)),matrices_per_size=len(arrays[0]),sizes=len(sizes)))
    return pd.DataFrame(results)


def _latex_table(df, caption, label, filename, precision=3):
    # Headers are curated display labels, never unescaped Python identifiers.
    text=df.to_latex(index=False,escape=True,float_format=lambda x:f'{x:.{precision}f}',caption=caption,label=label,column_format='l'+'r'*(len(df.columns)-1))
    text=text.replace('\\begin{table}\n','\\begin{table}\n\\centering\n\\small\n\\setlength{\\tabcolsep}{3pt}\n')
    Path(filename).write_text(text)


def analyze(out):
    out=Path(out)
    validate_campaign(out)
    config=json.loads((out/'declared_config.json').read_text())
    manifest=json.loads((out/'manifest.json').read_text())
    for name,digest in manifest.get('raw_sha256',{}).items():
        if _sha_file(out/name)!=digest:raise ValueError(f'Raw file checksum changed: {name}')
    clean=pd.read_csv(out/'raw_clean.csv');rob=pd.read_csv(out/'raw_robustness.csv');scale=pd.read_csv(out/'raw_scaling.csv')
    summary=summarize_conditions(pd.concat([clean,rob],ignore_index=True));summary.to_csv(out/'condition_summary.csv',index=False)
    cluster_intervals(pd.concat([clean,rob],ignore_index=True),config).to_csv(out/'matrix_cluster_intervals.csv',index=False)
    slopes=scaling_summary(scale,config);slopes.to_csv(out/'scaling_slopes.csv',index=False)
    table=summary[(summary.epsilon==.40)&(summary.delta==0)].copy()
    table.to_csv(out/'table_epsilon040.csv',index=False)
    pretty_table=table.copy();pretty_table['family']=pretty_table.family.map({'random_regular':'Regular','peg':'PEG'})
    _latex_table(pretty_table[['family','n','trials','trace_len','residual_size','check_ms','direct_ms','relative_mean_ratio']].rename(columns={'family':'Family','n':'n','trials':'Trials','trace_len':'Trace','residual_size':'Residual','check_ms':'Check ms','direct_ms':'Direct ms','relative_mean_ratio':'Mean C/D'}),
                 'New campaign at erasure probability 0.40: three matrices and ten trials per matrix. C/D is the internal check stage divided by decode time, averaged per trial. The check stage includes comparing checker and producer words.',
                 'tab:new-experiments',out/'table_epsilon040.tex')
    stage_fields=['init_s','peeling_s','residual_s','elimination_s','witness_s','backsub_s','other_decode_s','check_s']
    stages=clean[clean.epsilon==.40].groupby('n')[stage_fields].mean().mul(1000).reset_index()
    stages=stages.rename(columns={name:name.removesuffix('_s')+'_ms' for name in stage_fields})
    stages.to_csv(out/'runtime_stages_epsilon040_ms.csv',index=False)
    _latex_table(stages.rename(columns={'n':'n','init_ms':'Init','peeling_ms':'Peel','residual_ms':'Residual','elimination_ms':'GE','witness_ms':'Witness','backsub_ms':'Backsub','other_decode_ms':'Other','check_ms':'Check'}),
                 'Mean certified runtime stages in milliseconds at erasure probability 0.40, pooled equally over the two named families: six matrices and 60 trials per size. Witness is final vector extraction; row-transform tracking is included in GE. Other includes parsing, output reconstruction and timing overhead; Check includes comparing checker and producer words.',
                 'tab:runtime-stages',out/'runtime_stages_epsilon040.tex',precision=4)
    displayed_slopes=slopes.copy();displayed_slopes['algorithm']=displayed_slopes.algorithm.map({'sparse':'Sparse replay','direct':'Direct check','dense':'Dense replay'})
    _latex_table(displayed_slopes[['algorithm','slope','lower95','upper95']].rename(columns={'algorithm':'Checker','slope':'Slope','lower95':'Lower 95%','upper95':'Upper 95%'}),
                 'Finite-size log-log time slopes on blocklengths 256 through 4096, with 95 percent percentile bootstrap intervals resampling the three matrix identities at each size (2000 replicates). These describe this machine and protocol, not asymptotic guarantees.',
                 'tab:scaling-slopes',out/'scaling_slopes.tex')
    scale.groupby('n')[['sparse_s','direct_s','dense_s','sparse_peak_bytes','direct_peak_bytes','dense_peak_bytes']].mean().reset_index().to_csv(out/'checker_time_memory_summary.csv',index=False)
    # Completion, exact recovery and uniqueness are deliberately distinct.
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
    for ax,(family,data) in zip(axes,clean.groupby('family')):
        groups=data.groupby('epsilon')
        ax.plot(groups.size().index,groups.peeling_complete.mean(),'o-',label='Peeling completion')
        ax.plot(groups.size().index,groups.compatible.mean(),'s-',label='Valid completion')
        ax.plot(groups.size().index,groups.exact_recovery.mean(),'^-',label='Exact recovery')
        ax.plot(groups.size().index,groups.unique_completion.mean(),'d--',label='Unique completion')
        ax.set(title={'peg':'PEG','random_regular':'Regular'}[family],xlabel='Erasure probability',ylim=(-.03,1.03));ax.grid(alpha=.25)
    axes[0].set_ylabel('Rate (fixed campaign mixture)');axes[1].legend(fontsize=8,loc='lower left')
    fig.tight_layout();fig.savefig(out/'fig_completion.png',dpi=170);plt.close(fig)
    # Fair comparators; direct check is a verification-only operation.
    labels=['Peeling','GE only','Hybrid','Hybrid + check','Direct check']
    fields=['peeling_only_s','ge_s','hybrid_s','certified_s','direct_s']
    plotdata=clean[clean.epsilon==.4]
    fig,ax=plt.subplots(figsize=(8,4))
    for name,label in zip(fields,labels):
        by=plotdata.groupby('n')[name].mean();ax.plot(by.index,1000*by,'o-',label=label)
    ax.set(xlabel='Blocklength n',ylabel='Mean time (ms)',yscale='log');ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'fig_comparators.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for name,label in [('sparse','Sparse replay'),('dense','Dense replay'),('direct','Direct check')]:
        means=scale.groupby('n')[f'{name}_s'].mean()
        axes[0].loglog(means.index,1000*means,'o-',label=label)
        memory=scale.groupby('n')[f'{name}_peak_bytes'].mean()
        axes[1].loglog(memory.index,memory/1024,'o-',label=label)
    axes[0].set(xlabel='Blocklength n',ylabel='Mean median time (ms)')
    axes[1].set(xlabel='Blocklength n',ylabel='Peak tracked allocation (KiB)')
    for ax in axes:ax.grid(alpha=.25,which='both');ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'fig_checker_scaling.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    robust=rob.assign(corrupted=rob.flips>0,corrupt_compatible=(rob.flips>0)&rob.compatible)
    grouped=robust.groupby(['epsilon','delta'])
    pos=np.arange(len(grouped));width=.25
    for offset,field,label in [(-1,'corrupted','Realized corruption'),(0,'corrupt_compatible','Corrupted and compatible'),(1,'compatible','Any valid completion')]:
        ax.bar(pos+offset*width,grouped[field].mean(),width,label=label)
    ax.set_xticks(pos,[f'e={e:g}\nd={d:g}' for e,d in grouped.groups]);ax.set(ylabel='Fraction of trials',ylim=(0,1.05));ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(0.5,1.3),ncol=2)
    fig.tight_layout();fig.savefig(out/'fig_corruption.png',dpi=170);plt.close(fig)
    total_corrupted=int((rob.flips>0).sum());corrupted_compatible=int(((rob.flips>0)&rob.compatible).sum())
    facts={
        'clean_trials':len(clean),'robustness_trials':len(rob),'scaling_trials':len(scale),'campaign_matrices':clean.matrix_id.nunique(),
        'clean_completion_rate':float(clean.compatible.mean()),'clean_exact_recovery_rate':float(clean.exact_recovery.mean()),
        'clean_nonunique_count':int((clean.nullity>0).sum()),'clean_nonzero_transmitted_words':'uniform kernel sampling; reproducible using stored seeds',
        'actually_corrupted_robustness':total_corrupted,'corrupted_compatible':corrupted_compatible,
        'incompatible_robustness':int((~rob.compatible).sum()),'accepted_failure_count':int((rob.kind=='failure').sum()),
        'all_generated_certificates_accepted':bool(clean.accepted.all() and rob.accepted.all()),
        'scaling_slopes':slopes.to_dict('records'),
        'scaling_n4096':scale[scale.n==4096][['sparse_s','direct_s','dense_s','sparse_peak_bytes','direct_peak_bytes','dense_peak_bytes']].mean().to_dict(),
        'epsilon040_all':{'mean_relative':float((clean[clean.epsilon==.4].check_s/clean[clean.epsilon==.4].decode_s).mean()),'mean_fraction':float((clean[clean.epsilon==.4].check_s/clean[clean.epsilon==.4].total_s).mean())},
    }
    (out/'results.json').write_text(json.dumps(facts,indent=2))
    (out/'results.tex').write_text('% Generated only from raw campaign CSVs. See results.json and condition_summary.csv.\n'+
        f'The new campaign contains {len(clean)} clean-channel trials on {clean.matrix_id.nunique()} matrices, {len(rob)} corruption trials, and {len(scale)} separate checker-scaling trials. '+
        f'Valid completion was obtained in {clean.compatible.mean():.3f} of clean trials, whereas exact recovery occurred in {clean.exact_recovery.mean():.3f}; {int((clean.nullity>0).sum())} clean residual systems were nonunique. '+
        f'Among {total_corrupted} inputs with at least one visible flip, {corrupted_compatible} remained compatible.\n')
    return facts


RAW_NAMES = ['raw_clean.csv','raw_robustness.csv','raw_scaling.csv','timing_repetitions.csv','scaling_repetitions.csv','matrix_metadata.csv']


def validate_campaign(output):
    """Check the full declared grid and matrix identities, without altering measurements."""
    out=Path(output)
    config=json.loads((out/'declared_config.json').read_text())
    clean=pd.read_csv(out/'raw_clean.csv');rob=pd.read_csv(out/'raw_robustness.csv');scaling=pd.read_csv(out/'raw_scaling.csv')
    expected_clean=set();expected_rob=set();expected_scaling=set()
    for family in config['families']:
        for n in config['blocklengths']:
            for rep in range(config['matrix_replicates']):
                identity=f'campaign_{family}_n{n}_r{rep}'
                for epsilon in config['epsilons']:
                    for trial in range(config['clean_trials_per_matrix_condition']):
                        expected_clean.add((identity,epsilon,0.,trial))
                if n in config['robustness_blocklengths']:
                    for epsilon in config['robustness_epsilons']:
                        for delta in config['deltas']:
                            for trial in range(config['robustness_trials_per_matrix_condition']):
                                expected_rob.add((identity,epsilon,delta,trial))
    for n in config['scaling_blocklengths']:
        for rep in range(config['scaling_matrix_replicates']):
            identity=f"scaling_{config['scaling_family']}_n{n}_r{rep}"
            for trial in range(config['scaling_trials_per_matrix']):
                expected_scaling.add((identity,n,trial))
    for df,expected,keys in [(clean,expected_clean,['matrix_id','epsilon','delta','trial']),
                             (rob,expected_rob,['matrix_id','epsilon','delta','trial']),
                             (scaling,expected_scaling,['matrix_id','n','trial'])]:
        actual=set(df[keys].itertuples(index=False,name=None))
        if actual!=expected or len(df)!=len(expected):
            raise ValueError('Missing, duplicate or unrequested trial in raw campaign grid')
    all_trials=pd.concat([clean,rob],ignore_index=True)
    if not all_trials.accepted.all() or not (all_trials.compatible==(all_trials.kind=='success')).all():
        raise ValueError('Unexpected certificate outcome')
    if not all_trials.loc[all_trials.compatible,'direct_valid'].all():
        raise ValueError('A success output failed direct verification')
    if not np.allclose(all_trials.total_s,all_trials.decode_s+all_trials.check_s,rtol=1e-12,atol=1e-12):
        raise ValueError('Inconsistent runtime denominators')
    for field in ['init_s','peeling_s','residual_s','elimination_s','witness_s','backsub_s','check_s','decode_s','total_s','other_decode_s']:
        if not (all_trials[field]>=0).all():raise ValueError(f'Negative timing in {field}')
    seed_values=[int(v) for field in ['word_seed','erasure_seed','corruption_seed','order_seed'] for v in all_trials[field]]
    if len(set(seed_values))!=len(seed_values):raise ValueError('Trial stream seed collision')
    matrices=pd.read_csv(out/'matrix_metadata.csv')
    for row in matrices.itertuples():
        if _sha_file(out/'matrices'/f'{row.matrix_id}.json')!=row.matrix_sha256:
            raise ValueError('Matrix fingerprint mismatch')
    timings=pd.read_csv(out/'timing_repetitions.csv')
    expected_times=sum(config['timing_repetitions']*(6+int(v)) for v in all_trials.compatible)
    if len(timings)!=expected_times:raise ValueError('Missing timing repetitions')
    if len(pd.read_csv(out/'scaling_repetitions.csv'))!=len(scaling)*3*config['scaling_timing_repetitions']:
        raise ValueError('Missing checker scaling repetitions')
    return dict(clean_trials=len(clean),robustness_trials=len(rob),scaling_trials=len(scaling),matrices=len(matrices),timing_repetitions=len(timings),distinct_trial_streams=len(seed_values))


def finalize_existing(output):
    """Recover a completed measurement phase after an analysis failure; keep all raw data."""
    out=Path(output)
    validation=validate_campaign(out)
    manifest=json.loads((out/'manifest.json').read_text())
    for name,digest in manifest.get('raw_sha256',{}).items():
        if _sha_file(out/name)!=digest:raise ValueError(f'Previously recorded raw hash changed: {name}')
    facts=analyze(out)
    manifest.update(status='complete',analysis_completed_utc=datetime.now(timezone.utc).isoformat(),
                    raw_sha256={p:_sha_file(out/p) for p in RAW_NAMES},validation=validation,
                    analysis_code_sha256=_sha_file(__file__))
    manifest['analysis_environment']=environment()
    manifest['analysis_environment']['packages']['Jinja2']=importlib.metadata.version('Jinja2')
    archived=out/'source'
    if archived.exists():
        for name,digest in manifest['code_sha256'].items():
            if _sha_file(archived/name)!=digest:raise ValueError('Executed-source archive hash mismatch')
        manifest['measurement_source_archive']='source/; files match code_sha256 recorded before measurement'
    if 'completed_utc' not in manifest:
        total=validation['clean_trials']+validation['robustness_trials']+validation['scaling_trials']
        manifest['recovery_note']=f'All {total} declared trials completed; analysis initially failed on NumPy scalar JSON serialization, then on a missing Jinja2 dependency. Fixed analysis and finalized the complete raw dataset without rerunning or dropping measurements.'
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return facts


def run_campaign(output='publication_outputs'):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    manifest_path=out/'manifest.json'
    if manifest_path.exists():
        previous=json.loads(manifest_path.read_text())
        if previous.get('status')=='complete':
            for name,digest in previous['raw_sha256'].items():
                if _sha_file(out/name)!=digest:raise RuntimeError(f'Raw file checksum changed: {name}')
            print('Existing completed run verified; regenerating analysis from raw CSVs.',flush=True)
            return analyze(out)
        raise RuntimeError('Incomplete run directory exists. Preserve it and select a fresh --output directory.')
    manifest={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'config':CONFIG,'environment':environment(),
              'seed_scheme':'64-bit little-endian prefix of SHA256(JSON([base_seed, namespace labels...])), compact separators; NumPy PCG64 via default_rng.',
              'code_sha256':{p:_sha_file(Path(__file__).with_name(p)) for p in ['selltcfull_experiments.py','publication_experiments.py']}}
    manifest_path.write_text(json.dumps(manifest,indent=2))
    (out/'declared_config.json').write_text(json.dumps(CONFIG,indent=2))
    clean=[];rob=[];timings=[];scaling=[];scaling_times=[];matrices=[]
    graph_dir=out/'matrices';graph_dir.mkdir(exist_ok=True)
    for family in CONFIG['families']:
        for n in CONFIG['blocklengths']:
            for rep in range(CONFIG['matrix_replicates']):
                g,dense,basis,meta,encoded=matrix_record(family,n,rep)
                matrices.append(meta);(graph_dir/f"{meta['matrix_id']}.json").write_text(encoded)
                print('Matrix',meta['matrix_id'],'generated in',round(meta['generation_validation_s'],3),'s',flush=True)
                for epsilon in CONFIG['epsilons']:
                    for trial in range(CONFIG['clean_trials_per_matrix_condition']):
                        row,repetitions=run_trial(g,dense,basis,meta,epsilon,0.,trial);clean.append(row);timings.extend(repetitions)
                if n in CONFIG['robustness_blocklengths']:
                    for epsilon in CONFIG['robustness_epsilons']:
                        for delta in CONFIG['deltas']:
                            for trial in range(CONFIG['robustness_trials_per_matrix_condition']):
                                row,repetitions=run_trial(g,dense,basis,meta,epsilon,delta,trial);rob.append(row);timings.extend(repetitions)
                # Per-matrix checkpoints retain executed rows; finalization validates the full grid.
                for name,rows in [('raw_clean.csv',clean),('raw_robustness.csv',rob),('timing_repetitions.csv',timings),('matrix_metadata.csv',matrices)]:
                    pd.DataFrame(rows).to_csv(out/name,index=False)
                print('Completed',len(clean),'clean and',len(rob),'corruption trials',flush=True)
    for n in CONFIG['scaling_blocklengths']:
        for rep in range(CONFIG['scaling_matrix_replicates']):
            g,dense,basis,meta,encoded=matrix_record(CONFIG['scaling_family'],n,rep,'scaling')
            matrices.append(meta);(graph_dir/f"{meta['matrix_id']}.json").write_text(encoded)
            for trial in range(CONFIG['scaling_trials_per_matrix']):
                row,repetitions=run_scaling_trial(g,dense,meta,trial);scaling.append(row);scaling_times.extend(repetitions)
            print('Scaling completed',meta['matrix_id'],flush=True)
    for name,rows in [('raw_scaling.csv',scaling),('scaling_repetitions.csv',scaling_times),('matrix_metadata.csv',matrices)]:
        pd.DataFrame(rows).to_csv(out/name,index=False)
    validate_campaign(out)
    facts=analyze(out)
    manifest.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat(),raw_sha256={p:_sha_file(out/p) for p in RAW_NAMES})
    manifest_path.write_text(json.dumps(manifest,indent=2))
    return facts


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='publication_outputs');parser.add_argument('--analyze-only',action='store_true');parser.add_argument('--finalize-existing',action='store_true')
    args=parser.parse_args()
    print(json.dumps(finalize_existing(args.output) if args.finalize_existing else analyze(args.output) if args.analyze_only else run_campaign(args.output),indent=2))
