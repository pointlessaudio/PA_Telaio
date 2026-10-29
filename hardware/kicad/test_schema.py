"""
Test di mutazione della verifica dello schema disegnato: si rovina un foglio alla volta (copia di tutto in una
cartella temporanea) e verifica_schema.py deve accorgersene. Ogni riga deve dire RILEVATO.

    python3 test_schema.py
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

import verifica_schema as V

QUI = Path(__file__).resolve().parent


def leggi(nome):
    return (QUI / f"{nome}.kicad_sch").read_text()


def prima_etichetta(testo, vecchio, nuovo):
    t, n = re.subn(r'\(global_label "' + re.escape(vecchio) + '"', f'(global_label "{nuovo}"', testo, count=1)
    assert n == 1, vecchio
    return t


def scambia_etichette(testo, a, b):
    testo = prima_etichetta(testo, a, "__TMP__")
    testo = prima_etichetta(testo, b, a)
    return prima_etichetta(testo, "__TMP__", b)


def sposta_simbolo(testo, ref):
    """sposta di 2,54 mm in x il simbolo con quel riferimento"""
    blocchi = list(re.finditer(r'\(symbol \(lib_id "[^"]+"\) \(at ([-\d.]+) ([-\d.]+) (\d+)\)', testo))
    for i, m in enumerate(blocchi):
        fine = blocchi[i + 1].start() if i + 1 < len(blocchi) else len(testo)
        if f'(reference "{ref}")' in testo[m.start():fine]:
            x = float(m.group(1)) + 2.54
            return testo[:m.start(1)] + f"{x:.3f}" + testo[m.end(1):]
    raise AssertionError(ref)


def togli_primo(testo, prefisso):
    righe = testo.split("\n")
    i = next(k for k, r in enumerate(righe) if r.startswith(prefisso))
    return "\n".join(righe[:i] + righe[i + 1:])


def massa_in_vb(testo):
    """il primo simbolo di massa diventa VB"""
    m = re.search(r'\(symbol \(lib_id "PA:GND"\)', testo)
    assert m
    fine = testo.index("(instances", m.start())
    blocco = testo[m.start():fine].replace('(lib_id "PA:GND")', '(lib_id "PA:VB")').replace('"Value" "GND"', '"Value" "VB"')
    if '(symbol "PA:VB"' not in testo:            # il foglio deve avere anche il simbolo di libreria
        lib = re.search(r'\(symbol "PA:VB".*?\n\)', (QUI / "f01_alimentazione.kicad_sch").read_text(), re.S)
        testo = testo.replace("(lib_symbols\n", "(lib_symbols\n" + lib.group(0)[:-2] + ")\n", 1)
    return testo[:m.start()] + blocco + testo[fine:]


MUTAZIONI = [
    ("f04_buffer_ingresso", "etichetta SIN1 rinominata SIN2", lambda t: prima_etichetta(t, "SIN1", "SIN2")),
    ("f02_ingressi", "JINL e JINR scambiate", lambda t: scambia_etichette(t, "JINL", "JINR")),
    ("f01_alimentazione", "R1 spostata fuori dai suoi fili", lambda t: sposta_simbolo(t, "R1")),
    ("f05_buffer_uscita", "un filo tolto", lambda t: togli_primo(t, "(wire ")),
    ("f07_seed", "segno di non collegato tolto", lambda t: togli_primo(t, "(no_connect ")),
    ("f04_buffer_ingresso", "una massa diventa VB", massa_in_vb),
]


def main():
    err, voci, _ = V.verifica(QUI / "pa-telaio.kicad_sch")
    if err or any(v[0] == "error" for v in voci):
        print("CONTROLLO FALLITO: lo schema intatto non passa la verifica")
        return 1
    print("controllo: schema intatto OK")
    falliti = 0
    for foglio, nome, mut in MUTAZIONI:
        with tempfile.TemporaryDirectory() as tmp:
            for p in list(QUI.glob("*.kicad_sch")) + [QUI / "PA.kicad_sym", QUI / "sym-lib-table", QUI / "pa-telaio.kicad_pro"]:
                shutil.copy(p, Path(tmp) / p.name)
            vecchio = leggi(foglio)
            nuovo = mut(vecchio)
            assert nuovo != vecchio, f"{nome}: la mutazione non ha cambiato niente"
            (Path(tmp) / f"{foglio}.kicad_sch").write_text(nuovo)
            err, voci, _ = V.verifica(Path(tmp) / "pa-telaio.kicad_sch")
            tot = err + [f"ERC {v[1]}: {v[2]}" for v in voci if v[0] == "error"]
            if tot:
                print(f"{nome}: RILEVATO ({len(tot)}) {tot[:2]}")
            else:
                print(f"{nome}: NON RILEVATO")
                falliti += 1
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())
