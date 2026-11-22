import sys, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
from PIL import Image
F=load_stl('work/out/front_cover.stl'); P=load_stl('work/out/pcb.stl'); C=load_stl('work/out/comps.stl')
CF=(206,216,228); CP=(58,118,90); CC=(28,30,34)
render([(F,CF),(P,CP),(C,CC)],'work/_tmp_zoom3.png',2000, view=(-34,6), zoom=76)
im=Image.open('work/_tmp_zoom3.png'); w,h=im.size
im.crop((int(w*0.08), int(h*0.50), int(w*0.95), int(h*0.95))).resize((1100,700)).save('work/v3_button_zoom.png')
print('ok')
