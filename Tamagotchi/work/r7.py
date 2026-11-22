import sys, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
for n in ['sec_screen','sec_buttons']:
    t=load_stl(f'work/out/{n}.stl')
    render([(t,(215,221,228))],f'work/{n}.png',1000, view=(-90,0))
    render([(t,(215,221,228))],f'work/{n}_iso.png',1000, view=(-72,25))
