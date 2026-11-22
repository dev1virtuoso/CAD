import sys; sys.path.insert(0,'work')
from render3d import render, load_stl
F=load_stl('work/out/front_cover.stl')
render([(F,(226,231,238))],'work/t_left.png',800, view=(-12,0,90))
render([(F,(226,231,238))],'work/t_left2.png',800, view=(-25,-20,75))
