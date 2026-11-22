import sys; sys.path.insert(0,'work')
from render3d import render, load_stl
F='work/out/front_cover.stl'
t=load_stl(F)
print("tris",len(t),"bbox",t.reshape(-1,3).min(0),t.reshape(-1,3).max(0))
# front skin only
render([(t,(200,205,212))],'work/dbg_skin.png',900, rot=(0,0,0), clip_z=(9.0,10.4))
# back side (cavity)
render([(t,(200,205,212))],'work/dbg_cavity.png',900, rot=(0,0,0), clip_z=None)
# low z only
render([(t,(200,205,212))],'work/dbg_low.png',900, rot=(0,0,0), clip_z=(3.0,8.5))
