#!/usr/bin/env python3
"""Render the two slide-27 equations as transparent PNGs, tight-cropped.

The previous versions were clipped because they were placed at a width/height
that did not match the rendered aspect ratio. Here the image is cropped to its
ink and the placement is computed FROM the resulting aspect, so it cannot clip.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

INK = '#22333B'
FIG = '/sessions/sharp-elegant-gauss/mnt/outputs/thesis_clean/figures/'
EQ = {
 'deck_f_mcc.png':
   r'$\mathrm{MCC}=\frac{TP\cdot TN-FP\cdot FN}'
   r'{\sqrt{(TP+FP)\,(TP+FN)\,(TN+FP)\,(TN+FN)}}$',
 'deck_f_ef.png':
   r'$\mathrm{EF}_{k\%}=\frac{p_k}{p}$',
}
for name, tex in EQ.items():
    fig = plt.figure(figsize=(10, 3))
    fig.text(0.5, 0.5, tex, ha='center', va='center', fontsize=30, color=INK)
    fig.savefig(FIG + name, dpi=300, transparent=True,
                bbox_inches='tight', pad_inches=0.06)
    plt.close(fig)
    w, h = Image.open(FIG + name).size
    print(f'{name}: {w}x{h}px  aspect {w/h:.3f}')
