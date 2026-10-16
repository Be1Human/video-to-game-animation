"""Generate a synthetic counterexample: smooth motion can still violate foot contact."""
import argparse
import json
from pathlib import Path
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    target = out/'smooth-sliding.json'
    if target.exists():
        raise ValueError('Demo already exists; choose a new output directory')
    out.mkdir(parents=True, exist_ok=True)
    t = np.linspace(0, 1, 61)
    demo = {'name':'synthetic-smooth-sliding', 'time_s':t.tolist(), 'units':'m',
            'axes':'Z-up', 'up_axis':'Z', 'scale_m':1.7,
            'positions':{'sole':np.column_stack([t, np.zeros(61), np.zeros(61)]).tolist()},
            'contacts':[{'point':'sole', 'start_s':0, 'end_s':1,
                         'surface_stationary':True, 'evidence':'synthetic known planted contact'}],
            'provenance':{'source_type':'synthetic counterexample; not human or captured data', 'filter':'none'}}
    target.write_text(json.dumps(demo, indent=2))
    print(target)


if __name__ == '__main__':
    main()
