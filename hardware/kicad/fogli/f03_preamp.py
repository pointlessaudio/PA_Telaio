"""Foglio 3: preamp JFET della schedina, canale L sopra e canale R sotto (identici), partitore VG e
condensatori di alimentazione della schedina."""
FILE = "f03_preamp"
TITOLO = "Preamp JFET (schedina)"
G = 2.54

# distanze verticali rispetto alla riga di gate Y
Y_VAL = -6.35      # riga del drain
Y_SRC = 6.35       # riga del nodo di source
Y_VA = -21.59      # riga delle alimentazioni VA / VG sopra gli stadi


def canale(f, Y, r, lato):
    """r: dizionario dei riferimenti del canale; lato: "L" o "R"."""
    u = 1 if lato == "L" else 2
    # ---------------------------------------------------------------- stadio 1
    c1 = f.parte(r["C1"], 55.88, Y)
    f.porta(c1.pin("1"))                                    # ingresso in_X
    rg1 = f.parte(r["Rg1"], 66.04, Y - 5.08, rot=90)        # gate -> VG
    f.filo(rg1.pin("2"), (66.04, Y + Y_VA))
    f.alim("VG", (66.04, Y + Y_VA))
    rs1 = f.parte(r["Rst1"], 78.74, Y)
    f.filo(c1.pin("2"), rs1.pin("1"))
    q1 = f.parte(r["J1"], 96.52, Y - 1.27, scritte="dx")
    f.filo(rs1.pin("2"), q1.pin("3"))
    # drain
    xd = q1.pin("1").x
    rd1 = f.parte(r["Rd1"], xd, Y - 11.43, rot=90)
    f.filo(q1.pin("1"), rd1.pin("1"))
    f.filo(rd1.pin("2"), (xd, Y + Y_VA))
    f.alim("VA", (xd, Y + Y_VA))
    # source: Rs a massa, ramo GAIN
    ys = Y + Y_SRC
    f.filo(q1.pin("2"), (xd, ys))
    xs = 81.28
    rs = f.parte(r["Rs1"], xs, ys + 5.08, rot=270)
    f.filo((xs, ys), (xd, ys))
    f.filo((xs, ys), rs.pin("1"))
    f.porta(rs.pin("2"))
    xp, xa = 114.3, 129.54
    pot = f.parte("RV201", xp, ys + 5.08, rot=90, unit=u, scritte="sx")
    f.nc(pot.pin(f"1{lato}"))
    f.filo((xd, ys), (xa, ys))
    f.filo((xp, ys), pot.pin(f"3{lato}"))
    rp = f.parte(r["Rpar"], xa, ys + 5.08, rot=270)
    f.filo((xa, ys), rp.pin("1"))
    yg = ys + 12.7
    f.filo(pot.pin(f"2{lato}"), (pot.pin(f"2{lato}").x, yg), (xa, yg))
    f.filo(rp.pin("2"), (xa, yg))
    r220 = f.parte(r["R220"], xa, yg + 5.08, rot=270)
    f.filo((xa, yg), r220.pin("1"))
    cs = f.parte(r["Cs"], xa, yg + 20.32, rot=270)
    f.filo(r220.pin("2"), cs.pin("1"))
    f.porta(cs.pin("2"))
    # ---------------------------------------------------------------- stadio 2
    xc = xd + 10.16
    f.filo((xd, Y + Y_VAL), (xc, Y + Y_VAL), (xc, Y))
    c2 = f.parte(r["C2"], xc + 5.08, Y)
    f.filo((xc, Y), c2.pin("1"))
    rg2 = f.parte(r["Rg2"], c2.pin("2").x + 5.08, Y - 5.08, rot=90)
    f.filo(rg2.pin("2"), (rg2.x, Y + Y_VA))
    f.alim("VG", (rg2.x, Y + Y_VA))
    rs2 = f.parte(r["Rst2"], c2.pin("2").x + 15.24, Y)
    f.filo(c2.pin("2"), rs2.pin("1"))
    q2 = f.parte(r["J2"], 152.4, Y - 1.27, scritte="dx")
    f.filo(rs2.pin("2"), q2.pin("3"))
    xd2 = q2.pin("1").x
    rd2 = f.parte(r["Rd2"], xd2, Y - 11.43, rot=90)
    f.filo(q2.pin("1"), rd2.pin("1"))
    f.filo(rd2.pin("2"), (xd2, Y + Y_VA))
    f.alim("VA", (xd2, Y + Y_VA))
    rss = f.parte(r["Rs2"], xd2, Y + 3.81 + 5.08, rot=270)
    f.filo(q2.pin("2"), rss.pin("1"))
    f.porta(rss.pin("2"))
    # ---------------------------------------------------------------- uscita
    xc3 = xd2 + 10.16
    f.filo((xd2, Y + Y_VAL), (xc3, Y + Y_VAL), (xc3, Y))
    c3 = f.parte(r["C3"], xc3 + 5.08, Y)
    f.filo((xc3, Y), c3.pin("1"))
    xt = c3.pin("2").x + 10.16
    tr = f.parte(r["TR"], xt, Y, scritte="dx")
    f.filo(c3.pin("2"), tr.pin("1"))
    f.filo(tr.pin("3"), (tr.pin("3").x, Y + 5.08))
    f.alim("GND", (tr.pin("3").x, Y + 5.08))
    w = tr.pin("2")
    f.filo(w, (w.x, Y + 12.7), (w.x + 12.7, Y + 12.7))
    f.etichetta(w.rete, (w.x + 12.7, Y + 12.7), "dx")


def disegna(f):
    f.testo("Preamp JFET (schedina)", 25.4, 25.4, 4, True)
    f.testo("Due stadi J201 per canale. Primo stadio: il carattere (Rs 22k con ramo GAIN in parallelo). "
            "Secondo: quasi lineare, Rs 15k senza bypass.", 25.4, 33.02, 1.8)
    f.testo("Gate di tutti e quattro i JFET polarizzati a VG; uscita dal trimmer LEVEL verso il buffer.",
            25.4, 38.1, 1.8)

    L = dict(C1="C101", Rg1="R101", Rst1="R102", J1="Q101", Rd1="R103", Rs1="R104", Rpar="R205", R220="R105",
             Cs="C102", C2="C103", Rg2="R106", Rst2="R107", J2="Q102", Rd2="R108", Rs2="R109", C3="C104", TR="RV101")
    R = dict(C1="C105", Rg1="R110", Rst1="R111", J1="Q103", Rd1="R112", Rs1="R113", Rpar="R206", R220="R114",
             Cs="C106", C2="C107", Rg2="R115", Rst2="R116", J2="Q104", Rd2="R117", Rs2="R118", C3="C108", TR="RV102")
    yl, yr = 76.2, 177.8
    f.testo("Canale L", 25.4, yl - 30.48, 3, True)
    f.testo("Canale R", 25.4, yr - 30.48, 3, True)
    canale(f, yl, L, "L")
    canale(f, yr, R, "R")
    f.testo("Stadio 1", 96.52, yl - 30.48, 1.8, True)
    f.testo("Stadio 2", 152.4, yl - 30.48, 1.8, True)
    f.testo("Stadio 1", 96.52, yr - 30.48, 1.8, True)
    f.testo("Stadio 2", 152.4, yr - 30.48, 1.8, True)
    f.testo("GAIN: reostato (pot doppio RV201, gang L e R) con 47k in parallelo;", 160.02, yl + 40.64, 1.5)
    f.testo("il terzo capo di ogni gang e' libero (NC).", 160.02, yl + 43.18, 1.5)
    f.testo("J201: scelti con IDSS >= 0,5 mA.", 160.02, yl + 50.8, 1.5)
    f.testo("Punto di lavoro: drain fra 5,0 e 6,2 V sui 5 angoli del J201, nessun trimmer di drain.", 160.02, yl + 55.88, 1.5)
    f.testo("LEVEL a ~0,80 (si regola una volta)", 185.42, yl + 20.32, 1.5)
    f.testo("LEVEL a ~0,80 (si regola una volta)", 185.42, yr + 20.32, 1.5)

    # ---------------------------------------------------------------- polarizzazione VG e alimentazione della schedina
    x0 = 256.54
    f.testo("Polarizzazione dei gate (VG)", x0, 50.8, 2.4, True)
    f.testo("VG = 39k/10k da VA = 1,73 V, filtrata da 22u.", x0, 55.88, 1.5)
    r119 = f.parte("R119", x0 + 10.16, 73.66, rot=270)
    f.porta(r119.pin("1"))
    r120 = f.parte("R120", x0 + 10.16, 88.9, rot=270)
    f.filo(r119.pin("2"), r120.pin("1"))
    f.porta(r120.pin("2"))
    xn = x0 + 10.16
    yn = r120.pin("1").y
    c109 = f.parte("C109", x0 + 35.56, yn + 5.08, rot=270)
    f.filo((xn, yn), (x0 + 22.86, yn), (x0 + 35.56, yn), c109.pin("1"))
    f.porta(c109.pin("2"))
    f.filo((x0 + 22.86, yn), (x0 + 22.86, yn - 5.08))
    f.alim("VG", (x0 + 22.86, yn - 5.08))
    f.alim("PWR_FLAG", (x0 + 35.56, yn))           # VG la genera il partitore (per l'ERC)

    f.testo("Alimentazione della schedina", x0 + 66.04, 50.8, 2.4, True)
    f.testo("Disaccoppiamento di VA, vicino ai drain.", x0 + 66.04, 55.88, 1.5)
    xa = x0 + 76.2
    c110 = f.parte("C110", xa, 73.66, rot=270)
    c111 = f.parte("C111", xa + 15.24, 73.66, rot=270)
    f.filo(c110.pin("1"), c111.pin("1"))
    f.filo((xa + 7.62, c110.pin("1").y), (xa + 7.62, c110.pin("1").y - 5.08))
    f.alim("VA", (xa + 7.62, c110.pin("1").y - 5.08))
    f.porta(c110.pin("2"))
    f.porta(c111.pin("2"))
