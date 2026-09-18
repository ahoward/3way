#!/usr/bin/env python3
# tools/render.py — the 3WAY brand mark, generated (state lives in the repo, not a dropbox).
#
# v2: racier + female. A neon-boudoir treatment — a curvy feminine silhouette with a hip-sway
# walk, the grunge 3WAY wordmark neon-flickering, the green cursor blinking. Suggestive by
# curve + light, not by detail (clean silhouette). Outputs:
#   assets/logo.gif   512x512  animated mark
#   assets/logo.png   512x512  still (peak frame)
#   assets/morning.gif 800x450 the "she walks out at 5am" scene
#
#   python3 tools/render.py
import os, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
MAGENTA = (255, 20, 147)
HOTPINK = (255, 95, 191)
PURPLE  = (138, 43, 160)
CYAN    = (90, 220, 255)
GREEN   = (57, 255, 20)

def rng(seed): return np.random.default_rng(seed)

# ── the silhouette ──────────────────────────────────────────────────────────
# A parametric pin-up curve: for each normalized height t (0 head → 1 foot) a body half-width
# and a centerline x that sways with the hips (contrapposto). Filled as one smooth polygon,
# hair as a second blob. `sway` shifts weight hip-to-hip for the walk cycle.
def silhouette(size, sway=0.0, hair=0.0, scale=1.0, racy=0.0):
    W = H = size
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    cx, top, bot = W * 0.5, H * 0.15, H * 0.94
    span = (bot - top)

    # (t, half-width, centerline-offset) — the feminine profile. Head is drawn as a circle
    # separately (below) so the neck starts the polygon. Nipped waist, full hips, long legs.
    # offset builds the S-curve; sway animates the weight shift.
    # racy (0..1): exaggerate the hourglass (fuller bust/hips, tighter waist) + a cocked-hip
    # contrapposto lean (upper body leans one way, hips kick the other = a pin-up S).
    bust = 1 + 0.20*racy; waist = 1 - 0.28*racy; hip = 1 + 0.24*racy
    lean = 0.030*racy    # static hip-cock (added to sway)
    prof = [
        (0.115, 0.030,               0.00 - 0.010*racy),   # neck (leans back)
        (0.150, 0.088,               0.00 - 0.008*racy),   # shoulders
        (0.210, 0.108*bust,          0.005),               # bust (full)
        (0.255, 0.098*bust,          0.010),               # under-bust
        (0.360, 0.052*waist,         0.020 + 0.010*racy),  # nipped waist (tightest)
        (0.430, 0.088*hip,           0.028 + lean),        # hip rise
        (0.500, 0.140*hip,           0.032 + lean),        # hip crest (kicks out)
        (0.560, 0.150*hip,           0.030 + lean*0.9),    # seat (fullest)
        (0.650, 0.110*(1+0.12*racy), 0.018 + lean*0.5),    # thigh
        (0.760, 0.066,               0.006),               # knee
        (0.860, 0.045,               0.000),               # calf
        (0.940, 0.028,              -0.004),               # ankle
        (1.000, 0.052,              -0.006),               # heel/foot
    ]
    def curve(pts):
        ts = np.array([p[0] for p in pts]); xs = np.array([p[1] for p in pts]); os_ = np.array([p[2] for p in pts])
        tt = np.linspace(ts[0], 1, 240)
        w = np.interp(tt, ts, xs); off = np.interp(tt, ts, os_)
        s = np.sin((tt-ts[0])/(1-ts[0]) * math.pi) * sway     # weight shift peaks mid-body
        return tt, w, off + s
    tt, w, off = curve(prof)
    right, left = [], []
    for t, ww, of in zip(tt, w, off):
        y = top + t * span
        c = cx + of * span
        right.append((c + ww * span * scale, y))
        left.append((c - ww * span * scale, y))
    d.polygon(right + left[::-1], fill=255)
    # round head, sitting on the neck
    hr = 0.052 * span
    hcx = cx + off[0] * span
    hcy = top + 0.075 * span
    d.ellipse([hcx-hr, hcy-hr, hcx+hr, hcy+hr], fill=255)

    # hair — a soft rounded mane: a crown ellipse behind the head + long side-falls that sway.
    hd = ImageDraw.Draw(img)
    hcx = cx + off[0] * span
    hcy = top + 0.075 * span
    hr  = 0.052 * span
    lift = hair * 0.05 * span
    hd.ellipse([hcx-hr*1.35, hcy-hr*1.35, hcx+hr*1.35, hcy+hr*1.05], fill=255)  # rounded crown
    fall = [
        (hcx - hr*1.1, hcy),
        (hcx - hr*1.9 - lift, hcy + 0.12*span),
        (hcx - hr*1.7 - lift*1.3, hcy + 0.26*span),
        (hcx - hr*0.9, hcy + 0.30*span),
        (hcx - hr*0.4, hcy + 0.12*span),
        (hcx + hr*0.4, hcy + 0.12*span),
        (hcx + hr*0.9, hcy + 0.30*span),
        (hcx + hr*1.7 + lift*1.3, hcy + 0.26*span),
        (hcx + hr*1.9 + lift, hcy + 0.12*span),
        (hcx + hr*1.1, hcy),
    ]
    hd.polygon(fall, fill=255)
    return img

def tinted(mask, size, top_col, bot_col, rim_col):
    # vertical gradient fill + a neon rim light (cyan/pink edge glow)
    W = H = size
    grad = Image.new("RGB", (W, H))
    ga = np.zeros((H, W, 3), np.uint8)
    for y in range(H):
        f = y / H
        ga[y, :] = [int(top_col[i] + (bot_col[i]-top_col[i]) * f) for i in range(3)]
    grad = Image.fromarray(ga)
    body = Image.composite(grad, Image.new("RGB", (W, H), (0,0,0)), mask)
    # rim: dilate-minus-mask → bright edge, blurred to a glow
    edge = mask.filter(ImageFilter.MaxFilter(7))
    edge = ImageChops.subtract(edge, mask).filter(ImageFilter.GaussianBlur(2))
    rim = Image.composite(Image.new("RGB", (W,H), rim_col), Image.new("RGB",(W,H),(0,0,0)), edge)
    glow = Image.composite(Image.new("RGB", (W,H), HOTPINK), Image.new("RGB",(W,H),(0,0,0)),
                           mask.filter(ImageFilter.GaussianBlur(10))).point(lambda p:int(p*0.32))
    out = ImageChops.add(ImageChops.add(body, rim), glow)
    return out, mask

# ── grunge wordmark ─────────────────────────────────────────────────────────
def wordmark(size, text="3WAY", flick=1.0, seed=7):
    W = H = size
    fnt = ImageFont.truetype(FONT, int(size*0.265))
    layer = Image.new("L", (W, H), 0); d = ImageDraw.Draw(layer)
    bb = d.textbbox((0,0), text, font=fnt, stroke_width=0)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    tx, ty = (W-tw)//2 - bb[0], int(H*0.30) - bb[1]
    d.text((tx,ty), text, font=fnt, fill=255)
    # grunge: erode with noise so the ink looks worn/screened
    noise = (rng(seed).random((H,W)) * 255).astype(np.uint8)
    nmask = Image.fromarray(noise).filter(ImageFilter.GaussianBlur(1.2)).point(lambda p: 255 if p>96 else 0)
    ink = ImageChops.multiply(layer, nmask.point(lambda p: 60 + p*195//255))
    ink = ImageChops.lighter(ink, layer.point(lambda p: int(p*0.55)))  # keep it readable
    col = Image.composite(Image.new("RGB",(W,H),MAGENTA), Image.new("RGB",(W,H),(0,0,0)), ink)
    hi  = Image.composite(Image.new("RGB",(W,H),HOTPINK), Image.new("RGB",(W,H),(0,0,0)),
                          layer.filter(ImageFilter.MaxFilter(3)).point(lambda p:int(p*0.35)))
    glow = Image.composite(Image.new("RGB",(W,H),MAGENTA), Image.new("RGB",(W,H),(0,0,0)),
                           layer.filter(ImageFilter.GaussianBlur(9))).point(lambda p:int(p*0.6*flick))
    return ImageChops.add(ImageChops.add(col, hi), glow), (tx, ty, tw, th, fnt)

def background(size):
    W = H = size
    a = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx-W*0.5)/(W*0.6))**2 + ((yy-H*0.62)/(H*0.6))**2)
    glow = np.clip(1-r, 0, 1)**2
    for i,c in enumerate((60, 6, 40)):   # deep magenta-purple boudoir haze
        a[...,i] = (c*glow).astype(np.uint8)
    return Image.fromarray(a)

def cursor(size, on):
    W = H = size
    layer = Image.new("RGB",(W,H),(0,0,0))
    if on:
        d = ImageDraw.Draw(layer)
        cw, ch = int(W*0.05), int(H*0.014)
        x, y = (W-cw)//2, int(H*0.80)
        d.rectangle([x,y,x+cw,y+ch], fill=GREEN)
        g = layer.filter(ImageFilter.GaussianBlur(4))
        layer = ImageChops.add(layer, g)
    return layer

# ── frame compositor ────────────────────────────────────────────────────────
# place a scaled silhouette onto a full-size black layer at (cx_frac, top_frac)
def figure(size, hpx, cxf, topf, sway=0.0, hair=0.5, cols=(HOTPINK, PURPLE), racy=0.0):
    m = silhouette(hpx, sway=sway, hair=hair, scale=0.9, racy=racy)
    s,_ = tinted(m, hpx, cols[0], cols[1], CYAN)
    lay = Image.new("RGB", (size, size), (0,0,0))
    lay.paste(s, (int(size*cxf - hpx*0.5), int(size*topf)))
    return lay

def frame(size, phase):
    bg = background(size)
    flick = 0.7 + 0.3*math.sin(phase*2*math.pi*3) + (0.25 if rng(int(phase*97)).random()>0.85 else 0)
    flick = min(1.15, flick)
    # THREE humans — it's a 3way: a trio behind the wordmark. Center one forward+tallest, two
    # flanking, each swaying on its own phase so the group breathes.
    trio = [
        (0.145, 0.34, 0.50, 0.9),   # left  (cxf, topf, hpx-frac, hair-phase)
        (0.500, 0.10, 1.00, 0.0),   # center (tallest, forward)
        (0.855, 0.34, 0.50, 0.6),   # right
    ]
    out = bg
    for i,(cxf, topf, hf, hp) in enumerate(trio):
        sway = 0.012*math.sin(phase*2*math.pi + i*2.1)
        hair = 0.5+0.5*math.sin(phase*2*math.pi + hp*6.28)
        cols = (HOTPINK, PURPLE) if i==1 else (MAGENTA, (60,10,44))
        racy = 1.0 if i==1 else 0.0   # the center one is the show
        out = ImageChops.lighter(out, figure(size, int(size*hf), cxf, topf, sway, hair, cols, racy))
    wm,_ = wordmark(size, flick=flick)
    cur = cursor(size, on=(math.sin(phase*2*math.pi*2) > -0.2))
    out = ImageChops.lighter(out, wm)             # wordmark rides on top, letters cross them
    out = ImageChops.add(out, wm.point(lambda p:int(p*0.25)))  # a touch of type bloom
    out = ImageChops.add(out, cur)
    return out

def save_gif(path, frames, ms):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0,
                   optimize=True, disposal=2)

# ── the morning scene: she walks out at 5am (800x450) ───────────────────────
def morning_bg(W, H):
    a = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    # low dawn glow rising from the horizon, magenta→deep purple
    horizon = H*0.58
    g = np.clip(1 - np.abs(yy-horizon)/(H*0.62), 0, 1)**1.4
    a[...,0] = (95*g).astype(np.uint8); a[...,1]=(16*g).astype(np.uint8); a[...,2]=(78*g).astype(np.uint8)
    # bright doorway she's walking toward (right side) — the destination
    dr = np.clip(1 - np.sqrt(((xx-W*0.83)/(W*0.16))**2 + ((yy-H*0.5)/(H*0.42))**2), 0, 1)**1.7
    a[...,0]=np.clip(a[...,0]+ (210*dr),0,255).astype(np.uint8)
    a[...,1]=np.clip(a[...,1]+ (120*dr),0,255).astype(np.uint8)
    a[...,2]=np.clip(a[...,2]+ (185*dr),0,255).astype(np.uint8)
    return Image.fromarray(a)

def morning_frame(W, H, phase):
    bg = morning_bg(W, H)
    # she recedes toward the doorway: walks right + shrinks, hips sway, hair trails
    walk = phase
    S = int(H*0.86 * (1 - 0.18*walk))
    canvas = Image.new("RGB", (W, H), (0,0,0))
    canvas = ImageChops.add(canvas, bg)
    # the two who STAY — standing at frame-left, softer, watching her go
    for cxf, hf, ph, cols in [(0.13, 0.60, 0.0, (150,26,92)), (0.25, 0.54, 2.0, (108,18,66))]:
        hs = int(H*hf); sm = silhouette(hs, sway=0.01*math.sin(phase*6.28+ph), hair=0.5, scale=0.9)
        st,_ = tinted(sm, hs, cols, (34,6,30), CYAN)
        sl = Image.new("RGB",(W,H),(0,0,0)); sl.paste(st, (int(W*cxf-hs*0.5), int(H*0.32)))
        canvas = ImageChops.lighter(canvas, sl)
    # the one who LEAVES — recedes toward the doorway, hips swaying, rim-lit
    sway = 0.02*math.sin(walk*2*math.pi*2)
    hair = 0.5+0.5*math.sin(walk*2*math.pi*2 + 1.0)
    mask = silhouette(S, sway=sway, hair=hair, scale=0.92)
    sil, _ = tinted(mask, S, (150,25,90), (40,6,36), CYAN)
    x = int(W*0.46 + walk*W*0.28)
    y = int(H*0.12 + walk*H*0.02)
    layer = Image.new("RGB", (W, H), (0,0,0)); layer.paste(sil, (x, y))   # figure on black
    canvas = ImageChops.lighter(canvas, layer)                            # add her, no black box
    # blinking green cursor bottom-left — the driver, still at the keyboard
    if math.sin(phase*2*math.pi*3) > -0.2:
        d = ImageDraw.Draw(canvas)
        d.rectangle([int(W*0.06), int(H*0.9), int(W*0.06)+34, int(H*0.9)+7], fill=GREEN)
    return canvas

# ── afterglow: the morning-after room, neon-graphic (1280x720) ──────────────
# Two stay, one walks out. A reclining silhouette in the bed (afterglow), the leaving figure
# rim-lit in the dawn doorway, two laptops glowing green code. Same neon-boudoir palette.
def afterglow(W, H):
    a = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    # base room haze
    a[...,0]+=14; a[...,2]+=12
    # neon window glow, upper-left (the VACANCY sign bleeding through blinds)
    win = np.clip(1 - np.sqrt(((xx-W*0.20)/(W*0.24))**2 + ((yy-H*0.28)/(H*0.30))**2), 0, 1)**1.5
    a[...,0]=np.clip(a[...,0]+220*win,0,255); a[...,1]=np.clip(a[...,1]+30*win,0,255); a[...,2]=np.clip(a[...,2]+150*win,0,255)
    # dawn doorway, right
    dr = np.clip(1 - np.sqrt(((xx-W*0.88)/(W*0.13))**2 + ((yy-H*0.5)/(H*0.44))**2), 0, 1)**1.7
    a[...,0]=np.clip(a[...,0]+235*dr,0,255); a[...,1]=np.clip(a[...,1]+140*dr,0,255); a[...,2]=np.clip(a[...,2]+205*dr,0,255)
    img = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(img)

    # venetian-blind stripes over the window glow (thin dark bars)
    for i in range(9):
        y = int(H*0.06 + i*H*0.028)
        d.rectangle([int(W*0.03), y, int(W*0.37), y+int(H*0.010)], fill=(8,2,8))
    # neon VACANCY bar in the window
    d.rectangle([int(W*0.09), int(H*0.10), int(W*0.31), int(H*0.145)], fill=(255,60,170))

    # the bed — a low slab, warm magenta sheet
    bx0,by0,bx1,by1 = int(W*0.04), int(H*0.62), int(W*0.60), int(H*0.98)
    bcy = (by0+by1)//2
    d.rectangle([bx0,by0,bx1,by1], fill=(64,22,46))
    d.rectangle([bx0,by0,bx1,by0+int(H*0.03)], fill=(96,36,68))   # sheet edge highlight
    # pillow (head end, left)
    d.rounded_rectangle([bx0+int(W*0.015),by0+int(H*0.02),bx0+int(W*0.15),by0+int(H*0.12)], radius=16, fill=(128,66,102))

    # TWO reclining silhouettes lying ON the bed (the two who stay) — rotate the standing curve 90°.
    for k,(sc, yo, cols) in enumerate([
            (1.7, -0.11, (170,30,100)),    # front sleeper
            (1.5,  0.10, (120,20,74))]):   # the other, further back / dimmer
        S = int((by1-by0)*sc)
        rec = silhouette(S, sway=0.0, hair=0.4, scale=0.86).rotate(90, expand=True)  # head → left (pillow)
        sil,_ = tinted(rec.convert("L"), max(rec.size), cols, (60,10,44), CYAN)
        sil = sil.crop((0,0,rec.size[0],rec.size[1]))
        px = bx0 + int(W*(0.02 + k*0.06)); py = int(bcy + H*yo) - rec.size[1]//2
        layer = Image.new("RGB",(W,H),(0,0,0)); layer.paste(sil, (px, py))
        img = ImageChops.lighter(img, layer)

    # the leaving figure, rim-lit, fully in the dawn doorway (she walks out)
    GS = int(H*0.70)
    gmask = silhouette(GS, sway=0.015, hair=0.6, scale=0.9)
    g,_ = tinted(gmask, GS, (150,25,90), (36,6,32), CYAN)
    gl = Image.new("RGB",(W,H),(0,0,0)); gl.paste(g, (int(W*0.72), int(H*0.18)))
    img = ImageChops.lighter(img, gl)

    # two laptops glowing green code, on the bed (the coder + the driver)
    d = ImageDraw.Draw(img)
    for lx,ly,s in [(0.30,0.66,1.0),(0.47,0.70,0.9)]:
        w,h = int(W*0.11*s), int(H*0.10*s)
        x,y = int(W*lx), int(H*ly)
        scr = Image.new("RGB",(w,h),(6,26,10)); sd=ImageDraw.Draw(scr)
        for r in range(4):
            sd.rectangle([4, 4+r*h//5, 4+int(w*(0.7-0.12*r)), 4+r*h//5+max(2,h//12)], fill=(57,255,20))
        glow = scr.filter(ImageFilter.GaussianBlur(9))
        gl2 = Image.new("RGB",(W,H),(0,0,0)); gl2.paste(glow,(x-8,y-8)); gl2.paste(scr,(x,y))
        img = ImageChops.add(img, gl2)

    return img

def main():
    S = 512
    N = 24
    os.makedirs(f"{ROOT}/assets", exist_ok=True)
    frames = [frame(S, i/N).convert("P", palette=Image.ADAPTIVE, colors=128) for i in range(N)]
    save_gif(f"{ROOT}/assets/logo.gif", frames, 80)
    frame(S, 0.0).save(f"{ROOT}/assets/logo.png")
    frame(S, 0.0).convert("RGB").save(f"{ROOT}/assets/logo.jpg", quality=90)

    W, H, M = 800, 450, 28
    mf = [morning_frame(W, H, i/M).convert("P", palette=Image.ADAPTIVE, colors=128) for i in range(M)]
    save_gif(f"{ROOT}/assets/morning.gif", mf, 90)
    morning_frame(W, H, 0.25).convert("RGB").save(f"{ROOT}/assets/morning.jpg", quality=90)

    afterglow(1280, 720).convert("RGB").save(f"{ROOT}/assets/afterglow.jpg", quality=90)
    print("wrote assets/logo.gif logo.png logo.jpg morning.gif morning.jpg afterglow.jpg")

if __name__ == "__main__":
    main()
