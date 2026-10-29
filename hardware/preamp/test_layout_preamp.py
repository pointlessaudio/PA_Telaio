"""Test di mutazione di layout_preamp.py: ogni mutazione deve essere RILEVATA (errors non vuoto)."""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(QUI, "layout_preamp.py")).read()


def sost(a, b):
    assert a in src, f"stringa da mutare non trovata: {a}"
    return src.replace(a, b)


tests = {
    "tolgo il taglio sotto Rstop1 (G1A e G1 in corto)": sost("_CUT_R = [(3, 0), (6, 1), (4, 2),", "_CUT_R = [(3, 0), (6, 1),"),
    "tolgo il taglio tra S1 e S2": sost("(10, 3), (11, 4),", "(11, 4),"),
    "tolgo il taglio tra D1 e D2": sost("(10, 3), (11, 4),", "(10, 3),"),
    "tolgo il taglio tra IN e GNDc (corto ingresso-massa)": sost("[(3, 0), (6, 1),", "[(6, 1),"),
    "tolgo il taglio TOP/VG del LEVEL": sost("(18, 6), (21, 7)]", "(21, 7)]"),
    "tolgo il ponticello VG (aperto)": sost('    ("J4", (12, Y("L", 6)), (12, Y("R", 6)), "VG", "VG L -> VG R"),\n', ""),
    "tolgo il cavo del ritorno Cs1 R (aperto)": sost('    ("W2", (4, 17), (2, 8), "GND", "ritorno Cs1 R -> secondo foro dopo il pad GND"),\n', ""),
    "Rd1 sulla riga sbagliata (VA su D1 della striscia vicina)": sost('(9, y(4), n("d1"), "")', '(9, y(5), n("d1"), "")'),
    "Rs1 di nuovo sul ritorno del 47 uF (riga 0)": sost('(5, y(5), "GND", "")', '(5, y(0), "GND", "")'),
    "J201 con drain e source scambiati": sost('[(7, y(4), n("d1"), "D (1)"), (7, y(3), n("s1"), "S (2)")',
                                              '[(7, y(4), n("s1"), "D (1)"), (7, y(3), n("d1"), "S (2)")'),
    "valore Rd1 diverso dalla simulazione": sost('R("Rd1", c["Rd1"], "27k"', 'R("Rd1", 30e3, "27k"'),
    "220R del GAIN sul nodo sbagliato": sost('(5, y(1), n("gb"), "")', '(5, y(1), n("sp"), "")'),
    "trimmer LEVEL con cursore e capo alto scambiati": sost('[(22, y(6), n("top"), "1 alto"), (22, y(7), n("out"), "2 cursore")',
                                                           '[(22, y(6), n("out"), "1 alto"), (22, y(7), n("top"), "2 cursore")'),
    "C3 dimenticato (non c'e corrispondente alla sim)": sost('part(f"C3{s}", "film", c["C3"]', 'part(f"C3{s}", "film", 2e-6'),
    "Cs1 L e R sulla stessa striscia di ritorno (canali non distinti)": sost("y(0), n(\"gnc\")", "y(5), n(\"gnc\")"),
    "Cs1 L sulla massa di segnale (ritorno condiviso con Rs1)": sost('[(9, y(1), n("sp"), "+"), (9, y(0), n("gnc"), "-")]',
                                                                 '[(9, y(1), n("sp"), "+"), (9, y(5), "GND", "-")]'),
    "componente R sulla meta del canale L": sost('R("Rg1", c["Rg"], "1M", (2, y(2), n("g1a"), ""), (2, y(6), "VG", ""),',
                                                 'R("Rg1", c["Rg"], "1M", (2, y(2), n("g1a"), ""), (2, 20 - y(6), "VG", ""),'),
    "foro di fissaggio sul bordo": sost("FORI_FISSAGGIO = [(21, 1), (21, 16)]", "FORI_FISSAGGIO = [(23, 1), (21, 16)]"),
    "foro di fissaggio su un foro occupato (C3)": sost("FORI_FISSAGGIO = [(21, 1), (21, 16)]", "FORI_FISSAGGIO = [(20, 4), (21, 16)]"),
    "foro di fissaggio che spezza la striscia GND_a": sost("FORI_FISSAGGIO = [(21, 1), (21, 16)]", "FORI_FISSAGGIO = [(12, 5), (21, 16)]"),
    "foro di fissaggio contro il corpo del trimmer": sost("FORI_FISSAGGIO = [(21, 1), (21, 16)]", "FORI_FISSAGGIO = [(21, 1), (21, 9)]"),
    "100 uF spostato sotto il pad VA (corpo su una piazzola)": sost('[(4, 7, "VA", "+"), (4, 8, "GND", "-")],\n     vrect(4, 7, 8, 1, 1)',
                                                                    '[(1, 7, "VA", "+"), (1, 8, "GND", "-")],\n     vrect(1, 7, 8, 1, 1)'),
    "due componenti sovrapposti (Rvt su Rd1)": sost('part("Rvt", "res", c["Rvg_top"], "39k", [(10, 7, "VA", ""), (10, 6, "VG", "")], vrect(10, 6, 7),',
                                                    'part("Rvt", "res", c["Rvg_top"], "39k", [(9, 7, "VA", ""), (9, 6, "VG", "")], vrect(9, 6, 7),'),
    "elettrolitico troppo alto (14 mm)": sost('"2,5 mm", 11.5)', '"2,5 mm", 14.0)'),
}

for name, s in tests.items():
    ns = {"__name__": "mut", "__file__": os.path.join(QUI, "layout_preamp.py")}
    try:
        exec(compile(s, "x", "exec"), ns)
        errs = ns["errors"]
    except (AssertionError, KeyError, StopIteration, TypeError) as e:
        errs = [f"eccezione {type(e).__name__}"]
    print(f"{name}: {'RILEVATO' if errs else 'NON rilevato'} ({len(errs)}) {errs[:2]}")
