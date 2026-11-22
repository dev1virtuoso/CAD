#!/usr/bin/env python3
"""
Tamagotchi egg enclosure — parametric build (FreeCAD 1.0 / Part).
All values in mm.  Shell frame: X = pcb_x - CX, Y = CY - pcb_y, Z up.
PCB: z 0 .. 1.6  (back face at z=0, front face at z=1.6).
"""
import FreeCAD, Part, json, math, os, time

t0 = time.time()
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile.json')))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters ----------------
OUT_OFF = 6.0            # shell outer profile = board outline + 6
CAV_OFF = 2.8            # cavity = board outline + 2.8
Z_FRONT = 10.2           # front outer face
Z_FCEIL = 8.2            # front cavity ceiling  (2.0 wall, 6.6 clearance above pcb)
Z_BACK = -10.0           # back outer face
Z_BCEIL = -8.0           # back cavity ceiling (2.0 wall, 8.0 behind pcb)
Z_PCB0, Z_PCB1 = 0.0, 1.6
EDGE_F = 5.0             # fillet front rim
EDGE_B = 5.0             # fillet back rim
SPLIT = 0.0

POST_R = 3.2
POST_PILOT_D = 2.6       # M3 self-tapping pilot
POST_PILOT_DEPTH = 5.8
BOSS_R = 3.2
SCREW_HOLE_D = 3.4
CBORE_D, CBORE_DEPTH = 6.0, 1.2

# cutout centres in board coords
CX, CY = P['meta']['cx'], P['meta']['cy']
def S(x, y):
    return (x - CX, CY - y)

SCR_X, SCR_Y = 0.1, 0.05          # boss face interference (mm)

holes = [S(145.288, 65.024), S(117.348, 96.012), S(175.768, 113.792)]
screen_c = S(144.526, 102.50)
LED = S(145.288, 122.936)
buttons = [S(123.444, 123.952), S(137.668, 123.952), S(153.518, 123.952), S(169.164, 123.952)]
USB = (S(132.78, 78.23)[0], S(132.78, 78.23)[1])   # port face x, centre y
USB_Z = (2.95, 5.17)
USB_SLOT = (12.4, 6.6)    # width(Y) x height(Z) : admits plug overmould
USB_SLOT_CZ = 4.2

print("frame checks")
print("  board bbox", [round(v, 2) for v in P['meta']['bbox']])
print("  screws", [(round(a, 2), round(b, 2)) for a, b in holes])
print("  screen", tuple(round(v, 2) for v in screen_c), " led", tuple(round(v, 2) for v in LED))
print("  usb port x", round(USB[0], 2), "y", round(USB[1], 2))


# ---------------- helpers ----------------
def spline_face(points, z=0.0):
    bs = Part.BSplineCurve()
    bs.interpolate(Points=[FreeCAD.Vector(x, y, z) for x, y in points],
                   PeriodicFlag=True, Tolerance=1e-6)
    return Part.Face(Part.Wire([Part.Edge(bs)]))


def rr_pts(w, h, r, cx=0.0, cy=0.0, n=8):
    """rounded rectangle polygon (CCW), 4*(n+1) points"""
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    hw, hh = w / 2 - r, h / 2 - r
    pts = []
    corners = [(hw, hh, 0), (-hw, hh, 90), (-hw, -hh, 180), (hw, -hh, 270)]
    for ccx, ccy, a0 in corners:
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
    a = Part.Wire(Part.makePolygon([FreeCAD.Vector(x, y, z1) for x, y in rr_pts(w1, h1, r1, cx, cy, n)] + [FreeCAD.Vector(*rr_pts(w1, h1, r1, cx, cy, n)[0], z1)]))
    b = Part.Wire(Part.makePolygon([FreeCAD.Vector(x, y, z2) for x, y in rr_pts(w2, h2, r2, cx, cy, n)] + [FreeCAD.Vector(*rr_pts(w2, h2, r2, cx, cy, n)[0], z2)]))
    return Part.makeLoft([a, b], solid=True, ruled=True)


def cyl(r, z0, z1, x, y):
    if z1 < z0:
        z0, z1 = z1, z0
    return Part.makeCylinder(r, z1 - z0, FreeCAD.Vector(x, y, z0), FreeCAD.Vector(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, FreeCAD.Vector(x0, y0, z0))


def cut_all(base, tools):
    for t in tools:
        base = base.cut(t)
    return base


# ---------------- front cover ----------------
print("\n[front cover]")
front = spline_face(P['off6.0']).extrude(FreeCAD.Vector(0, 0, Z_FRONT))
front.translate(FreeCAD.Vector(0, 0, SPLIT))
top_edges = [e for e in front.Edges if abs(e.BoundBox.ZMax - Z_FRONT) < 1e-6 and abs(e.BoundBox.ZMin - Z_FRONT) < 1e-6]
front = front.makeFillet(EDGE_F, top_edges)
print("  outer + fillet:", round(front.Volume, 1), front.isValid())

cav = spline_face(P['off2.8']).extrude(FreeCAD.Vector(0, 0, Z_FCEIL - SPLIT))
cav.translate(FreeCAD.Vector(0, 0, SPLIT))
front = front.cut(cav)
print("  after cavity:", round(front.Volume, 1), front.isValid())

# posts + button/led bosses (they hang from the front ceiling)
adds = []
for hx, hy in holes:
    adds.append(cyl(POST_R, Z_PCB1, Z_FCEIL + 0.2, hx, hy))
for bx, by in buttons:
    adds.append(cyl(2.8, 3.30, Z_FCEIL + 0.2, bx, by))
adds.append(cyl(2.7, 3.20, Z_FCEIL + 0.2, LED[0], LED[1]))
for a in adds:
    front = front.fuse(a)
front = front.removeSplitter()
print("  + posts/bosses:", round(front.Volume, 1), front.isValid())

# registry ledge under the rim (drops into the back cover recess)
ledge_o = spline_face(P['off3.0']).extrude(FreeCAD.Vector(0, 0, 0.85))
ledge_o.translate(FreeCAD.Vector(0, 0, -0.85))
ledge_i = spline_face(P['off2.0']).extrude(FreeCAD.Vector(0, 0, 1.0))
ledge_i.translate(FreeCAD.Vector(0, 0, -1.0))
front = front.fuse(ledge_o.cut(ledge_i))
front = front.removeSplitter()
print("  + ledge:", round(front.Volume, 1), front.isValid())

# ---- cutouts
cuts = []
# M3 pilot holes
for hx, hy in holes:
    cuts.append(cyl(POST_PILOT_D / 2, Z_PCB1, Z_PCB1 + POST_PILOT_DEPTH, hx, hy))
# screen bezel recess + window
cuts.append(rr_solid(27.5, 18.5, 3.0, screen_c[0], screen_c[1], Z_FRONT - 0.8, Z_FRONT + 1))
cuts.append(loft_rr(24.0, 14.2, 2.2, 25.4, 15.6, 2.6, screen_c[0], screen_c[1], Z_FRONT - 0.8, Z_FCEIL - 0.1))
# LED
cuts.append(cyl(1.3, 3.1, Z_FRONT + 1, LED[0], LED[1]))
cuts.append(cyl(2.2, Z_FRONT - 0.6, Z_FRONT + 1, LED[0], LED[1]))
# buttons
for bx, by in buttons:
    cuts.append(cyl(1.8, 3.2, Z_FRONT + 1, bx, by))
    cuts.append(cyl(3.0, Z_FRONT - 1.0, Z_FRONT + 1, bx, by))
# USB-C charging slot (through the side wall, opens toward -X)
slot = poly_face(rr_pts(USB_SLOT[0], USB_SLOT[1], 2.0, USB[1], USB_SLOT_CZ), 0).extrude(FreeCAD.Vector(1, 0, 0))
# rr_pts returns pts in XY; build in YZ plane instead
def rr_yz(w, h, r, cy, cz, n=8):
    return rr_pts(w, h, r, cy, cz, n)
# build slot as an extruded YZ profile: create in XY then rotate
slot_shape = poly_face(rr_pts(USB_SLOT[0], USB_SLOT[1], 2.0, 0, 0), 0).extrude(FreeCAD.Vector(30, 0, 0))
slot_shape.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 0)  # placeholder
# simpler: build with Part.makeBox-like extrusion along X using a wire in the YZ plane
def prism_along_x(points_yz, x0, x1):
    pts = [FreeCAD.Vector(x0, y, z) for y, z in points_yz]
    pts.append(pts[0])
    f = Part.Face(Part.Wire(Part.makePolygon(pts)))
    return f.extrude(FreeCAD.Vector(x1 - x0, 0, 0))
slot_pts = rr_pts(USB_SLOT[0], USB_SLOT[1], 2.0, USB[1], USB_SLOT_CZ)
slot = prism_along_x([(y, z) for y, z in slot_pts], USB[0] - 22, USB[0] - 2)
cuts.append(slot)

front = cut_all(front, cuts)
front = front.removeSplitter()
print("  after cutouts:", round(front.Volume, 1), "valid", front.isValid(), "solids", len(front.Solids))

# ---------------- back cover ----------------
print("\n[back cover]")
back = spline_face(P['off6.0']).extrude(FreeCAD.Vector(0, 0, -Z_BACK))
back.translate(FreeCAD.Vector(0, 0, Z_BACK))
bot_edges = [e for e in back.Edges if abs(e.BoundBox.ZMin - Z_BACK) < 1e-6 and abs(e.BoundBox.ZMax - Z_BACK) < 1e-6]
back = back.makeFillet(EDGE_B, bot_edges)
print("  outer + fillet:", round(back.Volume, 1), back.isValid())

cavb = spline_face(P['off2.8']).extrude(FreeCAD.Vector(0, 0, -Z_BCEIL + 0.9))
cavb.translate(FreeCAD.Vector(0, 0, Z_BCEIL))
cavb2 = spline_face(P['off3.4']).extrude(FreeCAD.Vector(0, 0, 0.9))
cavb2.translate(FreeCAD.Vector(0, 0, -0.9))
back = back.cut(cavb).cut(cavb2)
print("  after cavity:", round(back.Volume, 1), back.isValid())

for hx, hy in holes:
    back = back.fuse(cyl(BOSS_R, Z_BCEIL - 0.2, SCR_Y, hx, hy))
back = back.removeSplitter()
cuts = []
for hx, hy in holes:
    cuts.append(cyl(SCREW_HOLE_D / 2, Z_BACK - 1, SCR_Y + 0.1, hx, hy))
    cuts.append(cyl(CBORE_D / 2, Z_BACK - 0.1, Z_BACK + CBORE_DEPTH, hx, hy))
back = cut_all(back, cuts)
back = back.removeSplitter()
print("  after screws:", round(back.Volume, 1), "valid", back.isValid(), "solids", len(back.Solids))

# ---------------- button caps ----------------
print("\n[buttons]")
caps = []
for i, (bx, by) in enumerate(buttons):
    fl = cyl(2.95, Z_FRONT - 1.0, Z_FRONT + 0.5, 0, 0)       # flange (protrudes 0.5)
    sh = cyl(1.70, 3.40, Z_FRONT - 1.0, 0, 0)                # shaft through the boss
    no = cyl(1.05, 2.30, 3.40, 0, 0)                         # nose onto the actuator
    c = fl.fuse(sh).fuse(no)
    c.translate(FreeCAD.Vector(bx + 40.0, by, 0))
    caps.append(c)
print("  cap volume", round(caps[0].Volume, 2))

# ---------------- PCB + component mock ----------------
print("\n[pcb]")
pcb = spline_face(P['board']).extrude(FreeCAD.Vector(0, 0, Z_PCB1 - Z_PCB0))
pcb.translate(FreeCAD.Vector(0, 0, Z_PCB0))
comps = []
# ESP32 module body (18 x 22.52) + usb-c
ex0, ey0 = S(145.542, 78.232)
m = box(ex0 - 11.26, ex0 + 11.26, ey0 - 9.0, ey0 + 9.0, Z_PCB1, Z_PCB1 + 1.0)
comps.append(m)
usb = box(ex0 - 12.76, ex0 - 5.41, ey0 - 4.46, ey0 + 4.46, Z_PCB1 + 1.35, Z_PCB1 + 3.57)
comps.append(usb)
# SSD1306 module (27.3 x 27.8) at 2.54 standoff + glass
sx, sy = S(144.526, 103.58)
mod = box(sx - 13.65, sx + 13.65, sy - 13.9, sy + 13.9, Z_PCB1 + 2.54, Z_PCB1 + 3.54)
comp = box(sx - 13.35, sx + 13.35, sy - 9.63, sy + 9.63, Z_PCB1 + 3.54, Z_PCB1 + 4.94)
comps += [mod, comp]
# switches
for bx, by in buttons:
    comps.append(box(bx - 2.25, bx + 2.25, by - 2.6, by + 2.6, Z_PCB1, Z_PCB1 + 0.55))
# LED
comps.append(box(LED[0] - 1.0, LED[0] + 1.0, LED[1] - 0.625, LED[1] + 0.625, Z_PCB1, Z_PCB1 + 0.6))
# passives
for px, py in [(121.007, 131.064), (126.05, 131.064), (134.724, 131.064), (140.274, 131.064),
               (145.288, 131.064), (150.876, 131.064), (155.956, 131.064), (165.608, 131.064), (170.688, 131.064)]:
    qx, qy = S(px, py)
    comps.append(box(qx - 1.0, qx + 1.0, qy - 0.625, qy + 0.625, Z_PCB1, Z_PCB1 + 0.6))

# ---------------- checks ----------------
print("\n[checks]")
print("  front vol", round(front.Volume, 1), "back vol", round(back.Volume, 1))
def clash(shape, container, label):
    remain = shape.cut(container).Volume
    v = shape.Volume - remain
    print(f"  {label}: overlap {v:.3f} mm3")
    return v

clash(pcb, front, "pcb vs front cover")
for i, c in enumerate(comps):
    clash(c, front, f"comp{i} vs front")
clash(pcb, back, "pcb vs back cover")
for i, c in enumerate(comps):
    clash(c, back, f"comp{i} vs back")

# ---------------- export ----------------
print("\n[export]")
def export(shape, name):
    m = Part.meshFromShape if False else None
    import MeshPart, Mesh
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02, AngularDeflection=0.25, Relative=False)
    mesh.write(os.path.join(OUT, name + '.stl'))
    shape.exportStep(os.path.join(OUT, name + '.step'))
    print("  ", name, "tris", mesh.CountFacets, "solids", len(shape.Solids))

export(front, 'front_cover')
export(pcb, 'pcb')
compall = comps[0]
for c in comps[1:]:
    compall = compall.fuse(c)
export(compall, 'comps')
export(back, 'back_cover')
# lay caps out flat, flange down, for printing
capset = None
for i, c in enumerate(caps):
    cc = c.copy()
    bb = cc.BoundBox
    cc.translate(FreeCAD.Vector(0, 0, -bb.ZMin))
    # mirror so flange is at the bottom
    cc = cc.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0))
    bb2 = cc.BoundBox
    cc.translate(FreeCAD.Vector(-bb2.XMin + i * 8.0, -bb2.YMin, -bb2.ZMin))
    capset = cc if capset is None else capset.fuse(cc)
export(capset, 'buttons')

# assembly
asm = front.fuse(back)
asm = asm.fuse(pcb)
for c in comps:
    asm = asm.fuse(c)
asm.exportStep(os.path.join(OUT, 'assembly.step'))
import MeshPart
mesh = MeshPart.meshFromShape(Shape=asm, LinearDeflection=0.05, AngularDeflection=0.4, Relative=False)
mesh.write(os.path.join(OUT, 'assembly.stl'))
print("  assembly tris", mesh.CountFacets)

# preview placement copies
front.exportStep(os.path.join(OUT, 'front_cover.step'))
print("\ndone in", round(time.time() - t0, 1), "s")
