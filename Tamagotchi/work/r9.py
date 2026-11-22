import sys; sys.path.insert(0,'work')
from render3d import render, load_stl
CF=(206,216,228); CB=(186,197,212); CP=(52,112,86); CC=(70,76,84)
for sec in ['secA','secB']:
    parts=[]
    for n,c in [('front_cover',CF),('back_cover',CB),('pcb',CP),('comps',CC)]:
        try: parts.append((load_stl(f'work/out/{sec}_{n}.stl'),c))
        except Exception as e: print('skip',n,e)
    render(parts,f'work/{sec}.png',1200, view=(-90,0), zoom=104)
print('ok')
