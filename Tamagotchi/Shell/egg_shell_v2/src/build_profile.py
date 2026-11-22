#!/usr/bin/env python3
"""Board silhouette -> smoothed shell-frame profiles with exact normal offsets."""
import json, math, sys
sys.path.insert(0, 'work')
src = open('work/parse_pcb.py').read().split("def main()")[0]
ns = {}
exec(src, ns)
tokenize, parse, find_all, get = ns['tokenize'], ns['parse'], ns['find_all'], ns['get']

root = parse(tokenize(open('PCB/Tamagotchi.kicad_pcb', encoding='utf-8').read()))[0]
curves = []
for c in root:
    if isinstance(c, list) and c and c[0] == 'gr_curve':
        l = get(c, 'layer')
        if l and l[1] == 'Edge.Cuts':
            p = get(c, 'pts')
            curves.append([(float(x[1]), float(x[2])) for x in p[1:] if isinstance(x, list) and x[0] == 'xy'])

n = len(curves)
used = [False] * n
chain = []
used[0] = True
chain.append(list(curves[0]))
for _ in range(n - 1):
    end = chain[-1][3]
    best = None
    bd = 1e9
    for j in range(n):
        if used[j]:
            continue
        for rev in (False, True):
            p = curves[j][3] if rev else curves[j][0]
            d = math.dist(end, p)
            if d < bd:
                bd, best = d, (j, rev)
    j, rev = best
    used[j] = True
    c = list(curves[j])
    chain.append(c[::-1] if rev else c)

CX, CY = 145.781, 103.531
NP = 20
pts = []
for seg in chain:
    for k in range(NP):
        t = k / NP
        mt = 1 - t
        x = mt**3*seg[0][0] + 3*mt*mt*t*seg[1][0] + 3*mt*t*t*seg[2][0] + t**3*seg[3][0]
        y = mt**3*seg[0][1] + 3*mt*mt*t*seg[1][1] + 3*mt*t*t*seg[2][1] + t**3*seg[3][1]
        pts.append((x - CX, CY - y))


def area(p):
    return sum(p[i][0]*p[(i+1) % len(p)][1] - p[(i+1) % len(p)][0]*p[i][1] for i in range(len(p))) / 2


if area(pts) < 0:
    pts = pts[::-1]

# smooth (periodic moving average, several passes)
def smooth(p, win, passes):
    for _ in range(passes):
        m = len(p)
        out = []
        for i in range(m):
            acc = [0.0, 0.0]
            for k in range(-win, win + 1):
                q = p[(i + k) % m]
                acc[0] += q[0]; acc[1] += q[1]
            out.append((acc[0] / (2*win+1), acc[1] / (2*win+1)))
        p = out
    return p

pts = smooth(pts, 6, 3)

# resample by arc length
def resample(p, m):
    n = len(p)
    seglen = [math.dist(p[i], p[(i+1) % n]) for i in range(n)]
    total = sum(seglen)
    step = total / m
    out = []
    idx = 0
    acc = 0.0
    for j in range(m):
        target = j * step
        while acc + seglen[idx] < target:
            acc += seglen[idx]
            idx = (idx + 1) % n
        f = (target - acc) / seglen[idx]
        a, b = p[idx], p[(idx+1) % n]
        out.append((a[0] + (b[0]-a[0])*f, a[1] + (b[1]-a[1])*f))
    return out

pts = resample(pts, 240)
A = area(pts)
print("smoothed area", round(A, 2), "perimeter", round(sum(math.dist(pts[i], pts[(i+1) % 240]) for i in range(240)), 2))


def normals(p):
    n = len(p)
    out = []
    for i in range(n):
        p0, p1 = p[i-1], p[(i+1) % n]
        tx, ty = p1[0]-p0[0], p1[1]-p0[1]
        L = math.hypot(tx, ty) or 1
        out.append((ty/L, -tx/L))
    return out

nrm = normals(pts)
out = {'board': pts, 'meta': {'cx': CX, 'cy': CY, 'area': A,
                              'bbox': [min(p[0] for p in pts), min(p[1] for p in pts),
                                       max(p[0] for p in pts), max(p[1] for p in pts)]}}
for d in (2.8, 6.0):
    o = [(pts[i][0]+nrm[i][0]*d, pts[i][1]+nrm[i][1]*d) for i in range(len(pts))]
    print(f"offset {d}: area {area(o):.2f} bbox {[round(v,2) for v in (min(q[0] for q in o),min(q[1] for q in o),max(q[0] for q in o),max(q[1] for q in o))]}")
    out[f'off{d}'] = o
json.dump(out, open('work/profile.json', 'w'))
print("saved")
