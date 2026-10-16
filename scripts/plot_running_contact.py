"""Rebuild the running-contact figure from committed measurement summaries."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=root/'docs/showcase/data/running-contact.json')
    parser.add_argument('--output', type=Path, default=root/'docs/showcase/running-contact.png')
    args = parser.parse_args()
    records = json.loads(args.data.read_text())['records']
    fig, ax = plt.subplots(figsize=(12, 5.3))
    fig.subplots_adjust(left=.12, right=.98, bottom=.15, top=.76)
    fig.patch.set_facecolor('#f4f7fb')
    ax.set_facecolor('#f4f7fb')
    y = np.arange(len(records))
    before = np.array([r['before']['stance_path_m']*1000 for r in records])
    after = np.array([r['after']['stance_path_m']*1000 for r in records])
    ax.barh(y-.17, before, height=.30, color='#70839c', label='Before')
    ax.barh(y+.17, after, height=.30, color='#12988b', label='After')
    for yi, a, b in zip(y, before, after):
        ax.text(a+6, yi-.17, f'{a:.1f}', va='center', color='#34455a')
        ax.text(b+6, yi+.17, f'{b:.2f}', va='center', color='#087b70', weight='bold')
    ax.set_yticks(y, [f"{r['clip'].split('_')[0]} / {'left' if r['side']=='L' else 'right'}" for r in records])
    ax.invert_yaxis()
    ax.set_xlim(0, 450)
    ax.set_xlabel('Horizontal sole path during one support interval (mm)')
    ax.set_title('Running contact: actual Blender evaluation', loc='left', fontsize=18, pad=42)
    fig.text(.12, .83, '120 Hz | fixed contact windows | same skin | designed ground speed: sprint 4.4 m/s, jog 4.0 m/s', fontsize=10, color='#53677e')
    ax.legend(loc='lower right')
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.grid(axis='x', alpha=.15)
    ax.set_axisbelow(True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=150)
    plt.close(fig)
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
