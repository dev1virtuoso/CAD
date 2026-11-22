import sys, numpy as np; sys.path.insert(0,'work')
from render3d import render, load_stl
K=load_stl('work/out/buttons.stl')
print("buttons bbox", K.reshape(-1,3).min(0), K.reshape(-1,3).max(0))
render([(K,(200,205,212))],'work/prev_buttons.png',900, view=(-56,8))
# one cap side view
import json
c=K.copy()
# cut to first cap region x<8
c=c[c.mean(1)[:,0]<9]
render([(c,(200,205,212))],'work/prev_cap.png',700, view=(-90,0), zoom=12)
