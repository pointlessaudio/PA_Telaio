"""Foglio 2: ingressi. Jack d'ingresso, Rs, deviatore INST/LINE (un polo per canale) e deviatore PRE. Canale L sopra,
canale R sotto, stesso disegno: segnale da sinistra a destra, jack -> Rs -> nodo INST/LINE -> PRE -> buffer."""
FILE = "f02_ingressi"
TITOLO = "Ingressi: jack, INST/LINE, PRE"
G = 2.54

# per canale: (nome, jack, Rs, deviatore INST/LINE, unità, Rsh, deviatore PRE, rete tip, rete in, rete out preamp, uscita buffer)
CANALI = (
    dict(nome="L", jack="J201", rs="R201", il="SW201", u=1, rsh="R203", pre="SW202", tip="tip_L", ing="in_L",
         out="out_L", buf="JINL", y=63.5),
    dict(nome="R", jack="J202", rs="R202", il="SW201", u=2, rsh="R204", pre="SW202", tip="tip_R", ing="in_R",
         out="out_R", buf="JINR", y=165.1),
)


def canale(f, c):
    yt = c["y"]                     # quota della linea del segnale
    f.testo(f"Canale {c['nome']}", 50.8, yt - 20.32, 2.5, True)

    # jack: la punta esce in alto, contatto di commutazione (TN) e manicotto a massa
    j = f.parte(c["jack"], 50.8, yt + G)
    xg = j.pin("S").x + 2 * G
    f.filo(j.pin("TN"), (xg, j.pin("TN").y), (xg, j.pin("S").y + G))
    f.filo(j.pin("S"), (xg, j.pin("S").y))
    f.alim("GND", (xg, j.pin("S").y + G))

    # punta -> Rs, con la derivazione verso il true bypass (tip)
    rs = f.parte(c["rs"], 101.6, yt)
    f.filo(j.pin("T"), rs.pin("1"))
    xt = 76.2
    f.filo((xt, yt), (xt, yt - 2 * G))
    f.etichetta(c["tip"], (xt, yt - 2 * G), "dx")
    f.testo("al footswitch (bypass)", xt + 1.5, yt - 7.6, 1.3)

    # nodo INST/LINE: il comune del deviatore sta sulla linea, i contatti scendono
    xn = 134.62
    il = f.parte(c["il"], xn, yt + 2 * G, rot=270, unit=c["u"], scritte="dx")
    f.filo(rs.pin("2"), il.pin(il_pin(c, "com")), (xn + 12 * G, yt))
    f.nc(il.pin(il_pin(c, "inst")))
    rsh = f.parte(c["rsh"], il.pin(il_pin(c, "line")).x, yt + 6 * G, rot=270, scritte="sx")
    f.filo(il.pin(il_pin(c, "line")), rsh.pin("1"))
    f.porta(rsh.pin("2"))
    f.testo("INST: aperto, nessun carico, 0 dB, ~1 MOhm", xn + 6.5, yt + 11 * G / 2 + 4.0, 1.4)
    f.testo("LINE: chiuso, Rsh a massa, -12 dB, ~13 kOhm", xn + 6.5, yt + 11 * G / 2 + 6.5, 1.4)
    f.testo("nodo INST/LINE", xn - 7.0, yt - 2.2, 1.4)

    # derivazione verso l'ingresso del preamp (la linea passa dritta fino al PRE)
    xi = 160.02
    f.filo((xi, yt), (xi, yt - 2 * G))
    f.etichetta(c["ing"], (xi, yt - 2 * G), "dx")
    f.testo("ingresso preamp", xi + 1.5, yt - 7.6, 1.3)

    # deviatore PRE (ruotato: comune a destra, verso il buffer)
    pre = f.parte(c["pre"], 205.74, yt - G, rot=180, unit=c["u"])
    f.filo((xn + 12 * G, yt), pre.pin(il_pin(c, "pre_off")))
    f.porta(pre.pin(il_pin(c, "pre_on")), lung=4 * G)
    f.porta(pre.pin(il_pin(c, "pre_com")), lung=4 * G)
    f.testo("PRE spento: JIN = nodo INST/LINE (in)", 190.5, yt + 8.0, 1.4)
    f.testo("PRE acceso: JIN = uscita preamp (out)", 190.5, yt + 10.5, 1.4)
    f.testo("al buffer d'ingresso", 232.0, yt - 7.6, 1.3)


def il_pin(c, ruolo):
    """numeri dei piedini per canale (L: unità 1, R: unità 2)"""
    l = c["u"] == 1
    return {"com": "2" if l else "5", "inst": "1" if l else "4", "line": "3" if l else "6",
            "pre_com": "2" if l else "5", "pre_off": "1" if l else "4", "pre_on": "3" if l else "6"}[ruolo]


def disegna(f):
    f.testo("Ingressi", 25.4, 25.4, 4, True)
    f.testo("Punta del jack -> Rs 10k (sempre inserita) -> nodo INST/LINE -> deviatore PRE -> buffer. Un polo per canale: "
            "i due canali non si toccano.", 25.4, 33.02, 1.8)
    f.testo("INST/LINE: Rsh 3k3 verso massa solo in LINE (Rs + Rsh = -12 dB). Il jack ha il contatto di commutazione "
            "della punta a massa: a jack scollegato l'ingresso non fruscia.", 25.4, 38.1, 1.8)
    for c in CANALI:
        canale(f, c)
