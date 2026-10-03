"""Tiny layer-based motion-graphics compositor (numpy + OpenCV -> ffmpeg)."""
import math, subprocess
import numpy as np, cv2

W, H, FPS = 1080, 1920, 30


def load(path):
    return cv2.imread(path, cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32) / 255


# ---------- easing ----------
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x

def prog(t, t0, dur):
    return clamp01((t - t0) / dur)

def out_cubic(p): return 1 - (1 - p) ** 3
def out_quart(p): return 1 - (1 - p) ** 4
def out_expo(p): return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)
def in_out_cubic(p): return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2
def in_out_sine(p): return -(math.cos(math.pi * p) - 1) / 2
def out_back(p, s=1.2):
    p -= 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


# ---------- matting helpers ----------
def white_matte(I, P):
    """alpha for pure-white overlay: I = a*1 + (1-a)*P."""
    a = (I - P) / np.maximum(1 - P, 1e-3)
    return np.clip(a.max(2), 0, 1)

def unpremult(I, P, a):
    """foreground colour so that a*F + (1-a)*P == I."""
    am = np.maximum(a, 1e-3)[..., None]
    return np.clip((I - (1 - a[..., None]) * P) / am, 0, 1)

def inpaint(I, mask, r=5, method=cv2.INPAINT_TELEA):
    u8 = (np.clip(I, 0, 1) * 255 + .5).astype(np.uint8)
    out = cv2.inpaint(u8, mask.astype(np.uint8) * 255, r, method)
    return out.astype(np.float32) / 255

def dilate(m, k):
    return cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))) > 0


# ---------- layers ----------
PAD = 60

class Layer:
    """Premultiplied RGBA crop placed at bbox (x0,y0,x1,y1) in canvas space."""

    def __init__(self, rgb, alpha, bbox, pad=PAD):
        x0, y0, x1, y1 = bbox
        self.bbox = bbox
        self.pad = pad
        h, w = y1 - y0, x1 - x0
        self.rgba = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
        a = alpha[y0:y1, x0:x1]
        self.rgba[pad:pad + h, pad:pad + w, :3] = rgb[y0:y1, x0:x1] * a[..., None]
        self.rgba[pad:pad + h, pad:pad + w, 3] = a
        self.ox, self.oy = x0 - pad, y0 - pad  # canvas position of crop origin
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2

    @staticmethod
    def white(alpha, bbox, pad=PAD):
        return Layer(np.ones(alpha.shape + (3,), np.float32), alpha, bbox, pad)

    def sub(self, bbox):
        """Layer restricted to a sub-rectangle (canvas coords)."""
        L = Layer.__new__(Layer)
        L.bbox, L.pad = bbox, self.pad
        x0, y0, x1, y1 = bbox
        sx0, sy0 = x0 - self.ox, y0 - self.oy
        sx1, sy1 = x1 - self.ox, y1 - self.oy
        p = self.pad
        L.rgba = np.zeros((y1 - y0 + 2 * p, x1 - x0 + 2 * p, 4), np.float32)
        L.rgba[p:-p, p:-p] = self.rgba[sy0:sy1, sx0:sx1]
        L.ox, L.oy = x0 - p, y0 - p
        L.cx, L.cy = (x0 + x1) / 2, (y0 + y1) / 2
        return L

    def letters(self, min_gap=3):
        """Split horizontally into glyph groups by empty columns."""
        x0, y0, x1, y1 = self.bbox
        a = self.rgba[self.pad:-self.pad, self.pad:-self.pad, 3]
        on = a.max(0) > 0.02
        spans, s = [], None
        for i, v in enumerate(list(on) + [False]):
            if v and s is None: s = i
            if not v and s is not None:
                spans.append([s, i]); s = None
        merged = []
        for sp in spans:
            if merged and sp[0] - merged[-1][1] < min_gap: merged[-1][1] = sp[1]
            else: merged.append(sp)
        return [self.sub((x0 + a_, y0, x0 + b_, y1)) for a_, b_ in merged]

    def draw(self, cv, opacity=1.0, tx=0., ty=0., s=1.0, rot=0.0, blur=0.0,
             origin=None, clip=None, wipe=None, sx=None, sy=None, tint=None):
        if opacity <= 0.001: return
        src = self.rgba
        if blur > 0.3:
            k = int(blur * 3) * 2 + 1
            src = cv2.GaussianBlur(src, (k, k), blur)
        ox_, oy_ = origin if origin else (self.cx, self.cy)
        sx_ = s if sx is None else sx
        sy_ = s if sy is None else sy
        # affine from crop coords -> canvas coords
        c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        # canvas = R*S*(p_canvas0 - origin) + origin + t,  p_canvas0 = p_crop + (ox,oy)
        A = np.array([[c * sx_, -sn * sy_], [sn * sx_, c * sy_]], np.float64)
        b = -A @ np.array([ox_, oy_]) + np.array([ox_ + tx, oy_ + ty]) + A @ np.array([self.ox, self.oy])
        h, w = src.shape[:2]
        corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], np.float64) @ A.T + b
        X0 = max(int(math.floor(corners[:, 0].min())), 0)
        Y0 = max(int(math.floor(corners[:, 1].min())), 0)
        X1 = min(int(math.ceil(corners[:, 0].max())) + 1, W)
        Y1 = min(int(math.ceil(corners[:, 1].max())) + 1, H)
        if clip:
            X0, Y0 = max(X0, int(clip[0])), max(Y0, int(clip[1]))
            X1, Y1 = min(X1, int(math.ceil(clip[2]))), min(Y1, int(math.ceil(clip[3])))
        if X1 <= X0 or Y1 <= Y0: return
        M = np.hstack([A, b[:, None]])
        M[:, 2] -= [X0, Y0]
        out = cv2.warpAffine(src, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        if wipe is not None:
            out = out * wipe_mask(wipe, X0, Y0, X1, Y1)[..., None]
        if tint is not None:
            out[..., :3] = out[..., :3] * (1 - tint[1]) + np.array(tint[0], np.float32) * out[..., 3:4] * tint[1]
        out *= opacity
        region = cv[Y0:Y1, X0:X1]
        region *= (1 - out[..., 3:4])
        region += out[..., :region.shape[2]]


def wipe_mask(wipe, X0, Y0, X1, Y1):
    """wipe=(angle_deg, p, feather, (x0,y0,x1,y1) extent) -> reveal mask, p in 0..1."""
    ang, p, feather, ext = wipe
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    e = np.array([[ext[0], ext[1]], [ext[2], ext[1]], [ext[0], ext[3]], [ext[2], ext[3]]], np.float32)
    proj = e[:, 0] * dx + e[:, 1] * dy
    lo, hi = proj.min() - feather, proj.max()
    edge = lo + (hi - lo + feather) * p
    v = (edge - (xs * dx + ys * dy)) / max(feather, 1e-3)
    return np.clip(v, 0, 1)


def draw_plate(cv, plate, s=1.0, tx=0., ty=0., origin=(W / 2, H / 2), blur=0.0, bright=1.0):
    src = plate
    if abs(s - 1) > 1e-4 or abs(tx) > 1e-3 or abs(ty) > 1e-3:
        M = np.array([[s, 0, (1 - s) * origin[0] + tx], [0, s, (1 - s) * origin[1] + ty]], np.float64)
        src = cv2.warpAffine(plate, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if blur > 0.3:
        k = int(blur * 3) * 2 + 1
        src = cv2.GaussianBlur(src, (k, k), blur)
    cv[:] = src * bright


def sheen(cv, mask, p, angle=-30, width=180, strength=0.22, color=(1, 1, 1)):
    """Specular light band sweeping across masked area. p: 0..1 position."""
    if p <= 0 or p >= 1: return
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    proj = xs * dx + ys * dy
    lo, hi = proj.min() - width, proj.max() + width
    c = lo + (hi - lo) * p
    band = np.exp(-((proj - c) / width) ** 2) * strength
    band = band * mask
    cv += (np.array(color, np.float32) - cv) * band[..., None]


class Writer:
    def __init__(self, path, fps=FPS):
        self.p = subprocess.Popen(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
             '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
             '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
             '-shortest', '-map', '0:v', '-map', '1:a',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-profile:v', 'high',
             '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
             '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', path],
            stdin=subprocess.PIPE)

    def write(self, cv):
        f = (np.clip(cv, 0, 1) * 255 + .5).astype(np.uint8)
        self.p.stdin.write(f.tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()


def to_u8(cv):
    return (np.clip(cv, 0, 1) * 255 + .5).astype(np.uint8)


def nc_fill(I, mask, sigmas=(1.5, 3, 6, 12, 24, 48)):
    """Fill masked pixels by multi-scale normalised convolution (smooth, artifact-free)."""
    known = (~mask).astype(np.float32)
    out = I.copy()
    todo = mask.copy()
    for s in sigmas:
        num = cv2.GaussianBlur(I * known[..., None], (0, 0), s)
        den = cv2.GaussianBlur(known, (0, 0), s)
        ok = todo & (den > 0.18)
        out[ok] = num[ok] / den[ok][:, None]
        todo &= ~ok
    if todo.any():
        num = cv2.GaussianBlur(I * known[..., None], (0, 0), 96); den = cv2.GaussianBlur(known, (0, 0), 96)
        out[todo] = num[todo] / np.maximum(den[todo], 1e-4)[:, None]
    return out


def text_mask(I, roi, hi=0.12, lo=0.04, k=21, grow=3):
    """White-ish thin text via top-hat with hysteresis, inside roi (bool)."""
    mn = I.min(2)
    se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    th = mn - cv2.morphologyEx(mn, cv2.MORPH_OPEN, se)
    spread = I.max(2) - mn
    core = (th > hi) & (spread < 0.12) & roi
    weak = (th > lo) & roi
    m = core.copy()
    for _ in range(6):
        m = dilate(m, 1) & weak | m
    return dilate(m, grow) & roi


def new_layer_canvas():
    return np.zeros((H, W, 4), np.float32)


def composite_camera(cv, rgba, s=1.0, origin=(W / 2, H / 2), tx=0., ty=0.):
    """Composite a premultiplied RGBA canvas over cv with the same camera move as the plate."""
    if abs(s - 1) > 1e-4 or abs(tx) > 1e-3 or abs(ty) > 1e-3:
        M = np.array([[s, 0, (1 - s) * origin[0] + tx], [0, s, (1 - s) * origin[1] + ty]], np.float64)
        rgba = cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    cv *= (1 - rgba[..., 3:4])
    cv += rgba[..., :3]
