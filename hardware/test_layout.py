import importlib, sys, re
src = open(__import__("os").path.join(__import__("os").path.dirname(__file__), "layout.py")).read()
tests = {
 "togli taglio sotto Seed": src.replace("    CUTS.add((6, y))    # tra", "    pass  # tra"),
 "R7 sulla riga sbagliata": src.replace('(7, 32, "INLF", "")', '(7, 33, "INLF", "")'),
 "togli ponticello J9 (VB)": src.replace('("J9", (28, 26), (28, 35), "VB", False),', ''),
 "C12 su net sbagliata nello schema": src.replace('"OLC": {"C12.+", "R11"},', '"OLC": {"C12.+", "R11", "R13"},'),
 "OLED rimesso sui vecchi pin (piazzola SCL in (0,13))": src.replace('("SCL", (0, 11), "SCL", "OLED SCL"),', '("SCL", (0, 13), "SCL", "OLED SCL"),'),
 "C0G spostato sulla riga sbagliata": src.replace('(1, 31, "JINL", "")', '(1, 32, "JINL", "")'),
 "fori di fissaggio vecchi (2,44) e (27,44)": src.replace("FORI_FISSAGGIO = [(1, 1), (28, 1), (7, 43), (28, 37)]",
                                                          "FORI_FISSAGGIO = [(1, 1), (28, 1), (2, 44), (27, 44)]"),
 "foro di fissaggio che spezza la striscia 37": src.replace("FORI_FISSAGGIO = [(1, 1), (28, 1), (7, 43), (28, 37)]",
                                                            "FORI_FISSAGGIO = [(1, 1), (28, 1), (7, 43), (20, 37)]"),
}
for name, s in tests.items():
    ns = {}
    try:
        exec(compile(s, "x", "exec"), ns)
        errs = ns["errors"]
    except AssertionError as e:
        errs = ["assert"]
    print(f"{name}: {'RILEVATO' if errs else 'NON rilevato'} ({len(errs)}) {errs[:2]}")
