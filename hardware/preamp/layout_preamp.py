"""
PA-TELAIO: schedina preamp JFET d'ingresso (circuito V4a, hardware/preamp/risultati.md) su stripboard.
Stesso metodo di hardware/layout.py: x = foro lungo la striscia, y = striscia; le strisce corrono lungo x.
Valori e topologia NON si decidono qui: i valori vengono da sim/sim_preamp.py (dizionario C) e la
topologia attesa viene LETTA dal netlist() della simulazione, poi confrontata col layout.
Verifiche: fori doppi/tagliati, corti e aperti (isole di rame), netlist vs simulazione, corpi dei
componenti che non si sovrappongono, canali su strisce distinte, ritorni di massa separati, fori di
fissaggio M3.

Canale L: righe y = r (r = 0..8). Canale R: specchiato, y = 17 - r. I due canali non condividono rame:
VA, VG e le masse si uniscono solo con ponticelli. I componenti comuni (partitore VG, 100 uF, 100 nF)
stanno sul lato L.

Righe del canale (r):
  0  IN | GNDc      ingresso (C1) | ritorno del solo Cs1 (47 uF)
  1  GB | SP        piazzola GAIN_B + 220R | nodo SP (+Cs1)
  2  G1A|G1|G2A|G2  nodi di gate, Rstop in orizzontale
  3  S1 | S2        source (piazzola GAIN_A su S1)
  4  D1 | D2        drain
  5  GND_a          massa di segnale: Rs1, Rs2, Rvg_bot, Cvg
  6  VG | TOP       polarizzazione di gate | capo alto del LEVEL
  7  VA | OUT       alimentazione | cursore LEVEL
  8  GND_b          massa di alimentazione: pad, 100 uF, 100 nF, capo basso del LEVEL
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "sim"))
import sim_preamp as S  # noqa: E402  (solo lettura: C e netlist)

W, H = 24, 18
PASSO = 2.54
ALTEZZA_MAX_MM = 13.0


def Y(side, r):
    return r if side == "L" else 17 - r


# ---------------------------------------------------------------- tagli
CUTS = set()
_CUT_R = [(3, 0), (6, 1), (4, 2), (9, 2), (14, 2), (10, 3), (11, 4), (18, 6), (21, 7)]
for _s in "LR":
    for _x, _r in _CUT_R:
        CUTS.add((_x, Y(_s, _r)))

# ---------------------------------------------------------------- componenti
P = []


def part(ref, kind, val, label, pins, rect, mount="", h=0.0, ch="C"):
    P.append(dict(ref=ref, kind=kind, val=val, label=label, pins=list(pins), rect=rect,
                  mount=mount, h=h, ch=ch))


def vrect(x, ya, yb, dx0=0, dx1=0):
    return (x - dx0, min(ya, yb), x + dx1, max(ya, yb))


c = S.C
for s in "LR":
    y = lambda r, s=s: Y(s, r)
    n = lambda name, s=s: f"{name}_{s}"

    def R(ref, val, label, a, b, rect, mount, h, s=s):
        part(f"{ref}{s}", "res", val, label, [a, b], rect, mount, h, s)

    part(f"C1{s}", "film", c["C1"], "47n film", [(1, y(0), n("in"), ""), (1, y(2), n("g1a"), "")],
         vrect(1, y(0), y(2)), "5 mm", 7.0, s)
    R("Rg1", c["Rg"], "1M", (2, y(2), n("g1a"), ""), (2, y(6), "VG", ""),
      vrect(2, y(2), y(6)), "giacente", 2.5)
    R("Rstop1", c["Rstop"], "1k", (3, y(2), n("g1a"), ""), (6, y(2), n("g1"), ""),
      (3, y(2), 6, y(2)), "orizzontale", 2.5)
    part(f"J1{s}", "jfet", None, "J201",
         [(7, y(4), n("d1"), "D (1)"), (7, y(3), n("s1"), "S (2)"), (7, y(2), n("g1"), "G (3)")],
         vrect(7, y(2), y(4)), "TO-92", 5.0, s)
    R("Rd1", c["Rd1"], "27k", (9, y(4), n("d1"), ""), (9, y(7), "VA", ""),
      vrect(9, y(4), y(7)), "giacente", 2.5)
    R("Rs1", c["Rs1"], "22k", (5, y(3), n("s1"), ""), (5, y(5), "GND", ""),
      vrect(5, y(3), y(5)), "in piedi", 8.5)
    R("R220_", c["Rgmin"], "220R", (5, y(1), n("gb"), ""), (8, y(1), n("sp"), ""),
      (5, y(1), 8, y(1)), "orizzontale", 2.5)
    part(f"Cs1{s}", "elco", c["Cs1"], "47u/16V 5x11 elco",
         [(9, y(1), n("sp"), "+"), (9, y(0), n("gnc"), "-")], vrect(9, y(0), y(1)), "2,5 mm", 11.0, s)
    part(f"C2{s}", "film", c["C2"], "220n film", [(10, y(4), n("d1"), ""), (10, y(2), n("g2a"), "")],
         vrect(10, y(2), y(4)), "5 mm", 8.0, s)
    R("Rg2", c["Rg"], "1M", (11, y(2), n("g2a"), ""), (11, y(6), "VG", ""),
      vrect(11, y(2), y(6)), "giacente", 2.5)
    R("Rstop2", c["Rstop"], "1k", (12, y(2), n("g2a"), ""), (15, y(2), n("g2"), ""),
      (12, y(2), 15, y(2)), "orizzontale", 2.5)
    part(f"J2{s}", "jfet", None, "J201",
         [(16, y(4), n("d2"), "D (1)"), (16, y(3), n("s2"), "S (2)"), (16, y(2), n("g2"), "G (3)")],
         vrect(16, y(2), y(4)), "TO-92", 5.0, s)
    R("Rd2", c["Rd2"], "20k", (14, y(4), n("d2"), ""), (14, y(7), "VA", ""),
      vrect(14, y(4), y(7)), "giacente", 2.5)
    R("Rs2", c["Rs2a"], "15k", (18, y(3), n("s2"), ""), (18, y(5), "GND", ""),
      vrect(18, y(3), y(5)), "in piedi", 8.5)
    part(f"C3{s}", "film", c["C3"], "1u film", [(20, y(4), n("d2"), ""), (20, y(6), n("top"), "")],
         vrect(20, y(4), y(6)), "5 mm (verificare passo)", 10.0, s)
    part(f"TR{s}", "trimmer", c["Plevel"], "100k LEVEL (3296W)",
         [(22, y(6), n("top"), "1 alto"), (22, y(7), n("out"), "2 cursore"), (22, y(8), "GND", "3 basso")],
         vrect(22, y(6), y(8)), "in linea, passo 2,54", 10.0, s)

# comuni, lato L (non hanno canale)
part("Rvt", "res", c["Rvg_top"], "39k", [(10, 7, "VA", ""), (10, 6, "VG", "")], vrect(10, 6, 7),
     "in piedi", 8.5)
part("Rvb", "res", c["Rvg_bot"], "10k", [(6, 6, "VG", ""), (6, 5, "GND", "")], vrect(6, 5, 6),
     "in piedi", 8.5)
part("Cvg", "elco", c["Cvg"], "22u/16V 5x11 elco", [(8, 6, "VG", "+"), (8, 5, "GND", "-")],
     vrect(8, 5, 6), "2,5 mm", 11.0)
part("CB", "elco", None, "100u/16V 6,3x11 elco (non simulato)", [(4, 7, "VA", "+"), (4, 8, "GND", "-")],
     vrect(4, 7, 8, 1, 1), "2,5 mm", 11.5)
part("CD", "mlcc", None, "100n MLCC (non simulato)", [(8, 7, "VA", ""), (8, 8, "GND", "")],
     vrect(8, 7, 8), "2,54 mm", 5.0)

# ---------------------------------------------------------------- ponticelli e cavi (tutti isolati)
LINKS = [
    ("J1", (7, Y("L", 5)), (7, Y("L", 8)), "GND", "GND_a L -> GND_b L"),
    ("J2", (7, Y("R", 5)), (7, Y("R", 8)), "GND", "GND_a R -> GND_b R"),
    ("J3", (6, Y("L", 8)), (6, Y("R", 8)), "GND", "GND_b L -> GND_b R"),
    ("J4", (12, Y("L", 6)), (12, Y("R", 6)), "VG", "VG L -> VG R"),
    ("J5", (13, Y("L", 7)), (13, Y("R", 7)), "VA", "VA L -> VA R"),
]
WIRES = [
    ("W1", (4, 0), (1, 8), "GND", "ritorno Cs1 L -> primo foro dopo il pad GND"),
    ("W2", (4, 17), (2, 8), "GND", "ritorno Cs1 R -> secondo foro dopo il pad GND"),
]
CNET = {"gnc_L": "GND", "gnc_R": "GND"}   # rame del ritorno Cs1: unito alla massa solo dal cavo

PADS = [
    ("VA", (0, 7), "VA", "alimentazione analogica"),
    ("GND", (0, 8), "GND", "massa: stella della scheda"),
    ("IN L", (0, 0), "in_L", "dal jack IN L"),
    ("IN R", (0, 17), "in_R", "dal jack IN R"),
    ("OUT L", (23, 7), "out_L", "verso il deviatore PRE, canale L"),
    ("OUT R", (23, 10), "out_R", "verso il deviatore PRE, canale R"),
    ("GAIN A L", (3, 3), "s1_L", "pot GAIN L (doppio C50K), capo verso S1; 47k fra i due capi, sul pot"),
    ("GAIN B L", (3, 1), "gb_L", "pot GAIN L, ritorno verso 220R"),
    ("GAIN A R", (3, 14), "s1_R", "pot GAIN R (doppio C50K), capo verso S1; 47k fra i due capi, sul pot"),
    ("GAIN B R", (3, 16), "gb_R", "pot GAIN R, ritorno verso 220R"),
]

FORI_FISSAGGIO = [(21, 1), (21, 16)]


def norm(net):
    return CNET.get(net, net)


# ================================================================= VERIFICA
def seg_of(x, y):
    assert (x, y) not in CUTS
    return (y, sum(1 for cx in range(0, x) if (cx, y) in CUTS))


errors = []
used = {}


def use(hole, who):
    x, y = hole
    if not (0 <= x < W and 0 <= y < H):
        errors.append(f"{who}: foro {hole} fuori scheda")
        return False
    if hole in CUTS:
        errors.append(f"{who}: foro {hole} e un taglio")
        return False
    if hole in used:
        errors.append(f"{who}: foro {hole} gia usato da {used[hole]}")
    used[hole] = who
    return True


conn = []  # (segmento, net, chi)
for p in P:
    for (x, y, net, pn) in p["pins"]:
        who = f"{p['ref']}.{pn}" if pn else p["ref"]
        if use((x, y), who):
            conn.append((seg_of(x, y), norm(net), who))
for name, a, b, net, _ in LINKS + WIRES:
    for h in (a, b):
        if use(h, name):
            conn.append((seg_of(*h), norm(net), name))
for name, h, net, _ in PADS:
    if use(h, name):
        conn.append((seg_of(*h), norm(net), name))


def fori_fissaggio_errori(fori):
    err = []
    for (x, y) in fori:
        h = (x, y)
        if not (1 <= x <= W - 2 and 1 <= y <= H - 2):
            err.append(f"foro di fissaggio {h}: a meno di un foro dal bordo")
        if h in used:
            err.append(f"foro di fissaggio {h}: occupato da {used[h]}")
            continue
        if h in CUTS:
            continue
        seg = seg_of(x, y)
        stessa = [u for u in used if u[1] == y and seg_of(*u) == seg]
        sx = [u for u in stessa if u[0] < x]
        dx = [u for u in stessa if u[0] > x]
        if sx and dx:
            err.append(f"foro di fissaggio {h}: spezza la striscia {y} fra {used[max(sx)]} e {used[min(dx)]}")
    return err


errors += fori_fissaggio_errori(FORI_FISSAGGIO)


def cells(r):
    x0, y0, x1, y1 = r
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def corpi_errori(parti, fori):
    err = []
    rc = {p["ref"]: cells(p["rect"]) for p in parti}
    refs = list(rc)
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            if rc[a] & rc[b]:
                err.append(f"corpi sovrapposti: {a} e {b} in {sorted(rc[a] & rc[b])[:2]}")
    altri = {}
    for p in parti:
        for (x, y, _, _) in p["pins"]:
            altri[(x, y)] = p["ref"]
    for name, a, b, _, _ in LINKS + WIRES:
        altri[a] = name
        altri[b] = name
    for name, h, _, _ in PADS:
        altri[h] = name
    for ref, cs in rc.items():
        for h in cs:
            if h in altri and altri[h] != ref:
                err.append(f"{altri[h]} in {h} sta sotto il corpo di {ref}")
    for (x, y) in fori:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for ref, cs in rc.items():
                    if (x + dx, y + dy) in cs:
                        err.append(f"foro di fissaggio {(x, y)}: testa/dado contro il corpo di {ref}")
    for p in parti:
        if p["h"] > ALTEZZA_MAX_MM:
            err.append(f"{p['ref']}: altezza {p['h']} mm oltre {ALTEZZA_MAX_MM}")
    return err


errors += corpi_errori(P, FORI_FISSAGGIO)

# --- isole di rame
parent = {}


def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


def union(a, b):
    parent[find(a)] = find(b)


for s_, _, _ in conn:
    find(s_)
for _, a, b, _, _ in LINKS + WIRES:
    union(seg_of(*a), seg_of(*b))

island_nets, net_islands = {}, {}
for s_, net, who in conn:
    r = find(s_)
    island_nets.setdefault(r, set()).add(net)
    net_islands.setdefault(net, set()).add(r)
for r, nets in island_nets.items():
    if len(nets) > 1:
        errors.append(f"CORTO: le net {sorted(nets)} sono sulla stessa isola di rame")
for net, rs in net_islands.items():
    if len(rs) > 1:
        errors.append(f"APERTO: la net {net} e divisa in {len(rs)} isole")
_count = {}
for _, net, _ in conn:
    _count[net] = _count.get(net, 0) + 1
for net, k in _count.items():
    if k < 2:
        errors.append(f"net {net} con un solo punto di connessione")


# --- netlist attesa, LETTA dal netlist() della simulazione
def sim_elementi():
    txt = S.netlist(1e-3, -0.9, 0.5, 0.8, "")
    out = []
    for riga in txt.splitlines():
        t = riga.split()
        if len(t) >= 4 and t[0][0] in "RCJ" and not riga.startswith("."):
            if t[0][0] == "J":
                out.append((t[0], "J", t[1:4], None))
            else:
                out.append((t[0], t[0][0], t[1:3], float(t[3])))
    return out


SIMNODO = {"a": "in", "g1a": "g1a", "g1": "g1", "s1": "s1", "sp": "sp", "d1": "d1", "g2a": "g2a",
           "g2": "g2", "s2": "s2", "d2": "d2", "lv": "top", "out": "out"}


def sim_net(nodo, side):
    if nodo == "va":
        return "VA"
    if nodo == "vg":
        return "VG"
    if nodo == "0":
        return "GND"
    return f"{SIMNODO[nodo]}_{side}"


def vicini(a, b):
    return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-30)


COMUNI_SIM = ("Rvt", "Rvb", "Cvg")


def confronto_con_sim():
    err = []
    el = sim_elementi()
    lay = [(p["ref"], p["kind"], frozenset(norm(pp[2]) for pp in p["pins"]), p["val"])
           for p in P if p["kind"] in ("res", "film", "elco", "mlcc") and p["val"] is not None]
    usati = set()

    def cerca(nets, val, tipo):
        for ref, kind, nn, v in lay:
            if ref not in usati and nn == nets and vicini(v, val) and (kind == "res") == (tipo == "R"):
                usati.add(ref)
                return True
        return False

    trim = {}
    visti = set()
    for nome, tipo, nodi, val in el:
        visti.add(nome)
        if nome in ("Rsrc", "Rload", "Rp1") or tipo == "J":
            continue                       # sorgente/carico/reostato GAIN esterni; J201 sotto
        if nome in ("Rlt", "Rlb"):
            trim[nome] = nodi
            continue
        for s in (["L"] if nome in COMUNI_SIM else ["L", "R"]):
            nets = frozenset(sim_net(nd, s) for nd in nodi)
            if not cerca(nets, val, tipo):
                err.append(f"sim {nome} {nodi} {val:g}: nessun componente uguale nel layout (canale {s})")
    for nome in ("Rs2a", "Rd2", "Rst2", "C3"):
        if nome not in visti:
            err.append(f"il netlist sim non contiene {nome}: letto male")
    pads = {name: net for name, _, net, _ in PADS}
    for s in "LR":
        if not cerca(frozenset({f"gb_{s}", f"sp_{s}"}), S.C["Rgmin"], "R"):
            err.append(f"220R del GAIN {s} mancante")
        if pads.get(f"GAIN A {s}") != f"s1_{s}" or pads.get(f"GAIN B {s}") != f"gb_{s}":
            err.append(f"piazzole GAIN {s} sulle net sbagliate")
        tr = next(p for p in P if p["ref"] == f"TR{s}")
        m = {pp[3].split()[0]: norm(pp[2]) for pp in tr["pins"]}
        if (m["1"], m["2"], m["3"]) != (f"top_{s}", f"out_{s}", "GND"):
            err.append(f"trimmer {s} sulle net sbagliate")
        if not vicini(tr["val"], S.C["Plevel"]):
            err.append("valore LEVEL diverso dalla sim")
    if trim.get("Rlt") != ["lv", "out"] or trim.get("Rlb") != ["out", "0"]:
        err.append(f"trimmer nel netlist sim diverso dall'atteso: {trim}")
    for nome, tipo, nodi, _ in el:
        if tipo == "J":                    # J1 d1 g1 s1
            for s in "LR":
                j = next(p for p in P if p["ref"] == f"{nome}{s}")
                m = {pp[3][0]: norm(pp[2]) for pp in j["pins"]}
                atteso = tuple(sim_net(nd, s) for nd in nodi)
                if (m["D"], m["G"], m["S"]) != atteso:
                    err.append(f"{nome}{s}: D/G/S {(m['D'], m['G'], m['S'])} != sim {atteso}")
    resto = sorted(r for r, _, _, _ in lay if r not in usati)
    if resto:
        err.append(f"componenti simulati senza controparte nella sim: {resto}")
    extra = sorted(p["ref"] for p in P if p["val"] is None and p["kind"] != "jfet")
    if extra != ["CB", "CD"]:
        err.append(f"componenti non simulati diversi da CB e CD: {extra}")
    return err


errors += confronto_con_sim()


def separazione_errori():
    err = []
    seg_ch = {}
    for p in P:
        for (x, y, _, _) in p["pins"]:
            seg_ch.setdefault(seg_of(x, y), set()).add(p["ch"])
    for sg, chs in seg_ch.items():
        if {"L", "R"} <= chs:
            err.append(f"striscia {sg} condivisa da componenti L e R")
    for p in P:
        for (x, y, _, _) in p["pins"]:
            if (p["ch"] == "L" and y > 8) or (p["ch"] == "R" and y < 9):
                err.append(f"{p['ref']} fuori dalla meta del suo canale")
    for s in "LR":                         # il rame del ritorno Cs1 porta solo Cs1 e il suo cavo
        cs = next(p for p in P if p["ref"] == f"Cs1{s}")
        sg = seg_of(cs["pins"][1][0], cs["pins"][1][1])
        extra = {w for sgg, _, w in conn if sgg == sg and not (w.startswith("Cs1") or w.startswith("W"))}
        if extra:
            err.append(f"ritorno Cs1 {s} condivide rame con {sorted(extra)}")
    sg_pad = seg_of(*PADS[1][1])           # Rs1, Rs2: massa di segnale (riga 5), non quella del pad
    for s in "LR":
        for ref in (f"Rs1{s}", f"Rs2{s}"):
            p = next(q for q in P if q["ref"] == ref)
            sg = seg_of(p["pins"][1][0], p["pins"][1][1])
            if sg == sg_pad or sg[0] != Y(s, 5):
                err.append(f"{ref}: ritorno su {sg}, deve stare sulla massa di segnale")
    return err


errors += separazione_errori()

if __name__ == "__main__":
    if errors:
        print("ERRORI:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    alt = max(p["h"] for p in P)
    print(f"OK: {len(P)} componenti, {len(LINKS)} ponticelli, {len(WIRES)} cavi, {len(PADS)} piazzole, "
          f"{len(CUTS)} tagli, {len(island_nets)} isole, {len(net_islands)} net, nessun corto, nessun aperto.")
    print(f"Scheda {W} x {H} fori = {W * PASSO:.1f} x {H * PASSO:.1f} mm (volume case 62 x 47 x 17,5); "
          f"altezza massima componenti {alt} mm; fori di fissaggio {FORI_FISSAGGIO}.")
