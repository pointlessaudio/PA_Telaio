# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0", "numpy"]
# ///
"""
Test di mutazione di cablaggio.py: a ogni difetto iniettato la verifica deve dire RILEVATO.
Se una riga dice "NON rilevato", la verifica e' cieca su quel difetto.

    uv run test_cablaggio.py             # ricalcola il cablaggio per ogni mutazione (circa un minuto ciascuna)
    uv run test_cablaggio.py torre       # solo le mutazioni col testo indicato nel nome
"""
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
SORGENTE = (QUI / "cablaggio.py").read_text()

MUTAZIONI = {
    "filo verso una piazzola inesistente": (
        'w(f"OUT {s} a", f"VB:OUT {s}"', 'w(f"OUT {s} a", f"VB:OUT {s} X"'),
    "filo IN L sulla piazzola IN R (reti diverse)": (
        'f"PRE:COM {s}", f"VB:IN {s}", f"IN {s}", "schermato"', 'f"PRE:COM {s}", "VB:IN R", f"IN {s}", "schermato"'),
    "piazzola del layout senza filo (cursore A3 non cablato)": (
        'w(f"POT{i} W", f"VB:A{i - 1}", f"POT{i}:W"', 'w(f"POT{i} W", f"VB:A{(i - 1) % 3}", f"POT{i}:W"'),
    "schedina ruotata che allunga l'ingresso oltre la soglia": (
        "ORI_IN_USO = None", 'ORI_IN_USO = "D ruotata 180"'),
    "fessura della torre sul lato sbagliato (filo nella torre)": (
        "FS_LATO = -1", "FS_LATO = 1"),
    "soglia di distanza dai digitali non rispettata": (
        "DIST_MIN_ERR = 2.0", "DIST_MIN_ERR = 50.0"),
}

FILTRO = sys.argv[1] if len(sys.argv) > 1 else ""
for nome, (prima, dopo) in MUTAZIONI.items():
    if FILTRO not in nome:
        continue
    assert SORGENTE.count(prima) == 1, f"{nome}: testo da mutare non trovato ({SORGENTE.count(prima)} volte)"
    ns = {"__file__": str(QUI / "cablaggio.py"), "__name__": "mutante"}
    exec(compile(SORGENTE.replace(prima, dopo), "cablaggio_mutante", "exec"), ns)
    try:
        errori = ns["analisi"]()["err"]
    except Exception as e:                       # un filo che punta nel vuoto puo far saltare il calcolo: e' rilevato
        errori = [f"eccezione: {e!r}"]
    esito = "RILEVATO" if errori else "NON rilevato"
    print(f"{nome}: {esito} ({len(errori)}) {errori[:2]}", flush=True)
