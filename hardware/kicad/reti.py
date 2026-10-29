"""
Aiuto per disegnare un foglio: per ogni piedino dei componenti indicati, la rete e gli altri piedini della stessa
rete (con il foglio dove stanno, se già piazzati).

    python3 reti.py R1 C1 U1
"""
import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
comp = json.loads((QUI / "componenti.json").read_text())["componenti"]
reti = json.loads((QUI / "reti_attese.json").read_text())["reti"]
for ref in sys.argv[1:]:
    c = comp[ref]
    print(f"{ref}  {c['sim']}  {c['val']}  (layout {c['layout']}, blocco {c['blocco']})")
    for p, n in c["pins"].items():
        altri = [f"{r}.{q}" for r, q in reti.get(n, []) if r != ref or q != p]
        print(f"   pin {p:>4}: {n:<12} {' '.join(altri[:14])}{' ...' if len(altri) > 14 else ''}")
