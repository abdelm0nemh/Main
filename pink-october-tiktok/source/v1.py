"""Design 1 — four-panel grid 'FOR EVERY WOMAN WE STAND WITH'."""
import sys, pickle, math
import numpy as np, cv2
from mg import *

DUR = 12.0
ORG = (540, 900)
E = pickle.load(open('l1/layers.pkl', 'rb'))
plate = np.load('l1/plate.npy')


def mk(k):
    rgb, a, (x0, y0, x1, y1) = E[k]
    fr = np.zeros((H, W, 3), np.float32); fa = np.zeros((H, W), np.float32)
    fr[y0:y1, x0:x1] = rgb; fa[y0:y1, x0:x1] = a
    return Layer(fr, fa, (x0, y0, x1, y1)), fa


L, A = {}, {}
for k in E:
    L[k], A[k] = mk(k)
words = L['we_stand'].letters(min_gap=22)          # WE / STAND / WITH
fe_letters = L['for_every'].letters(min_gap=2)
pink_l = L['pink'].letters(6)
band = np.zeros((H, W), np.float32); band[800:1110] = 1

x0, y0, x1, y1 = L['pink'].bbox
glow_bb = (x0 - 80, y0 - 60, x1 + 80, y1 + 60)
_g = cv2.GaussianBlur(A['pink'], (0, 0), 20)[glow_bb[1]:glow_bb[3], glow_bb[0]:glow_bb[2]]
pink_glow = np.clip(_g / _g.max(), 0, 1)[..., None] * np.array([1.0, 0.75, 0.85], np.float32) * 0.5


def frame(t):
    cv = np.empty((H, W, 3), np.float32)
    # camera: focus-pull + slow pull-back that settles exactly on the original framing
    s = 1 + 0.10 * (1 - out_cubic(prog(t, 0, 11.4)))
    blur = 16 * (1 - in_out_sine(prog(t, 0, 2.5)))
    bright = 0.3 + 0.7 * out_cubic(prog(t, 0, 0.9))
    draw_plate(cv, plate, s=s, blur=blur, bright=bright, origin=ORG)

    # satin sheen running along the ribbon
    for t0 in (3.3, 8.4):
        p = prog(t, t0, 1.6)
        if 0 < p < 1:
            pk = ((cv[..., 0] > 0.68) & (cv[..., 0] - cv[..., 1] > 0.2) & (cv[..., 2] - cv[..., 1] > 0.03)).astype(np.float32) * band
            pk = cv2.GaussianBlur(pk, (0, 0), 2)
            sheen(cv, pk, in_out_sine(p), angle=-25, width=120, strength=0.22)

    cam = cv
    cv = new_layer_canvas()
    # logo: handwriting wipe
    p = prog(t, 0.2, 1.2)
    L['logo'].draw(cv, opacity=min(1, p * 4), ty=8 * (1 - out_cubic(p)),
                   wipe=(0, in_out_cubic(p), 70, L['logo'].bbox))

    # FOR EVERY WOMAN: letters track in from wide spacing
    cx = (L['for_every'].bbox[0] + L['for_every'].bbox[2]) / 2
    p = prog(t, 0.55, 1.1); e = out_expo(p)
    for l in fe_letters:
        l.draw(cv, opacity=min(1, p * 1.8), tx=(l.cx - cx) * 0.35 * (1 - e), blur=6 * (1 - e))

    # WE STAND WITH: words rise out of a mask
    bb = L['we_stand'].bbox
    for i, wd in enumerate(words):
        p = prog(t, 0.85 + i * 0.16, 0.95); e = out_quart(p)
        if p > 0:
            wd.draw(cv, opacity=min(1, p * 2.5), ty=120 * (1 - e), clip=(0, bb[1] - 6, W, bb[3] + 4))

    # promo code
    p = prog(t, 1.5, 0.7); e = out_cubic(p)
    L['promo'].draw(cv, opacity=e, tx=-20 * (1 - e))
    p = prog(t, 1.65, 0.5)
    L['divider'].draw(cv, wipe=(90, out_cubic(p), 10, L['divider'].bbox))
    pcx = (L['pink'].bbox[0] + L['pink'].bbox[2]) / 2
    for i, l in enumerate(pink_l):
        p = prog(t, 1.75 + i * 0.08, 0.7); e = out_cubic(p)
        l.draw(cv, opacity=e, tx=(l.cx - pcx) * 0.5 * (1 - e), blur=8 * (1 - e))

    # footer
    for k, t0 in (('pink_oct', 1.95), ('arabic', 2.15)):
        p = prog(t, t0, 0.9); e = out_quart(p)
        L[k].draw(cv, opacity=e, ty=22 * (1 - e), blur=4 * (1 - e))

    composite_camera(cam, cv, s=s, origin=ORG)
    cv = cam
    # CTA glow pulse on the code
    g = math.sin(math.pi * prog(t, 5.4, 2.2)) ** 2
    if g > 0.001:
        X0, Y0, X1, Y1 = glow_bb
        cv[Y0:Y1, X0:X1] = 1 - (1 - cv[Y0:Y1, X0:X1]) * (1 - pink_glow * g)
    return cv


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        for t in map(float, sys.argv[2:]):
            cv2.imwrite(f'l1/f_{t:05.2f}.png', to_u8(frame(t))[:, :, ::-1])
    else:
        w = Writer(sys.argv[1])
        for i in range(int(DUR * FPS)):
            w.write(frame(i / FPS))
        w.close()
