import sys, json, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
F=load_stl('work/out/front_cover.stl')
B=load_stl('work/out/back_cover.stl')
A=load_stl('work/out/assembly.stl')
P=json.load(open('work/profile.json'))
# exploded: shift front cover +28 z, back cover -10
f2=F.copy(); f2[:,:,2]+=28
b2=B.copy(); b2[:,:,2]-=12
render([(b2,(176,186,198)),(A,(208,214,222)),(f2,(232,237,242))],'work/prev_explode.png',1200, rot=(62,0,14))
render([(b2,(176,186,198)),(A,(208,214,222)),(f2,(232,237,242))],'work/prev_explode_back.png',1200, rot=(-62,0,-14))
print("ok")
