#!/usr/bin/env python3
"""Minimal orthographic STL renderer (numpy + Pillow)."""
import sys, struct, math
import numpy as np
from PIL import Image


def load_stl(path):
    d = open(path, 'rb').read()
    if d[:5] == b'solid' and b'facet' in d[:3000]:
        import re
        v = re.findall(rb'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)', d)
        a = np.array(v, dtype=float).reshape(-1, 3, 3)
        return a
    n = struct.unpack('<I', d[80:84])[0]
    rec = np.frombuffer(d[84:84 + n * 50], dtype=np.uint8).reshape(n, 50)
    tri = rec[:, 12:48].copy().view('<f4').reshape(n, 3, 3).astype(float)
    return tri


def rot_matrix(rx, ry, rz):
    rx, ry, rz = math.radians(rx), math.radians(ry), math.radians(rz)
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def render(tri, out, size=900, rot=(0, 0, 0), zoom=None, center=None, bg=(255, 255, 255),
           color=(200, 200, 205), edges=False, clipz=None, scale_bar=None, ortho=True):
    if clipz is not None:
        zmin, zmax = clipz
        c = tri.mean(axis=1)
        tri = tri[(c[:, 2] >= zmin) & (c[:, 2] <= zmax)]
    R = rot_matrix(*rot)
    v = tri.reshape(-1, 3) @ R.T
    tri = v.reshape(-1, 3, 3)
    mn = tri.reshape(-1, 3).min(axis=0)
    mx = tri.reshape(-1, 3).max(axis=0)
    if center is None:
        ctr = (mn + mx) / 2
    else:
        ctr = np.array(center, dtype=float)
    if ortho:
        # project x -> u, y -> v, depth z
        u = tri[:, :, 0] - ctr[0]
        w = tri[:, :, 1] - ctr[1]
        dep = tri[:, :, 2]
    else:
        raise NotImplementedError
    span = max((mx - mn)[0], (mx - mn)[1]) if zoom is None else zoom
    k = (size * 0.88) / span
    px = u * k + size / 2
    py = -w * k + size / 2
    img = np.zeros((size, size, 3), dtype=np.float32)
    img[:, :] = np.array(bg, dtype=np.float32)
    zmin, zmax = dep.min(), dep.max()
    zbuf = np.full((size, size), -1e18, dtype=np.float32)
    # lighting: from camera-ish
    light = np.array([0.35, 0.45, 0.82])
    light = light / np.linalg.norm(light)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nl = np.linalg.norm(nrm, axis=1)
    nl[nl == 0] = 1
    nrm = nrm / nl[:, None]
    shade = np.abs(nrm @ light)
    shade = 0.32 + 0.68 * shade
    for i in range(len(tri)):
        x0, x1 = px[i].min(), px[i].max()
        y0, y1 = py[i].min(), py[i].max()
        ix0, ix1 = max(int(np.floor(x0)), 0), min(int(np.ceil(x1)), size - 1)
        iy0, iy1 = max(int(np.floor(y0)), 0), min(int(np.ceil(y1)), size - 1)
        if ix0 > ix1 or iy0 > iy1:
            continue
        ax, ay = px[i, 0], py[i, 0]
        bx, by = px[i, 1], py[i, 1]
        cx, cy = px[i, 2], py[i, 2]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        xs = np.arange(ix0, ix1 + 1) + 0.5
        ys = np.arange(iy0, iy1 + 1) + 0.5
        X, Y = np.meshgrid(xs, ys)
        w0 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den
        w1 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * dep[i, 0] + w1 * dep[i, 1] + w2 * dep[i, 2]
        sub = zbuf[iy0:iy1 + 1, ix0:ix1 + 1]
        upd = m & (z > sub)
        if not upd.any():
            continue
        sub[upd] = z[upd]
        col = np.array(color, dtype=np.float32) * shade[i]
        reg = img[iy0:iy1 + 1, ix0:ix1 + 1]
        reg[upd] = col
    if edges:
        e = img.copy()
    out_img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    out_img.save(out)
    return out


if __name__ == '__main__':
    path = sys.argv[1]
    out = sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    rot = tuple(float(x) for x in sys.argv[4].split(',')) if len(sys.argv) > 4 else (0, 0, 0)
    clipz = None
    if len(sys.argv) > 5 and sys.argv[5] != '-':
        a, b = sys.argv[5].split(',')
        clipz = (float(a), float(b))
    col = (198, 202, 208)
    render(load_stl(path), out, size=size, rot=rot, clipz=clipz, color=col)
    print('wrote', out)
