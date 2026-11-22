import sys, json; sys.path.insert(0,'work')
from render3d import render, load_stl
F='work/out/front_cover.stl'; B='work/out/back_cover.stl'; A='work/out/assembly.stl'
render([(load_stl(F),(214,221,228))],'work/prev_front_iso.png',1100, rot=(58,0,18), zoom=None)
render([(load_stl(F),(214,221,228))],'work/prev_front_back.png',1100, rot=(-58,0,-18))
render([(load_stl(B),(214,221,228))],'work/prev_back_iso.png',1100, rot=(-62,0,16))
render([(load_stl(F),(190,200,212))],'work/prev_front_flat.png',1000, rot=(0,0,0), zoom=None)
print("ok")
