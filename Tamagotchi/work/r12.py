import sys, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
F=load_stl('work/out/front_cover.stl'); B=load_stl('work/out/back_cover.stl')
P=load_stl('work/out/pcb.stl'); C=load_stl('work/out/comps.stl')
CF=(206,216,228); CB=(192,202,216); CP=(58,118,90); CC=(64,70,78)
render([(F,CF),(B,CB)],'work/v2_hero_front.png',1200, view=(-58,16))
render([(F,CF),(B,CB)],'work/v2_side.png',1000, view=(-6,0,78))
# front cover with PCB inside, seen from front-ish looking into the button holes
render([(F,CF),(P,CP),(C,CC)],'work/v2_buttons_ctx.png',1100, view=(-42,10), zoom=100)
