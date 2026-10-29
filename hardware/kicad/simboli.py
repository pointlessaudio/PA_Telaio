"""
Simboli della libreria PA (schema disegnato di PA-TELAIO). Coordinate del simbolo in mm, y verso l'alto come in
KiCad; i piedini si collegano nel loro punto (x, y), sulla griglia da 2,54. I numeri dei piedini sono quelli
di genera_schema.py (componenti.json): non cambiarli senza cambiare anche lì.

Ogni simbolo: dict(units={n: dict(pins=[...], gr=[...])}, nomi=mostra i nomi dei piedini, power=simbolo di rete).
"""
G = 2.54


def pin(num, nome, x, y, ang, lun=G, tipo="passive", nascosto=False):
    return dict(num=str(num), nome=nome, x=x, y=y, ang=ang, lun=lun, tipo=tipo, nascosto=nascosto)


def linea(*pts, w=0.254):
    xy = " ".join(f"(xy {x:g} {y:g})" for x, y in pts)
    return f"(polyline (pts {xy}) (stroke (width {w:g}) (type default)) (fill (type none)))"


def poli(*pts, w=0.254, fill="none"):
    xy = " ".join(f"(xy {x:g} {y:g})" for x, y in pts)
    return f"(polyline (pts {xy}) (stroke (width {w:g}) (type default)) (fill (type {fill})))"


def rett(x0, y0, x1, y1, fill="background", w=0.254):
    return f"(rectangle (start {x0:g} {y0:g}) (end {x1:g} {y1:g}) (stroke (width {w:g}) (type default)) (fill (type {fill})))"


def cerchio(x, y, r, fill="none", w=0.254):
    return f"(circle (center {x:g} {y:g}) (radius {r:g}) (stroke (width {w:g}) (type default)) (fill (type {fill})))"


def testo(s, x, y, size=1.27, ang=0):
    return f'(text "{s}" (at {x:g} {y:g} {ang * 10:g}) (effects (font (size {size:g} {size:g}))))'


def uno(pins, gr, nomi=False):
    return dict(units={1: dict(pins=pins, gr=gr)}, nomi=nomi, power=False)


# ---------------------------------------------------------------- passivi: orizzontali, pin 1 a sinistra
P1, P2 = pin(1, "~", -5.08, 0, 0), pin(2, "~", 5.08, 0, 180)
R = uno([P1, P2], [rett(-2.54, 1.016, 2.54, -1.016, fill="none")])
C = uno([P1, P2], [linea((-2.54, 0), (-0.635, 0)), linea((0.635, 0), (2.54, 0)),
                   linea((-0.635, 2.032), (-0.635, -2.032), w=0.508), linea((0.635, 2.032), (0.635, -2.032), w=0.508)])
CP = uno([pin(1, "+", -5.08, 0, 0), pin(2, "-", 5.08, 0, 180)],
         [linea((-2.54, 0), (-0.635, 0)), linea((0.889, 0), (2.54, 0)),
          linea((-0.635, 2.032), (-0.635, -2.032), w=0.508),
          poli((1.27, 2.032), (0.635, 1.27), (0.635, -1.27), (1.27, -2.032), w=0.508),
          testo("+", -1.778, 1.778)])
# diodo: anodo (2) a sinistra, catodo (1) a destra
_tri = [poli((-1.27, 1.27), (-1.27, -1.27), (1.27, 0), (-1.27, 1.27)), linea((1.27, 1.27), (1.27, -1.27)),
        linea((-2.54, 0), (-1.27, 0)), linea((1.27, 0), (2.54, 0))]
PD = [pin(2, "A", -5.08, 0, 0), pin(1, "K", 5.08, 0, 180)]
D = uno(PD, _tri)
LED = uno(PD, _tri + [linea((-0.254, 1.778), (0.762, 2.794)), poli((0.762, 2.794), (0.254, 2.54), (0.508, 2.286)),
                      linea((0.508, 1.778), (1.524, 2.794)), poli((1.524, 2.794), (1.016, 2.54), (1.27, 2.286))])


def _pot(n1, n2, n3):
    """resistenza orizzontale con cursore dal basso: n1 a sinistra, n3 a destra, cursore n2 sotto"""
    return dict(pins=[pin(n1, "~", -5.08, 0, 0), pin(n3, "~", 5.08, 0, 180), pin(n2, "~", 0, -5.08, 90)],
                gr=[rett(-2.54, 1.016, 2.54, -1.016, fill="none"), poli((0, -1.27), (-0.508, -2.286), (0.508, -2.286), (0, -1.27), fill="outline"),
                    linea((0, -2.286), (0, -2.54))])


POT = dict(units={1: _pot(1, 2, 3)}, nomi=False, power=False)
TRIM = POT
POT2 = dict(units={1: _pot("1L", "2L", "3L"), 2: _pot("1R", "2R", "3R")}, nomi=False, power=False)

# JFET a canale N: G a sinistra, D in alto, S in basso (pin 1 = D, 2 = S, 3 = G come il J201 Central)
NJFET = uno([pin(1, "D", 2.54, 5.08, 270, 3.81), pin(2, "S", 2.54, -5.08, 90, 3.81), pin(3, "G", -5.08, -1.27, 0, 2.54)],
            [cerchio(0.762, 0, 3.048), linea((0, 1.905), (0, -1.905), w=0.508), linea((0, 1.27), (2.54, 1.27)),
             linea((0, -1.27), (2.54, -1.27)), linea((-2.54, -1.27), (0, -1.27)),
             poli((-0.254, -1.27), (-1.016, -0.762), (-1.016, -1.778), (-0.254, -1.27), fill="outline")])


# operazionale: unità 1 (A), 2 (B), 3 (alimentazione)
def _amp(meno, piu, out):
    return dict(pins=[pin(meno, "-", -7.62, 2.54, 0), pin(piu, "+", -7.62, -2.54, 0), pin(out, "~", 7.62, 0, 180)],
                gr=[poli((-5.08, 5.08), (-5.08, -5.08), (5.08, 0), (-5.08, 5.08)), testo("-", -3.81, 2.54, 1.5),
                    testo("+", -3.81, -2.54, 1.5)])


TLC2272 = dict(units={1: _amp(2, 3, 1), 2: _amp(6, 5, 7),
                      3: dict(pins=[pin(8, "V+", 0, 5.08, 270), pin(4, "V-", 0, -5.08, 90)],
                              gr=[rett(-1.905, 2.54, 1.905, -2.54), testo("V+", 0, 1.27, 1), testo("V-", 0, -1.27, 1)])},
               nomi=False, power=False)


# deviatore: un polo per unità, comune a sinistra, due posizioni a destra
def _polo(com, su, giu):
    return dict(pins=[pin(com, "~", -5.08, 0, 0), pin(su, "~", 5.08, 2.54, 180), pin(giu, "~", 5.08, -2.54, 180)],
                gr=[cerchio(-2.032, 0, 0.508), cerchio(2.032, 2.54, 0.508), cerchio(2.032, -2.54, 0.508),
                    linea((-1.651, 0.254), (1.778, 2.032))])


DPDT = dict(units={1: _polo("2", "1", "3"), 2: _polo("5", "4", "6")}, nomi=False, power=False)
S3PDT = dict(units={1: _polo("A2", "A1", "A3"), 2: _polo("B2", "B1", "B3"), 3: _polo("C2", "C1", "C3")},
             nomi=False, power=False)


def scatola(sx, dx, sopra=(), sotto=(), w=None):
    """scatola coi nomi dei piedini; sx/dx dall'alto in basso, sopra/sotto da sinistra"""
    n = max(len(sx), len(dx), 1)
    h = 2 * G * ((n + 2) // 2)
    if w is None:
        lmax = max([len(nm) for _, nm in list(sx) + list(dx)] + [2])
        w = max(4 * G, 2 * G * (1 + int((lmax * 1.27 * 2 + 4) / (2 * G))))
    w = max(w, 2 * G * (max(len(sopra), len(sotto)) + 1))
    pins, top = [], h / 2
    for i, (num, nm) in enumerate(sx):
        pins.append(pin(num, nm, -w / 2 - G, top - G * (i + 1), 0))
    for i, (num, nm) in enumerate(dx):
        pins.append(pin(num, nm, w / 2 + G, top - G * (i + 1), 180))
    for i, (num, nm) in enumerate(sopra):
        pins.append(pin(num, nm, -w / 2 + 2 * G * (i + 1), h / 2 + G, 270))
    for i, (num, nm) in enumerate(sotto):
        pins.append(pin(num, nm, -w / 2 + 2 * G * (i + 1), -h / 2 - G, 90))
    return dict(units={1: dict(pins=pins, gr=[rett(-w / 2, h / 2, w / 2, -h / 2)])}, nomi=True, power=False)


JACK_TS = scatola([], [("T", "punta"), ("TN", "contatto"), ("S", "manicotto")], w=4 * G)
JACK_TRS = scatola([], [("T", "punta"), ("R", "anello"), ("S", "manicotto")], w=4 * G)
DC = scatola([], [("1", "centrale"), ("2", "manicotto"), ("3", "contatto")], w=4 * G)
ENC = scatola([("A", "A"), ("C", "C"), ("B", "B")], [("S1", "S1"), ("S2", "S2")])
OLED = scatola([("1", "GND"), ("2", "VCC"), ("3", "SCL"), ("4", "SDA")], [])
H11L1 = scatola([("1", "anodo"), ("2", "catodo"), ("3", "NC")], [("6", "VCC"), ("4", "uscita"), ("5", "GND")])
MICROSD = scatola([("7", "DAT0"), ("8", "DAT1"), ("1", "DAT2"), ("2", "DAT3"), ("3", "CMD")],
                  [("4", "VDD"), ("5", "CLK"), ("6", "VSS")])
TASTO = uno([pin(1, "~", -5.08, 0, 0), pin(2, "~", 5.08, 0, 180)],
            [cerchio(-2.032, 0, 0.508), cerchio(2.032, 0, 0.508), linea((-2.54, 1.524), (2.54, 1.524)),
             linea((0, 1.524), (0, 3.048))])
# massa del telaio (vite o torretta sulla schermatura)
MASSA = uno([pin(1, "~", 0, 2.54, 270)],
            [linea((0, 0), (0, -0.508)), linea((-2.032, -0.508), (2.032, -0.508), w=0.508),
             linea((-2.032, -0.508), (-2.794, -1.778)), linea((0, -0.508), (-0.762, -1.778)),
             linea((2.032, -0.508), (1.27, -1.778))])


def seed3(nomi):
    """Daisy Seed3: pin 1-20 a sinistra dall'alto, 40-21 a destra dall'alto, come la scheda vista da sopra"""
    return scatola([(p, nomi[str(p)]) for p in range(1, 21)], [(p, nomi[str(p)]) for p in range(40, 20, -1)], w=8 * G)


# ---------------------------------------------------------------- simboli di rete (alimentazioni e massa)
def _power(nome, giu):
    if giu:
        gr = [poli((0, 0), (0, -1.27), (1.27, -1.27), (0, -2.54), (-1.27, -1.27), (0, -1.27))]
    else:
        gr = [linea((0, 0), (0, 1.27)), poli((-0.762, 1.27), (0, 2.54), (0.762, 1.27), (-0.762, 1.27), fill="outline")]
    return dict(units={1: dict(pins=[pin(1, nome, 0, 0, 90 if giu else 270, 0, "power_in", True)], gr=gr)},
                nomi=False, power=True)


RAIL = ("VA", "VB", "3V3A", "3V3D", "VIN_S", "VG")
POWER = {"GND": _power("GND", True)}
for _n in RAIL:
    POWER[_n] = _power(_n, False)
POWER["PWR_FLAG"] = dict(units={1: dict(pins=[pin(1, "pwr", 0, 0, 90, 0, "power_out", True)],
                                        gr=[poli((0, 0), (0, 1.27), (-1.016, 1.905), (0, 2.54), (1.016, 1.905), (0, 1.27))])},
                         nomi=False, power=True)


def catalogo(seed_nomi):
    s = dict(R=R, C=C, CP=CP, D=D, LED=LED, POT=POT, TRIM=TRIM, POT2=POT2, NJFET=NJFET, TLC2272=TLC2272,
             DPDT=DPDT, JACK_TS=JACK_TS, JACK_TRS=JACK_TRS, DC=DC, ENC=ENC, OLED=OLED, H11L1=H11L1,
             MICROSD=MICROSD, TASTO=TASTO, MASSA=MASSA, SEED3=seed3(seed_nomi))
    s["3PDT"] = S3PDT
    s.update(POWER)
    return s
