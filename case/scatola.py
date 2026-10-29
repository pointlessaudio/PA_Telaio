# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0", "matplotlib"]
# ///
"""
PA-TELAIO in una scatola di alluminio pressofuso tipo Hammond 1590DD (Musikding "Typ DD", Tayda 1590DD).

Verifica d'ingombro con gli stessi corpi di case.py: la veroboard arriva da hardware/layout.py
(tramite case.componenti(), spostata in blocco), gli altri componenti con le misure dei dizionari
di case.py. La scatola viene dal disegno Hammond 1590DD: esterno 188 x 120 x 37, pareti e cielo
2,5, fondo 1,9; dentro 183 x 115 al bordo e 178 x 110 sotto il cielo (sformo), 6 borchie per le
viti del fondo.

    uv run scatola.py        # da case/: verifica, stampa le quote, disegna out/scatola/*.png
Deve finire con "OK ... nessuna collisione".

Coordinate: X da sinistra a destra visto da chi suona, Y dal fronte al retro, Z in su; origine
nello spigolo anteriore sinistro sotto il fondo. Il fondo (coperchio Hammond) sta sotto: la faccia
chiusa della scatola è il pannello dei comandi.
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Pos, Rot, export_stl

import case as C

OUT = Path(__file__).resolve().parent / "out" / "scatola"

# =========================================================== scatola (disegno Hammond 1590DD)
L_EST, P_EST, H_EST = 188.0, 120.0, 37.0
T_CIELO, T_FONDO = 2.5, 1.9
Z_FONDO_IN = T_FONDO                      # faccia interna del fondo
Z_CIELO_IN = H_EST - T_CIELO              # faccia interna del pannello dei comandi
DENTRO_BORDO = (183.0, 115.0)             # dentro, all'altezza del fondo
DENTRO_CIELO = (178.0, 110.0)             # dentro, sotto il cielo: lo sformo stringe salendo
BORDO_FONDO = (2.0, 4.0)                  # il fondo ha un bordino di 2 mm, alto fino a z 4,0
# borchie delle 6 viti del fondo: 4 negli angoli, 2 a metà dei lati lunghi (101 mm fra le facce)
# angoli: cilindri Ø10 intorno ai fori delle viti (4,4 mm dai bordi esterni); a metà: blocchi fino a 9,5
BORCHIE_ANGOLO = [(4.4, 4.4), (L_EST - 4.4, 4.4), (4.4, P_EST - 4.4), (L_EST - 4.4, P_EST - 4.4)]
BORCHIA_D = 10.0
BORCHIE = [(L_EST / 2 - 4.5, L_EST / 2 + 4.5, 0.0, 9.5), (L_EST / 2 - 4.5, L_EST / 2 + 4.5, P_EST - 9.5, P_EST)]


def parete(z):
    """spessore delle pareti a quota z (sformo lineare fra fondo e cielo), lati lunghi e corti"""
    f = min(max((z - Z_FONDO_IN) / (Z_CIELO_IN - Z_FONDO_IN), 0.0), 1.0)
    tx = (L_EST - DENTRO_BORDO[0]) / 2 + f * (DENTRO_BORDO[0] - DENTRO_CIELO[0]) / 2
    ty = (P_EST - DENTRO_BORDO[1]) / 2 + f * (DENTRO_BORDO[1] - DENTRO_CIELO[1]) / 2
    return tx, ty


def sotto_cielo(x, y, dx, dy, h, cilindro=False):
    """corpo appeso sotto il pannello dei comandi, centrato in (x, y), alto h verso il basso"""
    z = Z_CIELO_IN - h / 2 - 0.02
    return Pos(x, y, z) * (C.cil(dx, h) if cilindro else Box(dx, dy, h))


# =========================================================== disposizione (da iterare)
# pannello dei comandi: centri in pianta
POT_X = (116.0, 144.0, 172.0)            # 28 mm fra i centri, come nel case stampato
POT_Y = (84.0, 52.0)                     # 32 mm fra le file; la fila dietro resta davanti ai jack
ENC_C = (88.0, 74.0)
OLED_C = (44.0, 88.0)                    # centro del circuito del modulo
TASTI = ((24.0, 26.0), (46.0, 26.0))
# cappuccio Tayda A-4814 (disegno Tayda): corpo Ø11,5 che esce dal foro, flangia Ø12,8 sotto il pannello,
# fondo del cappuccio a 3,5 + 1,3 dal millefori, cima a 10,5. Flangia 0,5 sotto il pannello: sporge 1,8
TASTO_PILA, TASTO_SPORGE = 10.5, 1.8
LED_C = (64.0, 26.0)
LED_FS_C = (146.0, 24.0)
FS_C = (166.0, 24.0)
# retro: centri lungo X, tutti alla stessa quota
Z_RETRO = 14.0                           # telaio Ø19,1 sopra il bordino del fondo (z 4,0)
Z_MIDI = 9.8                             # Thonkiconn più in basso: lì la parete è più sottile
JACK635 = dict(d=19.1, prof=26.6)        # Switchcraft 12A/12B (Musikding): telaio Ø19,1
RETRO = [
    ("MIDI IN", 25.0, "jack35"),
    ("MIDI OUT", 39.0, "jack35"),
    ("PEDALE", 68.0, "jack635q"),
    ("IN L", 109.0, "jack635"),
    ("IN R", 129.0, "jack635"),
    ("OUT L", 149.0, "jack635q"),
    ("OUT R", 169.0, "jack635q"),
]
# fianco destro: centri lungo Y
DESTRA = [
    ("DC 9V", 72.0, "dc"),
    ("INST/LINE", 52.0, "levetta"),
]
# jack635q: Tayda A-1121 (PJ-629HAN, datasheet): corpo 15,8 x 15,8, profondo 23,5 più 3,6 di pin
CORPI_LATO = {"dc": (16.0, 16.0, 18.3), "levetta": (13.0, 13.0, 20.0), "jack35": (9.0, 10.5, 10.5),
              "jack635q": (15.8, 15.8, 27.1)}
MIDI_SCHEDA = dict(x=(18.0, 46.0), z=(4.5, 26.0), prof=16.0)
# veroboard sul fondo, USB-C del Seed contro il fianco sinistro
DISTANZIALE = 4.0
USB_GIOCO = 0.6
Y_SCHEDA_DIETRO = 88.0
# microSD sul fondo, fessura nella parete frontale
SD_SCHEDA = dict(x=(130.0, 156.0), y=None, z=(4.9, 8.5), prof=18.0)


# =========================================================== pezzi stampati in PETG per la 1590DD
# staffa del display: barra sotto il circuito, due piedini che lo spingono contro il pannello, due colonne
# alle estremità fino al pannello; la vite M2,5x8 scende dal pannello nel foro pilota (5,5 mm nel PETG)
STAFFA = dict(barra=(75.0, 4.5, 2.2), piedino=(4.0, 4.0, 1.5), colonna_d=6.0, pilota=2.2, pilota_prof=6.5)
# distanziale della millefori dei tasti: vite M2,5x12 dal pannello, passante, dado sotto la millefori
DIST_TASTI = dict(d=6.0, foro=2.7 + C.TOL_FORI)
# colonnina della veroboard: vite M3x12 dal fondo, passante, dado sopra la veroboard. Alta 4,0 esatti:
# sopra il Seed restano 1,2 mm prima dei pot
COLONNINA = dict(d=7.0, foro=3.2 + C.TOL_FORI)
DADO_M3, DADO_M25 = (6.4, 2.4), (5.5, 2.0)          # diametro sugli spigoli, altezza
# fori di fissaggio della veroboard: gli stessi del case stampato, da hardware/layout.py
FORI_SCATOLA = C.L.FORI_FISSAGGIO


def h_colonna_staffa():
    O = C.OLED
    return O["vetro_h"] + O["pcb"][2] + STAFFA["piedino"][2] + STAFFA["barra"][2]


def staffa_scatola():
    """staffa del display in posizione di stampa: barra sul piatto, piedini e colonne verso l'alto"""
    O = C.OLED
    bl, bw, bh = STAFFA["barra"]
    pw, pd, ph = STAFFA["piedino"]
    h = h_colonna_staffa()
    s = Pos(0, 0, bh / 2) * Box(bl, bw, bh)
    for sx in (-1, 1):
        s += Pos(sx * O["piedino_x"], 0, bh + ph / 2 - 0.01) * Box(pw, pd, ph + 0.02)
        s += Pos(sx * O["vite_x"], 0, h / 2) * C.cil(STAFFA["colonna_d"], h)
        s -= Pos(sx * O["vite_x"], 0, h - STAFFA["pilota_prof"] / 2 + 0.01) * C.cil(STAFFA["pilota"],
                                                                                   STAFFA["pilota_prof"] + 0.02)
    return s


def h_distanziale_tasti():
    return Z_CIELO_IN - (H_EST + TASTO_SPORGE - TASTO_PILA)


def tubo(d, foro, h):
    return Pos(0, 0, h / 2) * C.cil(d, h) - Pos(0, 0, h / 2) * C.cil(foro, h + 1)


def distanziale_tasti():
    return tubo(DIST_TASTI["d"], DIST_TASTI["foro"], h_distanziale_tasti())


def colonnina_veroboard():
    return tubo(COLONNINA["d"], COLONNINA["foro"], DISTANZIALE)


def z_scheda():
    return Z_FONDO_IN + DISTANZIALE


def spostamento_scheda():
    """traslazione della veroboard da case.py alla scatola"""
    dz = z_scheda() - C.Z_SCHEDA
    z_usb = C.usb_z() + dz
    x0 = parete(z_usb)[0] + USB_GIOCO + C.SEED["usb_oltre_pin1"]
    return x0 - C.X_STRISCIA0, Y_SCHEDA_DIETRO - C.Y_SCHEDA_DIETRO, dz


def componenti(comp_cuneo):
    """[(nome, solido, gruppo)] nella scatola"""
    dx, dy, dz = spostamento_scheda()
    c = [(n, Pos(dx, dy, dz) * s, g) for n, s, g in comp_cuneo if g == "scheda"]

    # pannello dei comandi
    P, E, O = C.POT, C.ENC, C.OLED
    for x in POT_X:
        for y in POT_Y:
            c.append((f"pot {x:.0f},{y:.0f}", sotto_cielo(x, y, *P["corpo"], P["prof"] + P["pin"]), "comandi"))
            c.append((f"manopola {x:.0f},{y:.0f}", Pos(x, y, H_EST + P["dado"] + 0.5 + P["manopola"][1] / 2)
                      * C.cil(P["manopola"][0], P["manopola"][1]), "manopole"))
    c.append(("encoder", sotto_cielo(*ENC_C, *E["corpo"], E["prof"] + E["pin"]), "comandi"))
    c.append(("manopola encoder", Pos(*ENC_C, H_EST + E["dado"] + 0.5 + E["manopola"][1] / 2)
              * C.cil(E["manopola"][0], E["manopola"][1]), "manopole"))
    ox, oy = OLED_C
    z = Z_CIELO_IN
    c.append(("OLED vetro", Pos(ox, oy, z - O["vetro_h"] / 2 - 0.02) * Box(*O["vetro"], O["vetro_h"] - 0.04), "oled"))
    z -= O["vetro_h"]
    c.append(("OLED circuito", Pos(ox, oy, z - O["pcb"][2] / 2) * Box(*O["pcb"][:2], O["pcb"][2]), "oled"))
    z -= O["pcb"][2]
    rw, rh, rz = O["retro"]
    c.append(("OLED componenti sul retro", Pos(ox, oy, z - rz / 2) * Box(rw, rh, rz), "oled"))
    # staffe stampate: la cima delle colonne tocca il pannello, i piedini il circuito
    for sy in (-1, 1):
        c.append((f"staffa OLED {sy:+d}", Pos(ox, oy + sy * O["staffa_y"], Z_CIELO_IN - h_colonna_staffa())
                  * staffa_scatola(), "stampati"))
    # tasti su millefori appesa sotto il pannello
    w_scheda = H_EST + TASTO_SPORGE - TASTO_PILA      # faccia superiore della millefori
    xs = [x for x, _ in TASTI]
    c.append(("scheda tasti", Pos((min(xs) + max(xs)) / 2, TASTI[0][1], w_scheda - 1.6 / 2 - 0.75)
              * Box(max(xs) - min(xs) + 25.0, 25.5, 1.6 + 1.5), "tasti"))
    xk = (TASTI[0][0] + TASTI[1][0]) / 2
    for sy in (-1, 1):
        yk = TASTI[0][1] + sy * 8.75
        c.append((f"distanziale tasti {sy:+d}", Pos(xk, yk, w_scheda) * distanziale_tasti(), "stampati"))
        c.append((f"dado M2,5 tasti {sy:+d}", Pos(xk, yk, w_scheda - 1.6 - DADO_M25[1] / 2) * C.cil(*DADO_M25), "tasti"))
    for i, (x, y) in enumerate(TASTI):
        c.append((f"tasto K{i + 1}", Pos(x, y, w_scheda + 3.5 / 2) * Box(12, 12, 3.5), "tasti"))
        z_flangia = w_scheda + 3.5 + 1.3
        c.append((f"flangia cappuccio K{i + 1}", Pos(x, y, z_flangia + 0.45) * C.cil(12.8, 0.9), "tasti"))
    c.append(("LED", sotto_cielo(*LED_C, C.LED["d"], 0, 8.0, True), "comandi"))
    # footswitch e LED del bypass
    bw, bd, bh = C.FS["corpo"]
    c.append(("footswitch 3PDT", sotto_cielo(*FS_C, bw, bd, bh), "comandi"))
    (nd, nh), (ad, ah) = C.FS["dado"], C.FS["attuatore"]
    c.append(("dado footswitch", Pos(*FS_C, H_EST + nh / 2 + 0.02) * C.cil(nd, nh), "manopole"))
    c.append(("LED bypass", sotto_cielo(*LED_FS_C, C.LED["d"], 0, 8.0, True), "comandi"))

    # retro: corpi dal filo interno della parete, misurato alla quota più alta del corpo
    for (nome, x, tipo) in RETRO:
        if tipo in ("jack35", "jack635q"):
            bw, bh, bd = CORPI_LATO[tipo]
            z = Z_MIDI if tipo == "jack35" else Z_RETRO
            y1 = P_EST - parete(z + bh / 2)[1]
            c.append((nome, C.box(x - bw / 2, x + bw / 2, y1 - bd, y1, z - bh / 2, z + bh / 2), "retro"))
            continue
        d, bd = JACK635["d"], JACK635["prof"]
        y1 = P_EST - parete(Z_RETRO + d / 2)[1]
        c.append((nome, Pos(x, y1 - bd / 2, Z_RETRO) * Rot(90, 0, 0) * C.cil(d, bd), "retro"))
    mx0, mx1 = MIDI_SCHEDA["x"]
    z0, z1 = MIDI_SCHEDA["z"]
    y1 = P_EST - parete(z1)[1]
    c.append(("scheda MIDI", C.box(mx0, mx1, y1 - MIDI_SCHEDA["prof"], y1 - CORPI_LATO["jack35"][2], z0, z1), "retro"))
    for (nome, y, tipo) in DESTRA:
        bw, bh, bd = CORPI_LATO[tipo]
        x1 = L_EST - parete(Z_RETRO + bh / 2)[0]
        c.append((nome, C.box(x1 - bd, x1, y - bw / 2, y + bw / 2, Z_RETRO - bh / 2, Z_RETRO + bh / 2), "destra"))
    # microSD sul fondo contro la parete frontale
    sx0, sx1 = SD_SCHEDA["x"]
    sz0, sz1 = SD_SCHEDA["z"]
    y0 = parete(sz1)[1]
    c.append(("scheda microSD", C.box(sx0, sx1, y0, y0 + SD_SCHEDA["prof"], sz0, sz1), "sd"))
    # colonnine della veroboard sul fondo, dado M3 e punta della vite sopra la scheda
    zt = C.Z_SCHEDA_TOP + dz
    for j, (hx, hy) in enumerate(FORI_SCATOLA):
        x, y = C.foro_xy(hx, hy)
        x, y = x + dx, y + dy
        c.append((f"colonnina veroboard {j + 1}", Pos(x, y, Z_FONDO_IN) * colonnina_veroboard(), "stampati"))
        c.append((f"dado M3 veroboard {j + 1}", Pos(x, y, zt + DADO_M3[1] / 2) * C.cil(*DADO_M3), "viti"))
        c.append((f"punta vite veroboard {j + 1}", Pos(x, y, zt + DADO_M3[1] + 1.0) * C.cil(3.0, 2.0), "viti"))
    return c


def ostacoli_scatola():
    """borchie delle viti e bordino del fondo, come solidi"""
    o = []
    h = Z_CIELO_IN - Z_FONDO_IN
    for i, (x, y) in enumerate(BORCHIE_ANGOLO):
        o.append((f"borchia d'angolo {i + 1}", Pos(x, y, Z_FONDO_IN + h / 2) * C.cil(BORCHIA_D, h)))
    for i, (x0, x1, y0, y1) in enumerate(BORCHIE):
        o.append((f"borchia centrale {'davanti' if i == 0 else 'dietro'}", C.box(x0, x1, y0, y1, Z_FONDO_IN, Z_CIELO_IN)))
    bw, bz = BORDO_FONDO
    tx, ty = parete(bz)
    for nome, b in (("bordino davanti", (tx, L_EST - tx, ty, ty + bw)),
                    ("bordino dietro", (tx, L_EST - tx, P_EST - ty - bw, P_EST - ty)),
                    ("bordino sinistro", (tx, tx + bw, ty, P_EST - ty)),
                    ("bordino destro", (L_EST - tx - bw, L_EST - tx, ty, P_EST - ty))):
        o.append((nome, C.box(*b, Z_FONDO_IN, bz)))
    return o


def fuori_cavita(s, gruppo):
    """quanto il corpo esce dalle pareti (sformo compreso) o dal fondo/cielo; 0 se dentro"""
    if gruppo == "manopole":
        return 0.0
    bb = s.bounding_box()
    z_alto = min(bb.max.Z, Z_CIELO_IN)
    tx, ty = parete(z_alto)
    fuori = [tx - bb.min.X, bb.max.X - (L_EST - tx), ty - bb.min.Y, bb.max.Y - (P_EST - ty),
             Z_FONDO_IN - bb.min.Z, bb.max.Z - Z_CIELO_IN]
    # i corpi montati a una parete la toccano per costruzione: si controllano solo le altre
    if gruppo == "retro":
        fuori[3] = 0.0
    if gruppo == "destra":
        fuori[1] = 0.0
    if gruppo in ("comandi", "oled", "stampati", "tasti"):
        fuori[5] = 0.0
    if gruppo == "sd":
        fuori[2] = 0.0
    return max(0.0, max(fuori))


def verifica_fori_veroboard():
    return C.L.fori_fissaggio_errori(FORI_SCATOLA)


def verifica(comp):
    errori, note = verifica_fori_veroboard(), []
    for n, s, g in comp:
        f = fuori_cavita(s, g)
        if f > 0.05:
            errori.append(f"{n} esce dalla scatola di {f:.1f} mm")
    for na, sa in ostacoli_scatola():
        for n, s, g in comp:
            if g == "manopole":
                continue
            v = C.urti(sa, s)
            if v:
                errori.append(f"COLLISIONE {n} / {na}: {v:.1f} mm³")
    for i in range(len(comp)):
        for j in range(i + 1, len(comp)):
            (na, sa, ga), (nb, sb, gb) = comp[i], comp[j]
            if ga == gb and ga in ("scheda", "oled", "manopole", "tasti"):
                continue
            v = C.urti(sa, sb)
            if v:
                errori.append(f"COLLISIONE {na} / {nb}: {v:.1f} mm³")
    # aria fra le manopole e dal footswitch
    pots = [(x, y) for x in POT_X for y in POT_Y]
    d_min = min(math.dist(a, b) for i, a in enumerate(pots) for b in pots[i + 1:]) - C.POT["manopola"][0]
    d_enc = min(math.dist(ENC_C, p) for p in pots) - (C.POT["manopola"][0] + C.ENC["manopola"][0]) / 2
    d_fs = min(math.dist(FS_C, p) for p in pots) - (C.FS["dado"][0] + C.POT["manopola"][0]) / 2
    note.append(f"aria fra le manopole: pot-pot {d_min:.1f} mm, encoder-pot {d_enc:.1f}, footswitch-pot {d_fs:.1f}")
    if d_min < 9.5:
        errori.append(f"manopole dei pot a {d_min:.1f} mm (minimo 9,5)")
    # boccole: filetto libero oltre la parete per il dado
    for nome, bocc, dado in (("pot", C.POT["boccola"], C.POT["dado"]), ("encoder", C.ENC["boccola"], C.ENC["dado"])):
        libero = bocc - T_CIELO - dado
        note.append(f"{nome}: {libero:.1f} mm di filetto oltre il dado")
        if libero < 0.3:
            errori.append(f"{nome}: la boccola non chiude il dado su {T_CIELO} mm di pannello")
    z_fl = H_EST + TASTO_SPORGE - TASTO_PILA + 3.5 + 1.3 + 0.9
    note.append(f"tasti: flangia del cappuccio {Z_CIELO_IN - z_fl:.1f} mm sotto il pannello, sporgono {TASTO_SPORGE:g} mm")
    if not 0.2 <= Z_CIELO_IN - z_fl <= 1.0:
        errori.append("tasti: la flangia del cappuccio non sta appena sotto il pannello")
    note.append(f"parete posteriore: {parete(Z_RETRO)[1]:.2f} mm ai jack da 6,35, {parete(Z_MIDI)[1]:.2f} ai jack "
                f"MIDI (Thonkiconn massimo 3,0)")
    return errori, note


def disegna(comp, nome_file):
    """vista dall'alto e vista da dietro, per controllo a occhio"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colori = {"scheda": "#7a8793", "comandi": "#c0562f", "oled": "#2f6fb0", "manopole": "#e0b44c",
              "retro": "#3b8f5a", "destra": "#3b8f5a", "sd": "#8a4fb0", "stampati": "#d4a017",
              "tasti": "#c0562f", "viti": "#555555"}
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 10.5), dpi=120, gridspec_kw={"height_ratios": [120, 45]})
    for ax, (i, j), titolo in ((a1, (0, 1), "dall'alto"), (a2, (0, 2), "da dietro, in trasparenza")):
        ax.add_patch(plt.Rectangle((0, 0), L_EST, P_EST if i == 0 and j == 1 else H_EST, fill=False, lw=1.5))
        for n, s, g in comp:
            if g == "manopole" and j == 2:
                continue
            bb = s.bounding_box()
            lo = (bb.min.X, bb.min.Y if j == 1 else bb.min.Z)
            hi = (bb.max.X, bb.max.Y if j == 1 else bb.max.Z)
            ax.add_patch(plt.Rectangle(lo, hi[0] - lo[0], hi[1] - lo[1], alpha=0.35 if g != "manopole" else 0.15,
                                       color=colori.get(g, "#444"), lw=0))
        for na, sa in ostacoli_scatola():
            bb = sa.bounding_box()
            if j == 1:
                ax.add_patch(plt.Rectangle((bb.min.X, bb.min.Y), bb.size.X, bb.size.Y, color="#222", alpha=0.5, lw=0))
        ax.set_aspect("equal")
        ax.set_title(titolo)
        ax.grid(alpha=0.2)
    a1.set_xlim(-5, L_EST + 5)
    a1.set_ylim(-5, P_EST + 5)
    a2.set_xlim(-5, L_EST + 5)
    a2.set_ylim(-3, H_EST + 5)
    fig.tight_layout()
    fig.savefig(OUT / nome_file)


# =========================================================== fori e dime
# diametri da trapano su alluminio; Tayda chiede +0,4 mm se la scatola è verniciata a polvere
D_FORO = dict(pot=7.5, encoder=7.5, footswitch=12.0, tasto=12.0, led=3.2, vite=3.0,
              jack635=10.0, jack635q=10.0, jack35=6.2, dc=12.0, levetta=6.2, fondo=3.2)
H_CORPO = H_EST - T_FONDO                 # altezza delle facce laterali, senza fondo
FACCE = {   # nome: (larghezza, altezza, descrizione della vista)
    "pannello": (L_EST, P_EST, "pannello dei comandi, visto da sopra, il fronte in basso"),
    "retro": (L_EST, H_CORPO, "retro, visto da dietro, il fondo in basso"),
    "destra": (P_EST, H_CORPO, "fianco destro, visto da destra, il fronte a sinistra"),
    "sinistra": (P_EST, H_CORPO, "fianco sinistro, visto da sinistra, il fronte a destra"),
    "fronte": (L_EST, H_CORPO, "fronte, visto davanti, il fondo in basso"),
    "fondo": (L_EST, P_EST, "fondo, visto dall'interno (appoggiato com'è montato), il fronte in basso"),
}


def uv(faccia, x, y, z):
    """dalle coordinate della scatola a quelle della faccia vista da fuori (origine in basso a sinistra)"""
    return {"pannello": (x, y), "retro": (L_EST - x, z - T_FONDO), "destra": (y, z - T_FONDO),
            "sinistra": (P_EST - y, z - T_FONDO), "fronte": (x, z - T_FONDO), "fondo": (x, y)}[faccia]


def fori():
    """[(faccia, codice, nome, u, v, diametro o (largo, alto))]: codice corto sul disegno, nome in tabella"""
    f = []
    for j, (y, x) in enumerate((y, x) for y in POT_Y for x in POT_X):
        f.append(("pannello", f"P{j + 1}", "pot", x, y, D_FORO["pot"]))
    f.append(("pannello", "ENC", "encoder", *ENC_C, D_FORO["encoder"]))
    for i, (x, y) in enumerate(TASTI):
        f.append(("pannello", f"K{i + 1}", f"tasto K{i + 1}", x, y, D_FORO["tasto"]))
    f.append(("pannello", "L1", "LED di stato", *LED_C, D_FORO["led"]))
    f.append(("pannello", "L2", "LED del bypass", *LED_FS_C, D_FORO["led"]))
    f.append(("pannello", "FS", "footswitch 3PDT", *FS_C, D_FORO["footswitch"]))
    s = 1.0 if C.OLED_PIATTINA_DAVANTI else -1.0          # l'area visibile sta dal lato opposto alla piattina
    ox, oy = OLED_C
    va = (round(C.OLED["va"][0] + 0.2, 1), round(C.OLED["va"][1] + 0.2, 1))
    f.append(("pannello", "OLED", "finestra del display (piattina verso il fronte)", ox, oy + s * C.OLED["off_va"], va))
    j = 0
    for sy in (1, -1):
        for sx in (-1, 1):
            j += 1
            f.append(("pannello", f"S{j}", "vite M2,5 delle staffe del display", ox + sx * C.OLED["vite_x"],
                      oy + sy * C.OLED["staffa_y"], D_FORO["vite"]))
    xk = (TASTI[0][0] + TASTI[1][0]) / 2
    for j, sy in enumerate((1, -1)):
        f.append(("pannello", f"T{j + 1}", "vite M2,5 della scheda tasti", xk, TASTI[0][1] + sy * 8.75, D_FORO["vite"]))
    codici = {"MIDI IN": "MI", "MIDI OUT": "MO", "PEDALE": "PED", "IN L": "IL", "IN R": "IR", "OUT L": "OL",
              "OUT R": "OR", "DC 9V": "DC", "INST/LINE": "SW"}
    for (nome, x, tipo) in RETRO:
        z = Z_MIDI if tipo == "jack35" else Z_RETRO
        f.append(("retro", codici[nome], nome, *uv("retro", x, 0, z), D_FORO[tipo]))
    for (nome, y, tipo) in DESTRA:
        f.append(("destra", codici[nome], nome, *uv("destra", 0, y, Z_RETRO), D_FORO[tipo]))
    dx, dy, dz = spostamento_scheda()
    y_usb = C.seed_y_centro() + dy
    f.append(("sinistra", "USB", "USB-C del Seed3 (asola)", *uv("sinistra", 0, y_usb, C.usb_z() + dz),
              C.SEED["usb_taglio"]))
    x_sd = sum(SD_SCHEDA["x"]) / 2
    f.append(("fronte", "SD", "microSD, posizione indicativa: fora dopo aver fissato la scheda",
              *uv("fronte", x_sd, 0, SD_SCHEDA["z"][1] - 1.1), (13.0, 2.6)))
    for j, (hx, hy) in enumerate(FORI_SCATOLA):
        x, y = C.foro_xy(hx, hy)
        f.append(("fondo", f"V{j + 1}", "vite M3 della veroboard", x + dx, y + dy, D_FORO["fondo"]))
    return f


def misura(d):
    return f"{d[0]:g} × {d[1]:g}" if isinstance(d, tuple) else f"Ø {d:g}"


def svg_faccia(faccia, lista):
    w, h, _ = FACCE[faccia]
    el = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="3" class="bordo"/>',
          f'<line x1="{w / 2}" y1="0" x2="{w / 2}" y2="{h}" class="asse"/>',
          f'<line x1="0" y1="{h / 2}" x2="{w}" y2="{h / 2}" class="asse"/>']
    for (_, cod, _, u, v, d) in lista:
        y = h - v
        if isinstance(d, tuple):
            a, b = d
            el.append(f'<rect x="{u - a / 2:.2f}" y="{y - b / 2:.2f}" width="{a:.2f}" height="{b:.2f}" rx="0.8" class="foro"/>')
            rx, ry = a / 2, b / 2
        else:
            rx = ry = d / 2
            el.append(f'<circle cx="{u:.2f}" cy="{y:.2f}" r="{rx:.2f}" class="foro"/>')
        el.append(f'<line x1="{u - rx - 1.5:.2f}" y1="{y:.2f}" x2="{u + rx + 1.5:.2f}" y2="{y:.2f}" class="croce"/>')
        el.append(f'<line x1="{u:.2f}" y1="{y - ry - 1.5:.2f}" x2="{u:.2f}" y2="{y + ry + 1.5:.2f}" class="croce"/>')
        if isinstance(d, tuple):                 # rettangoli: etichetta dentro, in alto a sinistra
            tx, ty, anc = u - rx + 1.0, y - ry + 3.2, "start"
        elif rx >= 5.0:                          # fori grandi: sotto, al centro
            tx, ty, anc = u, y + ry + 4.4, "middle"
        else:
            tx, ty, anc = u + rx + 1.2, y - ry - 0.8, "start"
        el.append(f'<text x="{tx:.2f}" y="{ty:.2f}" text-anchor="{anc}" class="nota">{cod}</text>')
    return (f'<svg width="{w}mm" height="{h}mm" viewBox="-0.5 -0.5 {w + 1} {h + 1}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(el) + "</svg>")


def dima_html(lista):
    righe = []
    for faccia, (w, h, descr) in FACCE.items():
        sel = [f for f in lista if f[0] == faccia]
        if not sel:
            continue
        tab = "".join(f"<tr><td class='cod'>{c}</td><td>{n}</td><td>{u - w / 2:+.1f}</td><td>{v - h / 2:+.1f}</td>"
                      f"<td>{misura(d)}</td></tr>" for (_, c, n, u, v, d) in sel)
        righe.append(f"""
<section class="faccia">
  <h2>{descr} · {w:g} × {h:g} mm</h2>
  <div class="riga">{svg_faccia(faccia, sel)}
  <table><thead><tr><th></th><th>Foro</th><th>X</th><th>Y</th><th>Misura</th></tr></thead>
  <tbody>{tab}</tbody></table></div>
</section>""")
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Dima 1590DD PA-TELAIO</title>
<style>
  @page {{ size: A4 landscape; margin: 8mm; }}
  body {{ font-family: Helvetica, Arial, sans-serif; font-size: 8pt; color: #111; margin: 0; }}
  h1 {{ font-size: 12pt; margin: 0 0 1.5mm; }}
  h2 {{ font-size: 9pt; margin: 0 0 1.5mm; }}
  p {{ margin: 0 0 1.5mm; max-width: 270mm; }}
  .faccia {{ break-inside: avoid; margin-bottom: 5mm; }}
  .riga {{ display: flex; gap: 5mm; align-items: flex-start; }}
  svg {{ display: block; overflow: visible; flex: none; }}
  .bordo {{ fill: none; stroke: #111; stroke-width: 0.3; }}
  .asse {{ stroke: #999; stroke-width: 0.15; stroke-dasharray: 2 1.5; }}
  .foro {{ fill: none; stroke: #c0392b; stroke-width: 0.25; }}
  .croce {{ stroke: #111; stroke-width: 0.12; }}
  .nota {{ font-size: 2.6px; font-weight: bold; fill: #1f4e8c; }}
  table {{ border-collapse: collapse; font-size: 7.5pt; }}
  td, th {{ border-bottom: 0.2mm solid #ccc; padding: 0.5mm 2.5mm 0.5mm 0; text-align: left; font-variant-numeric: tabular-nums; }}
  td.cod {{ font-weight: bold; color: #1f4e8c; }}
  .scala line {{ stroke: #111; stroke-width: 0.3; }}
</style></head><body>
<h1>PA-TELAIO · dima di foratura per scatola 1590DD (Hammond, Musikding Typ DD, Tayda 1590DD)</h1>
<p>Stampa al 100 %, senza adattare alla pagina: la barra qui sotto deve misurare 100 mm. Ritaglia ogni faccia sul bordo
nero, fissala con nastro di carta, segna i centri con il bulino, fora con una punta da 3 mm e allarga con la punta a
gradino. X e Y sono i millimetri dal centro della faccia (X a destra, Y in alto nella vista indicata): sono le coordinate
da dare a Tayda, che su scatola verniciata vuole 0,4 mm in più sui diametri.</p>
<svg width="104mm" height="5mm" viewBox="0 0 104 5" class="scala"><line x1="2" y1="2.5" x2="102" y2="2.5"/>
<line x1="2" y1="0.5" x2="2" y2="4.5"/><line x1="52" y1="1.3" x2="52" y2="3.7"/><line x1="102" y1="0.5" x2="102" y2="4.5"/></svg>
{"".join(righe)}
</body></html>"""


def esporta_pezzi():
    """STL dei pezzi in PETG, già orientati, e un piatto unico con tutti gli 8 pezzi a 25 mm fra loro"""
    d = OUT / "stampa"
    d.mkdir(exist_ok=True)
    pezzi = {"staffa_oled_1590DD": (staffa_scatola(), 2), "distanziale_tasti_1590DD": (distanziale_tasti(), 2),
             "colonnina_veroboard_1590DD": (colonnina_veroboard(), 4)}
    for nome, (s, _) in pezzi.items():
        export_stl(s, str(d / f"{nome}.stl"))
    passo = 25.0                          # due brim da 10 mm e 5 di aria, come piatto_unico.py
    bl, bw, _ = STAFFA["barra"]
    piatto = [Pos(0, i * (STAFFA["colonna_d"] + passo), 0) * staffa_scatola() for i in range(2)]
    tubi = [distanziale_tasti()] * 2 + [colonnina_veroboard()] * 4
    y0 = 2 * (STAFFA["colonna_d"] + passo)
    for i, t in enumerate(tubi):
        piatto.append(Pos(-bl / 2 + 3.5 + (i % 3) * (bl - 7.0) / 2, y0 + (i // 3) * (COLONNINA["d"] + passo), 0) * t)
    export_stl(Compound(piatto), str(d / "pezzi_interni_1590DD.stl"))
    for nome, (s, n) in pezzi.items():
        bb = s.bounding_box()
        print(f"  {nome} x{n}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, {s.volume / 1000:.2f} cm³")
    print(f"  pezzi da stampare in {d}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    comp = componenti(C.componenti())
    errori, note = verifica(comp)
    dx, dy, dz = spostamento_scheda()
    bb = C.box(*C.SCHEDA_X, *C.SCHEDA_Y, C.Z_SCHEDA, C.Z_SCHEDA_TOP).bounding_box()
    print(f"Scatola 1590DD {L_EST:.0f} x {P_EST:.0f} x {H_EST:.0f}, dentro alta {Z_CIELO_IN - Z_FONDO_IN:.1f}")
    print(f"  veroboard: x {bb.min.X + dx:.1f}-{bb.max.X + dx:.1f}, y {bb.min.Y + dy:.1f}-{bb.max.Y + dy:.1f}, "
          f"faccia sopra a z {C.Z_SCHEDA_TOP + dz:.1f}")
    alti = sorted(((s.bounding_box().max.Z, n) for n, s, g in comp if g == "scheda"), reverse=True)[:3]
    print("  più alti sulla scheda: " + ", ".join(f"{n} a z {z:.1f}" for z, n in alti))
    for n in note:
        print("  " + n)
    disegna(comp, "ingombri.png")
    if errori:
        print(f"ERRORI ({len(errori)}):")
        for e in errori:
            print(" -", e)
        sys.exit(1)
    lista = fori()
    (OUT / "dima_1590DD.html").write_text(dima_html(lista))
    # Tayda: su scatola verniciata a polvere i diametri crescono di 0,4 mm (si fora prima di verniciare)
    for nome_file, extra in (("coordinate_tayda.csv", 0.0), ("coordinate_tayda_verniciata.csv", 0.4)):
        with open(OUT / nome_file, "w") as fh:
            fh.write("faccia;foro;x_dal_centro_mm;y_dal_centro_mm;diametro_o_rettangolo_mm\n")
            for faccia, c, n, u, v, d in lista:
                w, h, _ = FACCE[faccia]
                m = (f"{d[0] + extra:g}x{d[1] + extra:g}" if isinstance(d, tuple) else f"{d + extra:g}")
                fh.write(f"{faccia};{c} {n};{u - w / 2:.2f};{v - h / 2:.2f};{m}\n")
    print(f"  {len(lista)} fori: dima in {OUT / 'dima_1590DD.html'}, coordinate in coordinate_tayda.csv")
    esporta_pezzi()
    print(f"OK: {len(comp)} corpi nella 1590DD, nessuna collisione.")


if __name__ == "__main__":
    main()
