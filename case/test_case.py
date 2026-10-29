# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0"]
# ///
"""
Test di mutazione del case: a ogni difetto iniettato la verifica di case.py deve dire
RILEVATO. Se una riga dice "NON rilevato", la verifica è cieca su quel difetto.

    uv run test_case.py            # qualche minuto: ricostruisce il case per ogni mutazione
    uv run test_case.py veroboard  # solo le mutazioni col testo indicato nel nome
"""
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
SORGENTE = (QUI / "case.py").read_text()

MUTAZIONI = {
    "pot spostato sopra il Seed": ("POT_X = (132.0, 160.0, 188.0)", "POT_X = (30.0, 160.0, 188.0)"),
    "jack del retro troppo alti": ("Z_RETRO = 18.5", "Z_RETRO = 33.0"),
    "foro dei tasti più stretto del cappuccio": ("foro=9.7, pila", "foro=8.6, pila"),
    "cappuccio dei tasti più largo del foro": ("TASTO = dict(cappuccio=9.5,", "TASTO = dict(cappuccio=12.0,"),
    "cappuccio dei tasti non sporge dal pannello": ("pila=11.5, sporgenza=1.8", "pila=11.5, sporgenza=0.4"),
    "cappuccio dei tasti sul corpo del tasto": ("pila=11.5, sporgenza", "pila=10.6, sporgenza"),
    "veroboard spinta sulla colonna posteriore": ("Y_SCHEDA_DIETRO = 95.0", "Y_SCHEDA_DIETRO = 118.0"),
    "USB-C lontana dalla parete": ("USB_GIOCO = 0.6", "USB_GIOCO = 3.0"),
    "case più basso di 4 mm": ("HF, HB = 25.0, 47.0", "HF, HB = 21.0, 43.0"),
    "logo fuori dal pannello": ("LOGO_C, LOGO_W, LOGO_PROF = (117.5, 26.0)", "LOGO_C, LOGO_W, LOGO_PROF = (117.5, 260.0)"),
    "footswitch sopra la scheda tasti": ("FS_C = (182.0, 26.0)", "FS_C = (60.0, 26.0)"),
    "footswitch attaccato ai pot": ("FS_C = (182.0, 26.0)", "FS_C = (182.0, 40.0)"),
    "finestra OLED più piccola dell'area visibile": (
        '    va_w, va_h = OLED["va"][0] + 0.2, OLED["va"][1] + 0.2\n    p -= sul_top(*OLED_C)',
        '    va_w, va_h = 20.0, 10.0\n    p -= sul_top(*OLED_C)'),
    "orecchie staccate dal bordo della vasca": ("ORECCHIE_DENTRO = 0.5", "ORECCHIE_DENTRO = -0.5"),
    "orecchie piene sopra le sedi delle viti": (
        "    return o - prisma(ORECCHIE_DENTRO, -1.0, ORECCHIE_H + 1.0)", "    return o"),
    "logo della variante servizio troppo stretto": ("LOGO_SERVIZIO = (48.0, 1.0)", "LOGO_SERVIZIO = (40.0, 1.0)"),
    # fori di fissaggio della veroboard: (2,44) taglia la striscia della massa e sta sul bordo; (29,38) sta sul
    # bordo; (2,37) è libero e non spezza niente, ma la testa della vite finisce su C13
    "foro di fissaggio sulla striscia della massa": (
        "FORI_FISSAGGIO = L.FORI_FISSAGGIO", "FORI_FISSAGGIO = [(1, 1), (28, 1), (2, 44), (28, 37)]"),
    "foro di fissaggio sul bordo della veroboard": (
        "FORI_FISSAGGIO = L.FORI_FISSAGGIO", "FORI_FISSAGGIO = [(1, 1), (28, 1), (7, 43), (29, 38)]"),
    "testa della vite della veroboard su un componente": (
        "FORI_FISSAGGIO = L.FORI_FISSAGGIO", "FORI_FISSAGGIO = [(1, 1), (28, 1), (2, 37), (28, 37)]"),
    # preamp d'ingresso: GAIN, PRE e volume della schedina
    "GAIN sopra il jack IN L": ("GAIN_X, GAIN_Z = 109.0, 33.5", "GAIN_X, GAIN_Z = 125.0, 19.0"),
    "PRE troppo vicino al jack IN L": ("PRE_X, PRE_Z = 109.0, Z_RETRO", "PRE_X, PRE_Z = 118.0, Z_RETRO"),
    "schedina preamp sulla veroboard": ("SCHEDINA = dict(x=(122.0, 184.0)", "SCHEDINA = dict(x=(60.0, 122.0)"),
    "schedina preamp contro i jack dietro": ("y=(51.0, 98.0), alt=17.5", "y=(60.0, 107.0), alt=17.5"),
    "schedina preamp troppo alta sotto i pot": ("y=(51.0, 98.0), alt=17.5", "y=(51.0, 98.0), alt=30.0"),
    "vite di massa L0 sul jack IN R": ('MASSA_L0 = ("massa L0", 135.5, 32.0', 'MASSA_L0 = ("massa L0", 146.0, 22.0'),
    "torretta di massa L1 sotto la veroboard": ("MASSA_L1 = dict(x=109.5, y=101.5", "MASSA_L1 = dict(x=60.0, y=60.0"),
    # jack DC Lumberg (foro a D) e microSD sul pannello posteriore
    "foro DC senza piatto (boccola libera di ruotare)": ('if "piatto" in t:', 'if "piatto_x" in t:'),
    "foro DC con piatti troppo stretti per la boccola": ('s = s & Box(t["piatto"] + TOL_FORI, 40, 40)',
                                                        's = s & Box(t["piatto"] - 1.0, 40, 40)'),
    "foro DC tondo da 11 (vecchio) con boccola da 12,8": ('"dc": dict(foro=12.8, piatto=11.8, flangia=16.0',
                                                         '"dc": dict(foro=12.8, piatto=12.8, flangia=16.0'),
    "flangia DC Ø 16 contro il bordo del pannello": ('("DC 9V", 22.0, "dc")', '("DC 9V", 12.0, "dc")'),
    "fessura microSD chiusa": ('fessura=(13.0, 2.6), pcb=(15.0', 'fessura=(10.0, 2.6), pcb=(15.0'),
    "fessura microSD collidente con il foro del DC": ("SD = dict(x=23.0, z=31.5", "SD = dict(x=23.0, z=28.0"),
    "microSD contro la scheda MIDI": ("SD = dict(x=23.0, z=31.5", "SD = dict(x=44.0, z=31.5"),
    "microSD lontana dai pad D4-D6": ("SD = dict(x=23.0, z=31.5", "SD = dict(x=196.0, z=31.5"),
    "microSD troppo alta sotto il pannello superiore": ("SD = dict(x=23.0, z=31.5", "SD = dict(x=23.0, z=41.0"),
}

FILTRO = sys.argv[1] if len(sys.argv) > 1 else ""
for nome, (prima, dopo) in MUTAZIONI.items():
    if FILTRO not in nome:
        continue
    assert SORGENTE.count(prima) == 1, f"{nome}: testo da mutare non trovato"
    ns = {"__file__": str(QUI / "case.py"), "__name__": "mutante"}
    exec(compile(SORGENTE.replace(prima, dopo), "case_mutante", "exec"), ns)
    pezzi = {"vasca": ns["vasca"](), "pannello superiore": ns["pannello_superiore"](),
             "pannello posteriore": ns["pannello_posteriore"]()}
    for i, s in enumerate(ns["staffe_in_posizione"]()):
        pezzi[f"staffa OLED {i + 1}"] = s
    errori, _ = ns["verifica"](pezzi, ns["componenti"]())
    if "servizio" in nome:                      # la variante per il servizio ha un controllo suo
        errori += ns["verifica_servizio"](ns["pannello_superiore"](logo=ns["LOGO_SERVIZIO"]))[0]
    esito = "RILEVATO" if errori else "NON rilevato"
    print(f"{nome}: {esito} ({len(errori)}) {errori[:2]}", flush=True)
