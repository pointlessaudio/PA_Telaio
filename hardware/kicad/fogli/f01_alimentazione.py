"""Foglio 1: alimentazione 9 V, rami VIN (Seed), VA (analogica) e VB (metà alimentazione), alimentazione degli
operazionali, massa del telaio, PWR_FLAG di tutte le reti di alimentazione del progetto."""
FILE = "f01_alimentazione"
TITOLO = "Alimentazione"
G = 2.54


def disegna(f):
    f.testo("Alimentazione", 25.4, 25.4, 4, True)
    f.testo("9 V centro negativo; D1 contro l'inversione. R1/C1 filtrano il VIN del Seed, R2/C2/C3 la VA degli stadi analogici.",
            25.4, 33.02, 1.8)
    f.testo("VB = VA/2 dal partitore R3/R4 con C4: polarizzazione di ingressi e uscite, solo nodi ad alta impedenza.",
            25.4, 38.1, 1.8)

    y = 81.28
    j = f.parte("J205", 50.8, y)
    f.porta(j.pin("1"))                                   # centrale = massa
    f.nc(j.pin("3"))
    d1 = f.parte("D1", 76.2, y + G)
    f.filo(j.pin("2"), (63.5, j.pin("2").y), (63.5, d1.pin("2").y), d1.pin("2"))
    v9 = (91.44, d1.pin("1").y)
    f.filo(d1.pin("1"), v9)
    f.testo("V9", 88.9, v9[1] - 1.27, 1.5)

    # VIN del Seed
    r1 = f.parte("R1", 104.14, v9[1])
    f.filo(v9, r1.pin("1"))
    c1 = f.parte("C1", 119.38, v9[1] + 10.16, rot=270)
    f.filo(r1.pin("2"), (132.08, v9[1]))
    f.filo((119.38, v9[1]), c1.pin("1"))
    f.porta(c1.pin("2"))
    f.etichetta("VIN_S", (132.08, v9[1]), "dx")
    f.testo("al VIN del Seed (pin 39)", 132.08, v9[1] + 5.08, 1.5)

    # VA
    ya = 111.76
    r2 = f.parte("R2", 104.14, ya)
    f.filo(v9, (91.44, ya), r2.pin("1"))
    xs = [119.38, 132.08, 144.78, 157.48]
    for ref, x in zip(("C2", "C3", "C11", "C18"), xs):
        c = f.parte(ref, x, ya + 10.16, rot=270)
        f.filo((x, ya), c.pin("1"))
        f.porta(c.pin("2"))
    f.testo("C11, C18: vicino a U1 e U2", 119.38, ya + 30.48, 1.5)
    xr = 177.8
    f.filo(r2.pin("2"), (xr, ya))
    f.filo((114.3, ya), (114.3, ya - 7.62))
    f.alim("VA", (114.3, ya - 7.62))

    # VB
    r3 = f.parte("R3", xr, ya + 10.16, rot=270)
    f.filo((xr, ya), r3.pin("1"))
    yb = ya + 20.32
    r4 = f.parte("R4", xr, yb + 10.16, rot=270)
    f.filo(r3.pin("2"), (xr, yb), r4.pin("1"))
    f.porta(r4.pin("2"))
    c4 = f.parte("C4", 195.58, yb + 10.16, rot=270)
    f.filo((xr, yb), (195.58, yb), c4.pin("1"))
    f.porta(c4.pin("2"))
    f.filo((195.58, yb), (208.28, yb))
    f.alim("VB", (208.28, yb))

    # alimentazione degli operazionali
    f.testo("TLC2272: alimentazione", 236.22, 99.06, 1.8)
    for ref, x in (("U1", 243.84), ("U2", 266.7)):
        u = f.parte(ref, x, ya + 5.08, unit=3)
        f.porta(u.pin("8"))
        f.porta(u.pin("4"))

    # massa del telaio
    f.testo("Massa del telaio (schermatura in rame, docs/schermatura_massa.md)", 25.4, 165.1, 1.8)
    for ref, x in (("H201", 50.8), ("H202", 88.9)):
        h = f.parte(ref, x, 185.42, scritte="dx")
        f.porta(h.pin("1"))
    f.testo("L0: vite sul pannello posteriore, punto unico di massa (filo F0 al manicotto di IN L)", 25.4, 198.12, 1.5)
    f.testo("L1: torretta sul fondo (filo F1 da L0)", 25.4, 203.2, 1.5)

    # PWR_FLAG: le reti di alimentazione hanno solo piedini passivi, KiCad vuole sapere chi le pilota.
    # Quelli di 3V3A e 3V3D sono nel foglio del Seed, quello di VG nel foglio del preamp: l'ERC di KiCad
    # vuole il PWR_FLAG in un foglio dove la rete tocca un componente.
    f.testo("Sorgenti delle reti di alimentazione (per l'ERC)", 254.0, 165.1, 1.8)
    for i, nome in enumerate(("GND", "VA", "VB", "VIN_S")):
        x, y = 256.54 + i * 15.24, 182.88
        f.filo((x, y), (x + 5.08, y))
        f.alim("PWR_FLAG", (x + 5.08, y))
        f.filo((x, y), (x, y + 5.08 if nome == "GND" else y - 5.08))
        f.alim(nome, (x, y + 5.08 if nome == "GND" else y - 5.08))
