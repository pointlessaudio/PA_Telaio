"""Foglio 7: il Daisy Seed3 con tutti i suoi piedini. Ogni piedino usato esce con la sua rete, i liberi sono NC."""
FILE = "f07_seed"
TITOLO = "Daisy Seed3"
G = 2.54


def disegna(f):
    f.testo("Daisy Seed3", 25.4, 25.4, 4, True)
    f.testo("Il Seed visto dall'alto: piedini 1-20 a sinistra, 21-40 a destra. Ogni rete esce con la sua etichetta e si ritrova sugli altri fogli.",
            25.4, 33.02, 1.8)

    a = f.parte("A1", 203.2, 139.7)
    for n in range(1, 21):
        p = a.pin(n)
        f.nc(p) if p.rete == "NC" else f.porta(p)
    for n in range(40, 20, -1):
        p = a.pin(n)
        if p.rete == "NC":
            f.nc(p)
        elif n == 40:
            f.porta(p, lung=35.56)       # massa e 3V3D più lontane, per non toccare l'etichetta del piedino sotto
        elif n in (38, 21):
            f.porta(p, lung=20.32)
            f.alim("PWR_FLAG", (p.x + 17.78, p.y))     # 3V3A e 3V3D escono dal regolatore del Seed (per l'ERC)
        else:
            f.porta(p)

    # mappa delle funzioni
    x, y = 25.4, 60.96
    f.testo("Funzioni dei piedini", x, y, 2.4, True)
    righe = [
        "1  D0: tasto K1 e punta del jack del pedale",
        "4, 8, 9  ENC_A, ENC_B, ENC_SW: encoder e suo tasto, pull-up interni",
        "5, 6, 7  SD_D0, SD_CMD, SD_CK: microSD in SDMMC a 1 bit",
        "10  LED: LED dei tasti, con 1 k in serie",
        "11  FS2: tasto K2 e anello del jack del pedale",
        "12, 13  SCL, SDA: I2C dell'OLED",
        "14, 15  MIDI_TX, MIDI_RX: USART del MIDI",
        "16, 17  SIN1, SIN2: ingressi audio",
        "18, 19  SOUT1, SOUT2: uscite audio",
        "2, 3  non usati",
    ]
    for i, s in enumerate(righe):
        f.testo(s, x, y + 7.62 + i * 5.08, 1.8)

    x = 276.86
    f.testo("Lato destro", x, y, 2.4, True)
    righe = [
        "22-27  POT1-POT6: cursori dei sei potenziometri, ingressi ADC A0-A5",
        "21  3V3A: capo alto dei potenziometri",
        "38  3V3D: OLED, MIDI, microSD",
        "39  VIN_S: 9 V filtrato dal foglio Alimentazione",
        "20, 40  massa",
        "28-37  non usati",
    ]
    for i, s in enumerate(righe):
        f.testo(s, x, y + 7.62 + i * 5.08, 1.8)
