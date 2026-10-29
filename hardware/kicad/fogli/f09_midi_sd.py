"""Foglio 9: scheda MIDI (ingresso con optoisolatore, uscita) e microSD."""
FILE = "f09_midi_sd"
TITOLO = "MIDI e microSD"
G = 2.54


def disegna(f):
    f.testo("MIDI e microSD", 25.4, 25.4, 4, True)
    f.testo("Jack MIDI TRS tipo A; la microSD parla SDMMC a 1 bit. Tutti i segnali del Seed arrivano per etichetta.", 25.4, 33.02, 1.8)

    # ================================================================ MIDI IN
    f.testo("MIDI IN", 38.1, 68.58, 2.4, True)
    f.testo("Anello = corrente dal 220 ohm al LED dell'optoisolatore, punta = ritorno; D301 lo protegge dalle inversioni", 38.1, 73.66, 1.5)
    j = f.parte("J207", 50.8, 101.6)
    r1 = f.parte("R301", 76.2, 101.6)
    d1 = f.parte("D301", 101.6, 101.6, rot=270, scritte="sx")
    u = f.parte("U301", 170.18, 104.14)
    c2 = f.parte("C302", 66.04, 109.22, rot=270)
    # anello -> 220 -> anodo (linea in basso); punta -> catodo (linea in alto, scende davanti all'opto)
    f.filo(j.pin("R"), r1.pin("1"))
    f.filo(r1.pin("2"), (88.9, 101.6), (88.9, 106.68), (124.46, 106.68), (124.46, 101.6), u.pin("1"))
    f.filo(j.pin("T"), (63.5, j.pin("T").y), (63.5, 96.52), (111.76, 96.52), (111.76, 104.14), u.pin("2"))
    f.filo(j.pin("S"), c2.pin("1"))
    f.porta(c2.pin("2"))
    f.nc(u.pin("3"))
    # alimentazione e uscita dell'opto
    f.filo(u.pin("6"), (190.5, 101.6), (190.5, 91.44), (213.36, 91.44))
    f.alim("3V3D", (190.5, 91.44))
    r2 = f.parte("R302", 200.66, 99.06, rot=90)
    f.filo(r2.pin("2"), (200.66, 91.44))
    c1 = f.parte("C301", 213.36, 96.52, rot=270)
    f.porta(c1.pin("2"))
    f.filo(u.pin("4"), r2.pin("1"))
    f.filo(r2.pin("1"), (200.66, 109.22))
    f.etichetta("MIDI_RX", (200.66, 109.22), "giu")
    f.porta(u.pin("5"))
    f.testo("D301 in antiparallelo al LED dell'opto", 88.9, 116.84, 1.5)
    f.testo("R302 tira su l'uscita open collector", 190.5, 127.0, 1.5)

    # ================================================================ MIDI OUT
    f.testo("MIDI OUT", 266.7, 68.58, 2.4, True)
    f.testo("Punta = MIDI_TX, anello = 3V3D, ciascuno con 10 ohm in serie", 266.7, 73.66, 1.5)
    jo = f.parte("J208", 312.42, 101.6, rot=180, scritte="dx")
    r4 = f.parte("R304", 289.56, 101.6)
    r3 = f.parte("R303", 289.56, 114.3)
    f.filo(jo.pin("S"), (299.72, jo.pin("S").y), (299.72, 83.82), (294.64, 83.82))
    f.alim("GND", (294.64, 83.82))
    f.filo(jo.pin("R"), r4.pin("2"))
    f.filo(r4.pin("1"), (284.48, 96.52))
    f.alim("3V3D", (284.48, 96.52))
    f.filo(jo.pin("T"), (299.72, jo.pin("T").y), (299.72, 114.3), r3.pin("2"))
    f.porta(r3.pin("1"))

    # ================================================================ microSD
    f.testo("microSD", 38.1, 177.8, 2.4, True)
    f.testo("SDMMC a 1 bit: D0, CMD e CK vanno al Seed;", 38.1, 182.88, 1.5)
    f.testo("DAT1-DAT3 e le altre linee tirate a 3V3D con 47 k", 38.1, 187.96, 1.5)
    cx, cy = 190.5, 215.9
    s = f.parte("J209", cx, cy)
    xp = cx - 10.16
    rows = {"7": (-15.24, 175.26, "R305"), "8": (-7.62, 170.18, "R307"), "1": (0.0, None, "R308"),
            "2": (7.62, 170.18, "R309"), "3": (15.24, 175.26, "R306")}
    xb = 149.86
    for num, (dy, xj, ref) in rows.items():
        yr = cy + dy
        r = f.parte(ref, 154.94, yr, rot=180, scritte="sx")
        p = s.pin(num)
        if xj is None:
            f.filo(p, r.pin("1"))
        else:
            f.filo(p, (xj, p.y), (xj, yr), r.pin("1"))
    f.etichetta("SD_D0", (175.26, cy - 15.24), "dx")
    f.etichetta("SD_CMD", (175.26, cy + 15.24), "dx")
    f.filo((xb, cy - 15.24), (xb, cy + 15.24))
    f.filo((xb, cy - 15.24), (xb, cy - 20.32))
    f.alim("3V3D", (xb, cy - 20.32))
    f.porta(s.pin("4"))
    f.porta(s.pin("5"))
    f.porta(s.pin("6"))
