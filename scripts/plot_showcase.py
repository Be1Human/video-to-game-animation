"""Rebuild README figures from the committed measured data; no character assets needed."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze_motion import analyze
from motion_math import quintic_weight


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',default='docs/showcase/data')
    ap.add_argument('--output',default='docs/showcase')
    args=ap.parse_args();data=Path(args.data);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    load=lambda name:json.loads((data/name).read_text())
    colors={'before':'#c46b3e','after':'#008b8b'}
    fig,axs=plt.subplots(2,1,figsize=(10,6.5),layout='constrained')
    for variant in ['before','after']:
        d=load(variant+'-walk.json');summary,curves=analyze(d)
        t=curves['time_s'];axs[0].plot(t,curves['linear']['head']['jerk'],color=colors[variant],label=variant)
        angular=curves['angular']['hand.L'];axs[1].plot(angular['time_s'],angular['accel_rad_s2'],color=colors[variant],label=variant)
        # Report consistency is checked at generation time, not silently overwritten.
        stored=load('walk-metrics.json')['joints']
        assert np.isclose(summary['positions']['head']['jerk_rms'],stored['head']['jerk_rms'][variant])
        assert np.isclose(summary['rotations']['hand.L']['angular_accel_p95_rad_s2'],stored['hand.L']['angular_accel_p95_rad_s2'][variant])
    axs[0].set(title='Measured walk: identical 1.167 s period, 30 Hz evaluation',ylabel='Head jerk magnitude (m/s^3)')
    axs[1].set(xlabel='Actual time (s)',ylabel='Left hand angular acceleration (rad/s^2)')
    axs[0].legend()
    for ax in axs:ax.grid(alpha=.2)
    fig.savefig(out/'motion-diagnostics.png',dpi=150);plt.close(fig)

    fig,ax=plt.subplots(figsize=(10,3.6),layout='constrained')
    for variant in ['before','after']:
        series=load(variant+'-back-frames.json')
        ax.plot([x['time_s'] for x in series],[1000*x['arm_shoulder_pull_core_max_m'] for x in series],label=variant,color=colors[variant])
    ax.set(title='Measured Run_Stop: shoulder/arm contribution to 122 fixed back vertices',xlabel='Actual time (s)',ylabel='Max mesh position difference (mm)');ax.legend();ax.grid(alpha=.2)
    fig.savefig(out/'back-contribution.png',dpi=150);plt.close(fig)

    fitting=load('shoulder-optimization.json');mesh=load('run-stop-binding-metrics.json')
    fig,axs=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
    hist=fitting['history'];axs[0].plot([x['call'] for x in hist],[x['loss'] for x in hist],marker='.',color='#008b8b')
    axs[0].set(title='Actual multi-pose fitting trace',xlabel='Objective evaluation call (not iteration)',ylabel='Weighted objective (project-specific)');axs[0].grid(alpha=.2)
    labels=['Shoulder cap','Armhole','Upper sleeve'];x=np.arange(3)
    for offset,variant,color in [(-.24,'original','#c46b3e'),(0,'previous','#d7ae57'),(.24,'current','#008b8b')]:
        vals=[mesh['variants'][variant]['regions'][r]['max'] for r in ['shoulder_cap','armhole','upper_sleeve']]
        axs[1].bar(x+offset,vals,width=.24,label=variant,color=color)
    axs[1].set(xticks=x,xticklabels=labels,ylabel='Peak edge length / rest length',title='Measured Run_Stop: identical motion');axs[1].legend(fontsize=8)
    fig.suptitle('63 fit poses; stopped at 200 iterations (not converged); full timeline checked separately',fontsize=11)
    fig.savefig(out/'skinning-optimization.png',dpi=150);plt.close(fig)

    s=np.linspace(0,1,201);w=quintic_weight(s)
    fig,axs=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    axs[0].plot(s,w,color='#008b8b');axs[0].set(title='Quintic blend envelope',xlabel='Normalized transition time',ylabel='Blend weight')
    q1=np.sin(2*np.pi*s);q2=np.sin(2*np.pi*s+np.pi)
    axs[1].plot(s,q1,label='matched phase',color='#008b8b');axs[1].plot(s,.5*(q1+q2),label='opposite-phase 50/50 blend',color='#c46b3e')
    axs[1].set(title='Why align gait events before blending',xlabel='Cycle phase',ylabel='Illustrative joint swing');axs[1].legend(fontsize=8)
    for ax in axs:ax.grid(alpha=.2)
    fig.suptitle('METHOD ILLUSTRATION ONLY - synthetic signals, not measured character data',fontsize=11)
    fig.savefig(out/'phase-method.png',dpi=150);plt.close(fig)
    print('SHOWCASE_FIGURES_OK: measured summaries reproduced; illustrative signals labelled')


if __name__=='__main__':main()
