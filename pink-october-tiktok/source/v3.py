"""Design 3 — frosted-glass panel 'FOR ME'."""
import sys, pickle, math
import numpy as np, cv2
from mg import *

DUR = 12.0
ORG = (540, 600)
E = pickle.load(open('l3/layers.pkl', 'rb'))
plate = np.load('l3/plate.npy')
panel = np.load('l3/panel.npy')


def mk(k, pad=PAD):
    rgb, a, (x0, y0, x1, y1) = E[k]
    fr = np.zeros((H, W, 3), np.float32); fa = np.zeros((H, W), np.float32)
    fr[y0:y1, x0:x1] = rgb; fa[y0:y1, x0:x1] = a
    return Layer(fr, fa, (x0, y0, x1, y1), pad), fa


L, A = {}, {}
for k in E:
    L[k], A[k] = mk(k, 120 if k == 'pill' else PAD)
forme = L['for_me'].letters(min_gap=4)
pink_l = L['pink'].letters(6)
x0, y0, x1, y1 = L['pink'].bbox
glow_bb = (x0 - 80, y0 - 60, x1 + 80, y1 + 60)
_g = cv2.GaussianBlur(A['pink'], (0, 0), 20)[glow_bb[1]:glow_bb[3], glow_bb[0]:glow_bb[2]]
pink_glow = np.clip(_g / _g.max(), 0, 1)[..., None] * np.array([1.0, 0.72, 0.84], np.float32) * 0.5


def cam_warp(m, s):
    if abs(s - 1) < 1e-4: return m
    M = np.array([[s, 0, (1 - s) * ORG[0]], [0, s, (1 - s) * ORG[1]]], np.float64)
    return cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)


def frame(t):
    cv = np.empty((H, W, 3), np.float32)
    s = 1 + 0.16 * (1 - out_cubic(prog(t, 0, 11.4)))
    blur = 18 * (1 - in_out_sine(prog(t, 0, 2.6)))
    bright = 0.3 + 0.7 * out_cubic(prog(t, 0, 0.9))
    draw_plate(cv, plate, s=s, blur=blur, bright=bright, origin=ORG)

    # light gliding across the frosted glass
    for t0 in (2.9, 9.0):
        p = prog(t, t0, 1.5)
        if 0 < p < 1:
            sheen(cv, cam_warp(panel, s), in_out_sine(p), angle=-62, width=95, strength=0.2)
    # satin sheen along the ribbon outside the glass
    p = prog(t, 6.6, 1.7)
    if 0 < p < 1:
        pk = ((cv[..., 0] > 0.6) & (cv[..., 0] - cv[..., 1] > 0.18) & (cv[..., 2] - cv[..., 1] > 0.05)).astype(np.float32)
        pk = cv2.GaussianBlur(pk, (0, 0), 2) * (1 - cam_warp(panel, s))
        sheen(cv, pk, in_out_sine(p), angle=-75, width=150, strength=0.25)

    cam = cv
    cv = new_layer_canvas()

    p = prog(t, 0.2, 1.2)
    L['logo'].draw(cv, opacity=min(1, p * 4), ty=8 * (1 - out_cubic(p)),
                   wipe=(0, in_out_cubic(p), 70, L['logo'].bbox))

    for k, t0 in (('pink_oct', 0.55), ('arabic', 0.75)):
        p = prog(t, t0, 0.9); e = out_quart(p)
        L[k].draw(cv, opacity=e, ty=-18 * (1 - e), blur=5 * (1 - e))

    # FOR ME: letters land from slightly larger, out of focus
    for i, l in enumerate(forme):
        p = prog(t, 0.95 + i * 0.1, 0.9); e = out_expo(p)
        l.draw(cv, opacity=min(1, p * 2.2), s=1 + 0.35 * (1 - e), blur=12 * (1 - e))

    # promo pill pops in, then its contents
    p = prog(t, 1.6, 0.75)
    if p > 0:
        L['pill'].draw(cv, opacity=min(1, p * 2.5), s=0.82 + 0.18 * out_back(p, 1.6))
    p = prog(t, 1.85, 0.6); e = out_cubic(p)
    L['promo'].draw(cv, opacity=e, tx=-16 * (1 - e))
    p = prog(t, 1.95, 0.45)
    L['divider'].draw(cv, wipe=(90, out_cubic(p), 10, L['divider'].bbox))
    pcx = (L['pink'].bbox[0] + L['pink'].bbox[2]) / 2
    for i, l in enumerate(pink_l):
        p = prog(t, 2.0 + i * 0.08, 0.7); e = out_cubic(p)
        l.draw(cv, opacity=e, tx=(l.cx - pcx) * 0.5 * (1 - e), blur=8 * (1 - e))

    composite_camera(cam, cv, s=s, origin=ORG)
    cv = cam
    g = math.sin(math.pi * prog(t, 4.6, 2.2)) ** 2
    if g > 0.001:
        X0, Y0, X1, Y1 = glow_bb
        cv[Y0:Y1, X0:X1] = 1 - (1 - cv[Y0:Y1, X0:X1]) * (1 - pink_glow * g)
    return cv


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        for t in map(float, sys.argv[2:]):
            cv2.imwrite(f'l3/f_{t:05.2f}.png', to_u8(frame(t))[:, :, ::-1])
    else:
        w = Writer(sys.argv[1])
        for i in range(int(DUR * FPS)):
            w.write(frame(i / FPS))
        w.close()
