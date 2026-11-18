"""Vectorize raster logo crops into multi-color SVGs via k-means on ink pixels + potrace."""
import os
import numpy as np
from PIL import Image, ImageFilter
import potrace

SRC = 'logos'
OUT = 'logos/vec'
os.makedirs(OUT, exist_ok=True)

SCALE = 6
MAX_COLORS = 6

def load_crop(path, cut_bottom=0):
    im = Image.open(path).convert('RGB')
    if cut_bottom:
        im = im.crop((0, 0, im.width, im.height - cut_bottom))
    return im

def auto_trim(im, thresh=245):
    a = np.array(im.convert('L'))
    mask = a < thresh
    if not mask.any():
        return im
    ys, xs = np.where(mask)
    box = (max(0, xs.min()-2), max(0, ys.min()-2), min(im.width, xs.max()+3), min(im.height, ys.max()+3))
    return im.crop(box)

def kmeans(pixels, k, iters=20, seed=0):
    rng = np.random.default_rng(seed)
    centers = [pixels[rng.integers(len(pixels))]]
    for _ in range(k-1):
        d = np.min([np.abs(pixels - c).sum(axis=1) for c in centers], axis=0)
        p = d / max(d.sum(), 1e-9)
        centers.append(pixels[rng.choice(len(pixels), p=p)])
    centers = np.array(centers, dtype=float)
    for _ in range(iters):
        dist = np.abs(pixels[:, None, :] - centers[None, :, :]).sum(axis=2)
        lab = dist.argmin(axis=1)
        new = centers.copy()
        for i in range(k):
            if (lab == i).any():
                new[i] = pixels[lab == i].mean(axis=0)
        if np.allclose(new, centers, atol=1):
            centers = new
            break
        centers = new
    return centers, lab

def trace_paths(m):
    bmp = potrace.Bitmap(~m)
    plist = bmp.trace(turdsize=12, alphamax=1.0, opticurve=1, opttolerance=0.25)
    parts = []
    for curve in plist:
        s = curve.start_point
        seg = [f"M{s.x:.1f},{s.y:.1f}"]
        for sgm in curve.segments:
            if sgm.is_corner:
                cc, e = sgm.c, sgm.end_point
                seg.append(f"L{cc.x:.1f},{cc.y:.1f}L{e.x:.1f},{e.y:.1f}")
            else:
                c1, c2, e = sgm.c1, sgm.c2, sgm.end_point
                seg.append(f"C{c1.x:.1f},{c1.y:.1f} {c2.x:.1f},{c2.y:.1f} {e.x:.1f},{e.y:.1f}")
        seg.append("Z")
        parts.append("".join(seg))
    return "".join(parts)

def vectorize(name, cut_bottom=0):
    im = load_crop(f'{SRC}/src_{name}.png', cut_bottom)
    im = auto_trim(im)
    big = im.resize((im.width*SCALE, im.height*SCALE), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
    a = np.array(big).astype(int)
    flat = a.reshape(-1, 3)
    dist_white = 255*3 - flat.sum(axis=1)
    ink = dist_white > 150
    pix = flat[ink]
    if len(pix) < 50:
        print(name, 'no ink!')
        return None
    centers, lab = kmeans(pix, MAX_COLORS)
    counts = np.bincount(lab, minlength=MAX_COLORS)
    h, w = a.shape[:2]
    paths = []
    for i, c in enumerate(centers):
        if counts[i] < 60:
            continue
        d = np.abs(flat - c).sum(axis=1)
        m = ((d < 165) & ink).reshape(h, w)
        if m.sum() < 60:
            continue
        dp = trace_paths(m)
        if dp:
            hexc = '#%02x%02x%02x' % tuple(int(x) for x in c)
            paths.append((hexc, int(counts[i]), dp))
    body = "".join(f'<path fill="{h}" fill-rule="nonzero" d="{d}"/>' for h, _, d in paths)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'width="{w}" height="{h}">{body}</svg>')
    with open(f'{OUT}/{name}.svg', 'w') as f:
        f.write(svg)
    print(f'{name}: {im.size} -> layers: {[(h, c) for h, c, _ in paths]}')
    return f'{OUT}/{name}.svg'

if __name__ == '__main__':
    cut = 52
    for name in ['mairie_landry', 'ski_club_pv', 'peisey_nancroix', 'str',
                 'enfants_terribles', 'rpb', 'sherpa',
                 'ads', 'ffs', 'esf', 'comite_ski_savoie', 'carre_neige', 'knot4']:
        vectorize(name, cut_bottom=(cut if name in ('ads','ffs','esf','comite_ski_savoie','carre_neige','knot4') else 0))
