# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0", "numpy"]
# ///
"""
Reti attese dello schema KiCad di PA-TELAIO, calcolate dalle netlist del progetto. Lo schema lo disegna
disegna_schema.py; verifica_schema.py controlla che il disegno dia esattamente queste reti.

Fonti (sorgenti di verità, questo script non ne cambia nessuna):
  hardware/layout.py                 veroboard principale (Seed3, TLC2272, alimentazione, ingressi, uscite)
  hardware/preamp/layout_preamp.py   schedina del preamp JFET
  case/cablaggio.py                  terminali delle parti fuori scheda e fili che li uniscono
  tabella FUORI qui sotto            le parti fuori scheda (jack, deviatori, pot, scheda tasti, scheda MIDI,
                                     microSD), trascritte da hardware/prototipo-veroboard-seed3.html e cablaggio.py

Le reti si calcolano come in un montaggio vero: ogni scheda ha le sue reti, ogni terminale fuori scheda è un
nodo a sé, e solo i fili di cablaggio.py li uniscono. Una massa non cablata esce come rete separata (GND_2)
e lo script lo segnala.

    uv run genera_schema.py            # scrive reti_attese.json e componenti.json (lo schema lo disegna disegna_schema.py)
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
    ("J201", "JACK_TS", "IN L (112AX)", {"T": "JIL:tip", "TN": "JIL:tn", "S": "JIL:sleeve"}, "Ingressi e preamp"),
    ("J202", "JACK_TS", "IN R (112AX)", {"T": "JIR:tip", "TN": "JIR:tn", "S": "JIR:sleeve"}, "Ingressi e preamp"),
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
    comp = {}
    for ref, sim, val, fp, orig, m, blocco in COMP:
        comp[ref] = dict(sim=sim, val=val, fp=fp, layout=orig, blocco=blocco,
                         pins={p: ("NC" if n == NC or (n.startswith("VB/NC") and sim == "SEED3") else rete_di[n])
                               for p, n in m.items()})
    (QUI / "componenti.json").write_text(json.dumps(
        {"seed_nomi": {str(k): v for k, v in L.seed_name.items()}, "componenti": comp}, indent=1, ensure_ascii=False))
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
    print("OK: reti_attese.json e componenti.json scritti" if not err else "scritti CON ERRORI")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
