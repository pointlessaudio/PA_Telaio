"""Foglio 8: sei potenziometri, encoder, OLED, tasti K1 e K2, LED dei tasti e jack del pedale."""
FILE = "f08_controlli"
TITOLO = "Controlli: pot, encoder, OLED, tasti, pedale"
G = 2.54


def disegna(f):
    f.testo("Controlli", 25.4, 25.4, 4, True)
    f.testo("Pot, encoder, OLED, tasti e pedale parlano con il Seed solo attraverso le etichette di rete del foglio Daisy Seed3.",
            25.4, 33.02, 1.8)

    # ---- sei potenziometri: capo alto 3V3A, capo basso massa, cursore all'ingresso ADC
    y = 63.5
    f.testo("Potenziometri", 63.5, 50.8, 2.4, True)
    xs = [50.8 + 38.1 * i for i in range(6)]
    for i, x in enumerate(xs):
        p = f.parte(f"RV20{i + 2}", x, y, rot=90, scritte="sx")
        f.porta(p.pin("2"))
    xl, top, bot = xs[0] - 12.7, y - 5.08, y + 5.08
    f.filo((xl, top), (xs[-1], top))
    f.filo((xl, top), (xl, top - 5.08))
    f.alim("3V3A", (xl, top - 5.08))
    f.filo((xl, bot), (xs[-1], bot))
    f.filo((xl, bot), (xl, bot + 5.08))
    f.alim("GND", (xl, bot + 5.08))
    f.testo("B10K: capo alto a 3V3A, capo basso a massa, cursore all'ingresso ADC (POT1-POT6)", 50.8, 88.9, 1.5)

    # ---- OLED
    f.testo("OLED", 299.72, 50.8, 2.4, True)
    o = f.parte("A201", 330.2, y, rot=180, scritte="sx")
    f.porta(o.pin("4"))
    f.porta(o.pin("3"))
    f.porta(o.pin("2"), lung=25.4)
    f.porta(o.pin("1"))
    f.testo("I2C: SCL e SDA con i pull-up sul modulo", 299.72, 88.9, 1.5)

    # ---- encoder
    yr = 127.0
    f.testo("Encoder", 50.8, 106.68, 2.4, True)
    f.testo("A, B e tasto con i pull-up interni del Seed; C e S2 a massa", 50.8, 111.76, 1.5)
    e = f.parte("ENC201", 101.6, yr)
    f.porta(e.pin("A"))
    f.porta(e.pin("B"))
    f.porta(e.pin("C"), lung=25.4)
    f.porta(e.pin("S1"))
    f.porta(e.pin("S2"))

    # ---- LED dei tasti
    f.testo("LED dei tasti", 190.5, 106.68, 2.4, True)
    f.testo("Acceso dal piedino LED del Seed, 1 k in serie", 190.5, 111.76, 1.5)
    r = f.parte("R208", 203.2, yr)
    d = f.parte("D202", 228.6, yr)
    f.porta(r.pin("1"))
    f.filo(r.pin("2"), d.pin("2"))
    f.porta(d.pin("1"))

    # ---- tasti e jack del pedale, in parallelo
    f.testo("Tasti K1, K2 e pedale", 50.8, 177.8, 2.4, True)
    f.testo("Il Seed legge D0 e FS2 con pull-up interni: premere un tasto, o il pedale, li porta a massa", 50.8, 182.88, 1.5)
    j = f.parte("J206", 63.5, 203.2, scritte="sx")
    xk1, xk2 = 152.4, 114.3
    yd0, yfs, ygn = 190.5, 203.2, 215.9
    f.filo(j.pin("T"), (76.2, j.pin("T").y), (76.2, yd0), (xk1 + 12.7, yd0))
    f.etichetta("D0", (xk1 + 12.7, yd0), "dx")
    f.filo(j.pin("R"), (xk2 + 10.16, yfs))
    f.etichetta("FS2", (xk2 + 10.16, yfs), "dx")
    f.filo(j.pin("S"), (76.2, j.pin("S").y), (76.2, ygn), (xk1, ygn))
    f.alim("GND", (xk1, ygn))
    k1 = f.parte("SW204", xk1, yd0 + 5.08, rot=270)
    f.filo(k1.pin("2"), (xk1, ygn))
    k2 = f.parte("SW205", xk2, yfs + 5.08, rot=270)
    f.filo(k2.pin("2"), (xk2, ygn))
    f.testo("Jack TRS: punta = D0 (K1), anello = FS2 (K2), manicotto = massa", 50.8, 228.6, 1.5)
