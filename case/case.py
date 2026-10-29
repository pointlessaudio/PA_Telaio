# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0"]
# ///
"""
PA-TELAIO — case stampato in 3D (variante A: cuneo, pot a 28 mm).

Sorgente di verità della meccanica, come hardware/layout.py lo è per la veroboard.
Costruisce i pezzi da stampare (vasca, pannello superiore, pannello posteriore, due staffe per
l'OLED) e due piastre di prova per tarare i fori, poi controlla le collisioni fra i pezzi
stampati e i componenti reali. La veroboard viene letta da hardware/layout.py, componente
per componente.

Uso (da case/):
    uv run case.py                 # costruisce, verifica, esporta in case/out/
    uv run case.py --solo-verifica # niente export
Deve finire con "OK ... nessuna collisione".

Coordinate: X da sinistra a destra visto da chi suona, Y dal fronte al retro, Z in su;
origine nello spigolo anteriore sinistro, sotto il fondo. Misure in mm.
"""
import math
import sys
from pathlib import Path

from build123d import (Axis, Box, Color, Compound, Cylinder, Plane, Pos, Rectangle, RectangleRounded,
                       Rot, export_gltf, export_step, export_stl, extrude, fillet, import_svg,
                       scale)

QUI = Path(__file__).resolve().parent
OUT = QUI / "out"
LOGO_SVG = QUI.parent.parent / "_studio" / "brand" / "assets" / "pointless_logo.svg"
sys.path.insert(0, str(QUI.parent / "hardware"))
import layout as L  # noqa: E402  (veroboard verificata)

# =========================================================== involucro
W, D = 210.0, 134.0          # pianta
HF, HB = 25.0, 47.0          # quota della faccia superiore: davanti / dietro
R_PIANTA = 8.0               # raggio degli spigoli verticali
T_TOP = 3.0                  # pannello superiore
T_WALL = 2.4                 # pareti della vasca
T_FLOOR = 2.4                # fondo
T_REAR = 2.4                 # pannello posteriore: lastra piatta, dentro contro la parete
R_PANNELLO = 3.0             # raccordo degli angoli del pannello posteriore (sul piatto non si alzano)
TACCA_Z0 = T_FLOOR + 3.0     # base della finestra nella parete posteriore
GIOCO = 0.3                  # gioco negli accoppiamenti fra pezzi stampati (PETG)
TOL_FORI = 0.3               # maggiorazione dei fori per componenti: tarala con le piastre di prova
# Niente smussi né raccordi sui lati che appoggiano sul piatto: OrcaSlicer li tratta come sporgenze e
# accende la ventola sui primi strati, e col PETG i bordi si alzano (prima stampa di a4-stand, 28/09).
# Lo schiacciamento del primo strato lo compensa lo slicer (elephant foot 0,15 mm).
LABBRO_H, LABBRO_T = 2.0, 1.6  # labbro di centraggio sotto il pannello superiore
Z_GIUNTO = 12.0              # quota d'incontro fra colonne della vasca e torrette del pannello

Y_PANNELLO_EST = D - T_WALL - GIOCO           # faccia esterna del pannello posteriore
Y_PANNELLO_INT = Y_PANNELLO_EST - T_REAR      # faccia interna
ALPHA = math.atan((HB - HF) / D)
L_TOP = D / math.cos(ALPHA)
T_TOP_V = T_TOP / math.cos(ALPHA)  # spessore misurato in verticale
NORMALE = (0.0, -math.sin(ALPHA), math.cos(ALPHA))
PIANO_TOP = Plane(origin=(0, 0, HF), x_dir=(1, 0, 0), z_dir=NORMALE)


def z_top(y):
    return HF + (HB - HF) * y / D


def z_sotto(y):
    """quota della faccia inferiore del pannello superiore"""
    return z_top(y) - T_TOP_V


def sul_top(x, y, w=0.0):
    """Location sulla faccia superiore sopra il punto di pianta (x, y); w lungo la normale"""
    n = NORMALE
    o = (x + w * n[0], y + w * n[1], z_top(y) + w * n[2])
    return Plane(origin=o, x_dir=(1, 0, 0), z_dir=n).location


def lungo_pendenza(y, dv):
    """y di pianta spostato di dv misurati lungo la faccia inclinata"""
    return y + dv * math.cos(ALPHA)


# =========================================================== pannello: posizioni in pianta
OLED_C = (44.0, 83.0)            # centro dell'area visibile, allineato al centro della griglia dei pot
ENC_C = (99.0, 83.0)
POT_X = (132.0, 160.0, 188.0)    # 28 mm fra i centri
POT_Y = (101.0, 65.0)            # fila dietro, fila davanti: 36 mm, 20 mm d'aria fra le manopole
TASTI = ((33.0, 26.0), (55.0, 26.0))
LED_C = (72.0, 26.0)
FS_C = (182.0, 26.0)             # footswitch 3PDT: true bypass stereo
LED_FS_C = (163.0, 26.0)         # LED del bypass, sul terzo polo del 3PDT
LOGO_C, LOGO_W, LOGO_PROF = (117.5, 26.0), 42.0, 0.5   # 0,5 = primo strato 0,2 + uno da 0,3
# stampa professionale (MJF/SLS PA12): tratto di almeno 0,5 mm e incisione di 1 mm, dalle linee guida
# PA12 MJF; a 48 mm il tratto più sottile è 0,50
LOGO_SERVIZIO = (48.0, 1.0)
LOGO_TRATTO_MIN = 0.0105         # tratto bianco più sottile / larghezza (misurato sul vettoriale)

# =========================================================== componenti (misure da datasheet)
# Pot Alpha 9 mm RD901F-40-15R1: boccola M7x0,75 lunga 5, albero liscio 6 mm lungo 15.
POT = dict(foro=7.0, boccola=5.0, dado=2.0, corpo=(11.5, 10.0), prof=7.0, pin=4.0,
           tasca=0.6, tasca_xy=(13.5, 12.0), manopola=(16.0, 15.0))   # corpo ruotato: pin verso il fianco
# Encoder Bourns PEC11R-4220K-S0024: boccola M7x0,75 lunga 7, albero 20, corpo 12,5x13,4x6,5.
ENC = dict(foro=7.0, boccola=7.0, dado=2.0, corpo=(12.5, 13.4), prof=6.5, pin=4.5,
           manopola=(22.0, 16.0))
# OLED Waveshare 2,42" SSD1309 (disegni 2D/3D Waveshare): vetro 60,5x37 centrato sul circuito
# 61,51x39,51; area visibile 57,01x29,49 spostata di 2,68 mm verso il lato opposto alla piattina.
# I 4 fori del modulo stanno sotto il vetro: il modulo si centra in una sede nel pannello e lo
# tengono due staffe stampate che premono gli angoli del circuito, avvitate fuori dall'ingombro.
OLED = dict(pcb=(61.51, 39.51, 1.6), vetro=(60.5, 37.0), va=(57.01, 29.49), aa=(55.01, 27.49), off_va=2.68,
            vetro_h=2.4, retro=(54.4, 30.0, 3.5), sede=(61.1, 38.8), sede_prof=1.0,
            staffa=(75.0, 4.5, 2.2), piedino=(4.0, 4.0, 1.5), piedino_x=27.75,
            staffa_y=17.5, vite_x=34.5)
OLED_PIATTINA_DAVANTI = True     # piattina del vetro verso chi suona: da confermare al collaudo
# Tasti: tattili 12x12x7,3 con cappuccio tondo, su una millefori sotto il pannello.
TASTO = dict(cappuccio=11.8, gioco=0.3, pila=10.0, sporgenza=1.5)
SCHEDA_TASTI = dict(x=(26.0, 76.0), y=(11.0, 36.5), fori=((44.0, 15.0), (44.0, 32.5)))
LED = dict(d=3.0)
# Footswitch 3PDT (9 terminali, boccola M12x0,75): corpo 17,5x17,5, alto 22,5 mm con i terminali.
# Sotto il pannello una torre fino al fondo porta al fondo della vasca il carico del piede.
FS = dict(foro=12.0, max_pannello=6.0, corpo=(18.0, 18.0, 22.5), attuatore=(12.0, 13.0),
          dado=(16.0, 3.0), torre_luce=21.0, torre_parete=2.4, fessura=(9.0, 7.0))
# LED del bypass da 3 mm: entra da sotto in un manicotto, cupola a filo del pannello
LED_FS = dict(d=3.0, lungo=5.3, manicotto=7.0)
# Retro, da sinistra: (nome, x, tipo). Centri tutti alla stessa quota, bassa: sopra i jack da 6,35
# (30 mm di corpo) passa la fila dietro dei pot.
Z_RETRO = 18.5
RETRO = [
    ("DC 9V", 22.0, "dc"),
    ("MIDI IN", 44.0, "jack35"),
    ("MIDI OUT", 58.0, "jack35"),
    ("INST/LINE", 76.0, "levetta"),
    ("PEDALE", 93.0, "jack635"),
    ("IN L", 125.0, "jack635"),
    ("IN R", 146.0, "jack635"),
    ("OUT L", 167.0, "jack635"),
    ("OUT R", 188.0, "jack635"),
]
# foro, spessore massimo del pannello, corpo dietro al pannello (largo, alto, profondo)
TIPI_RETRO = {
    "jack635": dict(foro=9.6, max_pannello=5.0, corpo=(16.0, 17.0, 30.0)),   # 6,35 mm, boccola 3/8"
    "jack35": dict(foro=6.0, max_pannello=3.0, corpo=(9.0, 10.5, 10.5)),     # Thonkiconn PJ366ST
    "dc": dict(foro=11.0, max_pannello=4.0, corpo=(13.0, 13.0, 22.0)),       # DC 2,1 da pannello
    "levetta": dict(foro=6.0, max_pannello=6.0, corpo=(13.0, 13.0, 20.0)),   # mini deviatore DPDT
}
# Scheda MIDI (millefori saldata sui due Thonkiconn) e scheda microSD
MIDI_SCHEDA = dict(x=(34.0, 66.0), z=(12.5, 35.0), prof=16.0)
SD = dict(x=(T_WALL, 25.0), y=(34.0, 54.0), z=(12.0, 16.5), fessura=(13.0, 2.6), z_fessura=14.4)
# Seed3 (modello STEP ufficiale): USB-C sporge 1,28 mm oltre il circuito, centrata sulla larghezza
SEED = dict(usb_oltre_pin1=2.71, pcb_oltre_pin20=1.43, larghezza=18.0, header_f=8.5,
            header_m=2.54, pcb=1.6, sopra_pcb=2.2, usb_lungo=7.7, usb_z=2.92, usb_alto=3.26,
            usb_taglio=(13.0, 7.0))

# =========================================================== veroboard nella vasca
PASSO = 2.54
DISTANZIALE = 4.0                 # altezza delle colonnine sotto la veroboard
USB_GIOCO = 0.6                   # fra faccia della USB-C e parete sinistra
Y_SCHEDA_DIETRO = 95.0            # bordo posteriore della veroboard
X_STRISCIA0 = T_WALL + USB_GIOCO + SEED["usb_oltre_pin1"]
Y_FORO0 = Y_SCHEDA_DIETRO - PASSO / 2
Z_SCHEDA = T_FLOOR + DISTANZIALE          # faccia inferiore della veroboard
Z_SCHEDA_TOP = Z_SCHEDA + 1.6
# fori di fissaggio della veroboard (foro x, striscia y), da forare a 3,2. Fino al 28/09 c'erano (2,44) e (27,44):
# tagliavano la striscia 44, che porta la massa di OUT L/R, J13 ed R18, stavano sul bordo e non avevano posto
# per la testa della vite. layout.fori_fissaggio_errori() e le teste delle viti nel modello lo escludono.
FORI_FISSAGGIO = L.FORI_FISSAGGIO     # lista e controllo elettrico in hardware/layout.py
TESTA_VITE_SCHEDA = (6.0, 2.4)    # testa della M3 autofilettante sulla veroboard: diametro, altezza
ALTEZZE = {"diode": 3.0, "elco": 12.5, "cap": 6.0, "film": 9.0, "dip8": 11.0}
MARGINI = {"diode": 1.6, "elco": 3.3, "cap": 2.0, "film": 2.0, "dip8": 1.3, "res": 1.6}


def foro_xy(x, y):
    """centro in pianta del foro (x lungo la striscia, y = striscia) della veroboard"""
    return (X_STRISCIA0 + y * PASSO, Y_FORO0 - x * PASSO)


SCHEDA_X = (X_STRISCIA0 - PASSO / 2, X_STRISCIA0 + (L.H - 0.5) * PASSO)
SCHEDA_Y = (Y_FORO0 - (L.W - 0.5) * PASSO, Y_SCHEDA_DIETRO)

# =========================================================== viti e piedini
COLONNE = [(9.5, 9.5), (W - 9.5, 9.5), (125.0, 9.5), (8.5, D - 14.0), (W - 8.5, D - 14.0)]
COLONNA_D, INSERTO_D, INSERTO_PROF = 10.0, 4.0, 6.0    # inserti M3 a caldo: 3 mm di parete intorno
VITE_PASSANTE, TESTA_D, TESTA_PROF = 3.4, 6.0, 3.2     # viti M3 dal fondo
DISTANZIALE_D, PILOTA_M3 = 6.0, 2.6                    # viti autofilettanti per la veroboard
PILOTA_M25 = 2.2
PIEDINI = [(24.0, 16.0), (W - 24.0, 16.0), (24.0, D - 16.0), (W - 24.0, D - 16.0)]
PIEDINO_D, PIEDINO_PROF = 13.0, 0.0   # niente sedi: sarebbero un ponte a ventola spenta nei primi strati
# orecchie: dischi sottili agli spigoli della vasca, solo nel file di stampa. Col PETG senza colla i
# rialzi di a4-stand hanno alzato le estremità (28/09): qui tengono giù gli angoli del fondo pieno.
# Stanno fuori dall'impronta, tranne una fascia sotto il bordo per saldarsi al pezzo: le sedi delle
# viti restano aperte. Si rifilano col cutter.
ORECCHIE_D, ORECCHIE_H = 30.0, 0.4    # 0,4 mm = due strati, sia a 0,2 sia a 0,3
ORECCHIE_DENTRO = 0.5                 # quanto entrano sotto il bordo della vasca


# =========================================================== utilità
def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def pianta(inset=0.0):
    r = max(R_PIANTA - inset, 0.5)
    return Pos(W / 2, D / 2) * RectangleRounded(W - 2 * inset, D - 2 * inset, r)


def prisma(inset=0.0, z0=0.0, z1=HB + 10):
    return Pos(0, 0, z0) * extrude(pianta(inset), z1 - z0)


def fascia(w0, w1):
    """lastra fra due piani paralleli alla faccia superiore (w dalla faccia, positivo in fuori)"""
    return (PIANO_TOP.location * Pos(W / 2, L_TOP / 2, (w0 + w1) / 2)
            * Box(W + 80, L_TOP + 80, w1 - w0))


def cil(d, h):
    return Cylinder(d / 2, h)


def oled_centro_pcb():
    s = -1.0 if OLED_PIATTINA_DAVANTI else 1.0
    # l'area visibile sta dal lato opposto alla piattina: il circuito è spostato verso la piattina
    return OLED_C[0], lungo_pendenza(OLED_C[1], s * OLED["off_va"])


# quote lungo la normale (w, 0 = faccia superiore) della pila dell'OLED
W_VETRO_TOP = -(T_TOP - OLED["sede_prof"])
W_PCB_TOP = W_VETRO_TOP - OLED["vetro_h"]
W_PCB_BOT = W_PCB_TOP - OLED["pcb"][2]
W_STAFFA_TOP = W_PCB_BOT - OLED["piedino"][2]
W_TASTI_PCB = TASTO["sporgenza"] - TASTO["pila"]   # faccia superiore della scheda tasti


# =========================================================== pannello superiore
def logo_solido(prof, larghezza=None):
    facce = [f for f in import_svg(str(LOGO_SVG)) if getattr(f, "area", 0) > 0]
    grezzo = Compound(facce)
    bb = grezzo.bounding_box()
    s = (larghezza or LOGO_W) / bb.size.X
    cx, cy = bb.min.X + bb.size.X / 2, bb.min.Y + bb.size.Y / 2
    # prima scala, poi sposta: scale() non scala una traslazione già applicata
    centrato = Pos(-cx * s, -cy * s) * scale(grezzo, s)
    return Compound([extrude(f, prof + 0.4) for f in centrato.faces()])


def pannello_superiore(logo=None):
    p = prisma() & fascia(-T_TOP, 0)      # bordo vivo: la faccia a vista si stampa sul piatto

    # labbro di centraggio su fronte e fianchi (dietro c'è il pannello posteriore)
    anello = ((prisma(T_WALL + GIOCO) - prisma(T_WALL + GIOCO + LABBRO_T))
              & fascia(-T_TOP - LABBRO_H, -T_TOP + 0.01))
    anello -= box(-1, W + 1, D - 14.0, D + 1, 0, HB + 10)
    p += anello

    # torrette delle viti, fino alla quota di giunto, con inserto M3. Il pannello è inclinato: sul loro
    # diametro la faccia inferiore sale di D/2*tan(alpha), quindi entrano nel pannello da 0,8 mm in su
    # (senza, sul lato alto restavano staccate e Orca stampava un ponte a mezzaluna)
    for (x, y) in COLONNE:
        h = z_sotto(y) - Z_GIUNTO + 0.8 + COLONNA_D / 2 * math.tan(ALPHA)
        p += Pos(x, y, Z_GIUNTO + h / 2) * cil(COLONNA_D, h)
        p -= Pos(x, y, Z_GIUNTO + INSERTO_PROF / 2 - 0.01) * cil(INSERTO_D, INSERTO_PROF)

    # OLED: finestra con smusso, sede del vetro, torrette delle staffe
    va_w, va_h = OLED["va"][0] + 0.2, OLED["va"][1] + 0.2
    p -= sul_top(*OLED_C) * Pos(0, 0, -T_TOP - 1) * extrude(RectangleRounded(va_w, va_h, 0.8), T_TOP + 2)
    p -= sul_top(*OLED_C) * Pos(0, 0, -1.0) * extrude(RectangleRounded(va_w, va_h, 0.8), 1.2, taper=-45)
    cx, cy = oled_centro_pcb()
    p -= sul_top(cx, cy) * Pos(0, 0, -T_TOP - 0.01) * extrude(Rectangle(*OLED["sede"]), OLED["sede_prof"] + 0.01)
    h_t = -T_TOP - W_STAFFA_TOP
    for sx in (-1, 1):
        for sy in (-1, 1):
            loc = sul_top(cx + sx * OLED["vite_x"], lungo_pendenza(cy, sy * OLED["staffa_y"]))
            p += loc * Pos(0, 0, -T_TOP - h_t / 2 + 0.01) * cil(6.0, h_t)
            p -= loc * Pos(0, 0, W_STAFFA_TOP + 6.5 / 2 - 0.01) * cil(PILOTA_M25, 6.5)

    # encoder e pot: fori per la boccola M7; tasca da sotto per i pot (boccola corta)
    p -= sul_top(*ENC_C) * cil(ENC["foro"] + TOL_FORI, 20)
    for x in POT_X:
        for y in POT_Y:
            loc = sul_top(x, y)
            p -= loc * cil(POT["foro"] + TOL_FORI, 20)
            p -= loc * Pos(0, 0, -T_TOP + POT["tasca"] / 2 - 0.01) * Box(*POT["tasca_xy"], POT["tasca"] + 0.02)

    # tasti e LED
    for (x, y) in TASTI:
        p -= sul_top(x, y) * cil(TASTO["cappuccio"] + 2 * TASTO["gioco"] + TOL_FORI, 20)
    p -= sul_top(*LED_C) * cil(LED["d"] + TOL_FORI, 20)

    # footswitch 3PDT: foro, torre di sostegno fino al fondo, fessura per i fili verso l'interno
    p -= sul_top(*FS_C) * cil(FS["foro"] + TOL_FORI, 20)
    # la torre segue l'inclinazione del footswitch e appoggia piatta sul fondo
    fx, fy = FS_C
    l_in, t = FS["torre_luce"], FS["torre_parete"]
    z_base = T_FLOOR + GIOCO
    torre = sul_top(*FS_C) * Pos(0, 0, -T_TOP - 30) * (Box(l_in + 2 * t, l_in + 2 * t, 60) - Box(l_in, l_in, 70))
    torre = torre & fascia(-200, -T_TOP + 0.01) & box(-1, W + 1, -1, D + 1, z_base, HB + 10)
    fw, fh = FS["fessura"]
    yf_base = fy + (z_top(fy) - (z_base + fh / 2)) * math.tan(ALPHA)
    torre -= box(fx - l_in / 2 - t - 1, fx - l_in / 2 + 0.01, yf_base - fw / 2, yf_base + fw / 2, 0, z_base + fh)
    p += torre
    # LED del bypass: manicotto sotto il pannello, il LED entra da sotto fino alla flangia
    h_m = LED_FS["lungo"] - T_TOP
    p += sul_top(*LED_FS_C) * Pos(0, 0, -T_TOP - h_m / 2 + 0.01) * cil(LED_FS["manicotto"], h_m)
    p -= sul_top(*LED_FS_C) * Pos(0, 0, -T_TOP) * cil(LED_FS["d"] + TOL_FORI, 20)

    # torrette per la scheda dei tasti
    h_st = -T_TOP - W_TASTI_PCB
    for (x, y) in SCHEDA_TASTI["fori"]:
        loc = sul_top(x, y)
        p += loc * Pos(0, 0, -T_TOP - h_st / 2 + 0.01) * cil(6.0, h_st)
        p -= loc * Pos(0, 0, W_TASTI_PCB + 7.0 / 2 - 0.01) * cil(PILOTA_M25, 7.0)

    # logo inciso in basso a destra
    lw, lp = logo or (LOGO_W, LOGO_PROF)
    p -= sul_top(*LOGO_C) * Pos(0, 0, -lp) * logo_solido(lp, lw)
    return p


def staffa_oled():
    sw, sd, sh = OLED["staffa"]
    pw, pd, ph = OLED["piedino"]
    s = Pos(0, 0, sh / 2) * Box(sw, sd, sh)
    for sx in (-1, 1):
        s += Pos(sx * OLED["piedino_x"], 0, sh + ph / 2 - 0.01) * Box(pw, pd, ph + 0.02)
        s -= Pos(sx * OLED["vite_x"], 0, sh / 2) * cil(2.8, sh + 1)
    return s


def staffe_in_posizione():
    cx, cy = oled_centro_pcb()
    out = []
    for sy in (-1, 1):
        loc = sul_top(cx, lungo_pendenza(cy, sy * OLED["staffa_y"]))
        out.append(loc * Pos(0, 0, W_STAFFA_TOP - OLED["staffa"][2] - OLED["piedino"][2]) * staffa_oled())
    return out


# =========================================================== vasca
def vasca():
    v = (prisma() - prisma(T_WALL, T_FLOOR)) & fascia(-200, -T_TOP)

    # finestra nella parete posteriore per il pannello I/O
    x0, x1 = R_PIANTA + 2, W - R_PIANTA - 2
    v -= box(x0, x1, D - T_WALL - 1, D + 1, TACCA_Z0, HB + 10)
    # costola sul fondo e montanti ai lati, attaccati alle pareti: tengono il pannello posteriore
    # contro la parete (la finestra gli fa da cornice)
    yf = Y_PANNELLO_INT - GIOCO
    v += box(12.0, W - 12.0, yf - 1.6, yf, T_FLOOR - 0.01, T_FLOOR + 2.0)
    for (a, b) in ((T_WALL - 0.6, x0 + 2), (x1 - 2, W - T_WALL + 0.6)):
        v += box(a, b, yf - 1.6, yf, T_FLOOR - 0.01, z_sotto(yf) - 1.0) & prisma(T_WALL - 0.6)

    # colonne per le viti dal fondo
    for (x, y) in COLONNE:
        h = Z_GIUNTO - GIOCO - T_FLOOR
        v += Pos(x, y, T_FLOOR + h / 2 - 0.01) * cil(COLONNA_D, h + 0.02)
        v -= Pos(x, y, 5) * cil(VITE_PASSANTE + TOL_FORI, 40)
        v -= Pos(x, y, TESTA_PROF / 2 - 0.01) * cil(TESTA_D + TOL_FORI, TESTA_PROF)
        # due strati a ponte sopra la sede della testa: prima una fessura larga quanto il foro, poi un
        # quadrato. Il foro esce pulito senza supporti (strati da 0,3: 3,2 = 0,2 + 10 x 0,3)
        fv, ft = VITE_PASSANTE + TOL_FORI, TESTA_D + TOL_FORI
        v -= Pos(x, y, TESTA_PROF + 0.15) * Box(fv, ft, 0.32)
        v -= Pos(x, y, TESTA_PROF + 0.45) * Box(fv, fv, 0.32)

    # colonnine per la veroboard
    for (hx, hy) in FORI_FISSAGGIO:
        x, y = foro_xy(hx, hy)
        v += Pos(x, y, T_FLOOR + DISTANZIALE / 2 - 0.01) * cil(DISTANZIALE_D, DISTANZIALE + 0.02)
        v -= Pos(x, y, Z_SCHEDA - 5.5 / 2 + 0.01) * cil(PILOTA_M3, 5.5)

    # USB-C del Seed e fessura microSD sulla parete sinistra
    uy, uz = seed_y_centro(), usb_z()
    ut = SEED["usb_taglio"]
    v -= Pos(T_WALL / 2, uy, uz) * Rot(0, 90, 0) * extrude(Pos(0, 0, -5) * RectangleRounded(ut[1], ut[0], 2.0), 10)
    fw, fh = SD["fessura"]
    v -= (Pos(T_WALL / 2, (SD["y"][0] + SD["y"][1]) / 2, SD["z_fessura"]) * Rot(0, 90, 0)
          * extrude(Pos(0, 0, -5) * RectangleRounded(fh, fw, 1.0), 10))

    # sedi per i piedini adesivi (con PIEDINO_PROF = 0 il fondo resta pieno)
    if PIEDINO_PROF > 0:
        for (x, y) in PIEDINI:
            v -= Pos(x, y, PIEDINO_PROF / 2 - 0.01) * cil(PIEDINO_D, PIEDINO_PROF + 0.02)
    return v


def orecchie():
    """i quattro dischi, centrati sugli spigoli della pianta, tolta l'impronta della vasca"""
    o = None
    for x in (0.0, W):
        for y in (0.0, D):
            c = Pos(x, y, ORECCHIE_H / 2) * cil(ORECCHIE_D, ORECCHIE_H)
            o = c if o is None else o + c
    return o - prisma(ORECCHIE_DENTRO, -1.0, ORECCHIE_H + 1.0)


def vasca_stampa(v):
    """la vasca come va sul piatto: con le orecchie. STEP, render e collisioni usano vasca()"""
    return v + orecchie()


# =========================================================== pannello posteriore
def pannello_posteriore():
    """lastra piatta dentro la vasca, contro la parete: la finestra le fa da cornice. Si stampa piatta,
    a faccia in giù, senza sporgenze; angoli raccordati perché non si alzino dal piatto"""
    z1 = z_sotto(Y_PANNELLO_INT) - GIOCO
    p = box(R_PIANTA, W - R_PIANTA, Y_PANNELLO_INT, Y_PANNELLO_EST, T_FLOOR + GIOCO, z1)
    p = fillet(p.edges().filter_by(Axis.Y), R_PANNELLO)
    for (nome, x, tipo) in RETRO:
        p -= Pos(x, D, Z_RETRO) * Rot(90, 0, 0) * cil(TIPI_RETRO[tipo]["foro"] + TOL_FORI, 20)
    return p


# =========================================================== componenti (per le verifiche)
def seed_y_centro():
    return (foro_xy(L.SEED_X_L, 0)[1] + foro_xy(L.SEED_X_R, 0)[1]) / 2


def usb_z():
    return Z_SCHEDA_TOP + SEED["header_f"] + SEED["header_m"] + SEED["usb_z"]


def componenti():
    """[(nome, solido, gruppo)]: i corpi reali. Le parti della veroboard (gruppo 'scheda')
    non si controllano fra loro: il loro passo è affare di layout.py"""
    c = []
    c.append(("veroboard", box(*SCHEDA_X, *SCHEDA_Y, Z_SCHEDA + 0.02, Z_SCHEDA_TOP), "scheda"))
    for ref, kind, val, pins in L.P:
        if kind == "seed":
            continue
        xs = [foro_xy(x, y)[0] for (x, y, _, _) in pins]
        ys = [foro_xy(x, y)[1] for (x, y, _, _) in pins]
        if kind == "res":
            span = max(abs(pins[0][0] - pins[1][0]), abs(pins[0][1] - pins[1][1]))
            h = 3.0 if span >= 3 else 11.0      # sdraiata o in piedi
        else:
            h = ALTEZZE[kind]
        m = MARGINI[kind]
        c.append((f"{ref} {val}", box(min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m,
                                       Z_SCHEDA_TOP, Z_SCHEDA_TOP + h), "scheda"))
    for name, a, b, net, _ in L.LINKS:
        (xa, ya), (xb, yb) = foro_xy(*a), foro_xy(*b)
        c.append((f"ponticello {name}", box(min(xa, xb) - 0.8, max(xa, xb) + 0.8, min(ya, yb) - 0.8,
                                             max(ya, yb) + 0.8, Z_SCHEDA_TOP, Z_SCHEDA_TOP + 2.0), "scheda"))
    # Seed3 sugli header femmina: circuito e componenti, più la USB-C sporgente
    xs0 = foro_xy(0, 0)[0] - (SEED["usb_oltre_pin1"] - 1.28)
    xs1 = foro_xy(0, 19)[0] + SEED["pcb_oltre_pin20"]
    yc = seed_y_centro()
    z_pcb = Z_SCHEDA_TOP + SEED["header_f"] + SEED["header_m"]
    c.append(("Seed3", box(xs0, xs1, yc - SEED["larghezza"] / 2, yc + SEED["larghezza"] / 2,
                           Z_SCHEDA_TOP, z_pcb + SEED["pcb"] + SEED["sopra_pcb"]), "scheda"))
    xu = foro_xy(0, 0)[0] - SEED["usb_oltre_pin1"]
    c.append(("USB-C del Seed3", box(xu, xu + SEED["usb_lungo"], yc - 4.5, yc + 4.5,
                                      z_pcb + 0.98, z_pcb + 0.98 + 3.88), "scheda"))
    # teste delle viti di fissaggio sopra la veroboard: devono stare fuori dai componenti
    td, th = TESTA_VITE_SCHEDA
    for (hx, hy) in FORI_FISSAGGIO:
        x, y = foro_xy(hx, hy)
        c.append((f"testa vite veroboard ({hx},{hy})", Pos(x, y, Z_SCHEDA_TOP + 0.02 + th / 2) * cil(td, th), "viti"))

    # sotto il pannello: pot, encoder, OLED, scheda tasti
    for x in POT_X:
        for y in POT_Y:
            h = POT["prof"] + POT["pin"]
            top = -(T_TOP - POT["tasca"]) - 0.02
            c.append((f"pot {x:.0f},{y:.0f}", sul_top(x, y) * Pos(0, 0, top - h / 2) * Box(*POT["corpo"], h), "comandi"))
            c.append((f"manopola {x:.0f},{y:.0f}", sul_top(x, y) * Pos(0, 0, POT["dado"] + 0.5 + POT["manopola"][1] / 2)
                      * cil(POT["manopola"][0], POT["manopola"][1]), "manopole"))
    h = ENC["prof"] + ENC["pin"]
    c.append(("encoder", sul_top(*ENC_C) * Pos(0, 0, -T_TOP - 0.02 - h / 2) * Box(*ENC["corpo"], h), "comandi"))
    c.append(("manopola encoder", sul_top(*ENC_C) * Pos(0, 0, ENC["dado"] + 0.5 + ENC["manopola"][1] / 2)
              * cil(ENC["manopola"][0], ENC["manopola"][1]), "manopole"))
    cx, cy = oled_centro_pcb()
    lo = sul_top(cx, cy)
    vh = OLED["vetro_h"]
    c.append(("OLED vetro", lo * Pos(0, 0, W_VETRO_TOP - 0.02 - (vh - 0.04) / 2) * Box(*OLED["vetro"], vh - 0.04), "oled"))
    c.append(("OLED circuito", lo * Pos(0, 0, (W_PCB_TOP + W_PCB_BOT) / 2) * Box(*OLED["pcb"][:2], OLED["pcb"][2]), "oled"))
    rw, rh, rz = OLED["retro"]
    c.append(("OLED componenti sul retro", lo * Pos(0, 0, W_PCB_BOT - rz / 2) * Box(rw, rh, rz), "oled"))
    sx0, sx1 = SCHEDA_TASTI["x"]
    sy0, sy1 = SCHEDA_TASTI["y"]
    lk = sul_top((sx0 + sx1) / 2, (sy0 + sy1) / 2)
    c.append(("scheda tasti", lk * Pos(0, 0, W_TASTI_PCB - (1.6 + 1.5) / 2)
              * Box(sx1 - sx0, (sy1 - sy0) / math.cos(ALPHA), 1.6 + 1.5), "comandi"))
    for i, (x, y) in enumerate(TASTI):
        c.append((f"tasto K{i + 1}", sul_top(x, y) * Pos(0, 0, W_TASTI_PCB + 3.5 / 2) * Box(12, 12, 3.5), "comandi"))
        hc = TASTO["pila"] - 3.5
        c.append((f"cappuccio K{i + 1}", sul_top(x, y) * Pos(0, 0, TASTO["sporgenza"] - hc / 2)
                  * cil(TASTO["cappuccio"], hc), "comandi"))
    c.append(("LED", sul_top(*LED_C) * Pos(0, 0, W_TASTI_PCB / 2) * cil(LED["d"], -W_TASTI_PCB), "comandi"))

    # footswitch: corpo sotto il pannello, dado e attuatore sopra; LED del bypass
    lf = sul_top(*FS_C)
    bw, bd, bh = FS["corpo"]
    c.append(("footswitch 3PDT", lf * Pos(0, 0, -T_TOP - 0.02 - bh / 2) * Box(bw, bd, bh), "comandi"))
    (nd, nh), (ad, ah) = FS["dado"], FS["attuatore"]
    c.append(("dado footswitch", lf * Pos(0, 0, 0.02 + nh / 2) * cil(nd, nh), "manopole"))
    c.append(("attuatore footswitch", lf * Pos(0, 0, nh + ah / 2) * cil(ad, ah), "manopole"))
    c.append(("LED bypass", sul_top(*LED_FS_C) * Pos(0, 0, -LED_FS["lungo"] / 2 - 0.01)
              * cil(LED_FS["d"], LED_FS["lungo"] - 0.02), "comandi"))

    # retro: corpi dietro al pannello, scheda MIDI, microSD
    yi = Y_PANNELLO_INT - 0.02
    for (nome, x, tipo) in RETRO:
        if tipo == "jack35":
            continue                                   # stanno sulla scheda MIDI
        bw, bh, bd = TIPI_RETRO[tipo]["corpo"]
        c.append((nome, box(x - bw / 2, x + bw / 2, yi - bd, yi, Z_RETRO - bh / 2, Z_RETRO + bh / 2), "retro"))
    mx0, mx1 = MIDI_SCHEDA["x"]
    c.append(("scheda MIDI", box(mx0, mx1, yi - MIDI_SCHEDA["prof"], yi, *MIDI_SCHEDA["z"]), "retro"))
    c.append(("scheda microSD", box(SD["x"][0] + 0.02, SD["x"][1], *SD["y"], *SD["z"]), "sd"))
    return c


# =========================================================== verifiche
def urti(a, b, soglia=1e-3):
    ba, bb = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
            or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
        return 0.0
    v = (a & b).volume
    return v if v > soglia else 0.0


def controlla_logo(top, larghezza, prof):
    """il logo è inciso davvero: materiale tolto quanto atteso, niente rimasto dentro l'incisione"""
    logo = sul_top(*LOGO_C) * Pos(0, 0, -prof) * logo_solido(prof, larghezza)
    atteso = logo.volume * prof / (prof + 0.4)
    nel_pannello = ((prisma() & fascia(-T_TOP, 0)) & logo).volume
    rimasto = (top & logo).volume
    if nel_pannello < 0.9 * atteso or rimasto > 1.0:
        return (f"logo non inciso: {nel_pannello:.0f} mm³ nel pannello su {atteso:.0f} attesi, "
                f"{rimasto:.0f} mm³ di materiale rimasto"), 0.0
    return None, nel_pannello - rimasto


def verifica(pezzi, comp):
    errori, note = [], []
    # componenti contro componenti (non dentro lo stesso gruppo 'scheda', 'oled' o 'manopole')
    for i in range(len(comp)):
        for j in range(i + 1, len(comp)):
            (na, sa, ga), (nb, sb, gb) = comp[i], comp[j]
            if ga == gb and ga in ("scheda", "oled", "manopole"):
                continue
            v = urti(sa, sb)
            if v:
                errori.append(f"COLLISIONE {na} / {nb}: {v:.2f} mm³")
    # componenti contro pezzi stampati
    for pn, ps in pezzi.items():
        for n, s, g in comp:
            v = urti(ps, s)
            if v:
                errori.append(f"COLLISIONE {pn} / {n}: {v:.2f} mm³")
    # pezzi stampati fra loro
    nomi = list(pezzi)
    for i in range(len(nomi)):
        for j in range(i + 1, len(nomi)):
            v = urti(pezzi[nomi[i]], pezzi[nomi[j]])
            if v:
                errori.append(f"COLLISIONE {nomi[i]} / {nomi[j]}: {v:.2f} mm³")

    # tagli che nessuna collisione controlla: finestra aperta su tutti i pixel, logo inciso davvero
    top = pezzi["pannello superiore"]
    finestra = sul_top(*OLED_C) * Pos(0, 0, -T_TOP / 2) * Box(OLED["aa"][0], OLED["aa"][1], T_TOP - 0.2)
    if urti(top, finestra):
        errori.append("finestra dell'OLED chiusa sopra l'area attiva")
    e, tolti = controlla_logo(top, LOGO_W, LOGO_PROF)
    if e:
        errori.append(e)
    note.append(f"logo inciso: {tolti:.0f} mm³ tolti")

    # USB-C allineata alla parete
    usb_x = foro_xy(0, 0)[0] - SEED["usb_oltre_pin1"]
    if not (T_WALL + 0.2 <= usb_x <= T_WALL + 1.2):
        errori.append(f"USB-C a {usb_x - T_WALL:.2f} mm dalla parete (atteso 0,2-1,2)")
    note.append(f"USB-C: faccia a {usb_x - T_WALL:.2f} mm dalla parete, centro a y {seed_y_centro():.1f}, z {usb_z():.1f}")

    # spessori di pannello per le boccole
    if T_TOP - POT["tasca"] > POT["boccola"] - POT["dado"]:
        errori.append("pannello troppo spesso per la boccola dei pot")
    if T_TOP > ENC["boccola"] - ENC["dado"]:
        errori.append("pannello troppo spesso per la boccola dell'encoder")
    for (nome, x, tipo) in RETRO:
        if T_REAR > TIPI_RETRO[tipo]["max_pannello"]:
            errori.append(f"pannello posteriore troppo spesso per {nome}")

    # spazio fra le manopole (bordo-bordo)
    pots = [(x, y) for x in POT_X for y in POT_Y]
    d_min = min(math.dist(a, b) for i, a in enumerate(pots) for b in pots[i + 1:]) - POT["manopola"][0]
    d_enc = min(math.dist(ENC_C, p) for p in pots) - (POT["manopola"][0] + ENC["manopola"][0]) / 2
    if d_min < 11.5:
        errori.append(f"manopole dei pot a {d_min:.1f} mm (minimo 11,5)")
    note.append(f"aria fra le manopole: pot-pot {d_min:.1f} mm, encoder-pot {d_enc:.1f} mm")
    passo_file = abs(POT_Y[0] - POT_Y[1])
    note.append(f"file dei pot a {passo_file:.0f} mm fra i centri ({passo_file - POT['manopola'][0]:.0f} mm d'aria)")

    # footswitch: aria verso le manopole (bordo-bordo) e boccola
    d_fs = min(math.dist(FS_C, p) for p in pots) - (FS["dado"][0] + POT["manopola"][0]) / 2
    if d_fs < 12.0:
        errori.append(f"footswitch a {d_fs:.1f} mm dalle manopole (minimo 12)")
    note.append(f"footswitch: {d_fs:.1f} mm d'aria dalla manopola più vicina")
    if T_TOP > FS["max_pannello"]:
        errori.append("pannello troppo spesso per la boccola del footswitch")

    # logo stampabile con ugello da 0,4
    t = LOGO_W * LOGO_TRATTO_MIN
    if t < 0.44:
        errori.append(f"logo: tratto minimo {t:.2f} mm, sotto 0,44")
    note.append(f"logo largo {LOGO_W:.0f} mm, tratto più sottile ~{t:.2f} mm")

    # la veroboard sta nella vasca, sui fori giusti
    if SCHEDA_X[0] < T_WALL or SCHEDA_X[1] > W - T_WALL or SCHEDA_Y[0] < T_WALL:
        errori.append("la veroboard esce dalla vasca")
    errori += L.fori_fissaggio_errori(FORI_FISSAGGIO)

    # vasca da stampare: orecchie saldate al pezzo, sedi delle viti aperte sul piatto
    vs = vasca_stampa(pezzi["vasca"])
    corpi = len(vs.solids())
    if corpi != 1:
        errori.append(f"vasca da stampare in {corpi} corpi: le orecchie non sono attaccate al bordo")
    for (x, y) in COLONNE:
        if urti(vs, Pos(x, y, 0.1) * cil(TESTA_D - 1.0, 0.1)):
            errori.append(f"sede della vite in ({x:.1f}, {y:.1f}) chiusa sul piatto dalle orecchie")
    note.append(f"orecchie: 4 dischi Ø {ORECCHIE_D:g} x {ORECCHIE_H:g} mm agli spigoli della vasca, "
                f"solo nel file di stampa")
    return errori, note


# =========================================================== piastre di prova
def prova_superiore():
    """3 mm come il pannello, faccia a vista in alto (z = T_TOP) come il pannello montato:
    pot con tasca, encoder, tasto, LED, finestra e sede dell'OLED, logo"""
    p = box(0, 150, 0, 62, 0, T_TOP)
    p -= Pos(12, 12, 0) * cil(POT["foro"] + TOL_FORI, 20)
    p -= Pos(12, 12, POT["tasca"] / 2 - 0.01) * Box(*POT["tasca_xy"], POT["tasca"] + 0.02)
    p -= Pos(12, 32, 0) * cil(ENC["foro"] + TOL_FORI, 20)
    p -= Pos(12, 50, 0) * cil(TASTO["cappuccio"] + 2 * TASTO["gioco"] + TOL_FORI, 20)
    p -= Pos(27, 50, 0) * cil(LED["d"] + TOL_FORI, 20)
    va_w, va_h = OLED["va"][0] + 0.2, OLED["va"][1] + 0.2
    ox, oy = 72.0, 31.0
    p -= Pos(ox, oy, -1) * extrude(RectangleRounded(va_w, va_h, 0.8), T_TOP + 2)
    p -= Pos(ox, oy, T_TOP - 1.0) * extrude(RectangleRounded(va_w, va_h, 0.8), 1.2, taper=-45)
    p -= Pos(ox, oy - OLED["off_va"], -0.01) * extrude(Rectangle(*OLED["sede"]), OLED["sede_prof"] + 0.01)
    p -= Pos(126, 31, T_TOP - LOGO_PROF) * logo_solido(LOGO_PROF)
    return p


def prova_posteriore():
    """2,4 mm come il pannello I/O: un foro per tipo e il taglio della USB-C"""
    p = box(0, 110, 0, 30, 0, T_REAR)
    for i, (tipo, t) in enumerate(TIPI_RETRO.items()):
        p -= Pos(14 + i * 22, 15, 0) * cil(t["foro"] + TOL_FORI, 20)
    ut = SEED["usb_taglio"]
    p -= Pos(98, 15, -5) * extrude(RectangleRounded(ut[0], ut[1], 2.0), 10)
    return p


# =========================================================== orientamento di stampa
def a_terra(s):
    bb = s.bounding_box()
    return Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * s


def per_stampa(nome, s):
    if nome == "pannello superiore":        # faccia a vista sul piatto
        return a_terra(Rot(180, 0, 0) * Rot(-math.degrees(ALPHA), 0, 0) * s)
    if nome == "pannello posteriore":       # faccia esterna sul piatto
        return a_terra(Rot(-90, 0, 0) * s)
    return a_terra(s)


def per_servizio(nome, s):
    """pezzi in piano con la faccia a vista in alto, per un servizio di stampa (orientano loro)"""
    if nome == "pannello superiore":
        return a_terra(Rot(-math.degrees(ALPHA), 0, 0) * s)
    if nome == "pannello posteriore":
        return a_terra(Rot(90, 0, 0) * s)
    return a_terra(s)


def verifica_servizio(top):
    """variante per un servizio di stampa (MJF/SLS): logo inciso, tratto >= 0,5, pieno sotto il logo"""
    errori, note = [], []
    lw, lp = LOGO_SERVIZIO
    e, tolti = controlla_logo(top, lw, lp)
    if e:
        errori.append(f"variante servizio: {e}")
    t = lw * LOGO_TRATTO_MIN
    if t < 0.5:
        errori.append(f"variante servizio: tratto del logo {t:.2f} mm, sotto 0,5")
    sotto = sul_top(*LOGO_C) * Pos(0, 0, -T_TOP) * logo_solido(T_TOP - lp - 0.4, lw)
    pieno = (top & sotto).volume / sotto.volume
    if pieno < 0.98:
        errori.append(f"variante servizio: sotto il logo il pannello è pieno al {pieno:.0%}")
    note.append(f"variante servizio: logo {lw:g} mm inciso {lp:g}, tratto ~{t:.2f} mm, "
                f"{tolti:.0f} mm³ tolti, sotto pieno al {pieno:.0%}")
    return errori, note


# =========================================================== main
def main():
    solo_verifica = "--solo-verifica" in sys.argv
    pezzi = {
        "vasca": vasca(),
        "pannello superiore": pannello_superiore(),
        "pannello posteriore": pannello_posteriore(),
    }
    for i, s in enumerate(staffe_in_posizione()):
        pezzi[f"staffa OLED {i + 1}"] = s
    comp = componenti()
    errori, note = verifica(pezzi, comp)
    top_servizio = pannello_superiore(logo=LOGO_SERVIZIO)
    e, n = verifica_servizio(top_servizio)
    errori, note = errori + e, note + n

    stampa = dict(pezzi, vasca=vasca_stampa(pezzi["vasca"]))
    print(f"Case {W:.0f} x {D:.0f} mm, alto {HF:.0f} davanti e {HB:.0f} dietro, pendenza {math.degrees(ALPHA):.1f}°")
    for n, s in pezzi.items():
        bb = per_stampa(n, stampa[n]).bounding_box()
        print(f"  {n:20s} ingombro di stampa {bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:5.1f} mm, "
              f"volume pieno {s.volume / 1000:6.1f} cm³")
    for n in note:
        print("  " + n)

    if not solo_verifica:
        OUT.mkdir(exist_ok=True)
        for n in ("vasca", "pannello superiore", "pannello posteriore"):
            f = n.replace(" ", "_")
            export_stl(per_stampa(n, stampa[n]), str(OUT / f"{f}.stl"))
            export_step(pezzi[n], str(OUT / f"{f}.step"))
        export_stl(staffa_oled(), str(OUT / "staffa_oled_x2.stl"))
        export_stl(a_terra(Rot(180, 0, 0) * prova_superiore()), str(OUT / "prova_superiore.stl"))
        export_stl(prova_posteriore(), str(OUT / "prova_posteriore.stl"))
        # file per un servizio di stampa: senza orecchie, logo della variante, in piano
        srv = OUT / "servizio"
        srv.mkdir(exist_ok=True)
        servizio = {"vasca": per_servizio("vasca", pezzi["vasca"]),
                    "pannello_superiore": per_servizio("pannello superiore", top_servizio),
                    "pannello_posteriore": per_servizio("pannello posteriore", pezzi["pannello posteriore"]),
                    "staffa_oled": staffa_oled()}
        for f, s in servizio.items():
            export_step(s, str(srv / f"{f}.step"))
            export_stl(s, str(srv / f"{f}.stl"))
            bb = s.bounding_box()
            print(f"  servizio/{f}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
                  f"{s.volume / 1000:.1f} cm³, {len(s.solids())} corpo/i")
        parti = []
        for n, s in pezzi.items():
            s.label, s.color = n, Color(0.17, 0.17, 0.17)
            parti.append(s)
        for n, s, g in comp:
            s.label, s.color = n, Color(0.75, 0.75, 0.72)
            parti.append(s)
        assieme = Compound(parti)
        export_step(assieme, str(OUT / "assieme.step"))
        export_gltf(assieme, str(OUT / "assieme.glb"), binary=True)
        print(f"  esportati in {OUT}")

    if errori:
        print("ERRORI:")
        for e in errori:
            print(" -", e)
        sys.exit(1)
    print(f"OK: {len(pezzi)} pezzi, {len(comp)} componenti controllati, nessuna collisione.")


if __name__ == "__main__":
    main()
