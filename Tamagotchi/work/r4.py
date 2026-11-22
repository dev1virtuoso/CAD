import sys; sys.path.insert(0,'work')
from render3d import render, load_stl
F=load_stl('work/out/front_cover.stl'); B=load_stl('work/out/back_cover.stl')
render([(F,(226,231,238))],'work/t_iso_a.png',800, view=(-58,18))
render([(F,(226,231,238))],'work/t_iso_b.png',800, view=(-58,-18))
render([(F,(226,231,238))],'work/t_iso_c.png',800, view=(-70,0))
