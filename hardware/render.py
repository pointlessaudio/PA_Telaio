import html
from collections import OrderedDict
import layout as L

assert not L.errors, L.errors

p = 22
ML, MR, MT, MB = 104, 110, 34, 24
BW, BH = L.W * p, L.H * p
SW, SH = ML + BW + MR, MT + BH + MB


def cx(x): return ML + x * p + p / 2
def cy(y): return MT + y * p + p / 2


NETCOL = {
    "GND": "#2a2d2f", "VA": "#b3245f", "VB": "#d9822b", "VIN_S": "#6a4bb5",
    "V9": "#b3245f",
}
SIG = "#11808a"


def ncol(net):
    return NETCOL.get(net, SIG)


def esc(s): return html.escape(str(s))


# ================================================================ lato componenti
def foro_fissaggio(a, b):
    """foro da 3,2 mm per vite M3, in scala (p pixel = 2,54 mm), con croce al centro"""
    rr = 1.6 / 2.54 * p
    return (f'<g stroke="#1f6fb2" stroke-width="2.2" fill="none">'
            f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{rr:.1f}"/>'
            f'<line x1="{a-5:.1f}" y1="{b:.1f}" x2="{a+5:.1f}" y2="{b:.1f}"/>'
            f'<line x1="{a:.1f}" y1="{b-5:.1f}" x2="{a:.1f}" y2="{b+5:.1f}"/></g>')


def board_svg():
    o = [f'<svg class="board" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}" '
         f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Veroboard lato componenti">']
    o.append(f'<rect x="{ML-6}" y="{MT-6}" width="{BW+12}" height="{BH+12}" rx="6" fill="#d8bb82"/>')
    # strisce (trasparenza: viste attraverso la scheda)
    for y in range(L.H):
        o.append(f'<rect x="{ML+2}" y="{cy(y)-p*0.3:.1f}" width="{BW-4}" height="{p*0.6:.1f}" '
                 f'fill="#b8733a" opacity="0.28"/>')
    # etichette righe e colonne
    for y in range(L.H):
        o.append(f'<text class="gl" x="{14}" y="{cy(y)+4:.1f}">{y+1}</text>')
        o.append(f'<text class="gl" x="{SW-14}" y="{cy(y)+4:.1f}" text-anchor="end">{y+1}</text>')
    for x in range(L.W):
        o.append(f'<text class="gl" x="{cx(x):.1f}" y="{MT-12}" text-anchor="middle">{x+1}</text>')
    # fori
    for y in range(L.H):
        for x in range(L.W):
            if (x, y) in L.CUTS:
                continue
            o.append(f'<circle cx="{cx(x):.1f}" cy="{cy(y):.1f}" r="2.6" fill="#6b4a22" opacity="0.55"/>')
    # tagli
    for (x, y) in sorted(L.CUTS):
        a, b = cx(x), cy(y)
        o.append(f'<g stroke="#c62f2f" stroke-width="2.6" stroke-linecap="round">'
                 f'<line x1="{a-6}" y1="{b-6}" x2="{a+6}" y2="{b+6}"/>'
                 f'<line x1="{a-6}" y1="{b+6}" x2="{a+6}" y2="{b-6}"/></g>')

    # fori di fissaggio
    for (x, y) in L.FORI_FISSAGGIO:
        o.append(foro_fissaggio(cx(x), cy(y)))

    # Seed
    x0, x1 = cx(L.SEED_X_L) - p * 0.5, cx(L.SEED_X_R) + p * 0.5
    y0, y1 = cy(0) - p * 0.55, cy(19) + p * 0.55
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="4" '
             f'fill="#1f2326" opacity="0.9"/>')
    o.append(f'<text x="{(x0+x1)/2:.1f}" y="{(y0+y1)/2:.1f}" class="seedt" '
             f'transform="rotate(-90 {(x0+x1)/2:.1f} {(y0+y1)/2:.1f})" text-anchor="middle">Daisy Seed3</text>')
    for pn in range(1, 41):
        x, y = L.seed_pos(pn)
        used = pn in L.seed_net
        o.append(f'<rect x="{cx(x)-5}" y="{cy(y)-5}" width="10" height="10" rx="1.5" '
                 f'fill="{"#e9c46a" if used else "#6d6d6d"}"/>')
        nm = L.seed_name[pn]
        if pn <= 20:
            o.append(f'<text class="pn" x="{cx(x)+9:.1f}" y="{cy(y)+3.5:.1f}">{pn} {esc(nm)}</text>')
        else:
            o.append(f'<text class="pn" x="{cx(x)-9:.1f}" y="{cy(y)+3.5:.1f}" text-anchor="end">{esc(nm)} {pn}</text>')
    o.append(f'<circle cx="{cx(L.SEED_X_L)-9}" cy="{cy(0)}" r="3.2" fill="#c62f2f"/>')

    # IC
    for ref, top in L.ICS:
        a, b = cx(12) - p * 0.45, cy(top) - p * 0.5
        w, h = cx(15) - cx(12) + p * 0.9, p * 4
        o.append(f'<rect x="{a}" y="{b}" width="{w}" height="{h}" rx="3" fill="#23272a"/>')
        o.append(f'<path d="M {a+w/2-6} {b} a 6 6 0 0 0 12 0" fill="#d8bb82"/>')
        o.append(f'<text class="ict" x="{a+w/2:.1f}" y="{b+h/2+1:.1f}" text-anchor="middle">{ref}</text>')
        o.append(f'<text class="icv" x="{a+w/2:.1f}" y="{b+h/2+13:.1f}" text-anchor="middle">TLC2272</text>')
        for i, pn in enumerate([1, 2, 3, 4]):
            o.append(f'<rect x="{cx(12)-4}" y="{cy(top+i)-4}" width="8" height="8" fill="#c9c9c9"/>')
            o.append(f'<text class="icp" x="{cx(12)+8:.1f}" y="{cy(top+i)+3:.1f}">{pn}</text>')
        for i, pn in enumerate([8, 7, 6, 5]):
            o.append(f'<rect x="{cx(15)-4}" y="{cy(top+i)-4}" width="8" height="8" fill="#c9c9c9"/>')
            o.append(f'<text class="icp" x="{cx(15)-8:.1f}" y="{cy(top+i)+3:.1f}" text-anchor="end">{pn}</text>')

    # ---- ostacoli per le etichette
    obst = []
    obst.append((cx(L.SEED_X_L) - p*0.5, cy(0) - p*0.55, cx(L.SEED_X_R) + p*0.5, cy(19) + p*0.55))
    for ref, top in L.ICS:
        obst.append((cx(12) - p*0.45, cy(top) - p*0.5, cx(15) + p*0.45, cy(top) + p*3.5))
    labels = []  # (testo, colore, candidati)

    def tw(t): return 5.4 * len(t) + 2

    def place(text, cands, cls, fill=None):
        for (x, y, anchor) in cands:
            w = tw(text)
            x0 = x if anchor == "start" else (x - w if anchor == "end" else x - w/2)
            box = (x0, y - 9, x0 + w, y + 2)
            if box[0] < ML - 4 or box[2] > ML + BW + 4:
                continue
            if all(box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3] for b in obst):
                obst.append(box)
                f = f' fill="{fill}"' if fill else ""
                o.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{f}>{esc(text)}</text>')
                return
        x, y, anchor = cands[0]
        f = f' fill="{fill}"' if fill else ""
        o.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{f}>{esc(text)}</text>')

    # corpi dei componenti come ostacoli
    bodies = []
    for ref, kind, val, pins in L.P:
        if kind in ("seed", "dip8"):
            continue
        (xa, ya, na, sa), (xb, yb, nb, sb) = pins
        A, B = (cx(xa), cy(ya)), (cx(xb), cy(yb))
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        vertical = xa == xb
        span = abs(ya - yb) if vertical else abs(xa - xb)
        blen = min(span * p - 8, 30) if span > 1 else 12
        bw = 9 if kind != "elco" else 12
        if vertical:
            r = (mx - bw/2, my - blen/2, mx + bw/2, my + blen/2)
        else:
            r = (mx - blen/2, my - bw/2, mx + blen/2, my + bw/2)
        bodies.append((ref, kind, val, pins, A, B, mx, my, vertical, span, blen, bw, r))
        obst.append(r)
    for name, a, b, net, bare in L.LINKS:
        x = cx(a[0])
        obst.append((x - 2, min(cy(a[1]), cy(b[1])), x + 2, max(cy(a[1]), cy(b[1]))))

    # ponticelli
    for name, a, b, net, bare in L.LINKS:
        col = "#9aa3a8" if bare else ncol(net)
        o.append(f'<line x1="{cx(a[0])}" y1="{cy(a[1])}" x2="{cx(b[0])}" y2="{cy(b[1])}" '
                 f'stroke="{col}" stroke-width="{2.4 if bare else 3.6}" stroke-linecap="round" opacity="0.92"/>')
        for h in (a, b):
            o.append(f'<circle cx="{cx(h[0])}" cy="{cy(h[1])}" r="3.4" fill="{col}"/>')

    # componenti a due terminali
    for (ref, kind, val, pins, A, B, mx, my, vertical, span, blen, bw, r) in bodies:
        (xa, ya, na, sa), (xb, yb, nb, sb) = pins
        o.append(f'<line x1="{A[0]}" y1="{A[1]}" x2="{B[0]}" y2="{B[1]}" stroke="#7d8488" stroke-width="1.6"/>')
        for P_ in (A, B):
            o.append(f'<circle cx="{P_[0]}" cy="{P_[1]}" r="3" fill="#7d8488"/>')
        fill = {"res": "#e7d3a8", "cap": "#e0a93b", "film": "#3f7f5f",
                "elco": "#274f86", "diode": "#1c1c1c"}[kind]
        rx, ry, rw, rh = r[0], r[1], r[2] - r[0], r[3] - r[1]
        if kind == "cap":
            o.append(f'<ellipse cx="{mx}" cy="{my}" rx="{rw/2 if not vertical else 5.5}" ry="{rh/2 if vertical else 5.5}" fill="{fill}" stroke="#6b4a22" stroke-width="0.6"/>')
        else:
            rad = 4 if kind in ("res", "film") else 3
            o.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" rx="{rad}" '
                     f'fill="{fill}" stroke="#4a3a22" stroke-width="0.6"/>')
        if kind == "diode":
            kx, ky = (B if sb == "K" else A)
            bx = mx + (kx - mx) * 0.36
            o.append(f'<line x1="{bx}" y1="{my-5}" x2="{bx}" y2="{my+5}" stroke="#e6e6e6" stroke-width="2"/>')
        if kind == "elco":
            px, py = (A if sa == "+" else B)
            o.append(f'<text class="plus" x="{px+6:.1f}" y="{py-3:.1f}">+</text>')

    for (ref, kind, val, pins, A, B, mx, my, vertical, span, blen, bw, r) in bodies:
        lab = f"{ref} {val}"
        if vertical:
            c = [(r[2]+3, my+3.5, "start"), (r[0]-3, my+3.5, "end"),
                 (r[2]+3, r[1]-2, "start"), (r[0]-3, r[1]-2, "end"),
                 (r[2]+3, r[3]+9, "start"), (r[0]-3, r[3]+9, "end"),
                 (mx, r[1]-4, "middle"), (mx, r[3]+11, "middle")]
        else:
            c = [(mx, r[1]-3, "middle"), (mx, r[3]+10, "middle"),
                 (r[2]+3, my+3.5, "start"), (r[0]-3, my+3.5, "end")]
        place(lab, c, "cl")
    for name, a, b, net, bare in L.LINKS:
        col = "#6f777c" if bare else ncol(net)
        mx, my = cx(a[0]), (cy(a[1]) + cy(b[1])) / 2
        c = [(mx+5, my+3, "start"), (mx-5, my+3, "end"), (mx+5, my-8, "start"),
             (mx-5, my-8, "end"), (mx+5, my+14, "start"), (mx-5, my+14, "end")]
        place(name, c, "jl", col)

    # cavi verso il Seed
    for name, a, b, net, lab in L.WIRES:
        A, B = (cx(a[0]), cy(a[1])), (cx(b[0]), cy(b[1]))
        dx = -12 if min(a[0], b[0]) <= 1 else 0
        ctrl = ((A[0] + B[0]) / 2 + dx, (A[1] + B[1]) / 2)
        col = ncol(net)
        o.append(f'<path d="M {A[0]} {A[1]} Q {ctrl[0]:.1f} {ctrl[1]:.1f} {B[0]} {B[1]}" fill="none" '
                 f'stroke="{col}" stroke-width="2.6" stroke-dasharray="6 4" stroke-linecap="round"/>')
        for P_ in (A, B):
            o.append(f'<circle cx="{P_[0]}" cy="{P_[1]}" r="3.6" fill="{col}"/>')

    # piazzole esterne
    inner = {}
    for name, (x, y), net, desc in L.PADS:
        a, b = cx(x), cy(y)
        o.append(f'<circle cx="{a}" cy="{b}" r="5.2" fill="none" stroke="#0b5d63" stroke-width="2"/>')
        if x <= 2:
            o.append(f'<text class="pl" x="{ML-10}" y="{b+4:.1f}" text-anchor="end">{esc(name)}</text>')
        elif x >= L.W - 3:
            o.append(f'<text class="pl" x="{ML+BW+10}" y="{b+4:.1f}">{esc(name)}</text>')
        else:
            inner.setdefault(y, []).append((x, name))
    for y, items in inner.items():
        xs = [x for x, _ in items]
        txt = ", ".join(n for _, n in sorted(items))
        xx = cx(15) if y == 0 else cx(max(xs)) + 9
        o.append(f'<text class="pl" x="{xx:.1f}" y="{cy(y)+4:.1f}">{esc(txt)}</text>')
    o.append('</svg>')
    return "\n".join(o)


# ================================================================ lato rame
def copper_svg():
    o = [f'<svg class="board" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}" '
         f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Lato rame con i tagli">']
    o.append(f'<rect x="{ML-6}" y="{MT-6}" width="{BW+12}" height="{BH+12}" rx="6" fill="#d8bb82"/>')

    def mx_(x): return cx(L.W - 1 - x)
    for y in range(L.H):
        o.append(f'<rect x="{ML+2}" y="{cy(y)-p*0.34:.1f}" width="{BW-4}" height="{p*0.68:.1f}" fill="#c07b40"/>')
        o.append(f'<text class="gl" x="{14}" y="{cy(y)+4:.1f}">{y+1}</text>')
        o.append(f'<text class="gl" x="{SW-14}" y="{cy(y)+4:.1f}" text-anchor="end">{y+1}</text>')
    for x in range(L.W):
        o.append(f'<text class="gl" x="{mx_(x):.1f}" y="{MT-12}" text-anchor="middle">{x+1}</text>')
    used = set(L.used.keys())
    for y in range(L.H):
        for x in range(L.W):
            if (x, y) in L.CUTS:
                continue
            f = "#f1e4c8" if (x, y) in used else "#5a3a1a"
            r = 3.4 if (x, y) in used else 2.4
            o.append(f'<circle cx="{mx_(x):.1f}" cy="{cy(y):.1f}" r="{r}" fill="{f}"/>')
    for (x, y) in L.CUTS:
        a, b = mx_(x), cy(y)
        o.append(f'<rect x="{a-8}" y="{b-p*0.36:.1f}" width="16" height="{p*0.72:.1f}" fill="#d8bb82"/>')
        o.append(f'<circle cx="{a}" cy="{b}" r="6.5" fill="none" stroke="#c62f2f" stroke-width="2.4"/>')
    for (x, y) in L.FORI_FISSAGGIO:
        o.append(foro_fissaggio(mx_(x), cy(y)))
    # riferimenti: pin 1 del Seed e pin 1 degli IC
    s1 = L.seed_pos(1)
    o.append(f'<text class="plc" x="{mx_(s1[0])+10:.1f}" y="{cy(s1[1])+4:.1f}">pin 1 Seed</text>')
    for ref, top in L.ICS:
        o.append(f'<text class="plc" x="{mx_(12)+10:.1f}" y="{cy(top)+4:.1f}">{ref} pin 1</text>')
    o.append('</svg>')
    return "\n".join(o)


# ================================================================ schema
class S:
    def __init__(s, w, h):
        s.w, s.h, s.o = w, h, []

    def ln(s, *pts, cls="w"):
        d = " ".join(f"{'M' if i==0 else 'L'} {x} {y}" for i, (x, y) in enumerate(pts))
        s.o.append(f'<path class="{cls}" d="{d}"/>')

    def dot(s, x, y):
        s.o.append(f'<circle class="dot" cx="{x}" cy="{y}" r="3.2"/>')

    def t(s, x, y, txt, anchor="start", cls="st"):
        s.o.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(txt)}</text>')

    def res(s, x, y, horiz, ref, val):
        # centro x,y ; lunghezza totale 60, corpo 30x12
        if horiz:
            s.ln((x-30, y), (x-15, y)); s.ln((x+15, y), (x+30, y))
            s.o.append(f'<rect class="sym" x="{x-15}" y="{y-6}" width="30" height="12"/>')
            s.t(x, y-11, f"{ref} {val}", "middle")
        else:
            s.ln((x, y-30), (x, y-15)); s.ln((x, y+15), (x, y+30))
            s.o.append(f'<rect class="sym" x="{x-6}" y="{y-15}" width="12" height="30"/>')
            s.t(x+11, y+4, f"{ref} {val}")

    def cap(s, x, y, horiz, ref, val, polar=False, plus_left=True):
        if horiz and polar and not plus_left:
            s.ln((x-30, y), (x-4, y)); s.ln((x+4, y), (x+30, y))
            s.ln((x+4, y-11), (x+4, y+11), cls="w2")
            s.o.append(f'<path class="w2" d="M {x-7} {y-11} Q {x-2} {y} {x-7} {y+11}"/>')
            s.t(x+14, y-3, "+", "middle", "stp")
            s.t(x, y-16, f"{ref} {val}", "middle")
            return
        if horiz:
            s.ln((x-30, y), (x-4, y)); s.ln((x+4, y), (x+30, y))
            s.ln((x-4, y-11), (x-4, y+11), cls="w2")
            if polar:
                s.o.append(f'<path class="w2" d="M {x+7} {y-11} Q {x+2} {y} {x+7} {y+11}"/>')
                s.t(x-14, y-3, "+", "middle", "stp")
            else:
                s.ln((x+4, y-11), (x+4, y+11), cls="w2")
            s.t(x, y-16, f"{ref} {val}", "middle")
        else:
            s.ln((x, y-30), (x, y-4)); s.ln((x, y+4), (x, y+30))
            s.ln((x-11, y-4), (x+11, y-4), cls="w2")
            if polar:
                s.o.append(f'<path class="w2" d="M {x-11} {y+7} Q {x} {y+2} {x+11} {y+7}"/>')
                s.t(x-15, y-6, "+", "middle", "stp")
            else:
                s.ln((x-11, y+4), (x+11, y+4), cls="w2")
            s.t(x+15, y+4, f"{ref} {val}")

    def diode(s, x, y, ref, val):
        s.ln((x-30, y), (x-8, y)); s.ln((x+8, y), (x+30, y))
        s.o.append(f'<path class="sym" d="M {x-8} {y-8} L {x-8} {y+8} L {x+8} {y} Z"/>')
        s.ln((x+8, y-8), (x+8, y+8), cls="w2")
        s.t(x, y-13, f"{ref} {val}", "middle")

    def gnd(s, x, y):
        s.ln((x, y), (x, y+8))
        s.ln((x-10, y+8), (x+10, y+8), cls="w2")
        s.ln((x-6, y+12), (x+6, y+12))
        s.ln((x-2, y+16), (x+2, y+16))

    def rail(s, x, y, name):
        s.ln((x, y), (x, y-8))
        s.ln((x-8, y-8), (x+8, y-8), cls="w2")
        s.t(x, y-13, name, "middle", "stb")

    def term(s, x, y, name, anchor="end"):
        s.o.append(f'<circle class="term" cx="{x}" cy="{y}" r="4.5"/>')
        s.t(x + (-9 if anchor == "end" else 9), y+4, name, anchor, "stb")

    def opamp(s, x, y, ref, plus_top=True):
        # x,y = punta sinistra centro ; triangolo largo 60, alto 64
        s.o.append(f'<path class="sym" d="M {x} {y-32} L {x} {y+32} L {x+60} {y} Z"/>')
        s.t(x+8, y-10 if plus_top else y+16, "+", "start", "stp")
        s.t(x+8, y+16 if plus_top else y-10, "−", "start", "stp")
        s.t(x+22, y+4, ref, "start", "sts")
        return (x, y-16), (x, y+16), (x+60, y)  # ingresso alto, basso, uscita

    def svg(s, label):
        return (f'<svg class="sch" viewBox="0 0 {s.w} {s.h}" width="{s.w}" height="{s.h}" '
                f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}">'
                + "".join(s.o) + "</svg>")


def sch_power():
    s = S(780, 400)
    y = 80
    s.t(40, 28, "AGND (pin 20) e DGND (pin 40) del Seed vanno sulla stessa massa, unite vicino al jack DC.", "start", "sts")
    s.term(70, y, "+9 V", "end")
    s.ln((70, y), (90, y))
    s.diode(120, y, "D1", "1N5817")
    s.ln((150, y), (250, y)); s.dot(220, y)
    s.res(280, y, True, "R1", "3R3")
    s.ln((310, y), (400, y)); s.dot(360, y)
    s.term(400, y, "VIN Seed, pin 39", "start")
    s.ln((360, y), (360, y+15)); s.cap(360, y+45, False, "C1", "100µF", True); s.gnd(360, y+75)
    s.ln((220, y), (220, y+45)); s.res(220, y+75, False, "R2", "10R")
    s.ln((220, y+105), (220, y+140)); s.dot(220, y+140)
    s.ln((220, y+140), (520, y+140))
    s.t(525, y+144, "VA ≈ 8,5 V → U1 e U2 pin 8", "start", "stb")
    for xx, ref, val, pol in ((290, "C2", "100µF", True), (390, "C3", "100nF", False)):
        s.dot(xx, y+140); s.ln((xx, y+140), (xx, y+145))
        s.cap(xx, y+175, False, ref, val, pol); s.gnd(xx, y+205)
    s.dot(490, y+140); s.ln((490, y+140), (490, y+145))
    s.res(490, y+175, False, "R3", "10K")
    s.ln((490, y+205), (490, y+225)); s.dot(490, y+225)
    s.ln((490, y+225), (680, y+225))
    s.t(685, y+229, "VB = VA/2", "start", "stb")
    for xx, kind in ((560, "r"), (640, "c")):
        s.dot(xx, y+225); s.ln((xx, y+225), (xx, y+232))
        if kind == "r":
            s.res(xx, y+262, False, "R4", "10K")
        else:
            s.cap(xx, y+262, False, "C4", "47µF", True)
        s.gnd(xx, y+292)
    return s.svg("Schema alimentazione")


def sch_input():
    s = S(740, 290)
    y = 145
    s.t(40, 24, "Buffer a 1 MΩ, poi passa-basso RC a circa 72 kHz verso il Seed.", "start", "sts")
    s.term(90, y, "IN L (R)", "end")
    s.ln((90, y), (140, y)); s.dot(120, y)
    s.ln((120, y), (120, y+20)); s.res(120, y+50, False, "R6", "1M (R9)"); s.gnd(120, y+80)
    s.cap(170, y, True, "C5", "100nF (C8)")
    s.ln((200, y), (270, y)); s.dot(230, y)
    s.ln((230, y), (230, y-20)); s.res(230, y-50, False, "R5", "1M (R8)")
    s.ln((230, y-80), (230, y-88)); s.rail(230, y-88, "VB")
    cy_ = y + 16
    s.o.append(f'<path class="sym" d="M 270 {cy_-32} L 270 {cy_+32} L 330 {cy_} Z"/>')
    s.t(278, y+5, "+", "start", "stp"); s.t(278, y+37, "−", "start", "stp")
    s.t(300, cy_-40, "U1A (U1B)", "middle", "sts")
    s.ln((330, cy_), (380, cy_)); s.dot(350, cy_)
    s.ln((350, cy_), (350, cy_+46), (256, cy_+46), (256, y+32), (270, y+32))
    s.res(410, cy_, True, "R7", "1K (R10)")
    s.ln((440, cy_), (490, cy_)); s.dot(470, cy_)
    s.ln((470, cy_), (470, cy_+20)); s.cap(470, cy_+50, False, "C6", "2.2nF (C9)"); s.gnd(470, cy_+80)
    s.cap(520, cy_, True, "C7", "10µF (C10)", True)
    s.ln((550, cy_), (580, cy_))
    s.term(580, cy_, "Seed pin 16 (17)", "start")
    return s.svg("Schema ingresso")


def sch_output():
    s = S(740, 330)
    y = 170
    cy_ = y + 16
    s.t(40, 28, "Invertente a guadagno −1, passa-basso a circa 41 kHz con R12 e C13.", "start", "sts")
    s.o.append(f'<circle class="term" cx="60" cy="{y}" r="4.5"/>')
    s.t(40, y+24, "Seed pin 18 (19)", "start", "stb")
    s.ln((64, y), (90, y))
    s.cap(120, y, True, "C12", "10µF (C15)", True, plus_left=False)
    s.ln((150, y), (170, y))
    s.res(200, y, True, "R11", "10K (R15)")
    s.ln((230, y), (270, y)); s.dot(250, y)
    s.o.append(f'<path class="sym" d="M 270 {cy_-32} L 270 {cy_+32} L 330 {cy_} Z"/>')
    s.t(278, y+5, "−", "start", "stp"); s.t(278, y+37, "+", "start", "stp")
    s.t(300, cy_+50, "U2A (U2B)", "middle", "sts")
    s.ln((270, y+32), (256, y+32), (256, y+60), (248, y+60)); s.t(242, y+64, "VB", "end", "stb")
    s.ln((250, y), (250, y-90)); s.dot(250, y-40)
    s.ln((250, y-40), (275, y-40)); s.res(305, y-40, True, "R12", "10K (R16)")
    s.ln((335, y-40), (360, y-40))
    s.ln((250, y-90), (275, y-90)); s.cap(305, y-90, True, "C13", "390pF (C16)")
    s.ln((335, y-90), (360, y-90), (360, cy_)); s.dot(360, y-40)
    s.ln((330, cy_), (390, cy_)); s.dot(360, cy_)
    s.cap(420, cy_, True, "C14", "10µF (C17)", True)
    s.ln((450, cy_), (470, cy_))
    s.res(500, cy_, True, "R13", "100R (R17)")
    s.ln((530, cy_), (580, cy_)); s.dot(560, cy_)
    s.ln((560, cy_), (560, cy_+20)); s.res(560, cy_+50, False, "R14", "100K (R18)"); s.gnd(560, cy_+80)
    s.term(580, cy_, "OUT L (R)", "start")
    return s.svg("Schema uscita")


# ================================================================ tabelle
def bom_rows():
    groups = OrderedDict()
    order = {"res": 0, "cap": 1, "film": 2, "elco": 3, "diode": 4, "dip8": 5}
    names = {"res": "Resistenza 1/4 W", "cap": "Condensatore ceramico",
             "film": "Condensatore a film", "elco": "Elettrolitico 16 V o più",
             "diode": "Diodo Schottky", "dip8": "Operazionale DIP-8"}
    items = [(r, k, v) for r, k, v, _ in L.P if k != "seed"]
    import re as _re
    def val(v):
        m = _re.match(r"([0-9.]+)\s*(p|n|µ|R|K|M)?", v.replace("R", ".R") if v.endswith("R") and "R" in v[1:-1] else v)
        if not m: return 0
        num = float(m.group(1).rstrip(".")) if m.group(1).rstrip(".") else 0
        mult = {"p":1e-12,"n":1e-9,"µ":1e-6,"R":1,"K":1e3,"M":1e6,None:1}[m.group(2)]
        if "R" in v and v.index("R") not in (len(v)-1,):  # 3R3
            a, b = v.split("R"); return float(a + "." + b)
        return num * mult
    items.sort(key=lambda t: (order[t[1]], val(t[2])))
    for r, k, v in items:
        groups.setdefault((k, v), []).append(r)
    rows = []
    for (k, v), refs in groups.items():
        rows.append((names[k], v, len(refs), ", ".join(refs)))
    rows += [
        ("Zoccolo", "DIP-8", 2, "U1, U2"),
        ("Header femmina", "1×20, passo 2,54", 2, "per il Seed3"),
        ("Stripboard", "almeno 30 fori × 45 strisce", 1, ""),
        ("Jack 6,35 mm mono", "boccola 3/8\"", 4, "IN L e IN R con commutazione sulla punta; OUT L, OUT R"),
        ("Jack DC 2,1 mm", "centro negativo", 1, ""),
        ("LED 3 mm + resistenza", "1K", 1, "fuori scheda, resistenza in linea"),
        ("Filo isolato", "unipolare 0,25 mm²", 1, "ponticelli J3-J13 e cavi W1-W7"),
        ("Cavetto schermato", "", 1, "ingressi e uscite verso i jack"),
    ]
    return rows


def cuts_rows():
    by_row = OrderedDict()
    for (x, y) in sorted(L.CUTS, key=lambda t: (t[1], t[0])):
        by_row.setdefault(y + 1, []).append(x + 1)
    return by_row


if __name__ == "__main__":
    import json
    open("board.svg", "w").write(board_svg())
    open("copper.svg", "w").write(copper_svg())
    print("svg ok")
