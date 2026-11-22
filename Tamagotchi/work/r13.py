import sys, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
F=load_stl('work/out/front_cover.stl'); P=load_stl('work/out/pcb.stl'); C=load_stl('work/out/comps.stl')
CF=(206,216,228); CP=(58,118,90); CC=(30,33,38)
# crop around button 2 in x
def crop(t, x0, x1, y0, y1):
    c=t.mean(1); m=(c[:,0]>=x0)&(c[:,0]<=x1)&(c[:,1]>=y0)&(c[:,1]<=y1); return t[m]
box=(-16,-2,-26,-15)
render([(crop(F,*box),CF),(crop(P,*box),CP),(crop(C,*box),CC)],'work/v2_button_closeup.png',900, view=(-30,4), zoom=16)
render([(crop(F,*box),CF),(crop(P,*box),CP),(crop(C,*box),CC)],'work/v2_button_top.png',900, view=(0,0), zoom=16)
