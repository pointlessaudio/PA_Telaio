# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0", "numpy"]
# ///
"""
Schema KiCad di PA-TELAIO generato dalle netlist del progetto, non disegnato a mano.

Fonti (sorgenti di verità, questo script non ne cambia nessuna):
  hardware/layout.py                 veroboard principale (Seed3, TLC2272, alimentazione, ingressi, uscite)
  hardware/preamp/layout_preamp.py   schedina del preamp JFET
  case/cablaggio.py                  terminali delle parti fuori scheda e fili che li uniscono
  tabella FUORI qui sotto            le parti fuori scheda (jack, deviatori, pot, scheda tasti, scheda MIDI,
                                     microSD), trascritte da hardware/prototipo-veroboard-seed3.html e cablaggio.py

Le reti si calcolano come in un montaggio vero: ogni scheda ha le sue reti, ogni terminale fuori scheda è un
nodo a sé, e solo i fili di cablaggio.py li uniscono. Una massa non cablata esce come rete separata (GND_2)
e lo script lo segnala. Lo schema usa etichette di rete sui piedini (nessun filo disegnato): corretto per
costruzione, si rigenera a ogni modifica delle fonti.

    uv run genera_schema.py            # scrive pa-telaio.kicad_sch, pa-telaio.kicad_pro, reti_attese.json
"""
import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
ROOT = QUI.parent.parent
sys.path.insert(0, str(ROOT / "case"))
_argv, sys.argv = sys.argv, [sys.argv[0]]
import cablaggio as K  # noqa: E402  (importa case.py, hardware/layout.py e preamp/layout_preamp.py)
sys.argv = _argv

L, LP = K.L, K.LP
NOME = "pa-telaio"
G = 2.54
from genera_uuid import uid  # noqa: E402


# ============================================================================ simboli
# ogni simbolo: lista di pin (numero, nome, x, y, angolo, lunghezza) + grafica + larghezza/altezza del corpo.
# Coordinate del simbolo: y verso l'alto (KiCad); il piedino si collega nel punto (x, y).
def pin(num, nome, x, y, ang, lun=G):
    return dict(num=str(num), nome=nome, x=x, y=y, ang=ang, lun=lun)


def due_pin(grafica, n1="~", n2="~"):
    """passivo orizzontale: pin 1 a sinistra, pin 2 a destra"""
    return dict(pins=[pin(1, n1, -3 * G / 2 - G / 2, 0, 0, G), pin(2, n2, 2 * G, 0, 180, G)],
                gr=grafica, w=3 * G, h=G, nomi=False)


SIMBOLI = {}
SIMBOLI["R"] = due_pin(["(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))"])
SIMBOLI["C"] = due_pin(["(polyline (pts (xy -0.762 1.524) (xy -0.762 -1.524)) (stroke (width 0.3048) (type default)) (fill (type none)))",
                        "(polyline (pts (xy 0.762 1.524) (xy 0.762 -1.524)) (stroke (width 0.3048) (type default)) (fill (type none)))",
                        "(polyline (pts (xy -2.54 0) (xy -0.762 0)) (stroke (width 0) (type default)) (fill (type none)))",
                        "(polyline (pts (xy 0.762 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))"])
SIMBOLI["CP"] = due_pin(SIMBOLI["C"]["gr"] + ["(text \"+\" (at -2.032 1.27 0) (effects (font (size 1.27 1.27))))"], "+", "-")
# diodo: anodo (pin 2) a sinistra, catodo (pin 1) a destra, come la convenzione KiCad 1 = K
_tri = ["(polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(polyline (pts (xy -2.54 0) (xy -1.27 0)) (stroke (width 0) (type default)) (fill (type none)))",
        "(polyline (pts (xy 1.27 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))"]
SIMBOLI["D"] = dict(pins=[pin(2, "A", -3 * G / 2 - G / 2, 0, 0), pin(1, "K", 2 * G, 0, 180)], gr=_tri, w=3 * G, h=G, nomi=False)
SIMBOLI["LED"] = dict(SIMBOLI["D"], gr=_tri + [
    "(polyline (pts (xy 0 1.524) (xy 1.016 2.54)) (stroke (width 0) (type default)) (fill (type none)))",
    "(polyline (pts (xy 0.762 1.524) (xy 1.778 2.54)) (stroke (width 0) (type default)) (fill (type none)))"])


def scatola(sx, dx, sopra=(), sotto=(), w=None):
    """simbolo a scatola: sx/dx = liste di (numero, nome) dall'alto in basso; sopra/sotto da sinistra"""
    n = max(len(sx), len(dx), 1)
    h = 2 * G * ((n + 2) // 2)              # pari in passi di griglia: i piedini cadono sulla griglia da 2,54
    if w is None:
        lmax = max([len(nm) for _, nm in list(sx) + list(dx)] + [2])
        w = max(4 * G, 2 * G * (1 + int((lmax * 1.27 * 2 + 4) / (2 * G))))
    pins = []
    top = h / 2
    for i, (num, nm) in enumerate(sx):
        pins.append(pin(num, nm, -w / 2 - G, top - G * (i + 1), 0))
    for i, (num, nm) in enumerate(dx):
        pins.append(pin(num, nm, w / 2 + G, top - G * (i + 1), 180))
    for i, (num, nm) in enumerate(sopra):
        pins.append(pin(num, nm, -w / 2 + G * (i + 1), h / 2 + G, 270))
    for i, (num, nm) in enumerate(sotto):
        pins.append(pin(num, nm, -w / 2 + G * (i + 1), -h / 2 - G, 90))
    gr = [f"(rectangle (start {-w / 2:.3f} {h / 2:.3f}) (end {w / 2:.3f} {-h / 2:.3f}) "
          "(stroke (width 0.254) (type default)) (fill (type background)))"]
    return dict(pins=pins, gr=gr, w=w, h=h, nomi=True)


SIMBOLI["POT"] = scatola([(1, "1"), (3, "3")], [(2, "cursore")])
SIMBOLI["TRIM"] = SIMBOLI["POT"]
SIMBOLI["NJFET"] = scatola([(3, "G")], [(1, "D"), (2, "S")])
SIMBOLI["TLC2272"] = scatola([(1, "OUTA"), (2, "-INA"), (3, "+INA"), (4, "V-")],
                             [(8, "V+"), (7, "OUTB"), (6, "-INB"), (5, "+INB")])
SIMBOLI["SEED3"] = scatola([(p, L.seed_name[p]) for p in range(1, 21)], [(p, L.seed_name[p]) for p in range(40, 20, -1)])
SIMBOLI["JACK_TS"] = scatola([], [("T", "punta"), ("TN", "contatto punta"), ("S", "manicotto")])
SIMBOLI["JACK_TRS"] = scatola([], [("T", "punta"), ("R", "anello"), ("S", "manicotto")])
SIMBOLI["DC"] = scatola([], [("1", "centrale"), ("2", "manicotto"), ("3", "contatto")])
SIMBOLI["DPDT"] = scatola([("1", "A1"), ("2", "A com"), ("3", "A2")], [("4", "B1"), ("5", "B com"), ("6", "B2")])
SIMBOLI["3PDT"] = scatola([("A1", "A bypass"), ("A2", "A com"), ("A3", "A effetto"), ("B1", "B bypass"), ("B2", "B com")],
                          [("B3", "B effetto"), ("C1", "C bypass"), ("C2", "C com"), ("C3", "C effetto")])
SIMBOLI["POT2"] = scatola([("1L", "L 1"), ("2L", "L cursore"), ("3L", "L 3")], [("1R", "R 1"), ("2R", "R cursore"), ("3R", "R 3")])
SIMBOLI["ENC"] = scatola([("A", "A"), ("C", "C"), ("B", "B")], [("S1", "S1"), ("S2", "S2")])
SIMBOLI["OLED"] = scatola([("1", "GND"), ("2", "VCC"), ("3", "SCL"), ("4", "SDA")], [])
SIMBOLI["TASTO"] = scatola([("1", "1")], [("2", "2")])
SIMBOLI["H11L1"] = scatola([("1", "anodo"), ("2", "catodo"), ("3", "NC")], [("6", "VCC"), ("4", "uscita"), ("5", "GND")])
SIMBOLI["MICROSD"] = scatola([("7", "DAT0"), ("8", "DAT1"), ("1", "DAT2"), ("2", "DAT3"), ("3", "CMD")],
                             [("4", "VDD"), ("5", "CLK"), ("6", "VSS")])
SIMBOLI["MASSA"] = scatola([("1", "massa")], [])

# ============================================================================ componenti
# (ref, simbolo, valore, footprint, rif. originale, {pin: nodo}, blocco)
COMP = []
FP = {
    "res": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "cap": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "mlcc": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm",
    "film": "Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
    "elco": "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm",
    "diode": "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
    "dip8": "Package_DIP:DIP-8_W7.62mm_Socket",
    "jfet": "Package_TO_SOT_THT:TO-92_Inline",
    "trimmer": "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical",
}
SIMB_DI = {"res": "R", "cap": "C", "mlcc": "C", "film": "C", "elco": "CP", "diode": "D", "jfet": "NJFET",
           "trimmer": "TRIM", "dip8": "TLC2272", "seed": "SEED3"}


def nodo_pin(kind, pins):
    """numeri dei pin per tipo, dall'ordine/nome dei pin nelle fonti"""
    out = {}
    if kind in ("res", "cap", "mlcc", "film"):
        for i, p in enumerate(pins):
            out[str(i + 1)] = p
    elif kind == "elco":
        for p, seg in pins:
            out["1" if seg == "+" else "2"] = p
    elif kind == "diode":
        for p, seg in pins:
            out["2" if seg == "A" else "1"] = p
    else:
        for p, seg in pins:
            out[seg.split()[-1].strip("()") if "(" in seg else seg.split()[0]] = p
    return out


# --- veroboard (layout.py): nodi "VB/<rete>"
for ref, kind, val, pins in L.P:
    if kind in ("res", "cap", "film"):
        m = {str(i + 1): f"VB/{net}" for i, (_, _, net, _) in enumerate(pins)}
    elif kind in ("elco", "diode"):
        m = nodo_pin(kind, [(f"VB/{net}", seg) for (_, _, net, seg) in pins])
    else:                                   # dip8, seed: numero del pin nelle fonti
        m = {n: f"VB/{net}" for (_, _, net, n) in pins}
    blocco = "Seed3 e operazionali" if kind in ("dip8", "seed") else "Veroboard: alimentazione, ingressi, uscite"
    r = "A1" if kind == "seed" else ref
    COMP.append((r, SIMB_DI[kind], val, FP.get(kind, ""), ref, m, blocco))

# --- schedina preamp (layout_preamp.py): nodi "SC/<rete>", riferimenti rinumerati da 101
_conta = {}


def nuovo_ref(prefisso, base):
    _conta[prefisso] = _conta.get(prefisso, base) + 1
    return f"{prefisso}{_conta[prefisso]}"


PREF = {"res": "R", "film": "C", "elco": "C", "mlcc": "C", "jfet": "Q", "trimmer": "RV"}
for p in LP.P:
    kind = p["kind"]
    nodi = [(f"SC/{LP.norm(net)}", seg) for (_, _, net, seg) in p["pins"]]
    if kind in ("res", "film", "mlcc"):
        m = {str(i + 1): n for i, (n, _) in enumerate(nodi)}
    elif kind == "elco":
        m = nodo_pin("elco", nodi)
    elif kind == "jfet":
        m = {seg.split("(")[1].strip(")"): n for n, seg in nodi}
    else:                                   # trimmer: "1 alto", "2 cursore", "3 basso"
        m = {seg.split()[0]: n for n, seg in nodi}
    val = p["label"].split()[0] if kind != "jfet" else "J201"
    COMP.append((nuovo_ref(PREF[kind], 100), SIMB_DI[kind], val, FP[kind], p["ref"], m, "Schedina preamp JFET"))

# --- fuori scheda: nodi = terminali di cablaggio.py ("JIL:tip"), o interni ("int:...") per i collegamenti
# fatti sul pezzo stesso (resistenze saldate sui terminali, piste delle schedine)
NC = "NC"
FUORI = [
    # ingresso: jack, Rs 10k sulla punta, deviatore INST/LINE con Rsh, deviatore PRE, GAIN con 47k
    ("J201", "JACK_TS", "IN L (112AX)", {"T": "JIL:tip", "TN": "JIL:sleeve", "S": "JIL:sleeve"}, "Ingressi e preamp"),
    ("J202", "JACK_TS", "IN R (112AX)", {"T": "JIR:tip", "TN": "JIR:sleeve", "S": "JIR:sleeve"}, "Ingressi e preamp"),
    ("R201", "R", "10k (Rs L)", {"1": "JIL:tip", "2": "JIL:rs"}, "Ingressi e preamp"),
    ("R202", "R", "10k (Rs R)", {"1": "JIR:tip", "2": "JIR:rs"}, "Ingressi e preamp"),
    ("SW201", "DPDT", "INST/LINE", {"1": NC, "2": "ILS:COM L", "3": "int:rsh L", "4": NC, "5": "ILS:COM R", "6": "int:rsh R"},
     "Ingressi e preamp"),
    ("R203", "R", "3k3 (Rsh L)", {"1": "int:rsh L", "2": "ILS:GND L"}, "Ingressi e preamp"),
    ("R204", "R", "3k3 (Rsh R)", {"1": "int:rsh R", "2": "ILS:GND R"}, "Ingressi e preamp"),
    ("SW202", "DPDT", "PRE", {"1": "PRE:OFF L", "2": "PRE:COM L", "3": "PRE:ON L", "4": "PRE:OFF R", "5": "PRE:COM R",
                             "6": "PRE:ON R"}, "Ingressi e preamp"),
    ("RV201", "POT2", "GAIN C50K doppio", {"1L": NC, "2L": "GAIN:B L", "3L": "GAIN:A L", "1R": NC, "2R": "GAIN:B R",
                                           "3R": "GAIN:A R"}, "Ingressi e preamp"),
    ("R205", "R", "47k (GAIN L)", {"1": "GAIN:A L", "2": "GAIN:B L"}, "Ingressi e preamp"),
    ("R206", "R", "47k (GAIN R)", {"1": "GAIN:A R", "2": "GAIN:B R"}, "Ingressi e preamp"),
    # uscite e true bypass; R 4,7k saldata sul comune del polo C, LED del bypass
    ("J203", "JACK_TS", "OUT L (112AX)", {"T": "JOL:tip", "TN": NC, "S": "JOL:sleeve"}, "Uscite e true bypass"),
    ("J204", "JACK_TS", "OUT R (112AX)", {"T": "JOR:tip", "TN": NC, "S": "JOR:sleeve"}, "Uscite e true bypass"),
    ("SW203", "3PDT", "true bypass", {"A1": "FS:A byp", "A2": "FS:A com", "A3": "FS:A eff", "B1": "FS:B byp",
                                      "B2": "FS:B com", "B3": "FS:B eff", "C1": NC, "C2": "int:fs C com",
                                      "C3": "FS:C eff"}, "Uscite e true bypass"),
    ("R207", "R", "4k7", {"1": "FS:C com", "2": "int:fs C com"}, "Uscite e true bypass"),
    ("D201", "LED", "LED bypass", {"2": "LEDFS:A", "1": "LEDFS:K"}, "Uscite e true bypass"),
    # alimentazione, pedale, schermatura
    ("J205", "DC", "DC 9V (NEB/J 21C)", {"1": "DC:center", "2": "DC:sleeve", "3": NC}, "Alimentazione, pedale, massa"),
    ("J206", "JACK_TRS", "PEDALE (112BX)", {"T": "JP:tip", "R": "JP:ring", "S": "JP:sleeve"}, "Alimentazione, pedale, massa"),
    ("H201", "MASSA", "massa L0 (vite)", {"1": "MASSA:L0"}, "Alimentazione, pedale, massa"),
    ("H202", "MASSA", "massa L1 (torretta)", {"1": "MASSA:L1"}, "Alimentazione, pedale, massa"),
    # controlli sul pannello
    ("ENC201", "ENC", "PEC11R", {"A": "ENC:A", "B": "ENC:B", "C": "ENC:C", "S1": "ENC:SW", "S2": "ENC:SW2"}, "Controlli"),
    ("A201", "OLED", "OLED 2,42 pollici I2C", {"1": "OLED:GND", "2": "OLED:VCC", "3": "OLED:SCL", "4": "OLED:SDA"}, "Controlli"),
    ("SW204", "TASTO", "K1", {"1": "TASTI:D0", "2": "TASTI:GND"}, "Controlli"),
    ("SW205", "TASTO", "K2", {"1": "TASTI:D10", "2": "TASTI:GND"}, "Controlli"),
    ("R208", "R", "1k", {"1": "TASTI:LED+", "2": "int:led a"}, "Controlli"),
    ("D202", "LED", "LED", {"2": "int:led a", "1": "TASTI:GND"}, "Controlli"),
] + [(f"RV{202 + i}", "POT", "B10K", {"1": f"POT{i + 1}:LO", "2": f"POT{i + 1}:W", "3": f"POT{i + 1}:HI"}, "Controlli")
     for i in range(6)] + [
    # scheda MIDI (datasheet Seed3 fig. 7.1, 7.3, 7.5)
    ("J207", "JACK_TRS", "MIDI IN (TRS tipo A)", {"T": "int:midi in T", "R": "int:midi in R", "S": "int:midi in S"}, "Scheda MIDI"),
    ("R301", "R", "220", {"1": "int:midi in R", "2": "int:opto A"}, "Scheda MIDI"),
    ("D301", "D", "1N4148", {"1": "int:opto A", "2": "int:midi in T"}, "Scheda MIDI"),
    ("U301", "H11L1", "H11L1M", {"1": "int:opto A", "2": "int:midi in T", "3": NC, "4": "MIDI:RX", "5": "MIDI:GND",
                                 "6": "MIDI:3V3"}, "Scheda MIDI"),
    ("R302", "R", "270", {"1": "MIDI:RX", "2": "MIDI:3V3"}, "Scheda MIDI"),
    ("C301", "C", "100n", {"1": "MIDI:3V3", "2": "MIDI:GND"}, "Scheda MIDI"),
    ("C302", "C", "100n", {"1": "int:midi in S", "2": "MIDI:GND"}, "Scheda MIDI"),
    ("J208", "JACK_TRS", "MIDI OUT (TRS tipo A)", {"T": "int:midi out T", "R": "int:midi out R", "S": "MIDI:GND"}, "Scheda MIDI"),
    ("R303", "R", "10", {"1": "MIDI:TX", "2": "int:midi out T"}, "Scheda MIDI"),
    ("R304", "R", "10", {"1": "MIDI:3V3", "2": "int:midi out R"}, "Scheda MIDI"),
    # microSD 1-bit (datasheet Seed3 fig. 5.1)
    ("J209", "MICROSD", "microSD", {"7": "SD:D0", "8": "int:sd DAT1", "1": "int:sd DAT2", "2": "int:sd DAT3", "3": "SD:CMD",
                                    "4": "SD:3V3", "5": "SD:CLK", "6": "SD:GND"}, "microSD"),
] + [(f"R{305 + i}", "R", "47k", {"1": n, "2": "SD:3V3"}, "microSD")
     for i, n in enumerate(["SD:D0", "SD:CMD", "int:sd DAT1", "int:sd DAT2", "int:sd DAT3"])]
for ref, sim, val, m, blocco in FUORI:
    COMP.append((ref, sim, val, "", ref, m, blocco))


# ============================================================================ reti
def reti():
    """union-find: nodi di scheda e terminali, uniti dai fili di cablaggio.py e dalle piazzole"""
    T = K.terminali(K.PROVVISORIA)
    W = K.fili(T)
    par = {}

    def f(a):
        par.setdefault(a, a)
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    def u(a, b):
        par[f(a)] = f(b)

    def nodo_term(k):
        if k.startswith("VB:"):
            return f"VB/{T[k]['net']}"
        if k.startswith("SC:"):
            return f"SC/{LP.norm(T[k]['net'])}"
        return k

    for w in W:
        u(nodo_term(w["da"]), nodo_term(w["a"]))
    usati = set()
    for ref, sim, val, fp, orig, m, blocco in COMP:
        for n in m.values():
            if n != NC:
                f(n)
                usati.add(n)
    # ogni terminale fuori scheda deve essere un piedino di qualche parte
    orfani = [k for k in T if not k.startswith(("VB:", "SC:")) and k not in usati and T[k]["net"] != "nc"]
    # nome della rete: rete della veroboard, poi della schedina, poi del terminale, poi del nodo interno
    gruppi = {}
    for n in list(par):
        gruppi.setdefault(f(n), []).append(n)

    def priorita(n):
        if n.startswith("VB/"):
            return (0, n[3:])
        if n.startswith("SC/"):
            return (1, n[3:])
        if n in T:
            return (2, T[n]["net"])
        return (3, n.split(":", 1)[1].replace(" ", "_"))

    nome = {}
    presi = {}
    for r, nodi in sorted(gruppi.items(), key=lambda kv: min(priorita(n) for n in kv[1])):
        base = min(priorita(n) for n in nodi)[1]
        presi[base] = presi.get(base, 0) + 1
        nome[r] = base if presi[base] == 1 else f"{base}_{presi[base]}"
    return {n: nome[f(n)] for n in par}, orfani


def main():
    rete_di, orfani = reti()
    attese = {}
    nc_pin = []
    for ref, sim, val, fp, orig, m, blocco in COMP:
        for p, n in m.items():
            if n == NC or (n.startswith("VB/NC") and sim == "SEED3"):
                nc_pin.append((ref, p))
                continue
            attese.setdefault(rete_di[n], []).append([ref, p])
    singole = sorted(k for k, v in attese.items() if len(v) < 2)
    doppie = sorted(k for k in attese if "_" in k and k.rsplit("_", 1)[1].isdigit() and k.rsplit("_", 1)[0] in attese)
    (QUI / "reti_attese.json").write_text(json.dumps(
        {"reti": {k: sorted(v) for k, v in sorted(attese.items())}, "nc": sorted(map(list, nc_pin))}, indent=1,
        ensure_ascii=False))
    scrivi_schema(rete_di)
    print(f"{len(COMP)} componenti, {len(attese)} reti, {len(nc_pin)} piedini non collegati (NC)")
    err = []
    if orfani:
        err.append(f"terminali di cablaggio.py senza parte: {orfani}")
    if singole:
        err.append(f"reti con un solo piedino: {singole}")
    if doppie:
        err.append(f"reti divise (stesso nome su due isole, manca un filo?): {doppie}")
    refs = [c[0] for c in COMP]
    if len(refs) != len(set(refs)):
        err.append("riferimenti doppi: " + str(sorted({r for r in refs if refs.count(r) > 1})))
    for e in err:
        print("ERRORE:", e)
    print("OK: schema scritto" if not err else "schema scritto CON ERRORI")
    return 1 if err else 0


# ============================================================================ scrittura del .kicad_sch
def fx(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def lib_symbol(nome, s, prefisso="PA:"):
    pins = []
    for p in s["pins"]:
        pins.append(f'(pin passive line (at {fx(p["x"])} {fx(p["y"])} {p["ang"]}) (length {fx(p["lun"])}) '
                    f'(name "{p["nome"]}" (effects (font (size 1.27 1.27)))) '
                    f'(number "{p["num"]}" (effects (font (size 1.27 1.27)))))')
    nomi = "(pin_names (offset 0.508))" if s["nomi"] else "(pin_names (offset 0) hide)"
    return (f'(symbol "{prefisso}{nome}" (pin_numbers hide) {nomi} (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
            f'  (property "Reference" "X" (at 0 0 0) (effects (font (size 1.27 1.27))))\n'
            f'  (property "Value" "{nome}" (at 0 0 0) (effects (font (size 1.27 1.27))))\n'
            f'  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (symbol "{nome}_0_1" {" ".join(s["gr"])})\n'
            f'  (symbol "{nome}_1_1" {" ".join(pins)}))')


def lungo_etichetta(t):
    return 1.27 * 0.75 * len(t) + 2.0


def griglia(v):
    return round(v / G) * G


def scrivi_schema(rete_di):
    radice = uid("radice")
    usati = sorted({c[1] for c in COMP})
    out = [f'(kicad_sch (version 20231120) (generator "pa_telaio_genera_schema") (generator_version "8.0") '
           f'(uuid "{radice}") (paper "A0")',
           '(title_block (title "PA-TELAIO") (comment 1 "generato da hardware/kicad/genera_schema.py: non modificare a mano") '
           '(comment 2 "fonti: hardware/layout.py, hardware/preamp/layout_preamp.py, case/cablaggio.py"))',
           "(lib_symbols"]
    out += [lib_symbol(n, SIMBOLI[n]) for n in usati]
    out.append(")")
    # impaginazione: un blocco dopo l'altro, a scaffali
    blocchi = []
    for c in COMP:
        if c[6] not in blocchi:
            blocchi.append(c[6])
    LARG = 1150.0
    x0, y = 25.4, 30.48
    for b in blocchi:
        out.append(f'(text "{b}" (exclude_from_sim no) (at {fx(x0)} {fx(y)} 0) (effects (font (size 3.5 3.5) bold) (justify left bottom)) (uuid "{uid("t", b)}"))')
        y += 7.62
        x, h_riga = x0, 0.0
        for ref, sim, val, fp, orig, m, blocco in COMP:
            if blocco != b:
                continue
            s = SIMBOLI[sim]
            et_sx = max([lungo_etichetta(rete_di.get(m.get(p["num"], NC), "")) for p in s["pins"] if p["ang"] == 0] + [0])
            et_dx = max([lungo_etichetta(rete_di.get(m.get(p["num"], NC), "")) for p in s["pins"] if p["ang"] == 180] + [0])
            larg = s["w"] + 2 * G + et_sx + et_dx + 10.0
            alt = s["h"] + 2 * G + 8.0
            if x + larg > LARG:
                x, y, h_riga = x0, y + h_riga, 0.0
            cx = griglia(x + et_sx + G + s["w"] / 2)
            cy = griglia(y + 5.08 + s["h"] / 2)
            out.append(istanza(radice, ref, sim, val, fp, orig, cx, cy, s))
            for p in s["pins"]:
                n = m.get(p["num"], NC)
                px, py = cx + p["x"], cy - p["y"]
                if n == NC or (sim == "SEED3" and n.startswith("VB/NC")):
                    out.append(f'(no_connect (at {fx(px)} {fx(py)}) (uuid "{uid("nc", ref, p["num"])}"))')
                    continue
                ang, gius = {0: (180, "right"), 180: (0, "left"), 270: (90, "left"), 90: (270, "right")}[p["ang"]]
                out.append(f'(label "{rete_di[n]}" (at {fx(px)} {fx(py)} {ang}) (fields_autoplaced yes) '
                           f'(effects (font (size 1.27 1.27)) (justify {gius} bottom)) (uuid "{uid("l", ref, p["num"])}"))')
            x += larg
            h_riga = max(h_riga, alt)
        y += h_riga + 7.62
    out.append(f'(sheet_instances (path "/" (page "1")))')
    out.append(")")
    (QUI / f"{NOME}.kicad_sch").write_text("\n".join(out) + "\n")
    # libreria di progetto con gli stessi simboli, registrata nella tabella del progetto
    (QUI / "PA.kicad_sym").write_text(
        '(kicad_symbol_lib (version 20231120) (generator "pa_telaio_genera_schema") (generator_version "8.0")\n'
        + "\n".join(lib_symbol(n, SIMBOLI[n], "") for n in sorted(SIMBOLI)) + "\n)\n")
    (QUI / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n  (lib (name "PA")(type "KiCad")(uri "${KIPRJMOD}/PA.kicad_sym")(options "")'
        '(descr "simboli di PA-TELAIO, generati da genera_schema.py"))\n)\n')
    pro = QUI / f"{NOME}.kicad_pro"
    if not pro.exists():
        pro.write_text(json.dumps({"meta": {"filename": f"{NOME}.kicad_pro", "version": 1}}, indent=2) + "\n")


def istanza(radice, ref, sim, val, fp, orig, cx, cy, s):
    pins = " ".join(f'(pin "{p["num"]}" (uuid "{uid("p", ref, p["num"])}"))' for p in s["pins"])
    yr = cy - s["h"] / 2 - 2.0
    yv = cy + s["h"] / 2 + 3.2
    return (f'(symbol (lib_id "PA:{sim}") (at {fx(cx)} {fx(cy)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) '
            f'(on_board yes) (dnp no) (uuid "{uid("s", ref)}")\n'
            f'  (property "Reference" "{ref}" (at {fx(cx)} {fx(yr)} 0) (effects (font (size 1.27 1.27))))\n'
            f'  (property "Value" "{val}" (at {fx(cx)} {fx(yv)} 0) (effects (font (size 1.27 1.27))))\n'
            f'  (property "Footprint" "{fp}" (at {fx(cx)} {fx(cy)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Datasheet" "" (at {fx(cx)} {fx(cy)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Description" "" (at {fx(cx)} {fx(cy)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Layout" "{orig}" (at {fx(cx)} {fx(cy)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  {pins}\n'
            f'  (instances (project "{NOME}" (path "/{radice}" (reference "{ref}") (unit 1)))))')


if __name__ == "__main__":
    sys.exit(main())
