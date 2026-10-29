"""Foglio 4: buffer d'ingresso, un inseguitore TLC2272 per canale fra il deviatore PRE (JINL/JINR) e gli ingressi
del codec del Seed (SIN1/SIN2)."""
FILE = "f04_buffer_ingresso"
TITOLO = "Buffer d'ingresso"
G = 2.54

CANALI = (
    # nome, unità, dy, JIN, riferimenti C5 R5 R6 C19 R7 C6 C7
    ("L", 1, 0.0, "JINL", dict(ca="C5", rb="R5", rm="R6", cr="C19", rf="R7", cf="C6", cu="C7"), "SIN1"),
    ("R", 2, 63.5, "JINR", dict(ca="C8", rb="R8", rm="R9", cr="C20", rf="R10", cf="C9", cu="C10"), "SIN2"),
)


def disegna(f):
    f.testo("Buffer d'ingresso", 25.4, 25.4, 4, True)
    f.testo("Inseguitore a guadagno 1, impedenza d'ingresso 1 MOhm: C5/R5 (C8/R8) accoppiano e polarizzano a VB, "
            "R6 (R9) e C19 (C20) chiudono l'ingresso verso massa.", 25.4, 33.02, 1.8)
    f.testo("Passa-basso R7/C6 (R10/C9): 1 kOhm e 2,2 nF, circa 72 kHz. C7 (C10) da 10 uF accoppia l'ingresso audio del Seed.",
            25.4, 38.1, 1.8)

    for nome, unit, dy, jin, r, sin in CANALI:
        yp = 78.74 + dy                      # linea del segnale sull'ingresso +
        f.testo(f"Canale {nome}", 25.4, 55.88 + dy, 2.2, True)

        # ingresso e chiusura a massa
        f.etichetta(jin, (33.02, yp), "sx")
        rm = f.parte(r["rm"], 45.72, yp + 10.16, rot=270)
        f.filo((45.72, yp), rm.pin("1"))
        f.porta(rm.pin("2"))
        cr = f.parte(r["cr"], 55.88, yp + 10.16, rot=270)
        f.filo((55.88, yp), cr.pin("1"))
        f.porta(cr.pin("2"))

        # accoppiamento e polarizzazione a VB
        ca = f.parte(r["ca"], 76.2, yp)
        f.filo((33.02, yp), ca.pin("1"))
        rb = f.parte(r["rb"], 91.44, yp - 15.24)
        u = f.parte("U1", 119.38, yp - 2.54, unit=unit)
        f.filo(ca.pin("2"), u.pin("3" if unit == 1 else "5"))
        f.filo(rb.pin("1"), (86.36, yp))
        f.filo(rb.pin("2"), (96.52, rb.pin("2").y - 5.08))
        f.alim("VB", (96.52, rb.pin("2").y - 5.08))

        # inseguitore: uscita riportata sul - da sopra
        neg, out = u.pin("2" if unit == 1 else "6"), u.pin("1" if unit == 1 else "7")
        yf = yp - 12.7
        f.filo(neg, (101.6, neg.y), (101.6, yf), (134.62, yf), (134.62, out.y))
        f.filo(out, (134.62, out.y))
        f.testo("guadagno 1", 106.68, yf - 1.27, 1.5)

        # passa-basso e accoppiamento verso il codec
        rf = f.parte(r["rf"], 147.32, out.y)
        f.filo((134.62, out.y), rf.pin("1"))
        f.filo(rf.pin("2"), (162.56, out.y))
        cf = f.parte(r["cf"], 162.56, out.y + 5.08, rot=270)
        f.porta(cf.pin("2"))
        cu = f.parte(r["cu"], 177.8, out.y)
        f.filo((162.56, out.y), cu.pin("1"))
        f.porta(cu.pin("2"), lung=4 * G)
        f.testo(f"al codec del Seed ({sin})", 190.5, out.y - 2.54, 1.5)
