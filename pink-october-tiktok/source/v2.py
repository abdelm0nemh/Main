"""Design 2 — burgundy 'FOR EVERY WOMAN WE CARE ABOUT'."""
import sys, pickle, math
import numpy as np, cv2
from mg import *

DUR = 12.0
D = pickle.load(open('l2/layers.pkl', 'rb'))
bg = np.load('l2/bg.npy')

def mk(k):
    rgb, a, (x0, y0, x1, y1) = D['els'][k]
    full_rgb = np.zeros((H, W, 3), np.float32); full_a = np.zeros((H, W), np.float32)
    full_rgb[y0:y1, x0:x1] = rgb; full_a[y0:y1, x0:x1] = a
    return Layer(full_rgb, full_a, (x0, y0, x1, y1))

L = {k: mk(k) for k in D['els']}
px = D['pbb']
ph_rgb = np.zeros((H, W, 3), np.float32); ph_rgb[px[1]:px[3], px[0]:px[2]] = D['photo']
ph_a = np.zeros((H, W), np.float32); ph_a[px[1]:px[3], px[0]:px[2]] = 1
photo = Layer(ph_rgb, ph_a, px, pad=120)
woman_l = L['woman'].letters(); about_l = L['about'].letters(); pink_l = L['pink'].letters(6)

# ribbon masks for satin sheen (full canvas)
rib_mask = np.zeros((H, W), np.float32)
for k in ('ribbon_tr', 'ribbon_bl'):
    _, a, (x0, y0, x1, y1) = D['els'][k]; rib_mask[y0:y1, x0:x1] = np.maximum(rib_mask[y0:y1, x0:x1], a)


_pa = np.zeros((H, W), np.float32)
_r, _a, (_x0, _y0, _x1, _y1) = D['els']['pink']; _pa[_y0:_y1, _x0:_x1] = _a
pink_glow_bb = (_x0 - 90, _y0 - 70, _x1 + 90, _y1 + 70)
_g = cv2.GaussianBlur(_pa, (0, 0), 22)[pink_glow_bb[1]:pink_glow_bb[3], pink_glow_bb[0]:pink_glow_bb[2]]
pink_glow = np.clip(_g / _g.max(), 0, 1)[..., None] * np.array([0.95, 0.55, 0.70], np.float32) * 0.45


def rise_letters(cv, letters, t, t0, stagger, dur, dist, bbox):
    for i, l in enumerate(letters):
        p = prog(t, t0 + i * stagger, dur)
        if p <= 0: continue
        e = out_quart(p)
        l.draw(cv, opacity=min(1, p * 2.5), ty=dist * (1 - e), clip=(0, bbox[1] - 4, W, bbox[3] + 6))


def frame(t):
    cv = bg.copy()

    # --- ribbons: slide in from their corners, then breathe outward a few px ---
    for k, t0, sgn in (('ribbon_tr', 0.0, (1, -1)), ('ribbon_bl', 0.15, (-1, 1))):
        p = prog(t, t0, 1.3); e = out_cubic(p)
        breathe = 7 * (1 - math.cos(2 * math.pi * max(0, t - t0 - 1.3) / 4.2)) / 2
        off = 340 * (1 - e) + breathe
        L[k].draw(cv, opacity=min(1, p * 3), tx=sgn[0] * off, ty=sgn[1] * off,
                  rot=sgn[0] * 8 * (1 - e))
    for t0 in (1.7, 7.2):
        p = prog(t, t0, 1.4)
        if 0 < p < 1:
            sheen(cv, rib_mask, in_out_sine(p), angle=-35, width=110, strength=0.28)

    # --- logo: handwriting-style wipe ---
    p = prog(t, 0.1, 1.2)
    L['logo'].draw(cv, opacity=min(1, p * 4), ty=8 * (1 - out_cubic(p)),
                   wipe=(0, in_out_cubic(p), 70, L['logo'].bbox))

    # --- FOR EVERY ---
    p = prog(t, 0.4, 0.9); e = out_quart(p)
    L['for_every'].draw(cv, opacity=e, tx=-40 * (1 - e), wipe=(0, e, 90, L['for_every'].bbox))
    # --- WOMAN: letters rise out of a mask ---
    rise_letters(cv, woman_l, t, 0.6, 0.07, 0.85, 115, L['woman'].bbox)

    # --- photo: curtain reveal top->bottom with inner zoom-out ---
    p = prog(t, 1.05, 1.15); e = in_out_cubic(p)
    if p > 0:
        zs = 1 + 0.24 * (1 - out_cubic(prog(t, 1.05, 9.0)))
        clip = (px[0], px[1], px[2], px[1] + (px[3] - px[1]) * e)
        photo.draw(cv, s=zs, origin=((px[0] + px[2]) / 2, px[1] + 0.38 * (px[3] - px[1])), clip=clip)
        # a hairline of light riding the reveal edge
        if 0 < p < 1:
            y = int(px[1] + (px[3] - px[1]) * e)
            y0, y1 = max(px[1], y - 2), min(px[3], y + 1)
            cv[y0:y1, px[0]:px[2]] = cv[y0:y1, px[0]:px[2]] * 0.4 + 0.6

    # --- WE CARE / ABOUT ---
    p = prog(t, 2.0, 0.9); e = out_quart(p)
    L['we_care'].draw(cv, opacity=e, tx=40 * (1 - e), wipe=(180, e, 90, L['we_care'].bbox))
    rise_letters(cv, about_l, t, 2.2, 0.07, 0.85, 130, L['about'].bbox)

    # --- promo block ---
    p = prog(t, 3.1, 0.9); e = out_cubic(p)
    L['line_l'].draw(cv, wipe=(180, e, 40, L['line_l'].bbox))
    L['line_r'].draw(cv, wipe=(0, e, 40, L['line_r'].bbox))
    p = prog(t, 3.3, 0.7); e = out_cubic(p)
    L['promo'].draw(cv, opacity=e, ty=14 * (1 - e))
    cx = (L['pink'].bbox[0] + L['pink'].bbox[2]) / 2
    for i, l in enumerate(pink_l):
        p = prog(t, 3.55 + i * 0.09, 0.8); e = out_cubic(p)
        l.draw(cv, opacity=e, tx=(l.cx - cx) * 0.6 * (1 - e), blur=10 * (1 - e))

    # --- footer ---
    for k, t0 in (('pink_oct', 4.3), ('arabic', 4.55)):
        p = prog(t, t0, 0.9); e = out_quart(p)
        L[k].draw(cv, opacity=e, ty=22 * (1 - e), blur=4 * (1 - e))
    # --- soft pink glow pulse behind the code (CTA emphasis) ---
    g = math.sin(math.pi * prog(t, 6.0, 2.2)) ** 2
    if g > 0.001:
        x0, y0, x1, y1 = pink_glow_bb
        cv[y0:y1, x0:x1] = 1 - (1 - cv[y0:y1, x0:x1]) * (1 - pink_glow * g)
    return cv


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        for t in map(float, sys.argv[2:]):
            cv2.imwrite(f'l2/f_{t:05.2f}.png', to_u8(frame(t))[:, :, ::-1])
    else:
        w = Writer(sys.argv[1])
        n = int(DUR * FPS)
        for i in range(n):
            w.write(frame(i / FPS))
        w.close()
