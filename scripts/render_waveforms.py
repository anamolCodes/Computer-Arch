"""Plot actual Icarus VCD samples; fail if traces or required signals are absent."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/alu-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OPS = 'and nand or nor xor xnor not shift add sub mul div'.split()
for figure_name in OPS + ['shift_left']:
    op = 'shift' if figure_name == 'shift_left' else figure_name
    codes, values, rows = {}, {}, []
    time = None
    for line in (ROOT / f'build/{op}.vcd').read_text().splitlines():
        fields = line.split()
        if line.startswith('$var'):
            codes[fields[4]] = fields[3]
        elif line.startswith('#'):
            if time is not None:
                rows.append((time, values.copy()))
            time = int(line[1:]) / 1000  # VCD precision is 1ps; plot ns.
        elif line.startswith('b'):
            values[fields[1]] = fields[0][1:]
        elif line and line[0] in '01xz' and not line.startswith('$'):
            values[line[1:]] = line[0]
    rows.append((time, values.copy()))
    signals = ['a'] + ([] if op == 'not' else ['b'])
    if op in ('add','sub'): signals += ['cin']
    signals += ['x']
    if op in ('shift','mul','div'): signals += ['y']
    if op in ('add','sub'): signals += ['cout']
    if op == 'div': signals += ['divide_by_zero']
    # Choose useful nonzero operands and include the two assignment shift examples.
    start = {'shift': 900, 'add': 2360, 'sub': 2360, 'mul': 2320, 'div': 2320, 'not': 0}.get(op, 2320)
    if figure_name == 'shift_left': start = 1800
    stop = start + (60 if op == 'shift' else 160)
    selected = [(t,v) for t,v in rows if start <= t <= stop]
    assert selected and all(s in codes for s in signals), op
    fig, axes = plt.subplots(len(signals), 1, figsize=(10, .65*len(signals)+.9), sharex=True)
    for ax, signal in zip(axes, signals):
        series=[]
        for t, v in selected:
            raw=v[codes[signal]]
            assert not any(c in raw for c in 'xz'), (op,signal,t)
            series.append(int(raw,2))
        times=[t for t,_ in selected]
        ax.step(times,series,where='post',color='#155e75')
        for t,val in zip(times[:-1],series[:-1]):
            ax.text(t+2,val,format(val,'x').upper(),fontsize=7,va='bottom')
        ax.set_ylabel(signal,rotation=0,ha='right',fontsize=8)
        ax.set_ylim(-1,max(series)+2)
        ax.set_yticks([])
        ax.grid(axis='x',alpha=.2)
    axes[-1].set_xlabel('Simulation time (ns); bus values shown in hexadecimal')
    fig.suptitle(f'{op.upper()}: actual simulation trace (cropped)',fontsize=11)
    fig.tight_layout()
    fig.savefig(ROOT/f'latex/figures/{figure_name}.pdf')
    plt.close(fig)
print('Rendered 13 waveform figures from VCD traces.')
