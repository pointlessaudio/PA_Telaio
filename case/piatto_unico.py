# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["trimesh", "numpy"]
# ///
"""
Mette tutti i pezzi del case su un solo piatto, già orientati per la stampa, in un unico STL,
a 25 mm l'uno dall'altro (i brim da 10 mm non si toccano). Due colonne: a sinistra la vasca con le
orecchie e sopra il pannello superiore; a destra il pannello posteriore e le due staffe dell'OLED,
girati in piedi sul piatto. Poi si affetta come un pezzo solo:

    uv run piatto_unico.py
    python3 <percorso di a4-stand>/slice_chiron.py --stl "$PWD/out/piatto_unico.stl" --out "$PWD/stampa" --bed 85 --brim 10 --copies 1
"""
import math
from pathlib import Path

import trimesh

OUT = Path(__file__).resolve().parent / "out"
PIATTO = 400.0
DISTANZA = 25.0      # due brim da 10 mm (slice_chiron v4) più 5 di aria


def carica(nome):
    m = trimesh.load_mesh(OUT / f"{nome}.stl")
    m.apply_translation(-m.bounds[0])
    return m


def gira(m):
    """90 gradi sul piatto, poi di nuovo con l'angolo in basso a sinistra nell'origine"""
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
    m.apply_translation(-m.bounds[0])
    return m


def main():
    vasca, sopra, retro = carica("vasca"), carica("pannello_superiore"), carica("pannello_posteriore")
    staffa = carica("staffa_oled_x2")

    sopra.apply_translation([0, vasca.bounds[1][1] + DISTANZA, 0])
    x = vasca.bounds[1][0] + DISTANZA
    gira(retro).apply_translation([x, 0, 0])
    pezzi, y = [vasca, sopra, retro], retro.bounds[1][1] + DISTANZA
    for _ in range(2):
        s = gira(staffa.copy())
        s.apply_translation([x, y, 0])
        pezzi.append(s)
        x = s.bounds[1][0] + DISTANZA
    tutto = trimesh.util.concatenate(pezzi)
    ext = tutto.extents
    if ext[0] > PIATTO - 20 or ext[1] > PIATTO - 20:
        raise SystemExit(f"non entra: {ext[0]:.0f} x {ext[1]:.0f} mm")
    tutto.export(OUT / "piatto_unico.stl")
    print(f"piatto unico: {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm su {PIATTO:.0f} x {PIATTO:.0f}")


if __name__ == "__main__":
    main()
