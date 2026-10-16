"""Analyze matched mesh samples. NPZ keys documented in data-contract.md."""
import argparse
import json
from pathlib import Path
import numpy as np


def analyze(rest, posed, edges, region, disabled=None, min_edge_m=.001):
    rest, posed = np.asarray(rest, float), np.asarray(posed, float)
    edges, region = np.asarray(edges), np.asarray(region)
    if rest.ndim != 2 or rest.shape[1] != 3 or posed.ndim != 3 or posed.shape[1:] != rest.shape:
        raise ValueError('Expected rest [V,3] and posed [T,V,3] with matching topology')
    if not len(posed) or not np.isfinite(rest).all() or not np.isfinite(posed).all():
        raise ValueError('Need finite nonempty mesh samples')
    if edges.ndim != 2 or edges.shape[1] != 2 or edges.dtype.kind not in 'iu':
        raise ValueError('Expected integer edges [E,2]')
    if region.ndim != 1 or region.dtype.kind not in 'iu' or not len(region):
        raise ValueError('Expected nonempty integer vertex region')
    if edges.size and (edges.min() < 0 or edges.max() >= len(rest)):
        raise ValueError('Edge index outside rest mesh')
    if region.min() < 0 or region.max() >= len(rest) or len(np.unique(region)) != len(region):
        raise ValueError('Invalid or duplicate region IDs')
    if not np.isfinite(min_edge_m) or min_edge_m <= 0:
        raise ValueError('min_edge_m must be positive')
    keep = np.isin(edges, region).all(axis=1)
    selected = edges[keep]
    length = np.linalg.norm(rest[selected[:, 1]]-rest[selected[:, 0]], axis=1)
    accepted = length >= min_edge_m
    selected, length = selected[accepted], length[accepted]
    result = {'region_vertices': len(region), 'edges_used': len(selected),
              'short_edges_excluded': int((~accepted).sum()), 'min_edge_m': min_edge_m,
              'samples': len(posed), 'status': 'descriptive diagnostics; no automatic acceptance'}
    if len(selected):
        ratio = np.linalg.norm(posed[:, selected[:, 1]]-posed[:, selected[:, 0]], axis=-1)/length
        result['edge_ratio'] = {'max_each_frame': ratio.max(axis=1).tolist(),
                                'p95_each_frame': np.percentile(ratio, 95, axis=1).tolist(),
                                'min_each_frame': ratio.min(axis=1).tolist()}
    else:
        result['edge_ratio'] = None
    if disabled is not None:
        disabled = np.asarray(disabled, float)
        if disabled.shape != posed.shape or not np.isfinite(disabled).all():
            raise ValueError('Disabled-chain samples must match posed mesh')
        delta = np.linalg.norm(posed[:, region]-disabled[:, region], axis=-1)
        result['chain_contribution_m'] = {'max_each_frame': delta.max(axis=1).tolist(),
                                        'p95_each_frame': np.percentile(delta, 95, axis=1).tolist()}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', help='NPZ; arrays in meters, same vertex order')
    ap.add_argument('--output', required=True)
    ap.add_argument('--min-edge-m', type=float, default=.001)
    args = ap.parse_args()
    with np.load(args.input, allow_pickle=False) as d:
        report = analyze(d['rest'], d['posed'], d['edges'], d['region'],
                         d['disabled'] if 'disabled' in d else None, args.min_edge_m)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
