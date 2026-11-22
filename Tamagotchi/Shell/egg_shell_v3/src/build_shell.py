#!/usr/bin/env python3
"""
Tamagotchi egg enclosure v3 — snap-fit (no screws), taller front for a long-leg ESP,
directly exposed switches, cable-tie strain relief, seam groove.
FreeCAD 1.0 / Part API.  Frame: X = pcb_x - CX, Y = CY - pcb_y, Z up.
PCB: z 0 .. 1.6
"""
import FreeCAD, Part, json, math, os, time

t0 = time.time()
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile.json')))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters ----------------
OUT_OFF = 6.0
CAV_OFF = 2.8
Z_FRONT = 12.3           # front outer face  (was 10.2)
Z_FCEIL = 10.3           # front cavity ceiling -> 8.7 mm clear above pcb
Z_BACK = -7.0
Z_BCEIL = -5.0
Z_PCB0, Z_PCB1 = 0.0, 1.6
EDGE_F = 5.0
EDGE_B = 5.0
SEAM_CH = 0.4            # chamfer at both sides of the split line

ESP_STANDOFF = 2.5       # assumed module stand-off above the pcb (2.54 mm header)
USB_AXIS = Z_PCB1 + ESP_STANDOFF + 2.46   # usb-c connector centre line

POST_R = 3.2
PIN_R = 1.55
BARB_R = 1.85
PIN_BOT = -1.20

CX, CY = P['meta']['cx'], P['meta']['cy']
def S(x, y):
    return (x - CX, CY - y)

holes = [S(145.288, 65.024), S(117.348, 96.012), S(175.768, 113.792)]
screen_c = S(144.526, 102.50)
LED = S(145.288, 122.936)
buttons = [S(123.444, 123.952), S(137.668, 123.952), S(153.518, 123.952), S(169.164, 123.952)]
USB = (S(132.78, 78.23)[0], S(132.78, 78.23)[1])
USB_SLOT = (12.4, 6.6)
USB_SLOT_CZ = USB_AXIS

print("z_front %.2f  ceiling %.2f  front clearance %.2f" % (Z_FRONT, Z_FCEIL, Z_FCEIL - Z_PCB1))
print("assumed esp standoff %.2f -> usb axis z %.2f, slot %.2f..%.2f"
      % (ESP_STANDOFF, USB_AXIS, USB_AXIS - USB_SLOT[1] / 2, USB_AXIS + USB_SLOT[1] / 2))


# ---------------- helpers ----------------
def spline_face(points, z=0.0):
    bs = Part.BSplineCurve()
    bs.interpolate(Points=[FreeCAD.Vector(x, y, z) for x, y in points],
                   PeriodicFlag=True, Tolerance=1e-6)
    return Part.Face(Part.Wire([Part.Edge(bs)]))


def rr_pts(w, h, r, cx=0.0, cy=0.0, n=8):
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    hw, hh = w / 2 - r, h / 2 - r
    pts = []
    for ccx, ccy, a0 in [(hw, hh, 0), (-hw, hh, 90), (-hw, -hh, 180), (hw, -hh, 270)]:
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + ccx + r * math.cos(a), cy + ccy + r * math.sin(a)))
    return pts


def poly_face(points, z):
    pts = [FreeCAD.Vector(x, y, z) for x, y in points]
    pts.append(pts[0])
    return Part.Face(Part.Wire(Part.makePolygon(pts).Edges))


def rr_solid(w, h, r, cx, cy, z0, z1):
    return poly_face(rr_pts(w, h, r, cx, cy), z0).extrude(FreeCAD.Vector(0, 0, z1 - z0))


def loft_rr(w1, h1, r1, w2, h2, r2, cx, cy, z1, z2, n=8):
    def w(wd, ht, rr, z):
        p = rr_pts(wd, ht, rr, cx, cy, n)
        return Part.Wire(Part.makePolygon([FreeCAD.Vector(x, y, z) for x, y in p] +
                                          [FreeCAD.Vector(p[0][0], p[0][1], z)]))
    return Part.makeLoft([w(w1, h1, r1, z1), w(w2, h2, r2, z2)], solid=True, ruled=True)


def cyl(r, z0, z1, x, y):
    if z1 < z0:
        z0, z1 = z1, z0
    return Part.makeCylinder(r, z1 - z0, FreeCAD.Vector(x, y, z0), FreeCAD.Vector(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, FreeCAD.Vector(x0, y0, z0))


def prism_along_x(points_yz, x0, x1):
    pts = [FreeCAD.Vector(x0, y, z) for y, z in points_yz]
    pts.append(pts[0])
    return Part.Face(Part.Wire(Part.makePolygon(pts))).extrude(FreeCAD.Vector(x1 - x0, 0, 0))


def cut_all(base, tools):
    for t in tools:
        base = base.cut(t)
    return base


def fuse_all(base, tools):
    for t in tools:
        base = base.fuse(t)
    return base


# ---------------- front cover ----------------
print("\n[front cover]")
front = spline_face(P['off6.0']).extrude(FreeCAD.Vector(0, 0, Z_FRONT))
top_edges = [e for e in front.Edges
             if abs(e.BoundBox.ZMax - Z_FRONT) < 1e-6 and abs(e.BoundBox.ZMin - Z_FRONT) < 1e-6]
front = front.makeFillet(EDGE_F, top_edges)
bot = [e for e in front.Edges if abs(e.BoundBox.ZMax) < 1e-6 and abs(e.BoundBox.ZMin) < 1e-6]
try:
    front = front.makeChamfer(SEAM_CH, bot)
    print("  seam chamfer ok", front.isValid())
except Exception as ex:
    print("  !! seam chamfer failed:", ex)
print("  outer:", round(front.Volume, 1), front.isValid())

cav = spline_face(P['off2.8']).extrude(FreeCAD.Vector(0, 0, Z_FCEIL))
front = front.cut(cav)
print("  cavity:", round(front.Volume, 1), front.isValid())

# posts + snap pins
adds = []
for hx, hy in holes:
    adds.append(cyl(POST_R, Z_PCB1, Z_FCEIL + 0.2, hx, hy))          # collar
    adds.append(cyl(PIN_R, PIN_BOT, Z_PCB1 + 0.1, hx, hy))          # through pcb
    adds.append(Part.makeCone(PIN_R, BARB_R, 0.90,
                              FreeCAD.Vector(hx, hy, -0.95), FreeCAD.Vector(0, 0, 1)))
front = fuse_all(front, adds)

front = front.removeSplitter()
print("  + posts:", round(front.Volume, 1), front.isValid())

# cutouts
cuts = []
# pin slits (split pins so the barbs can flex through the pcb holes)
for hx, hy in holes:
    cuts.append(box(hx - 0.45, hx + 0.45, hy - 3.2, hy + 3.2, PIN_BOT - 0.2, 0.75))
# screen bezel + window
cuts.append(rr_solid(27.5, 18.5, 3.0, screen_c[0], screen_c[1], Z_FRONT - 0.8, Z_FRONT + 1))
cuts.append(loft_rr(24.0, 14.2, 2.2, 25.4, 15.6, 2.6, screen_c[0], screen_c[1], Z_FRONT - 0.8, Z_FCEIL - 0.1))
# LED (plain hole - no counterbore, keeps the web to SW2 >= 1.2 mm)
cuts.append(cyl(1.2, Z_FCEIL - 0.1, Z_FRONT + 1, LED[0], LED[1]))
# buttons: 9.6 bore + 10.4 guide chamfer
for bx, by in buttons:
    cuts.append(cyl(4.8, Z_FCEIL - 0.1, Z_FRONT - 0.65, bx, by))
    cuts.append(Part.makeCone(4.8, 5.2, 0.7, FreeCAD.Vector(bx, by, Z_FRONT - 0.7),
                              FreeCAD.Vector(0, 0, 1)))
# usb-c slot
slot_pts = rr_pts(USB_SLOT[0], USB_SLOT[1], 2.2, USB[1], USB_SLOT_CZ)
cuts.append(prism_along_x([(y, z) for y, z in slot_pts], USB[0] - 24, USB[0] - 2))
# cable-tie slots either side of the usb opening
for dy in (-8.2, 8.2):
    tie = rr_pts(2.4, 3.2, 0.9, USB[1] + dy, USB_SLOT_CZ)
    cuts.append(prism_along_x([(y, z) for y, z in tie], USB[0] - 24, USB[0] - 2))
# snap-catch notches in the inner wall
# --- snap-fit: positions derived from the cavity outline ---
CAV = P['off2.8']
def cav_xmax(y0, half=1.5):
    return max(q[0] for q in CAV if abs(q[1] - y0) <= half)
def cav_ymax(x0, half=1.5):
    return max(q[1] for q in CAV if abs(q[0] - x0) <= half)
def cav_xmin(y0, half=1.5):
    return min(q[0] for q in CAV if abs(q[1] - y0) <= half)
def cav_ymin(x0, half=1.5):
    return min(q[1] for q in CAV if abs(q[0] - x0) <= half)

ARM_W, ARM_T = 3.0, 1.2
CLEAR = 0.20
HOOKP = []
# (position of arm inner face, axis, sign)
HOOKP.append((('x', cav_xmax(0.0) - CLEAR - ARM_T, 0.0), 'x', +1))
HOOKP.append((('x', cav_xmin(0.0) + CLEAR + ARM_T, 0.0), 'x', -1))
HOOKP.append((('y', 0.0, cav_ymax(0.0) - CLEAR - ARM_T), 'y', +1))
HOOKP.append((('y', 0.0, cav_ymin(0.0) + CLEAR + ARM_T), 'y', -1))
print("  hook bases:", [((round(a, 2), round(b, 2)), ax, sg) for (_, a, b), ax, sg in HOOKP])

# notch pockets 0.6 mm deep into the inner wall, 3.8 wide, 1.0 tall
for (_, a, b), ax, sg in HOOKP:
    if ax == 'x':
        cuts.append(box(a - sg * 0.05, a + sg * (ARM_T + CLEAR + 0.60), b - 1.9, b + 1.9, 4.45, 5.55))
    else:
        cuts.append(box(a - 1.9, a + 1.9, b - sg * 0.05, b + sg * (ARM_T + CLEAR + 0.60), 4.45, 5.55))

front = cut_all(front, cuts)
front = front.removeSplitter()
print("  after cutouts:", round(front.Volume, 1), "valid", front.isValid(), "solids", len(front.Solids))

# ---------------- back cover ----------------
print("\n[back cover]")
back = spline_face(P['off6.0']).extrude(FreeCAD.Vector(0, 0, -Z_BACK))
back.translate(FreeCAD.Vector(0, 0, Z_BACK))
be = [e for e in back.Edges if abs(e.BoundBox.ZMin - Z_BACK) < 1e-6 and abs(e.BoundBox.ZMax - Z_BACK) < 1e-6]
back = back.makeFillet(EDGE_B, be)
te = [e for e in back.Edges if abs(e.BoundBox.ZMax) < 1e-6 and abs(e.BoundBox.ZMin) < 1e-6]
try:
    back = back.makeChamfer(SEAM_CH, te)
    print("  seam chamfer ok", back.isValid())
except Exception as ex:
    print("  !! seam chamfer failed:", ex)
print("  outer:", round(back.Volume, 1), back.isValid())

cavb = spline_face(P['off2.8']).extrude(FreeCAD.Vector(0, 0, -Z_BCEIL))
cavb.translate(FreeCAD.Vector(0, 0, Z_BCEIL))
back = back.cut(cavb)
print("  cavity:", round(back.Volume, 1), back.isValid())

# support pads under the button row (stop the pcb flexing)
pad_y = buttons[0][1]
for px in (-15.53, 0.52, 15.47):
    back = back.fuse(cyl(2.6, Z_BCEIL - 0.2, 0.0, px, pad_y))

# snap hooks
# (x,y) = position of the arm's INNER face; u grows outward along the wall normal
# (x,y) = inner face of the arm; u runs outward.  L-profile: foot merges into the rim,
# arm rises into the front cover, barb snaps into a notch in its inner wall.
PROF = [(0.0, -0.90), (2.80, -0.90), (2.80, 0.0), (1.20, 0.0),
        (1.20, 4.55), (1.85, 4.55), (1.85, 4.72), (1.20, 5.45), (0.0, 5.45)]
for (_, a, b), ax, sg in HOOKP:
    if ax == 'x':
        pp = [FreeCAD.Vector(a + sg * u, b - ARM_W / 2, z) for u, z in PROF]
        hook = Part.Face(Part.Wire(Part.makePolygon(pp + [pp[0]]))).extrude(FreeCAD.Vector(0, ARM_W, 0))
    else:
        pp = [FreeCAD.Vector(a - ARM_W / 2, b + sg * u, z) for u, z in PROF]
        hook = Part.Face(Part.Wire(Part.makePolygon(pp + [pp[0]]))).extrude(FreeCAD.Vector(ARM_W, 0, 0))
    back = back.fuse(hook)

back = back.removeSplitter()
print("  after pads/hooks:", round(back.Volume, 1), "valid", back.isValid(), "solids", len(back.Solids))

# ---------------- PCB + component mock ----------------
print("\n[pcb]")
pcb = spline_face(P['board']).extrude(FreeCAD.Vector(0, 0, Z_PCB1 - Z_PCB0))
pcb.translate(FreeCAD.Vector(0, 0, Z_PCB0))
for hx, hy in holes:                      # real 3.2 mm mounting holes
    pcb = pcb.cut(cyl(1.6, -0.1, Z_PCB1 + 0.1, hx, hy))
comps = []
ex0, ey0 = S(145.542, 78.232)
comps.append(box(ex0 - 11.26, ex0 + 11.26, ey0 - 9.0, ey0 + 9.0, Z_PCB1 + ESP_STANDOFF, Z_PCB1 + ESP_STANDOFF + 1.0))
comps.append(box(ex0 - 12.76, ex0 - 5.41, ey0 - 4.46, ey0 + 4.46,
                 Z_PCB1 + ESP_STANDOFF + 1.35, Z_PCB1 + ESP_STANDOFF + 3.57))
sx, sy = S(144.526, 103.58)
comps.append(box(sx - 13.65, sx + 13.65, sy - 13.9, sy + 13.9, Z_PCB1 + 2.54, Z_PCB1 + 3.54))
comps.append(box(sx - 13.35, sx + 13.35, sy - 9.63, sy + 9.63, Z_PCB1 + 3.54, Z_PCB1 + 4.94))
for bx, by in buttons:
    comps.append(box(bx - 2.25, bx + 2.25, by - 2.6, by + 2.6, Z_PCB1, Z_PCB1 + 0.55))
comps.append(box(LED[0] - 1.0, LED[0] + 1.0, LED[1] - 0.625, LED[1] + 0.625, Z_PCB1, Z_PCB1 + 0.6))
for px, py in [(121.007, 131.064), (126.05, 131.064), (134.724, 131.064), (140.274, 131.064),
               (145.288, 131.064), (150.876, 131.064), (155.956, 131.064), (165.608, 131.064),
               (170.688, 131.064)]:
    qx, qy = S(px, py)
    comps.append(box(qx - 1.0, qx + 1.0, qy - 0.625, qy + 0.625, Z_PCB1, Z_PCB1 + 0.6))

# ---------------- checks ----------------
print("\n[checks]")
def overlap(shape, container, label, expect=0.0):
    inter = shape.common(container)
    v = inter.Volume if inter.Solids else 0.0
    flag = "" if abs(v - expect) <= 0.4 else "   <-- CHECK"
    extra = ""
    if v > 0.4:
        bb = inter.BoundBox
        extra = f"  bbox({bb.XMin:.1f},{bb.YMin:.1f},{bb.ZMin:.1f})-({bb.XMax:.1f},{bb.YMax:.1f},{bb.ZMax:.1f})"
    print(f"  {label}: {v:.3f} mm3{flag}{extra}")
    return v

overlap(pcb, front, "pcb vs front")
overlap(pcb, back, "pcb vs back")
for i, c in enumerate(comps):
    overlap(c, front, f"comp{i} vs front")
for i, c in enumerate(comps):
    overlap(c, back, f"comp{i} vs back")
overlap(front, back, "front vs back")
print("  front vol", round(front.Volume, 1), " back vol", round(back.Volume, 1))

# ---------------- export ----------------
print("\n[export]")
import MeshPart
def export(shape, name, lin=0.02, ang=0.25):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=lin, AngularDeflection=ang, Relative=False)
    m.write(os.path.join(OUT, name + '.stl'))
    shape.exportStep(os.path.join(OUT, name + '.step'))
    print("  ", name, "tris", m.CountFacets, "solids", len(shape.Solids))

export(front, 'front_cover')
export(back, 'back_cover')
export(pcb, 'pcb', 0.05, 0.4)
compall = comps[0]
for c in comps[1:]:
    compall = compall.fuse(c)
export(compall, 'comps', 0.05, 0.4)

asm = front.fuse(back).fuse(pcb)
for c in comps:
    asm = asm.fuse(c)
asm.exportStep(os.path.join(OUT, 'assembly.step'))
m = MeshPart.meshFromShape(Shape=asm, LinearDeflection=0.05, AngularDeflection=0.4, Relative=False)
m.write(os.path.join(OUT, 'assembly.stl'))
print("  assembly tris", m.CountFacets)
print("\ndone in", round(time.time() - t0, 1), "s")
