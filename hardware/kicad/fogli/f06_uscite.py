"""Foglio 6: jack d'uscita e true bypass stereo (footswitch 3PDT: polo A canale L, polo B canale R, polo C LED)."""
FILE = "f06_uscite"
TITOLO = "Uscite e true bypass"
G = 2.54

XS = 152.4            # colonna dei tre poli del footswitch


def polo_uscita(f, nome, jack, unit, y, effetto, bypass):
    """polo del 3PDT ruotato (comune a destra) verso il jack d'uscita; effetto in alto, bypass in basso"""
    f.testo(f"Canale {nome}", 50.8, y - 10.16, 2.5, True)
    sw = f.parte("SW203", XS, y, rot=180, unit=unit, scritte="su")
    pe, pb, pc = sw.pin(effetto), sw.pin(bypass), sw.pin(f"{'AB'[unit - 1]}2")
    f.porta(pe, lung=4 * G)
    f.porta(pb, lung=4 * G)
    f.testo("effetto", pe.x - 4 * G, pe.y - 1.1, 1.3)
    f.testo("bypass", pb.x - 4 * G, pb.y - 1.1, 1.3)

    # jack: la punta sta sul lato destro del simbolo, il filo del comune passa sopra il corpo e scende alla punta
    xj = 215.9
    j = f.parte(jack, xj, y + 3 * G, scritte="sx")
    xk = j.pin("T").x + G
    f.filo(pc, (xk, pc.y), (xk, j.pin("T").y), j.pin("T"))
    f.nc(j.pin("TN"))
    xg = j.pin("S").x + G
    f.filo(j.pin("S"), (xg, j.pin("S").y), (xg, j.pin("S").y + G))
    f.alim("GND", (xg, j.pin("S").y + G))
    return sw


def disegna(f):
    f.testo("Uscite e true bypass", 25.4, 25.4, 4, True)
    f.testo("Footswitch 3PDT: due poli scambiano la punta del jack d'uscita fra l'effetto (JOUT) e l'ingresso diretto "
            "(tip, prima di Rs); il terzo accende il LED.", 25.4, 33.02, 1.8)
    f.testo("In bypass l'ingresso resta collegato anche al buffer da 1 MOhm, che non carica il segnale. "
            "I tre poli sono un solo pezzo meccanico.", 25.4, 38.1, 1.8)

    polo_uscita(f, "L", "J203", 1, 66.04, "A3", "A1")
    polo_uscita(f, "R", "J204", 2, 116.84, "B3", "B1")

    # polo C: LED di stato, acceso a effetto inserito
    f.testo("Polo C: LED di stato", 50.8, 154.94, 2.5, True)
    yc = 170.18
    r = f.parte("R207", 114.3, yc - 2 * G, rot=270, scritte="sx")
    f.porta(r.pin("1"))
    sw = f.parte("SW203", XS, yc, unit=3, scritte="su")
    f.filo(r.pin("2"), sw.pin("C2"))
    f.nc(sw.pin("C1"))
    d = f.parte("D201", XS + 5 * G, yc + 3 * G, rot=270, scritte="dx")
    f.filo(sw.pin("C3"), d.pin("2"))
    f.porta(d.pin("1"))
    f.testo("bypass: libero", XS + 8.0, yc - G + 0.6, 1.3)
    f.testo("effetto", XS + 6.4, yc + 1.6, 1.3)
    f.testo("VA tramite R207: circa 1,5 mA con un LED rosso", XS + 40.0, yc + 3 * G, 1.4)
    f.testo("Non portare questo polo a un pin del Seed: porta VA (8,5 V)", XS + 40.0, yc + 3 * G + 3.0, 1.4)

    f.testo("Posizione EFFETTO: l'uscita prende JOUT, il LED e acceso.", 254.0, 66.04 - 2.54, 1.5)
    f.testo("Posizione BYPASS: l'uscita prende l'ingresso diretto (tip), il LED e spento.", 254.0, 66.04 + 0.5, 1.5)
