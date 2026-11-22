import sys, numpy as np
sys.path.insert(0, 'work')
from render3d import render, load_stl

D = 'work/out/'
F = load_stl(D + 'front_cover.stl'); B = load_stl(D + 'back_cover.stl')
P = load_stl(D + 'pcb.stl');         C = load_stl(D + 'comps.stl')
K = load_stl(D + 'buttons.stl')

CF = (206, 216, 228); CB = (192, 202, 216)
CP = (58, 118, 90);   CC = (64, 70, 78);   CK = (150, 160, 172)

def sh(t, dz=0.0, dy=0.0, dx=0.0):
    c = t.copy(); c[:, :, 0] += dx; c[:, :, 1] += dy; c[:, :, 2] += dz; return c

def back(t):
    c = t.copy(); c[:, :, 0] *= -1; c[:, :, 2] *= -1; return c

# closed hero
render([(F, CF), (B, CB)], 'work/final_hero_front.png', 1200, view=(-58, 16))
render([(back(B), CB), (back(F), CF)], 'work/final_hero_back.png', 1200, view=(-58, -16))
render([(F, CF), (B, CB)], 'work/final_side_left.png', 1000, view=(-6, 0, 78))
render([(F, CF), (B, CB)], 'work/final_front_ortho.png', 1100, view=(0, 0))
# interiors
render([(F.copy() * np.array([1, 1, -1]), CF)], 'work/final_inside_front.png', 1100, view=(-52, 12))
render([(B.copy() * np.array([1, 1, -1]), CB)], 'work/final_inside_back.png', 1100, view=(-52, 12))
# exploded
render([(sh(B, -16), CB), (sh(P, -3), CP), (sh(C, -3), CC), (sh(F, 28), CF)],
       'work/final_exploded.png', 1400, view=(-60, 18), zoom=165)
# buttons
render([(K, CK)], 'work/final_buttons.png', 900, view=(-52, 6))
print('done')

# PCB sitting in back cover (assembly step)
render([(B, CB), (P, CP), (C, CC)], 'work/final_pcb_in_back.png', 1200, view=(-58, 14))
# PCB on front cover posts (viewed from behind)
render([(F.copy() * np.array([1, 1, -1]), CF), (P, CP), (C, CC)], 'work/final_pcb_on_front.png', 1200, view=(-58, 14))

# exploded incl. button plungers
KP = load_stl(D + 'caps_inplace.stl')
KP[:, :, 0] -= 40.0
render([(sh(B, -16), CB), (sh(P, -3), CP), (sh(C, -3), CC), (sh(KP, 19), CK), (sh(F, 30), CF)],
       'work/final_exploded.png', 1400, view=(-60, 18), zoom=165)
# installed view (front cover off, PCB + plungers in back)
render([(B, CB), (P, CP), (C, CC), (KP, CK)], 'work/final_pcb_in_back.png', 1200, view=(-58, 14))
print('extra done')
