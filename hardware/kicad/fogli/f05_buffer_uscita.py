"""Foglio 5: buffer d'uscita, un invertitore a guadagno -1 (TLC2272) per canale fra gli ingressi di uscita del Seed
(SOUT1/SOUT2) e il footswitch (JOUTL/JOUTR)."""
FILE = "f05_buffer_uscita"
TITOLO = "Buffer d'uscita"
G = 2.54

CANALI = (
    ("L", 1, 0.0, "SOUT1", "JOUTL", dict(ci="C12", ri="R11", rr="R12", cr="C13", cu="C14", rs="R13", rm="R14")),
    ("R", 2, 63.5, "SOUT2", "JOUTR", dict(ci="C15", ri="R15", rr="R16", cr="C16", cu="C17", rs="R17", rm="R18")),
)


def disegna(f):
    f.testo("Buffer d'uscita", 25.4, 25.4, 4, True)
    f.testo("Invertitore a guadagno -1 (R12/R11 = 1): il firmware inverte la fase per compensare.", 25.4, 33.02, 1.8)
    f.testo("Retroazione R12 || C13 (10 kOhm e 390 pF): passa-basso circa 41 kHz. Uscita: C14 da 10 uF, R13 da 100 Ohm "
            "in serie, R14 da 100 kOhm a massa.", 25.4, 38.1, 1.8)

    for nome, unit, dy, sout, jout, r in CANALI:
        yl = 73.66 + dy                      # linea del segnale sull'ingresso -
        f.testo(f"Canale {nome}", 25.4, 48.26 + dy, 2.2, True)

        # ingresso dal Seed: C12 va girato, il + sta dal lato di R11
        f.etichetta(sout, (33.02, yl), "sx")
        ci = f.parte(r["ci"], 45.72, yl, rot=180)
        f.filo((33.02, yl), ci.pin("2"))
        ri = f.parte(r["ri"], 63.5, yl)
        f.filo(ci.pin("1"), ri.pin("1"))

        u = f.parte("U2", 119.38, yl + 2.54, unit=unit)
        neg, pos, out = (u.pin(n) for n in (("2", "3", "1") if unit == 1 else ("6", "5", "7")))
        f.filo(ri.pin("2"), (96.52, yl), neg)
        f.filo(pos, (pos.x - 5.08, pos.y))
        f.etichetta("VB", (pos.x - 5.08, pos.y), "sx")
        xo = 134.62
        f.filo(out, (xo, out.y))

        # retroazione sopra l'operazionale: R12 sotto, C13 sopra, in parallelo
        rr = f.parte(r["rr"], 115.57, yl - 10.16)
        cr = f.parte(r["cr"], 115.57, yl - 20.32)
        f.filo((96.52, yl), (96.52, cr.pin("1").y), cr.pin("1"))
        f.filo((96.52, rr.pin("1").y), rr.pin("1"))
        f.filo(rr.pin("2"), (xo, rr.pin("2").y))
        f.filo(cr.pin("2"), (xo, cr.pin("2").y), (xo, out.y))

        # uscita
        cu = f.parte(r["cu"], 149.86, out.y)
        f.filo((xo, out.y), cu.pin("1"))
        rs = f.parte(r["rs"], 167.64, out.y)
        f.filo(cu.pin("2"), rs.pin("1"))
        xj = 185.42
        f.filo(rs.pin("2"), (xj, out.y), (xj + 7.62, out.y))
        f.etichetta(jout, (xj + 7.62, out.y), "dx")
        rm = f.parte(r["rm"], xj, out.y + 5.08, rot=270)
        f.filo((xj, out.y), rm.pin("1"))
        f.porta(rm.pin("2"))
        f.testo(f"al footswitch ({jout})", xj + 17.78, out.y - 2.54, 1.5)
