"""
Scrive lo schema disegnato di PA-TELAIO: un foglio radice (indice) e un foglio A3 per blocco, uno per ogni modulo
in fogli/ (fNN_nome.py, con FILE, TITOLO e disegna(f)). Simboli in PA.kicad_sym, registrati in sym-lib-table.

    python3 disegna_schema.py            # tutti i fogli; "OK ..." se ogni foglio passa i suoi controlli
    python3 disegna_schema.py f03        # solo i fogli il cui nome comincia così (gli altri restano fuori dalla radice)
    python3 disegna_schema.py --out /tmp/x f01 f03    # scrive tutto in un'altra cartella (prove in parallelo)

Dopo: python3 verifica_schema.py (netlist di KiCad contro reti_attese.json, ERC).
"""
import importlib.util
import json
import sys
from pathlib import Path

import disegno as D
from genera_uuid import uid

QUI = Path(__file__).resolve().parent
NOME = "pa-telaio"


def carica_fogli(filtro):
    mods = []
    for p in sorted((QUI / "fogli").glob("f[0-9][0-9]_*.py")):
        if filtro and not any(p.stem.startswith(x) for x in filtro):
            continue
        spec = importlib.util.spec_from_file_location(p.stem, p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        mods.append(m)
    return mods


def radice(fogli, radice_uuid):
    out = [f'(kicad_sch (version 20231120) (generator "pa_telaio_disegna_schema") (generator_version "8.0") '
           f'(uuid "{radice_uuid}") (paper "A3")',
           '(title_block (title "PA-TELAIO: indice dei fogli") '
           '(comment 1 "generato da hardware/kicad/disegna_schema.py: non modificare a mano") '
           '(comment 2 "reti verificate contro layout.py, layout_preamp.py, cablaggio.py"))',
           "(lib_symbols)",
           '(text "PA-TELAIO: schema elettrico" (exclude_from_sim no) (at 25.4 30.48 0) (effects (font (size 5 5) bold) (justify left bottom)) (uuid "' + uid("t-radice") + '"))',
           '(text "Strumento da tavolo su Daisy Seed3. Un foglio per blocco; fra un foglio e l\'altro le reti passano per etichette globali con lo stesso nome." (exclude_from_sim no) (at 25.4 38.1 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "' + uid("t-radice2") + '"))']
    for i, f in enumerate(fogli):
        col, riga = i % 3, i // 3
        x, y = 25.4 + col * 127.0, 55.88 + riga * 50.8
        su = uid("sheet", f.file)
        out.append(f'(sheet (at {x} {y}) (size 101.6 30.48) (fields_autoplaced yes) (stroke (width 0.1524) (type solid)) '
                   f'(fill (color 0 0 0 0.0000)) (uuid "{su}")\n'
                   f'  (property "Sheetname" "{f.titolo}" (at {x} {y - 0.7:.2f} 0) (effects (font (size 2 2)) (justify left bottom)))\n'
                   f'  (property "Sheetfile" "{f.file}.kicad_sch" (at {x} {y + 31.1:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))\n'
                   f'  (instances (project "{NOME}" (path "/{radice_uuid}" (page "{i + 2}")))))')
        out.append(f'(text "pagina {i + 2}" (exclude_from_sim no) (at {x + 5.08} {y + 17.78} 0) '
                   f'(effects (font (size 3 3)) (justify left bottom)) (uuid "{uid("t-pag", f.file)}"))')
    out.append('(sheet_instances (path "/" (page "1")))')
    out.append(")")
    return "\n".join(out) + "\n"


def main():
    args = sys.argv[1:]
    out = QUI
    if args and args[0] == "--out":
        out = Path(args[1]).resolve()
        out.mkdir(parents=True, exist_ok=True)
        args = args[2:]
    filtro = args
    mods = carica_fogli(filtro)
    fogli, errori = [], 0
    for m in mods:
        f = D.Foglio(m.FILE, m.TITOLO)
        m.disegna(f)
        err = f.controlla()
        fogli.append(f)
        stato = "OK" if not err else f"{len(err)} ERRORI"
        print(f"{m.FILE}: {len(f.parti)} simboli, {len(f.fili)} fili, {len(f.etichette)} etichette: {stato}")
        for e in err:
            print("   -", e)
        errori += len(err)
    # ogni unità di ogni componente piazzata una volta sola
    piazzate = {}
    for f in fogli:
        for p in f.parti:
            if not p.power:
                piazzate.setdefault((p.ref, p.unit), []).append(f.file)
    for k, v in piazzate.items():
        if len(v) > 1:
            print(f"ERRORE: {k[0]} unità {k[1]} piazzata {len(v)} volte ({v})")
            errori += 1
    mancanti = [f"{r}/{u}" for r, c in D.COMP.items() for u in D.SIMB[c["sim"]]["units"] if (r, u) not in piazzate]
    ru = uid("radice")
    for f in fogli:
        (out / f"{f.file}.kicad_sch").write_text(f.kicad(ru, uid("sheet", f.file), 0))
    (out / f"{NOME}.kicad_sch").write_text(radice(fogli, ru))
    (out / "PA.kicad_sym").write_text(
        '(kicad_symbol_lib (version 20231120) (generator "pa_telaio_disegna_schema") (generator_version "8.0")\n'
        + "\n".join(D.lib_symbol(n, D.SIMB[n], "") for n in sorted(D.SIMB)) + "\n)\n")
    (out / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n  (lib (name "PA")(type "KiCad")(uri "${KIPRJMOD}/PA.kicad_sym")(options "")'
        '(descr "simboli di PA-TELAIO, scritti da disegna_schema.py"))\n)\n')
    pro = out / f"{NOME}.kicad_pro"
    if not pro.exists():
        pro.write_text(json.dumps({"meta": {"filename": f"{NOME}.kicad_pro", "version": 1}}, indent=2) + "\n")
    (out / "piazzati.json").write_text(json.dumps(
        {f.file: sorted({f"{p.ref}:{n}" for p in f.parti if not p.power for n in p.pins}) for f in fogli}, indent=1))
    if mancanti and not filtro:
        print(f"componenti non ancora piazzati ({len(mancanti)}): {' '.join(mancanti)}")
    print("OK: fogli scritti" if not errori else f"scritti CON {errori} ERRORI")
    return 1 if errori or (mancanti and not filtro) else 0


if __name__ == "__main__":
    sys.exit(main())
