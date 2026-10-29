"""
Test di mutazione della verifica dello schema: si rovina pa-telaio.kicad_sch in un punto alla volta (copia in
una cartella temporanea) e verifica_schema.py deve accorgersene. Ogni riga deve dire RILEVATO.

    python3 test_schema.py
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

import verifica_schema as V

QUI = Path(__file__).resolve().parent
SCH = (QUI / "pa-telaio.kicad_sch").read_text()


def etichetta(ref, pin):
    """riga dell'etichetta sul piedino ref.pin (uuid deterministico di genera_schema.py)"""
    import genera_uuid
    return genera_uuid.uid("l", ref, pin)


def sostituisci_rete(testo, uuid_l, nuova):
    pat = re.compile(r'\(label "([^"]*)"(.*?)\(uuid "' + uuid_l + r'"\)\)')
    m = pat.search(testo)
    assert m, uuid_l
    return testo[:m.start()] + f'(label "{nuova}"{m.group(2)}(uuid "{uuid_l}"))' + testo[m.end():], m.group(1)


def mut_rinomina(testo):            # il cursore del pot 1 finisce sulla rete del pot 2
    return sostituisci_rete(testo, etichetta("RV202", "2"), "POT2")[0]


def mut_scambia(testo):              # U1: ingressi - e + del primo operazionale invertiti
    a, b = etichetta("U1", "2"), etichetta("U1", "3")
    testo, ra = sostituisci_rete(testo, a, "__TMP__")
    testo, rb = sostituisci_rete(testo, b, ra)
    return sostituisci_rete(testo, a, rb)[0]


def mut_togli(testo):                # manca l'etichetta sul manicotto del jack OUT L
    u = etichetta("J203", "S")
    return re.sub(r'\(label "[^"]*"[^\n]*\(uuid "' + u + r'"\)\)\n', "", testo)


def mut_sposta(testo):               # R1 spostata di 2,54 mm: i suoi piedini non toccano più le etichette
    u = genera_uuid_uid("s", "R1")
    pat = re.compile(r'(\(symbol \(lib_id "PA:R"\) \(at )([-\d.]+)( [-\d.]+ 0\)[^\n]*\(uuid "' + u + r'"\))')
    m = pat.search(testo)
    assert m
    return testo[:m.start()] + m.group(1) + f"{float(m.group(2)) + 2.54:.3f}" + m.group(3) + testo[m.end():]


def mut_nc(testo):                   # tolto il segno di non collegato su un pin libero del Seed (D1)
    u = genera_uuid_uid("nc", "A1", "2")
    return re.sub(r'\(no_connect [^\n]*\(uuid "' + u + r'"\)\)\n', "", testo)


def mut_gnd(testo):                  # la massa della schedina preamp separata dalla massa della veroboard
    for ref, p in (("R104", "2"), ("R109", "2")):
        testo = sostituisci_rete(testo, etichetta(ref, p), "GND_SCHEDINA")[0]
    return testo


def genera_uuid_uid(*k):
    import genera_uuid
    return genera_uuid.uid(*k)


MUTAZIONI = [
    ("cursore del pot 1 sulla rete del pot 2", mut_rinomina),
    ("ingressi - e + di U1A scambiati", mut_scambia),
    ("etichetta mancante sul manicotto di OUT L", mut_togli),
    ("R1 spostata fuori dalle sue etichette", mut_sposta),
    ("pin libero del Seed senza segno di NC", mut_nc),
    ("massa di due resistenze della schedina staccata", mut_gnd),
]


def main():
    # controllo: lo schema intatto deve passare
    err, voci, _ = V.verifica(QUI / "pa-telaio.kicad_sch")
    if err or any(v[0] == "error" for v in voci):
        print("CONTROLLO FALLITO: lo schema intatto non passa la verifica")
        return 1
    print("controllo: schema intatto OK")
    falliti = 0
    with tempfile.TemporaryDirectory() as tmp:
        for f in ("sym-lib-table", "PA.kicad_sym", "pa-telaio.kicad_pro"):
            shutil.copy(QUI / f, Path(tmp) / f)
        for nome, mut in MUTAZIONI:
            p = Path(tmp) / "pa-telaio.kicad_sch"
            nuovo = mut(SCH)
            assert nuovo != SCH, f"{nome}: la mutazione non ha cambiato niente"
            p.write_text(nuovo)
            err, voci, _ = V.verifica(p)
            erc = [v for v in voci if v[0] == "error"]
            tot = err + [f"ERC {v[1]}: {v[2]}" for v in erc]
            if tot:
                print(f"{nome}: RILEVATO ({len(tot)}) {tot[:2]}")
            else:
                print(f"{nome}: NON RILEVATO")
                falliti += 1
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())
