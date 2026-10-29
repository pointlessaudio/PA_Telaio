"""
PA-TELAIO veroboard: Daisy Seed3 + 2x TLC2272 (DIP-8) a 9 V, stereo in/out.
Coordinate: x = foro lungo la striscia (0..W-1), y = striscia (0..H-1).
Le strisce di rame corrono in orizzontale (lungo x).
Tutto viene verificato: fori doppi, fori tagliati, zona sotto il Seed,
e soprattutto che ogni net elettrica corrisponda esattamente a una isola di rame.
"""

W, H = 30, 45

# ---------------------------------------------------------------- tagli
CUTS = set()
for y in range(0, 20):
    CUTS.add((6, y))    # tra le due file del Seed: OBBLIGATORIO
    CUTS.add((14, y))   # accorcia le strisce dei pin destri
CUTS.add((4, 21))
CUTS.add((15, 21))
for y in range(27, 34):
    CUTS.add((13, y))   # centro U1 + separazione canali
for y in range(36, 44):
    CUTS.add((13, y))   # centro U2 + separazione canali

# ---------------------------------------------------------------- Seed3
SEED_X_L, SEED_X_R = 3, 9
seed_net = {
    1: "D0", 4: "ENC_A", 5: "SD_D0", 6: "SD_CMD", 7: "SD_CK", 8: "ENC_B", 9: "ENC_SW",
    10: "LED", 11: "FS2", 12: "SCL", 13: "SDA", 14: "MIDI_TX", 15: "MIDI_RX",
    16: "SIN1", 17: "SIN2", 18: "SOUT1", 19: "SOUT2",
    20: "GND", 21: "3V3A", 22: "POT1", 23: "POT2", 24: "POT3", 25: "POT4",
    26: "POT5", 27: "POT6", 38: "3V3D", 39: "VIN_S", 40: "GND",
}
seed_name = {
    1: "D0", 2: "D1", 3: "D2", 4: "D3", 5: "D4", 6: "D5", 7: "D6", 8: "D7",
    9: "D8", 10: "D9", 11: "D10", 12: "D11", 13: "D12", 14: "D13", 15: "D14",
    16: "IN 1", 17: "IN 2", 18: "OUT 1", 19: "OUT 2", 20: "AGND", 21: "3V3A",
    22: "A0", 23: "A1", 24: "A2", 25: "A3", 26: "A4", 27: "A5", 28: "A6",
    29: "A7", 30: "A8", 31: "A9", 32: "A10", 33: "D26", 34: "D27", 35: "A11",
    36: "D29", 37: "D30", 38: "3V3D", 39: "VIN", 40: "DGND",
}


def seed_pos(p):
    return (SEED_X_L, p - 1) if p <= 20 else (SEED_X_R, 40 - p)


SEED_BODY = {(x, y) for x in range(SEED_X_L, SEED_X_R + 1) for y in range(0, 20)}

# ---------------------------------------------------------------- componenti
# (ref, tipo, valore, [(x, y, net, nota_pin)])
P = []


def part(ref, kind, value, *pins):
    P.append((ref, kind, value, list(pins)))


# Alimentazione
part("D1", "diode", "1N5817", (2, 21, "DCIN", "A"), (6, 21, "V9", "K"))
part("R1", "res", "3R3", (13, 21, "V9", ""), (17, 21, "VIN_S", ""))
part("C1", "elco", "100µF", (20, 21, "VIN_S", "+"), (20, 22, "GND", "-"))
part("R2", "res", "10R", (8, 21, "V9", ""), (8, 24, "VA", ""))
part("C2", "elco", "100µF", (10, 24, "VA", "+"), (10, 25, "GND", "-"))
part("C3", "cap", "100nF", (11, 24, "VA", ""), (11, 25, "GND", ""))
part("R3", "res", "10K", (13, 24, "VA", ""), (13, 23, "VB", ""))
part("R4", "res", "10K", (14, 23, "VB", ""), (14, 22, "GND", ""))
part("C4", "elco", "47µF", (16, 23, "VB", "+"), (16, 22, "GND", "-"))

# Ingresso L
part("C5", "film", "100nF", (3, 31, "JINL", ""), (3, 29, "INLB", ""))
part("R5", "res", "1M", (5, 29, "INLB", ""), (5, 26, "VB", ""))
part("R6", "res", "1M", (2, 31, "JINL", ""), (2, 30, "GND", ""))
part("C19", "cap", "100pF", (1, 31, "JINL", ""), (1, 30, "GND", ""))
part("R7", "res", "1K", (7, 28, "U1A_OUT", ""), (7, 32, "INLF", ""))
part("C6", "cap", "2.2nF", (8, 32, "INLF", ""), (8, 34, "GND", ""))
part("C7", "elco", "10µF", (10, 32, "INLF", "+"), (10, 33, "SIN1", "-"))
# Ingresso R
part("C8", "film", "100nF", (19, 33, "JINR", ""), (19, 30, "INRB", ""))
part("R8", "res", "1M", (21, 30, "INRB", ""), (21, 26, "VB", ""))
part("R9", "res", "1M", (23, 33, "JINR", ""), (23, 34, "GND", ""))
part("C20", "cap", "100pF", (28, 33, "JINR", ""), (28, 34, "GND", ""))
part("R10", "res", "1K", (25, 29, "U1B_OUT", ""), (25, 31, "INRF", ""))
part("C9", "cap", "2.2nF", (26, 31, "INRF", ""), (26, 34, "GND", ""))
part("C10", "elco", "10µF", (27, 31, "INRF", "+"), (27, 32, "SIN2", "-"))
part("C11", "cap", "100nF", (19, 27, "VA", ""), (19, 25, "GND", ""))

# Uscita L
part("C12", "elco", "10µF", (3, 42, "OLC", "+"), (3, 43, "SOUT1", "-"))
part("R11", "res", "10K", (5, 42, "OLC", ""), (5, 37, "U2A_NEG", ""))
part("R12", "res", "10K", (8, 37, "U2A_NEG", ""), (8, 36, "U2A_OUT", ""))
part("C13", "cap", "390pF", (3, 37, "U2A_NEG", ""), (3, 36, "U2A_OUT", ""))
part("C14", "elco", "10µF", (7, 36, "U2A_OUT", "+"), (7, 40, "OLO", "-"))
part("R13", "res", "100R", (4, 40, "OLO", ""), (4, 41, "JOUTL", ""))
part("R14", "res", "100K", (2, 41, "JOUTL", ""), (2, 39, "GND", ""))
# Uscita R
part("C15", "elco", "10µF", (24, 42, "ORC", "+"), (24, 43, "SOUT2", "-"))
part("R15", "res", "10K", (21, 42, "ORC", ""), (21, 38, "U2B_NEG", ""))
part("R16", "res", "10K", (22, 38, "U2B_NEG", ""), (22, 37, "U2B_OUT", ""))
part("C16", "cap", "390pF", (23, 38, "U2B_NEG", ""), (23, 37, "U2B_OUT", ""))
part("C17", "elco", "10µF", (25, 37, "U2B_OUT", "+"), (25, 40, "ORO", "-"))
part("R17", "res", "100R", (27, 40, "ORO", ""), (27, 41, "JOUTR", ""))
part("R18", "res", "100K", (28, 41, "JOUTR", ""), (28, 44, "GND", ""))
part("C18", "cap", "100nF", (16, 36, "VA", ""), (16, 34, "GND", ""))

# Integrati (DIP-8 su zoccolo): colonna sinistra 12, destra 15
ICS = []


def dip8(ref, top, nets):
    # nets: dict pin -> net
    pins = []
    for i, p in enumerate([1, 2, 3, 4]):
        pins.append((12, top + i, nets[p], str(p)))
    for i, p in enumerate([8, 7, 6, 5]):
        pins.append((15, top + i, nets[p], str(p)))
    P.append((ref, "dip8", "TLC2272", pins))
    ICS.append((ref, top))


dip8("U1", 27, {1: "U1A_OUT", 2: "U1A_OUT", 3: "INLB", 4: "GND",
               5: "INRB", 6: "U1B_OUT", 7: "U1B_OUT", 8: "VA"})
dip8("U2", 36, {1: "U2A_OUT", 2: "U2A_NEG", 3: "VB", 4: "GND",
               5: "VB", 6: "U2B_NEG", 7: "U2B_OUT", 8: "VA"})

# Seed header come "componente"
seed_pins = []
for p in range(1, 41):
    x, y = seed_pos(p)
    seed_pins.append((x, y, seed_net.get(p, f"NC{p}"), str(p)))
P.append(("SEED", "seed", "Daisy Seed3", seed_pins))

# ---------------------------------------------------------------- ponticelli sulla scheda
# (nome, (x1,y1), (x2,y2), net, nudo?)
LINKS = [
    ("J1", (11, 27), (11, 28), "U1A_OUT", True),
    ("J2", (16, 28), (16, 29), "U1B_OUT", True),
    ("J3", (17, 27), (17, 24), "VA", False),
    ("J4", (18, 27), (18, 36), "VA", False),
    ("J5", (4, 30), (4, 34), "GND", False),
    ("J6", (6, 25), (6, 34), "GND", False),
    ("J7", (28, 22), (28, 25), "GND", False),
    ("J8", (29, 23), (29, 26), "VB", False),
    ("J9", (28, 26), (28, 35), "VB", False),
    ("J10", (10, 38), (10, 35), "VB", False),
    ("J11", (20, 39), (20, 35), "VB", False),
    ("J12", (11, 39), (11, 34), "GND", False),
    ("J13", (1, 39), (1, 44), "GND", False),
]
# cavetti verso i pin del Seed (isolati)
WIRES = [
    ("W1", (29, 21), (12, 1), "VIN_S", "VIN → pin 39"),
    ("W2", (1, 22), (1, 19), "GND", "massa → AGND pin 20"),
    ("W3", (27, 22), (13, 0), "GND", "massa → DGND pin 40"),
    ("W4", (0, 33), (0, 15), "SIN1", "→ IN 1 pin 16"),
    ("W5", (14, 32), (1, 16), "SIN2", "→ IN 2 pin 17"),
    ("W6", (0, 43), (0, 17), "SOUT1", "OUT 1 pin 18 →"),
    ("W7", (14, 43), (1, 18), "SOUT2", "OUT 2 pin 19 →"),
]

# ---------------------------------------------------------------- piazzole esterne (fili fuori scheda)
PADS = [
    ("DC +9V", (0, 21), "DCIN", "Jack DC: +9 V (manicotto)"),
    ("DC GND", (0, 22), "GND", "Jack DC: massa (centrale)"),
    ("IN L", (0, 31), "JINL", "Da Rs del jack IN L (INST/LINE)"),
    ("IN L GND", (0, 34), "GND", "Jack IN L: manicotto"),
    ("IN R", (29, 33), "JINR", "Da Rs del jack IN R (INST/LINE)"),
    ("IN R GND", (29, 34), "GND", "Jack IN R: manicotto"),
    ("OUT L", (0, 41), "JOUTL", "3PDT polo A, posizione effetto"),
    ("OUT L GND", (0, 44), "GND", "Jack OUT L: manicotto"),
    ("OUT R", (29, 41), "JOUTR", "3PDT polo B, posizione effetto"),
    ("OUT R GND", (29, 44), "GND", "Jack OUT R: manicotto"),
    ("FS1", (0, 0), "D0", "Tasto K1 (e pedale esterno, punta)"),
    ("ENC A", (0, 3), "ENC_A", "Encoder A"),
    ("SD D0", (0, 4), "SD_D0", "microSD DAT0"),
    ("SD CMD", (0, 5), "SD_CMD", "microSD CMD"),
    ("SD CK", (0, 6), "SD_CK", "microSD CLK"),
    ("ENC B", (0, 7), "ENC_B", "Encoder B"),
    ("ENC SW", (0, 8), "ENC_SW", "Encoder pulsante"),
    ("LED", (0, 9), "LED", "LED anodo tramite 1K"),
    ("FS2", (0, 10), "FS2", "Tasto K2 (e pedale esterno, anello)"),
    ("SCL", (0, 11), "SCL", "OLED SCL"),
    ("SDA", (0, 12), "SDA", "OLED SDA"),
    ("MIDI TX", (0, 13), "MIDI_TX", "MIDI OUT verso scheda I/O"),
    ("MIDI RX", (0, 14), "MIDI_RX", "MIDI IN da scheda I/O"),
    ("POT GND", (2, 19), "GND", "Pot 1-6: capo basso"),
    ("CTRL GND", (10, 0), "GND", "Masse digitali: FS, encoder, LED"),
    ("OLED GND", (11, 0), "GND", "OLED GND"),
    ("IO GND", (12, 0), "GND", "Massa scheda I/O esterna"),
    ("3V3D", (12, 2), "3V3D", "OLED VCC"),
    ("IO 3V3D", (13, 2), "3V3D", "Alimentazione scheda I/O esterna"),
    ("A5", (12, 13), "POT6", "Pot 6 cursore"),
    ("A4", (12, 14), "POT5", "Pot 5 cursore"),
    ("A3", (12, 15), "POT4", "Pot 4 cursore"),
    ("A2", (12, 16), "POT3", "Pot 3 cursore"),
    ("A1", (12, 17), "POT2", "Pot 2 cursore"),
    ("A0", (12, 18), "POT1", "Pot 1 cursore"),
    ("3V3A", (12, 19), "3V3A", "Pot 1-6: capo alto"),
]


# ================================================================= VERIFICA
def seg_of(x, y):
    """isola di rame: (y, indice segmento) dati i tagli sulla riga y"""
    assert (x, y) not in CUTS
    idx = sum(1 for cx in range(0, x) if (cx, y) in CUTS)
    return (y, idx)


errors = []
used = {}


def use(hole, who):
    x, y = hole
    if not (0 <= x < W and 0 <= y < H):
        errors.append(f"{who}: foro {hole} fuori scheda")
        return
    if hole in CUTS:
        errors.append(f"{who}: foro {hole} è un taglio")
    if hole in used:
        errors.append(f"{who}: foro {hole} già usato da {used[hole]}")
    used[hole] = who


conn = []  # (segmento, net, chi)
for ref, kind, val, pins in P:
    for (x, y, net, n) in pins:
        who = f"{ref}.{n}" if n else ref
        if kind != "seed" and (x, y) in SEED_BODY:
            errors.append(f"{who}: foro {(x, y)} sotto il corpo del Seed")
        use((x, y), who)
        conn.append((seg_of(x, y), net, who))
for name, a, b, net, _ in LINKS:
    for h in (a, b):
        use(h, name)
        conn.append((seg_of(*h), net, name))
for name, a, b, net, _ in WIRES:
    for h in (a, b):
        if h in SEED_BODY:
            errors.append(f"{name}: estremo {h} sotto il Seed")
        use(h, name)
        conn.append((seg_of(*h), net, name))
for name, h, net, _ in PADS:
    if h in SEED_BODY:
        errors.append(f"{name}: piazzola {h} sotto il Seed")
    use(h, name)
    conn.append((seg_of(*h), net, name))

# ================================================================= FORI DI FISSAGGIO
# (x, y) a base 0, da forare a 3,2 mm per viti M3; nella pagina sono numerati da 1. Unica lista:
# case.py e scatola.py la leggono da qui. Fino al 28/09 c'erano (2,44) e (27,44): spezzavano la
# striscia 44 (masse OUT L/R, J13, R18) e stavano a 1,27 mm dal bordo della scheda.
FORI_FISSAGGIO = [(1, 1), (28, 1), (7, 43), (28, 37)]


def fori_fissaggio_errori(fori):
    """controllo elettrico dei fori di fissaggio: liberi, ad almeno un foro dal bordo, e senza
    spezzare una striscia usata (il foro da 3,2 toglie il rame della sua striscia). Lo spazio per
    teste e dadi contro i componenti lo controlla chi conosce gli ingombri (case.py, scatola.py)."""
    err = []
    for (x, y) in fori:
        h = (x, y)
        if not (1 <= x <= W - 2 and 1 <= y <= H - 2):
            err.append(f"foro di fissaggio {h}: a meno di un foro dal bordo")
        if h in used:
            err.append(f"foro di fissaggio {h}: occupato da {used[h]}")
            continue
        if h in CUTS:
            continue                      # la striscia lì è già tagliata
        seg = seg_of(x, y)
        stessa = [u for u in used if u[1] == y and seg_of(*u) == seg]
        sx = [u for u in stessa if u[0] < x]
        dx = [u for u in stessa if u[0] > x]
        if sx and dx:
            err.append(f"foro di fissaggio {h}: spezza la striscia {y} fra {used[max(sx)]} e {used[min(dx)]}")
    return err


errors += fori_fissaggio_errori(FORI_FISSAGGIO)

# union-find sui segmenti uniti da ponticelli e cavi
parent = {}


def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


def union(a, b):
    parent[find(a)] = find(b)


for s, _, _ in conn:
    find(s)
for _, a, b, _, _ in LINKS + WIRES:
    union(seg_of(*a), seg_of(*b))

island_nets = {}
net_islands = {}
for s, net, who in conn:
    r = find(s)
    island_nets.setdefault(r, set()).add(net)
    net_islands.setdefault(net, set()).add(r)

for r, nets in island_nets.items():
    if len(nets) > 1:
        errors.append(f"CORTO: le net {sorted(nets)} sono sulla stessa isola di rame")
for net, rs in net_islands.items():
    if len(rs) > 1:
        errors.append(f"APERTO: la net {net} è divisa in {len(rs)} isole")

# ogni net interna deve avere almeno due punti
count = {}
for _, net, _ in conn:
    count[net] = count.get(net, 0) + 1
for net, c in count.items():
    if c < 2 and not net.startswith("NC"):
        errors.append(f"net {net} con un solo punto di connessione")

# Controllo elettrico della topologia rispetto allo schema
EXPECTED = {
    # net: insieme di pin che DEVONO starci
    "INLB": {"C5", "R5", "U1.3"},
    "U1A_OUT": {"U1.1", "U1.2", "R7"},
    "INLF": {"R7", "C6", "C7.+"},
    "SIN1": {"C7.-", "SEED.16"},
    "INRB": {"C8", "R8", "U1.5"},
    "U1B_OUT": {"U1.7", "U1.6", "R10"},
    "INRF": {"R10", "C9", "C10.+"},
    "SIN2": {"C10.-", "SEED.17"},
    "SOUT1": {"C12.-", "SEED.18"},
    "OLC": {"C12.+", "R11"},
    "U2A_NEG": {"R11", "R12", "C13", "U2.2"},
    "U2A_OUT": {"R12", "C13", "C14.+", "U2.1"},
    "OLO": {"C14.-", "R13"},
    "JOUTL": {"R13", "R14"},
    "SOUT2": {"C15.-", "SEED.19"},
    "ORC": {"C15.+", "R15"},
    "U2B_NEG": {"R15", "R16", "C16", "U2.6"},
    "U2B_OUT": {"R16", "C16", "C17.+", "U2.7"},
    "ORO": {"C17.-", "R17"},
    "JOUTR": {"R17", "R18"},
    "VA": {"R2", "C2.+", "C3", "R3", "U1.8", "U2.8", "C11", "C18"},
    "VB": {"R3", "R4", "C4.+", "R5", "R8", "U2.3", "U2.5"},
    "VIN_S": {"R1", "C1.+", "SEED.39"},
    "V9": {"D1.K", "R1", "R2"},
    "DCIN": {"D1.A"},
    "GND": {"C1.-", "C2.-", "C3", "R4", "C4.-", "R6", "C6", "R9", "C9",
            "C11", "U1.4", "U2.4", "R14", "R18", "C18", "C19", "C20", "SEED.20", "SEED.40"},
    "JINL": {"C5", "R6", "C19"},
    "JINR": {"C8", "R9", "C20"},
    # mappa pin digitale: OLED su I2C1 (D11/D12), MIDI su USART1 (D13/D14), microSD 1-bit (D4/D5/D6)
    "SCL": {"SEED.12", "SCL"},
    "SDA": {"SEED.13", "SDA"},
    "MIDI_TX": {"SEED.14", "MIDI TX"},
    "MIDI_RX": {"SEED.15", "MIDI RX"},
    "SD_D0": {"SEED.5", "SD D0"},
    "SD_CMD": {"SEED.6", "SD CMD"},
    "SD_CK": {"SEED.7", "SD CK"},
}
by_net = {}
for s, net, who in conn:
    by_net.setdefault(net, set()).add(who)
for net, must in EXPECTED.items():
    have = by_net.get(net, set())
    # confronto per riferimento (C5 può comparire come "C5" o "C5.x")
    have_refs = have | {h.split(".")[0] for h in have if not h.split(".")[-1].isdigit() and h.split(".")[-1] not in "+-AK"}
    for m in must:
        if m not in have and m not in have_refs:
            errors.append(f"Net {net}: manca {m}")

if __name__ == "__main__":
    if errors:
        print("ERRORI:")
        for e in errors:
            print(" -", e)
    else:
        n_isl = len(island_nets)
        print(f"OK: {len(P)} gruppi componenti, {len(LINKS)} ponticelli, "
              f"{len(WIRES)} cavi, {len(PADS)} piazzole, {len(CUTS)} tagli, "
              f"{n_isl} isole, {len(net_islands)} net, nessun corto, nessun aperto.")
