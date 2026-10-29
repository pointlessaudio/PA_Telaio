# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["build123d==0.13.0", "pillow"]
# ///
"""
Esporta dal modello di case.py quello che serve al render: i pezzi per gruppo di materiale
(STL in mm) e scena.json con posizioni e orientamenti di manopole, OLED, LED e jack.
Genera anche la schermata dell'OLED (128x64, ingrandita a pixel pieni).

    uv run render/esporta.py      # da case/
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI.parent))
sys.argv = [sys.argv[0]]
import case as C  # noqa: E402
from build123d import Compound, Pos, export_stl  # noqa: E402

PARTI = QUI / "parti"
PARTI.mkdir(exist_ok=True)

# valori dei sei parametri: la schermata e gli indici delle manopole dicono la stessa cosa
NOMI = (("mix", "size", "tono"), ("damp", "mod", "out"))
VALORI = ((0.06, 0.39, 0.72), (0.50, 0.94, 0.22))


def loc_info(loc):
    p, r = loc.position, loc.orientation
    return {"pos": [p.X, p.Y, p.Z], "rot": [r.X, r.Y, r.Z]}


def main():
    pezzi = {"vasca": C.vasca(), "pannello_superiore": C.pannello_superiore(),
             "pannello_posteriore": C.pannello_posteriore()}
    for n, s in pezzi.items():
        export_stl(s, str(PARTI / f"{n}.stl"))
    comp = {n: s for n, s, g in C.componenti()}
    gruppi = {
        "manopole": [s for n, s in comp.items() if n.startswith("manopola")],
        "cappucci": [s for n, s in comp.items() if n.startswith("cappuccio")],
        "led": [comp["LED"], comp["LED bypass"]],
        "oled_vetro": [comp["OLED vetro"]],
    }
    for g, lista in gruppi.items():
        export_stl(Compound(lista), str(PARTI / f"{g}.stl"))

    # posizioni: centro della faccia superiore di ogni manopola, con l'angolo dell'indice
    scena = {"alpha_gradi": C.math.degrees(C.ALPHA), "manopole": [], "retro": []}
    for fila, y in enumerate(C.POT_Y):
        for col, x in enumerate(C.POT_X):
            h = C.POT["dado"] + 0.5 + C.POT["manopola"][1]
            v = VALORI[fila][col]
            scena["manopole"].append({**loc_info(C.sul_top(x, y, h)), "d": C.POT["manopola"][0],
                                      "angolo": -135 + 270 * v})
    h = C.ENC["dado"] + 0.5 + C.ENC["manopola"][1]
    scena["encoder"] = {**loc_info(C.sul_top(*C.ENC_C, h)), "d": C.ENC["manopola"][0]}
    scena["oled"] = {**loc_info(C.sul_top(*C.OLED_C, C.W_VETRO_TOP + 0.02)), "aa": list(C.OLED["aa"])}
    for nome, x, tipo in C.RETRO:
        t = C.TIPI_RETRO[tipo]
        scena["retro"].append({"nome": nome, "pos": [x, C.Y_PANNELLO_EST, C.Z_RETRO], "tipo": tipo, "foro": t["foro"]})
    scena["usb"] = [C.T_WALL + C.USB_GIOCO, C.seed_y_centro(), C.usb_z()]
    scena["footswitch"] = {**loc_info(C.sul_top(*C.FS_C)), "dado": list(C.FS["dado"]), "attuatore": list(C.FS["attuatore"])}
    scena["pianta"] = [C.W, C.D]
    scena["piedini"] = [list(p) for p in C.PIEDINI]
    scena["piedino"] = [C.PIEDINO_D, C.PIEDINO_PROF]
    (QUI / "scena.json").write_text(json.dumps(scena, indent=1))

    # schermata dell'OLED: 128x64 bianco su nero, griglia 3x2 come i pot
    img = Image.new("L", (128, 64), 0)
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((2, 0), "catacomba", fill=255, font=font)
    d.line((2, 12, 125, 12), fill=255)
    for r in range(2):
        for c in range(3):
            x0, y0 = 2 + c * 42, 16 + r * 24
            d.text((x0, y0), NOMI[r][c], fill=255, font=font)
            d.rectangle((x0, y0 + 13, x0 + 37, y0 + 17), outline=255)
            w = int(round(36 * VALORI[r][c]))
            if w > 0:
                d.rectangle((x0 + 1, y0 + 14, x0 + w, y0 + 16), fill=255)
    img.resize((1024, 512), Image.NEAREST).save(QUI / "oled_schermata.png")
    print("parti:", sorted(p.name for p in PARTI.iterdir()))


if __name__ == "__main__":
    main()
