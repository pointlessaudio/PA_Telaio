# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0", "numpy"]
# ///
"""
PA-TELAIO: cablaggio del case stampato.

Elenca ogni filo (da terminale a terminale, con le coordinate 3D dei due capi), ne calcola la lunghezza da
tagliare, sceglie l'orientamento della schedina preamp e verifica il percorso libero. Sorgenti di verita:
  case/case.py              coordinate di jack, pot, encoder, OLED, tasti, footswitch, schede, schedina (SOLA LETTURA)
  hardware/layout.py        piazzole della veroboard (fili fuori scheda)
  hardware/preamp/layout_preamp.py  piazzole della schedina preamp

Uso (da case/):
    uv run cablaggio.py                 # tabelle, orientamento, verifica
    uv run cablaggio.py --scrivi-md     # riscrive anche cablaggio.md
Deve finire con "OK: ..." (altrimenti elenca gli ERRORI e esce con 1).

Coordinate come case.py: X sinistra->destra, Y fronte->retro, Z in su, origine nello spigolo anteriore
sinistro sotto il fondo, mm.

CONVENZIONI (tutte dichiarate, da correggere a banco se il pezzo vero e' diverso)
- Lunghezza di taglio = percorso a gambe assiali (Manhattan, 3D) + margine: MARGINE_FISSO (spelatura, saldatura e
  piega ai due capi) piu MARGINE_PCT del percorso (giri intorno ai corpi), +10 % sui fili intrecciati
  (l'intreccio accorcia); arrotondata per eccesso a 5 mm.
- Gambe: salita/discesa sul capo piu basso, tratto orizzontale alla quota piu alta (x poi y). Un filo che
  incontra un corpo solido passa da un punto intermedio cercato su griglia (il piu corto che libera).
- Capi: piazzole veroboard e schedina sulla faccia componenti (+0,3 mm); jack, pot, encoder, footswitch sui
  terminali stimati dalle misure di ingombro di case.py (le posizioni dei terminali dentro al corpo sono
  STIME, vedi le funzioni terminali_*).
- Rs 10 kOhm saldata sul terminale di punta del jack IN (filtro RF vicino al jack: il cavo dopo la Rs vede
  10 kOhm + sorgente, non la sorgente nuda); Rsh 3,3 kOhm fra il terminale LINE del deviatore INST/LINE e il
  giunto di massa del deviatore. Non sono fili: stanno in distinta.
- PRE e' un DPDT con un polo per canale: commuta l'USCITA (COM = piazzola IN della veroboard; OFF = nodo
  INST/LINE; ON = OUT della schedina). L'ingresso della schedina resta sempre sul nodo INST/LINE: con un solo
  polo per canale non si possono commutare entrambi i capi.
"""
import math
import sys
import time
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
sys.path.insert(0, str(QUI.parent / "hardware"))
sys.path.insert(0, str(QUI.parent / "hardware" / "preamp"))


def _importa_case():
    """case.py e' modificato in parallelo da un altro agente: se l'import fallisce a meta modifica, riprova."""
    ultimo = None
    for _ in range(6):
        try:
            import case as modulo
            return modulo
        except Exception as e:                      # SyntaxError/NameError a meta salvataggio
            ultimo = e
            sys.modules.pop("case", None)
            print(f"  (import di case.py fallito: {e!r}; riprovo fra 20 s)", flush=True)
            time.sleep(20)
    raise ultimo


C = _importa_case()
L = C.L                                     # hardware/layout.py gia importato da case.py
import layout_preamp as LP  # noqa: E402  (verifica la schedina all'import)

from build123d import Edge, Vector  # noqa: E402

# ----------------------------------------------------------------------------- parametri
MARGINE_FISSO = 12.0        # mm: 6 per capo (spelatura 3 + saldatura/piega 3)
MARGINE_PCT = 0.10          # giri intorno ai corpi
EXTRA_INTRECCIO = 0.10      # un filo intrecciato si accorcia intrecciando
ARROTONDA = 5.0             # mm, per eccesso
DIST_MIN_ERR = 2.0         # mm: sotto questa distanza la verifica da errore
DIST_DIGITALE_MIN = 15.0    # mm: distanza minima voluta fra fili d'ingresso e linee digitali
TOLL_HZ = 1.10              # la verifica accetta una lunghezza HZ fino a 1,10 volte il migliore
LUNGO = 150.0               # mm: oltre questo un filo e' segnalato come lungo
FS_LATO = -1                # -1: la fessura della torre del footswitch sta sul lato sinistro (come case.py)
ORI_IN_USO = None           # None: orientamento di case.py (SCHEDINA_ORI) o, se manca, quello scelto qui
PASSO = C.PASSO
YI = C.Y_PANNELLO_INT
ZR = C.Z_RETRO
SA, CA = math.sin(C.ALPHA), math.cos(C.ALPHA)

# ----------------------------------------------------------------------------- orientamenti della schedina
# (foro_dir, striscia_dir, trasposta): foro_dir/striscia_dir = +1 se foro 0 / striscia 0 stanno verso il valore minimo
# dell'asse del case su cui cadono, -1 verso il massimo. trasposta: i fori corrono lungo Y invece che lungo X.
ORIENTAMENTI = {
    "A identica (provvisoria)":      (+1, +1, False),
    "B foro 0 verso x maggiore":     (-1, +1, False),
    "C striscia 0 verso y maggiore": (+1, -1, False),
    "D ruotata 180":                 (-1, -1, False),
    "E trasposta, foro 0 y-, str 0 x-": (+1, +1, True),
    "F trasposta, foro 0 y-, str 0 x+": (+1, -1, True),
    "G trasposta, foro 0 y+, str 0 x-": (-1, +1, True),
    "H trasposta, foro 0 y+, str 0 x+": (-1, -1, True),
}
PROVVISORIA = "A identica (provvisoria)"
BU, BV = LP.W * PASSO, LP.H * PASSO                     # 60,96 x 45,72: fori x strisce
SCH_BOX = (C.SCHEDINA["x"][1] - C.SCHEDINA["x"][0], C.SCHEDINA["y"][1] - C.SCHEDINA["y"][0])   # 62 x 47
SCH_ORG0 = (C.SCHEDINA["x"][0], C.SCHEDINA["y"][0])
Z_SCH_PAD = C.T_FLOOR + C.SCHEDINA["colonnina"] + 1.6 + 0.3


def sched_xy(hx, hy, ori, org):
    fd, sd, tr = ORIENTAMENTI[ori]
    u, v = (hx + 0.5) * PASSO, (hy + 0.5) * PASSO
    uu = u if fd > 0 else BU - u
    vv = v if sd > 0 else BV - v
    return (org[0] + (vv if tr else uu), org[1] + (uu if tr else vv))


def sched_box(ori, org):
    tr = ORIENTAMENTI[ori][2]
    w, d = (SCH_BOX[1], SCH_BOX[0]) if tr else SCH_BOX
    return (org[0], org[0] + w, org[1], org[1] + d,
            C.T_FLOOR + C.SCHEDINA["colonnina"] + 0.02, C.T_FLOOR + C.SCHEDINA["alt"])


# ----------------------------------------------------------------------------- geometria del pannello inclinato
def sul(x, y, w=0.0, u=0.0, v=0.0):
    """punto sotto/sopra il pannello superiore: (x,y) in pianta sulla faccia a vista, w lungo la normale
    (negativo = sotto), (u, v) = spostamenti locali (u lungo X, v lungo la pendenza)"""
    n = C.NORMALE
    return (x + w * n[0] + u, y + w * n[1] + v * CA, C.z_top(y) + w * n[2] + v * SA)


def vb(nome):
    for n, (x, y), net, desc in L.PADS:
        if n == nome:
            X, Y = C.foro_xy(x, y)
            return (X, Y, C.Z_SCHEDA_TOP + 0.3), net
    return None, None


# ----------------------------------------------------------------------------- terminali
def terminali(ori=None, org=SCH_ORG0):
    """{chiave: dict(p, net, owner, desc)}. Le piazzole della schedina ci sono solo se ori non e' None."""
    T = {}

    def add(k, p, net, owner, desc=""):
        T[k] = dict(p=tuple(float(c) for c in p), net=net, owner=owner, desc=desc)

    # --- veroboard: tutte le piazzole di layout.py
    for n, (x, y), net, desc in L.PADS:
        X, Y = C.foro_xy(x, y)
        add(f"VB:{n}", (X, Y, C.Z_SCHEDA_TOP + 0.3), net, "veroboard", desc)

    # --- schedina preamp: piazzole di layout_preamp.py, trasformate con l'orientamento
    if ori is not None:
        for n, (hx, hy), net, desc in LP.PADS:
            x, y = sched_xy(hx, hy, ori, org)
            add(f"SC:{n}", (x, y, Z_SCH_PAD), net, "schedina preamp", desc)

    # --- jack del retro (lug a 12 mm dalla parete, sul fondo del corpo): STIMA
    yl, zl = YI - 12.0, ZR - 6.5
    xr = {n: x for n, x, t in C.RETRO}
    for s, nome in (("L", "IN L"), ("R", "IN R")):
        x = xr[nome]
        add(f"JI{s}:tip", (x - 3.5, yl, zl), f"tip_{s}", nome, "punta")
        add(f"JI{s}:rs", (x - 3.5, yl, zl), f"in_{s}", nome, "capo libero della Rs 10k sulla punta")
        add(f"JI{s}:sleeve", (x + 3.5, yl, zl), "GND", nome, "manicotto")
    for s, nome in (("L", "OUT L"), ("R", "OUT R")):
        x = xr[nome]
        add(f"JO{s}:tip", (x - 3.5, yl, zl), f"jo_{s}", nome, "punta")
        add(f"JO{s}:sleeve", (x + 3.5, yl, zl), "GND", nome, "manicotto")
    x = xr["PEDALE"]
    add("JP:tip", (x - 4.0, yl, zl), "D0", "PEDALE", "punta = D0")
    add("JP:ring", (x, yl, zl), "FS2", "PEDALE", "anello = D10")
    add("JP:sleeve", (x + 4.0, yl, zl), "GND", "PEDALE", "manicotto")
    x = xr["DC 9V"]
    add("DC:sleeve", (x + 4.0, YI - 14.0, ZR - 5.0), "DCIN", "DC 9V", "manicotto = +9 V")
    add("DC:center", (x - 3.0, YI - 14.0, ZR - 5.0), "GND", "DC 9V", "centrale = massa")

    # --- deviatori INST/LINE e PRE (mini DPDT, lug dietro al corpo, poli a x +-3, righe a passo 4,7): STIMA
    xi = xr["INST/LINE"]
    for s, dx in (("L", -3.0), ("R", 3.0)):
        add(f"ILS:COM {s}", (xi + dx, YI - 18.0, ZR), f"in_{s}", "INST/LINE", "comune: nodo dopo la Rs")
        add(f"ILS:GND {s}", (xi + dx, YI - 18.0, ZR - 8.0), "GND", "INST/LINE", "giunto di massa (capo di Rsh)")
    pre = {n: (x, z) for n, x, z, t in C.RETRO_PRE}["PRE"]
    for s, dx in (("L", -3.0), ("R", 3.0)):
        add(f"PRE:COM {s}", (pre[0] + dx, YI - 18.0, pre[1]), f"JIN{s}", "PRE", "comune verso la veroboard")
        add(f"PRE:OFF {s}", (pre[0] + dx, YI - 18.0, pre[1] - 4.7), f"in_{s}", "PRE", "posizione OFF: nodo INST/LINE")
        add(f"PRE:ON {s}", (pre[0] + dx, YI - 18.0, pre[1] + 4.7), f"out_{s}", "PRE", "posizione ON: OUT schedina")
    # PRE:COM porta la stessa net della piazzola IN della veroboard
    for s in "LR":
        T[f"PRE:COM {s}"]["net"] = T[f"VB:IN {s}"]["net"]

    # --- pot doppio GAIN (INGOMBRO STIMATO): pin dietro al corpo, gang L davanti, gang R dietro
    gx, gz = {n: (x, z) for n, x, z, t in C.RETRO_PRE}["GAIN"]
    for s, yy in (("L", YI - 6.0), ("R", YI - 14.0)):
        add(f"GAIN:A {s}", (gx - 2.5, yy, gz - 6.5), f"s1_{s}", "GAIN", f"gang {s}: capo verso S1")
        add(f"GAIN:B {s}", (gx + 2.5, yy, gz - 6.5), f"gb_{s}", "GAIN", f"gang {s}: ritorno verso 220R")

    # --- pot 1-6: pin sul fianco sinistro del corpo (verso la veroboard), 2,5 mm di passo; ordine di lettura
    # (riga dietro 1-3, riga davanti 4-6): ipotesi, si scambia in firmware
    ordine = [(x, C.POT_Y[0]) for x in C.POT_X] + [(x, C.POT_Y[1]) for x in C.POT_X]
    hw = C.POT["corpo"][0] / 2
    wp = -(C.T_TOP - C.POT["tasca"]) - 0.02 - (C.POT["prof"] + C.POT["pin"]) + 0.5
    for i, (x, y) in enumerate(ordine, 1):
        nome = f"pot {x:.0f},{y:.0f}"
        add(f"POT{i}:LO", sul(x, y, wp, -hw + 0.8, -2.5), "GND", nome, "capo basso")
        add(f"POT{i}:W", sul(x, y, wp, -hw + 0.8, 0.0), f"POT{i}", nome, "cursore")
        add(f"POT{i}:HI", sul(x, y, wp, -hw + 0.8, 2.5), "3V3A", nome, "capo alto")

    # --- encoder: A-C-B sul fianco sinistro, i due pin del pulsante sul destro
    we = -C.T_TOP - 0.02 - (C.ENC["prof"] + C.ENC["pin"]) + 0.5
    ex, ey = C.ENC_C
    for k, (nome, net, uu, vv) in enumerate([("A", "ENC_A", -3.75, -2.5), ("C", "GND", -3.75, 0.0),
                                             ("B", "ENC_B", -3.75, 2.5), ("SW", "ENC_SW", 3.75, -2.5),
                                             ("SW2", "GND", 3.75, 2.5)]):
        add(f"ENC:{nome}", sul(ex, ey, we, uu, vv), net, "encoder", "pin dell'encoder")

    # --- OLED: pad sul bordo anteriore del circuito (verso la piattina), lato inferiore: STIMA, da confermare
    cx, cy = C.oled_centro_pcb()
    wo = C.W_PCB_BOT
    vo = -C.OLED["pcb"][1] / 2 + 1.5
    for nome, net, uu in (("GND", "GND", -3.81), ("VCC", "3V3D", -1.27), ("SCL", "SCL", 1.27), ("SDA", "SDA", 3.81)):
        add(f"OLED:{nome}", sul(cx, cy, wo, uu, vo), net, "OLED circuito", "pad del modulo")

    # --- scheda tasti (millefori sotto il pannello): terminali sul bordo posteriore, lato rame
    wt = C.W_TASTI_PCB - 3.1
    ytb = C.SCHEDA_TASTI["y"][1] - 2.5
    x0 = C.SCHEDA_TASTI["x"][0]
    for k, (nome, net) in enumerate([("D0", "D0"), ("D10", "FS2"), ("GND", "GND")]):
        add(f"TASTI:{nome}", sul(x0 + 3.0 + 3.0 * k, ytb, wt), net, "scheda tasti", "terminale sulla millefori")
    add("TASTI:LED+", sul(C.LED_C[0] + 1.5, ytb, wt), "LED", "scheda tasti", "anodo del LED (con la 1K sulla scheda)")

    # --- footswitch 3PDT: 9 lug sul fondo del corpo, poli A (OUT L), B (OUT R), C (LED); riga bypass/comune/effetto
    bw, bd, bh = C.FS["corpo"]
    wf = -C.T_TOP - bh + 0.5
    fx, fy = C.FS_C
    for pk, uu in (("A", -6.0), ("B", 0.0), ("C", 6.0)):
        for rk, vv, desc in (("byp", -6.0, "posizione bypass"), ("com", 0.0, "comune"), ("eff", 6.0, "posizione effetto")):
            add(f"FS:{pk} {rk}", sul(fx, fy, wf, uu, vv), "?", "footswitch 3PDT", f"polo {pk}, {desc}")
    for s, pk in (("L", "A"), ("R", "B")):
        T[f"FS:{pk} byp"]["net"] = f"tip_{s}"
        T[f"FS:{pk} com"]["net"] = f"jo_{s}"
        T[f"FS:{pk} eff"]["net"] = T[f"VB:OUT {s}"]["net"]
    T["FS:C com"]["net"] = "VA"      # VA arriva al lug tramite la R 4,7k saldata sul lug stesso
    T["FS:C eff"]["net"] = "ledfs_a"
    T["FS:C byp"]["net"] = "nc"
    # LED del bypass: i due reofori escono sotto al manicotto
    wl = -(C.LED_FS["lungo"]) - 6.0
    add("LEDFS:A", sul(C.LED_FS_C[0], C.LED_FS_C[1], wl, -1.27, 0.0), "ledfs_a", "LED bypass", "anodo")
    add("LEDFS:K", sul(C.LED_FS_C[0], C.LED_FS_C[1], wl, 1.27, 0.0), "GND", "LED bypass", "catodo")

    # --- scheda MIDI: terminali sul bordo anteriore della scheda (a 16 mm dal pannello)
    mx0, mx1 = C.MIDI_SCHEDA["x"]
    zm = C.MIDI_SCHEDA["z"][0] + 5.0
    for k, (nome, net) in enumerate([("TX", "MIDI_TX"), ("RX", "MIDI_RX"), ("3V3", "3V3D"), ("GND", "GND")]):
        add(f"MIDI:{nome}", (mx0 + 6.0 + 4.0 * k, YI - C.MIDI_SCHEDA["prof"], zm), net, "scheda MIDI", "terminale scheda MIDI")

    # --- piastrina microSD (sul pannello posteriore, x e z da case.SD): terminali sul bordo anteriore, lato rame
    sdx = C.SD["x"]
    zsd = C.SD["z"] - C.SD["scheda_z"] - C.SD["pcb"][2]
    ysd = YI - 0.2 - C.SD["pcb"][1]
    for k, (nome, net) in enumerate([("D0", "SD_D0"), ("CMD", "SD_CMD"), ("CLK", "SD_CK"), ("3V3", "3V3D"), ("GND", "GND")]):
        add(f"SD:{nome}", (sdx - 6.0 + 3.0 * k, ysd + 1.0, zsd), net, "piastrina microSD", "terminale piastrina microSD")

    # --- massa della schermatura (docs/schermatura_massa.md): capocorda L0 sulla vite del retro, L1 sulla torretta
    _, x0, z0, _ = C.MASSA_L0
    add("MASSA:L0", (x0, YI - 3.0, z0), "GND", "massa L0", "capocorda sulla vite del pannello posteriore")
    add("MASSA:L1", (C.MASSA_L1["x"], C.MASSA_L1["y"], C.T_FLOOR + C.MASSA_L1["h"] + 1.0), "GND", "capocorda massa L1",
        "capocorda sulla torretta del fondo")

    return T


# ----------------------------------------------------------------------------- elenco dei fili


def catena_greedy(T, partenza, pot_chiavi):
    """ordine dei pot per una catena che parte da una piazzola: sempre il piu vicino non ancora collegato"""
    cur = T[partenza]["p"]
    rest = list(pot_chiavi)
    ordine = []
    while rest:
        k = min(rest, key=lambda i: math.dist(cur[:2], T[f"POT{i}:W"]["p"][:2]))
        ordine.append(k)
        rest.remove(k)
        cur = T[f"POT{k}:W"]["p"]
    return ordine


def fili(T):
    """lista di dict: id, da, a, sig, tipo, calza, nota, coppia"""
    W = []

    def w(id_, da, a, sig, tipo, nota="", calza="", coppia=None, hz=False, via=None):
        W.append(dict(id=id_, da=da, a=a, sig=sig, tipo=tipo, nota=nota, calza=calza, coppia=coppia, hz=hz, via=via))

    for s in "LR":
        w(f"IN {s} a", f"JI{s}:rs", f"ILS:COM {s}", f"IN {s}", "schermato",
          "punta (con Rs 10k) -> deviatore INST/LINE", "lato INST/LINE", hz=True)
        w(f"IN {s} b", f"ILS:COM {s}", f"SC:IN {s}", f"IN {s}", "schermato",
          "nodo INST/LINE -> ingresso schedina", "lato schedina", hz=True)
        w(f"IN {s} c", f"ILS:COM {s}", f"PRE:OFF {s}", f"IN {s}", "schermato",
          "nodo INST/LINE -> PRE, posizione OFF", "lato INST/LINE", hz=True)
        w(f"IN {s} d", f"SC:OUT {s}", f"PRE:ON {s}", f"IN {s}", "schermato",
          "uscita schedina -> PRE, posizione ON", "lato schedina", hz=True)
        w(f"IN {s} e", f"PRE:COM {s}", f"VB:IN {s}", f"IN {s}", "schermato",
          "PRE comune -> piazzola IN della veroboard", "lato veroboard", hz=True)
        w(f"IN {s} f", f"ILS:GND {s}", f"JI{s}:sleeve", "GND", "normale",
          "giunto di massa di Rsh/calze -> manicotto IN")
        w(f"IN {s} g", f"JI{s}:sleeve", f"VB:IN {s} GND", "GND", "normale", "manicotto IN -> piazzola GND")
        pk = "A" if s == "L" else "B"
        w(f"BYP {s}", f"JI{s}:tip", f"FS:{pk} byp", f"IN {s}", "schermato",
          "ingresso diretto -> 3PDT, posizione bypass", "lato jack", hz=True)
        w(f"OUT {s} a", f"VB:OUT {s}", f"FS:{pk} eff", f"OUT {s}", "normale",
          "veroboard (100R) -> 3PDT, posizione effetto")
        w(f"OUT {s} b", f"FS:{pk} com", f"JO{s}:tip", f"OUT {s}", "schermato",
          "3PDT comune -> punta jack OUT (in bypass porta il segnale diretto)", "lato jack")
        w(f"OUT {s} c", f"JO{s}:sleeve", f"VB:OUT {s} GND", "GND", "normale", "manicotto OUT -> piazzola GND")
    # schedina: alimentazione e GAIN
    w("SC VA", "VB:VA EXT", "SC:VA", "VA", "intrecciato", "VA -> schedina (piazzola VA EXT, 29/10)", coppia="SCHEDINA")
    w("SC GND", "VB:PRE GND", "SC:GND", "GND", "intrecciato", "massa schedina (piazzola PRE GND, 29/10)", coppia="SCHEDINA")
    for s in "LR":
        w(f"GAIN A {s}", f"SC:GAIN A {s}", f"GAIN:A {s}", f"GAIN {s}", "intrecciato", "S1 -> capo A della gang", coppia=f"GAIN {s}")
        w(f"GAIN B {s}", f"SC:GAIN B {s}", f"GAIN:B {s}", f"GAIN {s}", "intrecciato", "220R -> capo B della gang", coppia=f"GAIN {s}")
    # massa della schermatura: un solo punto (L0), unito al manicotto di IN L e al rame del fondo (L1)
    w("F0", "MASSA:L0", "JIL:sleeve", "GND", "normale", "punto unico di massa -> manicotto IN L")
    w("F1", "MASSA:L0", "MASSA:L1", "GND", "normale", "rame del pannello posteriore -> rame del fondo")
    # DC
    w("DC +9V", "VB:DC +9V", "DC:sleeve", "+9V", "intrecciato", "+9 V al manicotto", coppia="DC")
    w("DC GND", "VB:DC GND", "DC:center", "GND", "intrecciato", "massa al centrale", coppia="DC")
    # tasti, pedale, LED
    w("K1", "VB:FS1", "TASTI:D0", "D0", "normale", "tasto K1")
    w("K2", "VB:FS2", "TASTI:D10", "D10", "normale", "tasto K2")
    w("KGND", "VB:CTRL GND", "TASTI:GND", "GND", "normale", "massa tasti e LED")
    w("LED", "VB:LED", "TASTI:LED+", "LED", "normale", "LED (1K sulla scheda)")
    w("PED tip", "JP:tip", "TASTI:D0", "D0", "normale", "pedale punta, in parallelo a K1")
    w("PED ring", "JP:ring", "TASTI:D10", "D10", "normale", "pedale anello, in parallelo a K2")
    w("PED sleeve", "JP:sleeve", "TASTI:GND", "GND", "normale", "pedale manicotto")
    # encoder
    w("ENC A", "VB:ENC A", "ENC:A", "ENC_A", "normale")
    w("ENC B", "VB:ENC B", "ENC:B", "ENC_B", "normale")
    w("ENC SW", "VB:ENC SW", "ENC:SW", "ENC_SW", "normale")
    w("ENC GND", "VB:CTRL GND", "ENC:C", "GND", "normale", "massa encoder")
    w("ENC ponte", "ENC:C", "ENC:SW2", "GND", "normale", "ponticello fra comune e 2o pin del pulsante (sull'encoder)")
    # OLED
    w("OLED SCL", "VB:SCL", "OLED:SCL", "SCL", "normale", "I2C: corto, accanto a SDA")
    w("OLED SDA", "VB:SDA", "OLED:SDA", "SDA", "normale", "I2C: corto, accanto a SCL")
    w("OLED 3V3", "VB:3V3D", "OLED:VCC", "3V3D", "intrecciato", coppia="OLED")
    w("OLED GND", "VB:OLED GND", "OLED:GND", "GND", "intrecciato", coppia="OLED")
    # MIDI / microSD
    w("MIDI TX", "VB:MIDI TX", "MIDI:TX", "MIDI_TX", "normale")
    w("MIDI RX", "VB:MIDI RX", "MIDI:RX", "MIDI_RX", "normale")
    w("MIDI 3V3", "VB:IO 3V3D", "MIDI:3V3", "3V3D", "intrecciato", coppia="MIDI")
    w("MIDI GND", "VB:IO GND", "MIDI:GND", "GND", "intrecciato", coppia="MIDI")
    w("SD D0", "VB:SD D0", "SD:D0", "SD_D0", "normale")
    w("SD CMD", "VB:SD CMD", "SD:CMD", "SD_CMD", "normale")
    w("SD CLK", "VB:SD CK", "SD:CLK", "SD_CK", "normale", "clock: il piu corto possibile")
    w("SD 3V3", "VB:IO 3V3D", "SD:3V3", "3V3D", "intrecciato", coppia="SD")
    w("SD GND", "VB:IO GND", "SD:GND", "GND", "intrecciato", coppia="SD")
    # pot: cursori e due catene (3V3A, AGND)
    for i in range(1, 7):
        w(f"POT{i} W", f"VB:A{i - 1}", f"POT{i}:W", f"A{i - 1}", "normale", "cursore, lontano dall'I2C")
    for partenza, estremo, sig in (("VB:3V3A", "HI", "3V3A"), ("VB:POT GND", "LO", "AGND")):
        prec = partenza
        for i in catena_greedy(T, partenza, range(1, 7)):
            w(f"{sig} P{i}", prec, f"POT{i}:{estremo}", sig, "normale", "catena a margherita")
            prec = f"POT{i}:{estremo}"
    # LED del bypass
    w("LEDFS +", "VB:VA EXT", "FS:C com", "LEDFS", "normale",
      "VA -> R 4,7k saldata sul lug comune del polo C (~1,5 mA a 8,5 V con LED rosso)")
    w("LEDFS A", "FS:C eff", "LEDFS:A", "LEDFS", "normale", "polo C, posizione effetto -> anodo")
    gl = min(["CTRL GND", "OUT L GND", "OUT R GND"], key=lambda n: math.dist(T["LEDFS:K"]["p"][:2], T[f"VB:{n}"]["p"][:2]))
    w("LEDFS K", "LEDFS:K", f"VB:{gl}", "GND", "normale", f"catodo -> massa piu vicina ({gl}); ~1 mA continui")
    return W


# ----------------------------------------------------------------------------- ostacoli
class Ost:
    def __init__(self, nome, solido=None, bb=None):
        self.nome = nome
        self.solido = solido
        if bb is None:
            b = solido.bounding_box()
            bb = (b.min.X, b.max.X, b.min.Y, b.max.Y, b.min.Z, b.max.Z)
        self.bb = tuple(bb)


def torre_footswitch():
    """torre di sostegno del footswitch, con la fessura per i fili (copia fedele del taglio di case.py)"""
    fx, fy = C.FS_C
    l_in, t = C.FS["torre_luce"], C.FS["torre_parete"]
    z_base = C.T_FLOOR + C.GIOCO
    torre = C.sul_top(*C.FS_C) * C.Pos(0, 0, -C.T_TOP - 30) * (C.Box(l_in + 2 * t, l_in + 2 * t, 60) - C.Box(l_in, l_in, 70))
    torre = torre & C.fascia(-200, -C.T_TOP + 0.01) & C.box(-1, C.W + 1, -1, C.D + 1, z_base, C.HB + 10)
    fw, fh = C.FS["fessura"]
    yf = fy + (C.z_top(fy) - (z_base + fh / 2)) * math.tan(C.ALPHA)
    torre -= C.box(fx - l_in / 2 - t - 1, fx - l_in / 2 + 0.01, yf - fw / 2, yf + fw / 2, 0, z_base + fh)
    via_dentro = (fx + FS_LATO * (l_in / 2 - 1.5), yf, z_base + 2.5)
    via_fuori = (fx + FS_LATO * (l_in / 2 + t + 1.5), yf, z_base + 2.5)
    return torre, via_dentro, via_fuori


def ostacoli():
    comp = C.componenti()
    O = []
    for nome, s, g in comp:
        if nome in ("schedina preamp",):
            continue
        O.append(Ost(nome, s))
    torre, vd, vf = torre_footswitch()
    O.append(Ost("torre footswitch", torre))
    for (x, y) in C.COLONNE:
        h = C.z_sotto(y) - C.T_FLOOR
        O.append(Ost(f"colonna {x:.0f},{y:.0f}", C.Pos(x, y, C.T_FLOOR + h / 2) * C.cil(C.COLONNA_D, h)))
    for (hx, hy) in C.FORI_FISSAGGIO:
        x, y = C.foro_xy(hx, hy)
        O.append(Ost(f"colonnina veroboard {hx},{hy}", C.Pos(x, y, C.T_FLOOR + C.DISTANZIALE / 2) * C.cil(C.DISTANZIALE_D, C.DISTANZIALE)))
    return O, vd, vf


# nomi dei componenti di scheda che i fili ignorano alla partenza (corpi bassi, 12,5 mm al massimo): il filo sale
# sopra. Seed3, USB-C e teste delle viti restano ostacoli.
def _bassi_scheda():
    out = {"veroboard"}
    for ref, kind, val, pins in L.P:
        if kind != "seed":
            out.add(f"{ref} {val}")
    for name, a, b, net, _ in L.LINKS:
        out.add(f"ponticello {name}")
    return out


BASSI = _bassi_scheda()


def box_sovrapposti(a, b, eps=0.05):
    return (a[0] < b[1] - eps and b[0] < a[1] - eps and a[2] < b[3] - eps and b[2] < a[3] - eps
            and a[4] < b[5] - eps and b[4] < a[5] - eps)


def esatto(p, q, solido):
    r = solido & Edge.make_line(Vector(*p), Vector(*q))
    return sum(e.length for e in r.edges()) > 0.05


def segm_bb(p, q):
    return (min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1]), min(p[2], q[2]), max(p[2], q[2]))


def segm_incrocia_bb(p, q, bb):
    """segmento qualsiasi contro un parallelepipedo (slab)"""
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = q[i] - p[i]
        lo, hi = bb[2 * i], bb[2 * i + 1]
        if abs(d) < 1e-12:
            if p[i] < lo or p[i] > hi:
                return False
        else:
            a, b = (lo - p[i]) / d, (hi - p[i]) / d
            if a > b:
                a, b = b, a
            t0, t1 = max(t0, a), min(t1, b)
            if t0 > t1:
                return False
    return True


class Mondo:
    def __init__(self):
        self.O, self.via_dentro, self.via_fuori = ostacoli()
        self.sch_box = None             # (bb) della schedina, se presente
        self.sch_nome = "schedina preamp"
        self.digit_bb, self.digit_pts = [], []

    def esenti(self, wire, T):
        ex = set()
        for k in (wire["da"], wire["a"]):
            t = T.get(k)
            if t:
                ex.add(t["owner"])
                if t["owner"] == "veroboard":
                    ex |= BASSI
        if "piastrina microSD" in ex:
            ex |= {"zoccolo microSD"}
        return ex

    def blocca(self, pts, ex, sch_wire):
        """prima voce che il percorso (lista di punti, gambe assiali) attraversa; None se libero"""
        for p, q in zip(pts, pts[1:]):
            sb = segm_bb(p, q)
            orizz = abs(p[2] - q[2]) < 1e-9
            # cavita: pareti, sotto al pannello
            ymin = min(p[1], q[1])
            if (sb[0] < C.T_WALL + 0.4 or sb[1] > C.W - C.T_WALL - 0.4 or sb[2] < C.T_WALL + 0.4
                    or sb[3] > YI - 0.2 or sb[4] < C.T_FLOOR + 0.1 or sb[5] > C.z_sotto(ymin) - 0.8):
                return "pareti/pannello"
            for o in self.O:
                if o.nome in ex or not box_sovrapposti(sb, o.bb):
                    continue
                if o.solido is not None and not esatto(p, q, o.solido):
                    continue
                return o.nome
            if self.sch_box is not None:
                b = self.sch_box
                if sch_wire:
                    # i fili della schedina salgono dalla piazzola (tratti verticali esenti) e escono dal bordo:
                    # i tratti orizzontali non passano sopra i componenti (nucleo, 3 mm di bordo esclusi)
                    if orizz:
                        nucleo = (b[0] + 3.0, b[1] - 3.0, b[2] + 3.0, b[3] - 3.0, b[4], b[5])
                        if box_sovrapposti(sb, nucleo):
                            return self.sch_nome
                elif box_sovrapposti(sb, b):
                    return self.sch_nome
        return None

    def diretto_attraversa(self, a, b, ex, sch_wire):
        out = []
        for o in self.O:
            if o.nome in ex:
                continue
            if segm_incrocia_bb(a, b, o.bb) and (o.solido is None or esatto(a, b, o.solido)):
                out.append(o.nome)
        if self.sch_box is not None and not sch_wire and segm_incrocia_bb(a, b, self.sch_box):
            out.append(self.sch_nome)
        return out


def gambe(a, b):
    """gambe assiali da a a b: z sul capo piu basso, tratto orizzontale alla quota piu alta, x poi y"""
    zh = max(a[2], b[2])
    pts = [tuple(a), (a[0], a[1], zh), (b[0], a[1], zh), (b[0], b[1], zh), tuple(b)]
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 1e-9:
            out.append(p)
    return out


def percorso(punti):
    pts = [tuple(punti[0])]
    for q in punti[1:]:
        for p in gambe(pts[-1], q)[1:]:
            pts.append(p)
    return pts


def lung(pts):
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


GRIGLIA = [(x, y, z) for z in range(6, 34, 2) for y in range(4, 128, 4) for x in range(4, 208, 4)]


def penale(mondo, pts):
    """costo di vicinanza alle linee digitali: per ogni campione (2 mm) a meno di 10 mm, 10 - distanza"""
    if not mondo.digit_bb and not mondo.digit_pts:
        return 0.0
    P = campiona(pts, 2.0)
    d = np.full(len(P), 1e9)
    for nome, bb in mondo.digit_bb:
        d = np.minimum(d, dist_bb(P, bb))
    for nome, Q in mondo.digit_pts:
        d = np.minimum(d, np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(-1)).min(1))
    return float(np.maximum(0.0, 10.0 - d).sum())


def instrada(mondo, a, b, ex, sch_wire, hz=False):
    """percorso libero piu corto: diretto, altrimenti un punto intermedio su griglia (poi due).
    hz=True: fra i primi 25 percorsi liberi sceglie quello con meno vicinanza ai fili digitali.
    Ritorna (pts, via, nome_ostacolo_del_diretto)"""
    diretto = percorso([a, b])
    ost = mondo.blocca(diretto, ex, sch_wire)
    if ost is None and not hz:
        return diretto, [], None
    cand = ([[]] if ost is None else []) + [[p] for p in sorted(GRIGLIA, key=lambda p: lung(percorso([a, p, b])))[:6000]]
    trovati = []
    for vv in cand:
        pts = percorso([a] + vv + [b])
        if mondo.blocca(pts, ex, sch_wire) is None:
            trovati.append((lung(pts), pts, vv))
            if not hz or len(trovati) >= 25:
                break
    if trovati:
        if hz:
            ln, pts, vv = min(trovati, key=lambda t: t[0] + penale(mondo, t[1]))
        else:
            ln, pts, vv = trovati[0]
        return pts, vv, ost
    rada = [p for p in GRIGLIA if p[0] % 8 == 4 and p[1] % 8 == 4 and p[2] % 4 == 2]
    best = None
    for p in rada:
        for q in rada:
            if p >= q:
                continue
            for pp, qq in ((p, q), (q, p)):
                ln = lung(percorso([a, pp, qq, b]))
                if best is None or ln < best[0]:
                    pts = percorso([a, pp, qq, b])
                    if mondo.blocca(pts, ex, sch_wire) is None:
                        best = (ln, pts, [pp, qq])
    if best:
        return best[1], best[2], ost
    return diretto, [], (ost or "") + " (NON INSTRADABILE)"


# ----------------------------------------------------------------------------- calcolo dei fili
def calcola(mondo, T, W, schedina=True):
    R = {}
    for w in W:
        ta, tb = T.get(w["da"]), T.get(w["a"])
        r = dict(w)
        r["mancante"] = None
        if ta is None or tb is None:
            r["mancante"] = f"terminale inesistente: {w['da'] if ta is None else w['a']}"
            R[w["id"]] = r
            continue
        if ta.get("manca") or tb.get("manca"):
            r["mancante"] = (ta if ta.get("manca") else tb)["desc"]
            R[w["id"]] = r
            continue
        a, b = ta["p"], tb["p"]
        sch_wire = "schedina preamp" in (ta["owner"], tb["owner"])
        ex = mondo.esenti(w, T)
        hz = w["id"] in HZ_ORI or w["hz"]
        if "footswitch 3PDT" in (ta["owner"], tb["owner"]):
            # il filo esce dalla fessura della torre (percorso fisso dal lug alla fessura), poi cerca la strada
            vd, vf = mondo.via_dentro, mondo.via_fuori
            if ta["owner"] == "footswitch 3PDT":
                dentro = percorso([a, vd, vf])
                fuori, via2, ost = instrada(mondo, vf, b, ex, sch_wire, hz)
                pts = dentro + fuori[1:]
                via = [vd, vf] + via2
            else:
                fuori, via2, ost = instrada(mondo, a, vf, ex, sch_wire, hz)
                dentro = percorso([vf, vd, b])
                pts = fuori + dentro[1:]
                via = via2 + [vf, vd]
            ost = mondo.blocca(pts, ex, sch_wire)
        else:
            pts, via, ost = instrada(mondo, a, b, ex, sch_wire, hz)
        r.update(pa=a, pb=b, pts=pts, via=via, ostacolo=ost, hzw=hz, nom=lung(pts),
                 retto=math.dist(a, b), attraversa=mondo.diretto_attraversa(a, b, ex, sch_wire))
        r["taglio"] = taglio(r["nom"], w["tipo"])
        R[w["id"]] = r
    return R


def taglio(nom, tipo):
    v = nom * (1 + MARGINE_PCT) + MARGINE_FISSO
    if tipo == "intrecciato":
        v *= 1 + EXTRA_INTRECCIO
    return math.ceil(v / ARROTONDA) * ARROTONDA


# ----------------------------------------------------------------------------- orientamento della schedina
DIGITALI_PREF = ("Seed3", "USB-C", "OLED", "scheda MIDI", "piastrina", "zoccolo")
SEG_DIGITALI = ("SCL", "SDA", "MIDI_TX", "MIDI_RX", "SD_D0", "SD_CMD", "SD_CK", "ENC_A", "ENC_B", "ENC_SW", "D0", "D10", "LED")
HZ_IN = ("IN L b", "IN R b")                     # ingresso schedina: i piu sensibili (10k + sorgente)
HZ_GAIN = ("GAIN A L", "GAIN B L", "GAIN A R", "GAIN B R")   # nodo di source del primo stadio
HZ_OUT = ("IN L d", "IN R d")                    # uscita schedina verso PRE (dopo il LEVEL)
HZ_ORI = HZ_IN + HZ_GAIN + HZ_OUT                # i fili che dipendono dall'orientamento
PESO_OUT = 0.5                                   # peso dell'uscita rispetto a ingresso e GAIN nel punteggio
CATENA_IN = [f"IN {s} {k}" for s in "LR" for k in "abcde"]


def campiona(pts, passo=1.0):
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.dist(p, q) / passo))
        for i in range(n):
            t = i / n
            out.append([p[j] + (q[j] - p[j]) * t for j in range(3)])
    out.append(list(pts[-1]))
    return np.array(out)


def dist_bb(P, bb):
    d = np.zeros(len(P))
    for i in range(3):
        lo, hi = bb[2 * i], bb[2 * i + 1]
        d += np.maximum(np.maximum(lo - P[:, i], P[:, i] - hi), 0.0) ** 2
    return np.sqrt(d)


def distanza_digitale(pts, digit_bb, digit_pts):
    P = campiona(pts)
    dmin, chi = 1e9, ""
    for nome, bb in digit_bb:
        d = dist_bb(P, bb).min()
        if d < dmin:
            dmin, chi = d, nome
    for nome, Q in digit_pts:
        d = np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(-1)).min()
        if d < dmin:
            dmin, chi = d, "filo " + nome
    return dmin, chi


def box_libero(mondo_O, ori, org):
    """la schedina nel suo volume non tocca componenti (esatto) ne pareti"""
    bb = sched_box(ori, org)
    if bb[0] < C.T_WALL + 0.5 or bb[1] > C.W - C.T_WALL - 0.5 or bb[2] < C.T_WALL + 0.5 or bb[3] > YI - 0.2:
        return False
    sol = C.box(*bb)
    for o in mondo_O:
        if box_sovrapposti(bb, o.bb) and (o.solido is None or C.urti(sol, o.solido) > 0):
            return False
    return True


def valuta_orientamento(mondo, ori, org, W, fissi_cache, digit_bb, digit_pts):
    T = terminali(ori, org)
    mondo.sch_box = sched_box(ori, org)
    ris = {}
    for w in W:
        if w["id"] in HZ_ORI:
            ris[w["id"]] = calcola_uno(mondo, T, w)
    l_in = sum(ris[i]["nom"] for i in HZ_IN)
    l_gain = sum(ris[i]["nom"] for i in HZ_GAIN)
    l_out = sum(ris[i]["nom"] for i in HZ_OUT)
    hz = l_in + l_gain + PESO_OUT * l_out
    dmin, chi = 1e9, ""
    for i in HZ_ORI:
        d, c_ = distanza_digitale(ris[i]["pts"], digit_bb, digit_pts)
        if d < dmin:
            dmin, chi = d, c_
    # catena d'ingresso completa: i fili fissi si prendono dalla cache
    tot = sum(ris[i]["nom"] for i in HZ_IN + HZ_OUT) + sum(fissi_cache[i]["nom"] for i in CATENA_IN if i not in HZ_ORI)
    bloccati = [i for i in HZ_ORI if ris[i]["ostacolo"] and "NON INSTRADABILE" in str(ris[i]["ostacolo"])]
    return dict(hz=hz, l_in=l_in, l_gain=l_gain, l_out=l_out, dmin=dmin, chi=chi, tot=tot, bloccati=bloccati, ris=ris)


def calcola_uno(mondo, T, w):
    return calcola(mondo, T, [w])[w["id"]]


def analizza_orientamento(mondo, W0, T0):
    """prova gli orientamenti. Ritorna (tabella, scelta, org_scelta)"""
    # fili fissi e digitali (non dipendono dalla schedina)
    mondo.sch_box = None
    fissi = calcola(mondo, T0, [w for w in W0 if w["id"] in CATENA_IN and w["id"] not in HZ_ORI])
    dig_w = [w for w in W0 if w["sig"] in SEG_DIGITALI]
    dr = calcola(mondo, T0, dig_w)
    digit_pts = [(k, campiona(r["pts"])) for k, r in dr.items() if not r["mancante"]]
    digit_bb = [(o.nome, o.bb) for o in mondo.O if o.nome.startswith(DIGITALI_PREF)]
    mondo.digit_bb, mondo.digit_pts = digit_bb, digit_pts
    tab = {}
    for ori in ORIENTAMENTI:
        tr = ORIENTAMENTI[ori][2]
        if not tr:
            org = SCH_ORG0
            if not box_libero(mondo.O, ori, org):
                tab[ori] = dict(org=org, libero=False)
                continue
        else:
            org = trasposta_posizione(mondo, ori)
            if org is None:
                tab[ori] = dict(org=None, libero=False)
                continue
        v = valuta_orientamento(mondo, ori, org, W0, fissi, digit_bb, digit_pts)
        v.update(org=org, libero=True)
        tab[ori] = v
    buoni = {k: v for k, v in tab.items() if v["libero"] and not v["bloccati"]}
    ok_dist = {k: v for k, v in buoni.items() if v["dmin"] >= DIST_DIGITALE_MIN}
    pool = ok_dist or buoni
    mn = min(v["hz"] for v in pool.values())
    vicini = [k for k, v in pool.items() if v["hz"] <= mn + 5.0]
    scelta = max(vicini, key=lambda k: round(pool[k]["dmin"], 0)) if len(vicini) > 1 else vicini[0]
    if PROVVISORIA in vicini and round(pool[PROVVISORIA]["dmin"]) >= round(pool[scelta]["dmin"]):
        scelta = PROVVISORIA
    return tab, scelta, fissi, dr


def trasposta_posizione(mondo, ori):
    """posizione libera del volume ruotato di 90 gradi, vicino al centro del volume attuale: scansione"""
    cx = SCH_ORG0[0] + SCH_BOX[0] / 2
    cy = SCH_ORG0[1] + SCH_BOX[1] / 2
    w, d = SCH_BOX[1], SCH_BOX[0]
    best = None
    for ox in range(int(SCH_ORG0[0]) - 2, int(SCH_ORG0[0]) + 40, 2):
        for oy in range(int(SCH_ORG0[1]) - 30, int(SCH_ORG0[1]) + 6, 2):
            dd = math.hypot(ox + w / 2 - cx, oy + d / 2 - cy)
            if best is not None and dd >= best[0]:
                continue
            if box_libero(mondo.O, ori, (float(ox), float(oy))):
                best = (dd, (float(ox), float(oy)))
    return best[1] if best else None


def scansione_spostamento(mondo, ori, org, W, T):
    """sposta il volume della schedina di qualche mm dove e' libero (componenti esatti) e misura la distanza
    in pianta (Manhattan) dei capi dei fili sensibili; ritorna (costo_nominale, miglior_costo, (dx, dy))"""
    def costo(o):
        c = 0.0
        for w in W:
            if w["id"] in HZ_IN + HZ_GAIN:
                altro = w["da"] if w["a"].startswith("SC:") else w["a"]
                sc = w["a"] if w["a"].startswith("SC:") else w["da"]
                hx, hy = next(pp for n, pp, _, _ in LP.PADS if f"SC:{n}" == sc)
                x, y = sched_xy(hx, hy, ori, o)
                q = T[altro]["p"]
                c += abs(x - q[0]) + abs(y - q[1])
        return c
    nom = costo(org)
    best = (nom, (0, 0))
    for dx in range(-4, 5):
        for dy in range(-8, 9):
            o = (org[0] + dx, org[1] + dy)
            if (dx or dy) and box_libero(mondo.O, ori, o):
                c = costo(o)
                if c < best[0] - 0.01:
                    best = (c, (dx, dy))
    return nom, best[0], best[1]


# ----------------------------------------------------------------------------- verifica
def ori_case():
    """orientamento gia scritto in case.py (SCHEDINA_ORI = dict(foro=+-1, striscia=+-1, trasposta=bool)), o None"""
    o = getattr(C, "SCHEDINA_ORI", None)
    if not o:
        return None
    t = (o["foro"], o["striscia"], bool(o["trasposta"]))
    for k, v in ORIENTAMENTI.items():
        if v == t:
            return k
    return None


def verifica(T, W, R, tab, scelta, ori_uso, org_uso):
    err = []
    # 1. terminali esistenti
    for w in W:
        for k in (w["da"], w["a"]):
            if k not in T:
                err.append(f"filo {w['id']}: il terminale {k} non esiste (nessuna piazzola/terminale definito)")
    # 2. reti coerenti ai due capi
    for w in W:
        ta, tb = T.get(w["da"]), T.get(w["a"])
        if ta and tb and ta["net"] != tb["net"]:
            err.append(f"filo {w['id']}: collega le reti {ta['net']} e {tb['net']} ({w['da']} -> {w['a']})")
    # 3. ogni piazzola dei layout ha almeno un filo
    usati = {k for w in W for k in (w["da"], w["a"])}
    for n, _, net, _ in L.PADS:
        if f"VB:{n}" not in usati:
            err.append(f"piazzola veroboard '{n}' senza nessun filo")
    for n, _, net, _ in LP.PADS:
        if f"SC:{n}" not in usati:
            err.append(f"piazzola schedina '{n}' senza nessun filo")
    # 4. percorsi liberi
    for i, r in R.items():
        if r.get("mancante"):
            continue
        if r["ostacolo"] and "NON INSTRADABILE" in r["ostacolo"]:
            err.append(f"filo {i}: percorso bloccato da {r['ostacolo']}")
        elif r_blocca_finale(r):
            err.append(f"filo {i}: il percorso attraversa {r_blocca_finale(r)}")
        if r["nom"] < 3.0:
            err.append(f"filo {i}: lunghezza {r['nom']:.1f} mm, capi coincidenti")
    # 5. orientamento in uso: ingresso entro la soglia del migliore
    best = min(v["hz"] for v in tab.values() if v["libero"] and not v["bloccati"])
    uso = tab.get(ori_uso)
    if uso is None or not uso["libero"]:
        err.append(f"orientamento in uso '{ori_uso}': volume che urta componenti")
    else:
        if uso["hz"] > TOLL_HZ * best:
            err.append(f"orientamento in uso '{ori_uso}': fili d'ingresso (punteggio) a {uso['hz']:.0f} mm, oltre {TOLL_HZ:.2f} volte il migliore ({best:.0f} mm di punteggio)")
        if uso["dmin"] < DIST_MIN_ERR:
            err.append(f"orientamento in uso: filo d'ingresso a {uso['dmin']:.1f} mm da {uso['chi']}")
    return err


_MONDO_CACHE = {}


def r_blocca_finale(r):
    m = _MONDO_CACHE["mondo"]
    T = _MONDO_CACHE["T"]
    ex = m.esenti(r, T)
    return m.blocca(r["pts"], ex, "schedina preamp" in (T[r["da"]]["owner"], T[r["a"]]["owner"]))


# ----------------------------------------------------------------------------- stampa
COLORI = {"IN L": "bianco", "IN R": "rosso", "OUT L": "bianco", "OUT R": "rosso", "GND": "nero", "+9V": "rosso",
          "VA": "rosso", "3V3D": "arancione", "3V3A": "arancione", "AGND": "nero", "SCL": "giallo", "SDA": "verde",
          "MIDI_TX": "blu", "MIDI_RX": "viola", "SD_D0": "grigio", "SD_CMD": "marrone", "SD_CK": "bianco",
          "ENC_A": "giallo", "ENC_B": "verde", "ENC_SW": "blu", "D0": "giallo", "D10": "verde", "LED": "viola",
          "LEDFS": "arancione", "GAIN L": "bianco", "GAIN R": "rosso"}


def colore(w):
    if w["sig"].startswith("A") and w["sig"][1:].isdigit():
        return "grigio"
    return COLORI.get(w["sig"], "grigio")


def tabella(R):
    righe = []
    for i, r in R.items():
        if r.get("mancante"):
            righe.append((i, r["da"], r["a"], r["sig"], r["tipo"], colore(r), None, None, r["mancante"]))
        else:
            righe.append((i, r["da"], r["a"], r["sig"], r["tipo"], colore(r), r["nom"], r["taglio"],
                          r["nota"] + (f" [via {len(r['via'])} pt]" if r["via"] else "")))
    return righe


def totali(R):
    tot = {}
    for r in R.values():
        if r.get("mancante"):
            continue
        t = tot.setdefault(r["tipo"], [0, 0.0])
        t[0] += 1
        t[1] += r["taglio"]
    return tot


def fmt_p(p):
    return f"({p[0]:.1f}, {p[1]:.1f}, {p[2]:.1f})"


def stampa_tutto(T, W, R, tab, scelta, ori_uso, org_uso, err, mondo):
    print(f"Cablaggio PA-TELAIO: {len(W)} fili, {sum(1 for r in R.values() if r.get('mancante'))} senza piazzola/terminale")
    print(f"margine di taglio: {MARGINE_FISSO:.0f} mm fissi + {MARGINE_PCT:.0%} del percorso (+{EXTRA_INTRECCIO:.0%} se intrecciato), "
          f"arrotondato a {ARROTONDA:.0f} mm")
    print()
    print(f"{'filo':11s} {'da':16s} {'a':16s} {'segnale':8s} {'tipo':11s} {'colore':9s} {'perc.':>6s} {'taglio':>6s}  note")
    for (i, da, a, sig, tipo, col, nom, tg, nota) in tabella(R):
        if nom is None:
            print(f"{i:11s} {da:16s} {a:16s} {sig:8s} {tipo:11s} {col:9s} {'-':>6s} {'-':>6s}  SENZA PIAZZOLA: {nota}")
        else:
            print(f"{i:11s} {da:16s} {a:16s} {sig:8s} {tipo:11s} {col:9s} {nom:6.0f} {tg:6.0f}  {nota}")
    print()
    print("Capi 3D dei fili (mm, X sinistra->destra, Y fronte->retro, Z in su):")
    for i, r in R.items():
        if r.get("mancante"):
            continue
        extra = f"  via {', '.join(fmt_p(v) for v in r['via'])}" if r["via"] else ""
        print(f"  {i:11s} {fmt_p(r['pa'])} -> {fmt_p(r['pb'])}{extra}")
    print()
    print("Totale da tagliare per tipo di filo (lunghezze di taglio, senza i fili senza piazzola):")
    for t, (n, mm) in sorted(totali(R).items()):
        print(f"  {t:11s} {n:3d} fili  {mm:7.0f} mm  ({mm / 1000:.2f} m)")
    print(f"  {'TOTALE':11s} {sum(v[0] for v in totali(R).values()):3d} fili  {sum(v[1] for v in totali(R).values()):7.0f} mm")
    print()
    print("Orientamento della schedina. Lunghezze di percorso in mm, L+R: IN b = nodo INST/LINE -> ingresso schedina, GAIN = 4 fili del pot,")
    print(f"  OUT d = uscita schedina -> PRE; punteggio = IN b + GAIN + {PESO_OUT} x OUT d; catena = i 10 fili IN a-e; dist. = minimo da corpi e fili digitali")
    print(f"  dei fili sensibili (voluta {DIST_DIGITALE_MIN:.0f} mm). Scelta: punteggio piu basso (entro 5 mm vince la distanza maggiore, poi l'ordine):")
    print(f"  {'opzione':36s} {'origine':>9s} {'IN b':>6s} {'GAIN':>6s} {'OUT d':>6s} {'punt.':>6s} {'catena':>7s} {'dist.':>6s}  piu vicino digitale")
    for k, v in tab.items():
        if not v["libero"]:
            print(f"  {k:36s} {'-':>13s}  volume urta componenti: scartata")
            continue
        flag = " <- scelta" if k == scelta else ""
        flag += " (in uso)" if k == ori_uso and k != scelta else ""
        print(f"  {k:36s} {f'({v['org'][0]:.0f},{v['org'][1]:.0f})':>9s} {v['l_in']:6.0f} {v['l_gain']:6.0f} {v['l_out']:6.0f} {v['hz']:6.0f} {v['tot']:7.0f} {v['dmin']:6.1f}  {v['chi']}{flag}")
    print()
    prima = tab[PROVVISORIA]
    dopo = tab[scelta]
    print(f"Fili sensibili: provvisoria IN b {prima['l_in']:.0f} + GAIN {prima['l_gain']:.0f} mm -> scelta IN b {dopo['l_in']:.0f} + GAIN {dopo['l_gain']:.0f} mm "
          f"(catena IN L+R {prima['tot']:.0f} -> {dopo['tot']:.0f} mm di percorso); distanza dai digitali {prima['dmin']:.1f} -> {dopo['dmin']:.1f} mm")
    print()
    print("Percorso libero: fili che il segmento dritto fra i capi attraversa (HZ e lunghi) e punto di passaggio proposto")
    for i, r in R.items():
        if r.get("mancante"):
            continue
        if (r["hz"] or r["taglio"] >= LUNGO) and r["attraversa"]:
            via = f" -> passa da {', '.join(fmt_p(v) for v in r['via'])}" if r["via"] else " (percorso a gambe assiali gia libero)"
            print(f"  {i:11s} {r['retto']:5.0f} mm dritti, attraversa: {', '.join(r['attraversa'])}{via}")
    print()
    lunghi = [(i, r["taglio"]) for i, r in R.items() if not r.get("mancante") and r["taglio"] >= LUNGO]
    if lunghi:
        print("Fili lunghi (>= %d mm di taglio): " % LUNGO + ", ".join(f"{i} {t:.0f}" for i, t in sorted(lunghi, key=lambda x: -x[1])))
    print()
    print("Costanti per case.py (orientamento scelto, schedina):")
    fd, sd, tr = ORIENTAMENTI[scelta]
    org = tab[scelta]["org"]
    print(f"  SCHEDINA_ORI = dict(foro={fd:+d}, striscia={sd:+d}, trasposta={tr})   # {scelta}")
    print(f"  SCHEDINA = dict(x=({org[0]:.0f}.0, {org[0] + (SCH_BOX[1] if tr else SCH_BOX[0]):.0f}.0), "
          f"y=({org[1]:.0f}.0, {org[1] + (SCH_BOX[0] if tr else SCH_BOX[1]):.0f}.0), alt=17.5, colonnina=4.0, colonnina_d=6.0)")
    cols = [sched_xy(hx, hy, scelta, org) for hx, hy in C.SCHEDINA_FORI]
    print(f"  colonnine (x, y) = {[(round(x, 2), round(y, 2)) for x, y in cols]}   # foro (21,1) e (21,16) trasformati")
    print("  sched_xy(hx, hy) = x0/y0 + ((hx+0.5)*2.54 oppure 60.96-..., ...) come in cablaggio.py: sched_xy()")
    oc = ori_case()
    print(f"  case.py oggi: {'SCHEDINA_ORI = ' + str(oc) if oc else 'nessuna SCHEDINA_ORI (orientamento provvisorio identico)'}")
    print()
    if err:
        print("ERRORI:")
        for e in err:
            print(" -", e)
    else:
        n_ok = sum(1 for r in R.values() if not r.get("mancante"))
        print(f"OK: {len(W)} fili ({n_ok} con capi definiti), reti coerenti ai due capi, ogni piazzola dei layout cablata, "
              f"percorsi liberi, orientamento '{ori_uso}' entro {TOLL_HZ:.2f}x il migliore.")


def scrivi_md(T, W, R, tab, scelta, ori_uso):
    prima, dopo = tab[PROVVISORIA], tab[scelta]
    fd, sd, tr = ORIENTAMENTI[scelta]
    org = dopo["org"]
    L_ = []
    p = L_.append
    p("# PA-TELAIO: cablaggio del case stampato\n")
    p("Generato da `case/cablaggio.py` (`cd case && uv run cablaggio.py --scrivi-md`). Le coordinate dei capi e le")
    p("lunghezze vengono dal modello `case/case.py` e dai layout; se cambiano, rilancia lo script e rileggi questa pagina.")
    p("Le posizioni dei terminali dentro i corpi (jack, deviatori, pot, encoder, footswitch, OLED) sono STIME dalle misure")
    p("di ingombro: prima di tagliare i fili controllali sul pezzo vero.\n")
    p("## Regole\n")
    p("- **Ingressi schermati**: ogni filo audio d'ingresso (jack IN, nodo INST/LINE, PRE, schedina, bypass) e' un cavetto")
    p("  schermato (un conduttore, calza). La calza va a massa **da un solo lato** (colonna `calza`), mai da tutti e due: l'altro")
    p("  capo resta tagliato corto e isolato con guaina.")
    p("- **Rs 10 kOhm sul jack**: la Rs d'ingresso e' saldata sulla punta del jack IN, cosi il cavo dopo la Rs vede 10 kOhm piu la")
    p("  sorgente e non la sorgente nuda. Rsh 3,3 kOhm: fra il terminale LINE del deviatore INST/LINE e il giunto di massa del")
    p("  deviatore (stesso giunto del filo `IN x f` e delle calze).")
    p("- **Alimentazione intrecciata**: DC (+9 V e massa), VA e massa della schedina, 3V3D e massa di OLED, MIDI e microSD, e i due")
    p("  capi di ogni gang del GAIN, intrecciati a coppie (circa 3 giri per cm). Il taglio e' gia maggiorato del 10 %.")
    p("- **I2C corto**: SCL e SDA affiancati, il piu corti possibile, lontani dai fili d'ingresso e dai cursori dei pot.")
    p("  Cursori dei pot: lontani dall'I2C e dal clock della microSD.")
    p("- Piu fili nello stesso foro (massa controlli, 3V3D/GND della scheda I/O, massa OUT): al massimo due per foro; se non")
    p("  entrano, un giunto di massa sul filo.")
    p("- Sezione: AWG 24-26 per alimentazione, AWG 26-28 per segnali.\n")
    p("## Convenzioni di calcolo\n")
    p(f"- Lunghezza di taglio = percorso a gambe assiali in 3D (salita sul capo piu basso, tratto orizzontale alla quota piu alta,")
    p(f"  x poi y) piu un margine: **{MARGINE_FISSO:.0f} mm fissi** (6 per capo: spelatura e saldatura) piu **{MARGINE_PCT:.0%}** del percorso per i giri")
    p(f"  intorno ai corpi, piu {EXTRA_INTRECCIO:.0%} se intrecciato; arrotondata per eccesso a {ARROTONDA:.0f} mm.")
    p("- Un filo che incontra un corpo passa da un punto intermedio (colonna `via` nello script) cercato su griglia: il piu corto")
    p("  che lo libera. I fili del footswitch escono dalla fessura della torre.")
    p("- Per PRE: DPDT, un polo per canale, commuta l'USCITA (comune = piazzola IN della veroboard; OFF = nodo INST/LINE; ON = OUT")
    p("  schedina). L'ingresso della schedina resta sempre sul nodo INST/LINE (con un polo per canale non si commutano i due capi):")
    p("  con PRE spento la schedina carica comunque il nodo con ~1 MOhm in parallelo e resta alimentata.\n")
    p("## Orientamento della schedina preamp\n")
    p(f"**Scelta: {scelta}.** In `case.py` aggiungere `SCHEDINA_ORI = dict(foro={fd:+d}, striscia={sd:+d}, trasposta={tr})`")
    p("(`foro=+1`: foro 0 verso x/y minore dell'asse su cui cade; `-1`: verso il maggiore; `trasposta`: i fori corrono lungo Y)")
    p(f"e usare `x0, y0 = ({org[0]:.0f}, {org[1]:.0f})`. Colonnine sui fori (21,1) e (21,16):")
    cols = [sched_xy(hx, hy, scelta, org) for hx, hy in C.SCHEDINA_FORI]
    p("`" + "`, `".join(f"({x:.2f}, {y:.2f})" for x, y in cols) + "` (x, y del case).")
    p("")
    p("| Opzione | Origine (x0, y0) | IN b | GAIN | OUT d | Punteggio | Catena IN (mm) | Distanza dai digitali (mm) | Piu vicino |")
    p("|---|---|---|---|---|---|---|---|---|")
    for k, v in tab.items():
        if not v["libero"]:
            p(f"| {k} | - | scartata: il volume urta componenti | | | |")
        else:
            p(f"| {k}{' **(scelta)**' if k == scelta else ''} | ({v['org'][0]:.0f}, {v['org'][1]:.0f}) | {v['l_in']:.0f} | {v['l_gain']:.0f} | {v['l_out']:.0f} | {v['hz']:.0f} | {v['tot']:.0f} | {v['dmin']:.1f} | {v['chi']} |")
    p("")
    p("Lunghezze di percorso, L+R. IN b = nodo INST/LINE -> ingresso schedina; GAIN = i 4 fili del pot; OUT d = uscita schedina -> PRE;")
    p(f"punteggio = IN b + GAIN + {PESO_OUT} x OUT d (ingresso e GAIN sono i nodi piu sensibili). Provvisoria: IN b {prima['l_in']:.0f} mm, GAIN {prima['l_gain']:.0f} mm;")
    p(f"scelta: IN b {dopo['l_in']:.0f} mm, GAIN {dopo['l_gain']:.0f} mm. Catena d'ingresso completa (IN a-e, L e R): {prima['tot']:.0f} -> {dopo['tot']:.0f} mm di percorso.\n")
    p("## Fili da tagliare\n")
    p("Lunghezza = percorso nominale; taglio = con margine, arrotondato. Colore: suggerimento (L bianco, R rosso, massa nera,")
    p("alimentazioni rosso/arancione). Schermato: cavetto con calza, calza a massa dal lato indicato.\n")
    p("| Filo | Da | A | Segnale | Tipo | Colore | Perc. (mm) | Taglio (mm) | Schermato | Calza a massa dal lato | Nota |")
    p("|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in R.items():
        sch = "si" if r["tipo"] == "schermato" else "no"
        if r.get("mancante"):
            p(f"| {i} | {r['da']} | {r['a']} | {r['sig']} | {r['tipo']} | {colore(r)} | - | - | {sch} | {r['calza'] or '-'} | **SENZA PIAZZOLA**: {r['mancante']} |")
        else:
            p(f"| {i} | {r['da']} | {r['a']} | {r['sig']} | {r['tipo']} | {colore(r)} | {r['nom']:.0f} | **{r['taglio']:.0f}** | {sch} | {r['calza'] or '-'} | {r['nota']}{' (via)' if r['via'] else ''} |")
    p("")
    p("### Totali per tipo\n")
    p("| Tipo | Fili | Lunghezza di taglio totale |")
    p("|---|---|---|")
    for t, (n, mm) in sorted(totali(R).items()):
        p(f"| {t} | {n} | {mm:.0f} mm ({mm / 1000:.2f} m) |")
    p("")
    p("Componenti fuori scheda da saldare (non sono fili): Rs 10 kOhm sulla punta di IN L e IN R; Rsh 3,3 kOhm fra LINE e il giunto")
    p("di massa del deviatore INST/LINE (due, uno per canale); 1K in serie al LED dei tasti (sulla scheda tasti); 4,7 kOhm sul lug comune del polo C del 3PDT, in serie al LED del bypass;")
    p("47 kOhm sui due terminali usati di ogni gang del pot GAIN.\n")
    p("## Problemi aperti\n")
    lunghi = [(i, r["taglio"]) for i, r in R.items() if not r.get("mancante") and r["taglio"] >= LUNGO]
    if lunghi:
        p("- Fili lunghi (taglio >= %d mm): " % LUNGO + ", ".join(f"{i} ({t:.0f})" for i, t in sorted(lunghi, key=lambda x: -x[1])) + ".")
    (QUI / "cablaggio.md").write_text("\n".join(L_) + "\n")




# ----------------------------------------------------------------------------- main
def analisi():
    mondo = Mondo()
    _MONDO_CACHE["mondo"] = mondo
    T0 = terminali(None)
    W0 = fili(terminali(PROVVISORIA))
    tab, scelta, fissi, dr = analizza_orientamento(mondo, W0, T0)
    oc = ori_case()
    if ORI_IN_USO is not None:
        ori_uso = ORI_IN_USO
    else:
        ori_uso = oc or scelta
    org_uso = tab[ori_uso]["org"] if ori_uso in tab and tab[ori_uso].get("libero") else SCH_ORG0
    Tf = terminali(ori_uso, org_uso)
    mondo.sch_box = sched_box(ori_uso, org_uso)
    W = fili(Tf)
    R = calcola(mondo, Tf, W)
    _MONDO_CACHE["T"] = Tf
    err = verifica(Tf, W, R, tab, scelta, ori_uso, org_uso)
    spost = scansione_spostamento(mondo, ori_uso, org_uso, W, Tf)
    return dict(spost=spost, T=Tf, W=W, R=R, tab=tab, scelta=scelta, ori_uso=ori_uso, org_uso=org_uso, err=err, mondo=mondo)


def main():
    a = analisi()
    stampa_tutto(a["T"], a["W"], a["R"], a["tab"], a["scelta"], a["ori_uso"], a["org_uso"], a["err"], a["mondo"])
    nom, mig, (dx, dy) = a["spost"]
    print(f"Spostamento del volume della schedina (dx, dy fino a 4 e 8 mm, solo dove non urta componenti): "
          f"distanza in pianta dei capi sensibili {nom:.0f} mm -> {mig:.0f} mm con ({dx:+d}, {dy:+d}) mm"
          f"{'' if mig < nom - 5 else ': guadagno trascurabile, non conviene spostare'}")
    if "--scrivi-md" in sys.argv:
        scrivi_md(a["T"], a["W"], a["R"], a["tab"], a["scelta"], a["ori_uso"])
        print(f"scritto {QUI / 'cablaggio.md'}")
    if a["err"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
