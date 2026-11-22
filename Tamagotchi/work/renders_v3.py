import sys, numpy as np
sys.path.insert(0,'work')
from render3d import render, load_stl
D='work/out/'
F=load_stl(D+'front_cover.stl'); B=load_stl(D+'back_cover.stl')
P=load_stl(D+'pcb.stl'); C=load_stl(D+'comps.stl')
CF=(206,216,228); CB=(192,202,216); CP=(58,118,90); CC=(64,70,78)
def sh(t,dz=0.0):
    c=t.copy(); c[:,:,2]+=dz; return c
def back(t):
    c=t.copy(); c[:,:,0]*=-1; c[:,:,2]*=-1; return c
render([(F,CF),(B,CB)],'work/v3_hero_front.png',1200, view=(-58,16))
render([(back(B),CB),(back(F),CF)],'work/v3_hero_back.png',1200, view=(-58,-16))
render([(F,CF),(B,CB)],'work/v3_side.png',1000, view=(-6,0,78))
render([(F.copy()*np.array([1,1,-1]),CF)],'work/v3_inside_front.png',1100, view=(-52,12))
render([(B.copy()*np.array([1,1,-1]),CB)],'work/v3_inside_back.png',1100, view=(-52,12))
render([(sh(B,-14),CB),(sh(P,-3),CP),(sh(C,-3),CC),(sh(F,26),CF)],'work/v3_exploded.png',1400, view=(-60,18), zoom=155)
print('ok')
