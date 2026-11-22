import sys; sys.path.insert(0,'work')
from render3d import render, load_stl
for n in ['sec_screen','sec_buttons','sec_usb']:
    t=load_stl(f'work/out/{n}.stl')
    render([(t,(214,220,228))],f'work/{n}.png',1000, view=(-90,0))
