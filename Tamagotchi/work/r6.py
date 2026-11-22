import sys, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
F=load_stl('work/out/front_cover.stl'); B=load_stl('work/out/back_cover.stl')
F2=F.copy(); F2[:,:,2]*=-1
B2=B.copy(); B2[:,:,2]*=-1
render([(F2,(212,218,226))],'work/t_cavity.png',900, view=(-52,12))
render([(B2,(212,218,226))],'work/t_backcav.png',900, view=(-52,12))
