#!/usr/bin/env python3
"""Multi-part orthographic STL renderer with per-part colour + z-buffer."""
import sys, struct, math
import numpy as np
from PIL import Image, ImageDraw


def load_stl(path):
    d = open(path, 'rb').read()
    if d[:5] == b'solid' and b'facet' in d[:3000]:
        import re
        v = re.findall(rb'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)', d)
        return np.array(v, dtype=float).reshape(-1, 3, 3)
    n = struct.unpack('<I', d[80:84])[0]
    rec = np.frombuffer(d[84:84 + n * 50], dtype=np.uint8).reshape(n, 50)
    return rec[:, 12:48].copy().view('<f4').reshape(n, 3, 3).astype(float)


def rot_matrix(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def view_matrix(tilt, spin, yaw=0.0):
    """R = Rx(tilt) @ Ry(yaw) @ Rz(spin)"""
    a = math.radians(tilt); b = math.radians(spin); c = math.radians(yaw)
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(c), 0, math.sin(c)], [0, 1, 0], [-math.sin(c), 0, math.cos(c)]])
    Rz = np.array([[math.cos(b), -math.sin(b), 0], [math.sin(b), math.cos(b), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def render(parts, out, size=1000, rot=(0, 0, 0), zoom=None, bg=(250, 250, 252),
           clip_z=None, clip_y=None, clip_x=None, keep=None, view=None):
    """parts: list of (tris, rgb). view=(tilt,spin) alternative to rot"""
    R = view_matrix(*view) if view is not None else rot_matrix(*rot)
    allt = []
    for tris, col in parts:
        if tris is None or len(tris) == 0:
            continue
        v = tris.reshape(-1, 3) @ R.T
        t = v.reshape(-1, 3, 3)
        allt.append((t, np.array(col, float)))
    allv = np.concatenate([t.reshape(-1, 3) for t, _ in allt])
    mn, mx = allv.min(0), allv.max(0)
    ctr = (mn + mx) / 2
    span = max((mx - mn)[0], (mx - mn)[1]) if zoom is None else zoom
    k = (size * 0.9) / span
    img = np.tile(np.array(bg, float), (size, size, 1))
    zbuf = np.full((size, size), -1e18, np.float32)
    light = np.array([0.35, 0.42, 0.84])
    light /= np.linalg.norm(light)
    for t, col in allt:
        # clipping
        m = np.ones(len(t), bool)
        if clip_z is not None:
            c = t.mean(1)[:, 2]
            m &= (c >= clip_z[0]) & (c <= clip_z[1])
        if clip_y is not None:
            c = t.mean(1)[:, 1]
            m &= (c >= clip_y[0]) & (c <= clip_y[1])
        if clip_x is not None:
            c = t.mean(1)[:, 0]
            m &= (c >= clip_x[0]) & (c <= clip_x[1])
        t = t[m]
        if len(t) == 0:
            continue
        px = (t[:, :, 0] - ctr[0]) * k + size / 2
        py = -(t[:, :, 1] - ctr[1]) * k + size / 2
        dep = t[:, :, 2]
        nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        nl = np.linalg.norm(nrm, axis=1)
        nl[nl == 0] = 1
        nrm = nrm / nl[:, None]
        shade = 0.34 + 0.66 * np.abs(nrm @ light)
        for i in range(len(t)):
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
            mm = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not mm.any():
                continue
            z = w0 * dep[i, 0] + w1 * dep[i, 1] + w2 * dep[i, 2]
            sub = zbuf[iy0:iy1 + 1, ix0:ix1 + 1]
            upd = mm & (z > sub)
            if not upd.any():
                continue
            sub[upd] = z[upd]
            img[iy0:iy1 + 1, ix0:ix1 + 1][upd] = col * shade[i]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out)
    return out


if __name__ == '__main__':
    import json
    spec = json.load(open(sys.argv[1]))
    render([(load_stl(p), c) for p, c in spec['parts']], spec['out'],
           size=spec.get('size', 1000), rot=tuple(spec.get('rot', (0, 0, 0))),
           zoom=spec.get('zoom'), clip_z=spec.get('clip_z'), clip_y=spec.get('clip_y'),
           clip_x=spec.get('clip_x'))
    print('wrote', spec['out'])
