#!/usr/bin/env python3
"""
Controllo dei G-code di case/stampa/, cioè dei file che vanno davvero sulla SD della Chiron.

Per ogni file: temperature di piatto e ugello come le comanda il G-code (M190/M109, non le chiavi
di configurazione), strati, dove Orca stampa sporgenze e ponti, da che strato gira davvero la
ventola (il primo strato che estrude dopo un M106 acceso: Orca lo scrive in coda allo strato
prima), se c'è il brim, e le impostazioni che contano per la presa col PETG.
Se non riconosce il formato (nessuna parete esterna trovata) si ferma: un controllo che non trova
niente perché legge il formato sbagliato direbbe "nessun ponte" su tutto.

    python3 gcode_check.py            # da case/
"""
import collections
import re
import sys
from pathlib import Path

STAMPA = Path(__file__).resolve().parent / "stampa"
CHIAVI = ("filament_type", "curr_bed_type", "brim_width", "close_fan_the_first_x_layers", "retraction_length",
          "layer_height", "fan_max_speed")


def leggi(path):
    layer, z, zs, tipi, conf = 0, 0.0, {}, collections.defaultdict(set), {}
    temp, ugello = {}, []          # primo valore di ogni comando; ugello: ogni M104/M109 acceso
    ventola_pendente, ventola = False, None
    for riga in path.open(errors="replace"):
        if riga.startswith(";LAYER_CHANGE"):
            layer += 1
        elif riga.startswith(";Z:"):
            z = float(riga[3:])
            zs[layer] = z
        elif riga.startswith(";TYPE:"):
            tipi[riga[6:].strip()].add(layer)
        elif m := re.match(r"(M140|M190|M104|M109)\s+S(\d+)", riga):
            temp.setdefault(m.group(1), int(m.group(2)))
            if m.group(1) in ("M104", "M109") and int(m.group(2)) > 0:
                ugello.append(int(m.group(2)))
        elif ventola is None and re.match(r"M106\s+S[1-9]", riga):
            ventola_pendente = True
        elif ventola_pendente and re.match(r"G1 .*E\d*\.?\d+", riga) and " E-" not in riga:
            ventola, ventola_pendente = (layer, z), False
        elif riga.startswith("; ") and " = " in riga:
            k, v = riga[2:].split(" = ", 1)
            if k.strip() in CHIAVI:
                conf[k.strip()] = v.strip()
    temp["ugello"] = ugello
    return layer, zs, tipi, ventola, conf, temp


def main():
    files = sorted(STAMPA.glob("*.gcode"))
    if not files:
        sys.exit("nessun G-code in case/stampa/")
    for f in files:
        layer, zs, tipi, ventola, conf, temp = leggi(f)
        if "Outer wall" not in tipi:
            sys.exit(f"{f.name}: nessuna parete esterna trovata, il formato del G-code è cambiato")
        z = lambda ls: sorted({round(zs.get(l, 0), 1) for l in ls})
        vent = f"dallo strato {ventola[0]} (z {ventola[1]:g})" if ventola else "mai (pezzo più basso)"
        print(f"{f.name}")
        u = temp["ugello"]
        print(f"  piatto {temp.get('M190', '?')} °C, ugello {u[0] if u else '?'} al primo strato "
              f"poi {u[-1] if u else '?'}; ventola {vent}; brim {'sì' if 'Brim' in tipi else 'NO'}")
        print(f"  {layer} strati; sporgenze a z {z(tipi.get('Overhang wall', set()))}; "
              f"ponti a z {z(tipi.get('Bridge', set()))}")
        print("  " + ", ".join(f"{k} {conf[k]}" for k in CHIAVI if k in conf))


if __name__ == "__main__":
    main()
