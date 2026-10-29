# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["trimesh", "shapely", "numpy", "networkx", "scipy", "rtree", "manifold3d"]
# ///
"""
Controllo di stampabilità sugli STL di case/out/, nell'orientamento in cui si stampano.

Per ogni pezzo:
- mesh chiusa e numero di corpi (un pezzo = un corpo);
- ingombro sul piatto e superficie d'appoggio al primo strato;
- strato per strato (come uno slicer): isole che nascono nel vuoto, cioè servirebbero supporti;
  materiale senza appoggio sotto (ponti e sbalzi) con la distanza massima dall'appoggio;
- pareti sottili: sotto 0,4 mm lo slicer le perde, fra 0,4 e 0,8 mm sono una linea sola.

    uv run stampabilita.py            # da case/
    uv run stampabilita.py --autotest # difetti costruiti apposta: ognuno deve essere RILEVATO
Deve finire con "OK ... stampabili senza supporti".
"""
import sys
from pathlib import Path

import numpy as np
import shapely
import trimesh
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union

OUT = Path(__file__).resolve().parent / "out"
STRATO = 0.2
PIATTO = (400.0, 400.0, 450.0)     # Anycubic Chiron
SBALZO_OK = STRATO                 # 45 gradi: ogni strato può sporgere di uno strato
PONTE_MAX = 7.5                    # distanza massima dall'appoggio (ponte da 15 mm in PETG)
SBALZO_MAX = 1.5                   # sporgenza massima di uno sbalzo senza appoggio su un lato solo
PERSO, FRAGILE = 0.4, 0.8          # pareti: perse dallo slicer / una linea sola
PEZZI = {
    "vasca": "vasca.stl",
    "pannello superiore": "pannello_superiore.stl",
    "pannello posteriore": "pannello_posteriore.stl",
    "staffa OLED": "staffa_oled_x2.stl",
    "prova superiore": "prova_superiore.stl",
    "prova posteriore": "prova_posteriore.stl",
}


def strati(mesh):
    zs = np.arange(STRATO / 2, mesh.bounds[1][2], STRATO)
    sezioni = mesh.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=zs)
    out = []
    for s in sezioni:
        if s is None or len(s.polygons_full) == 0:
            out.append(Polygon())
        else:
            out.append(unary_union([p.buffer(0) for p in s.polygons_full]))
    return zs, out


def pezzi_di(g):
    if g.is_empty:
        return []
    return list(g.geoms) if isinstance(g, MultiPolygon) else [g] if isinstance(g, Polygon) else [
        x for x in getattr(g, "geoms", []) if isinstance(x, Polygon)]


def distanza_max(pezzo, appoggio):
    """distanza massima di un punto del pezzo dal materiale che lo regge (campionamento)"""
    minx, miny, maxx, maxy = pezzo.bounds
    passo = max(0.15, min(maxx - minx, maxy - miny) / 12)
    xs, ys = np.meshgrid(np.arange(minx, maxx + passo, passo), np.arange(miny, maxy + passo, passo))
    punti = shapely.points(xs.ravel(), ys.ravel())
    dentro = punti[shapely.contains(pezzo, punti)]
    bordo = shapely.points(np.array(pezzo.exterior.coords))
    tutti = np.concatenate([dentro, bordo])
    d = shapely.distance(tutti, appoggio)
    i = int(np.argmax(d))
    return float(d[i]), (tutti[i].x, tutti[i].y)


def analizza(nome, mesh):
    righe, errori, avvisi = [], [], []
    ext = mesh.extents
    corpi = mesh.split(only_watertight=False)
    righe.append(f"{ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm, {len(mesh.faces)} triangoli, "
                 f"{'chiusa' if mesh.is_watertight else 'NON chiusa'}, {len(corpi)} corpo/i")
    if not mesh.is_watertight:
        errori.append("mesh non chiusa: lo slicer può riempire male")
    if nome != "staffa OLED" and len(corpi) != 1:
        errori.append(f"{len(corpi)} corpi separati: qualcosa galleggia o non è attaccato")
    if any(e > p for e, p in zip(ext, PIATTO)):
        errori.append("non entra nel piatto della Chiron")

    zs, layers = strati(mesh)
    righe.append(f"appoggio al primo strato: {layers[0].area:.0f} mm² su un ingombro di {ext[0] * ext[1]:.0f}")

    isole, ponti = [], []
    sottili_persi, sottili_fragili = [], []
    for i in range(len(layers)):
        cur = layers[i]
        # pareti sottili: apertura morfologica
        for soglia, lista in ((PERSO, sottili_persi), (FRAGILE, sottili_fragili)):
            r = soglia / 2
            resto = cur.difference(cur.buffer(-r, join_style=2).buffer(r, join_style=2))
            for p in pezzi_di(resto):
                if p.area > (0.02 if soglia == PERSO else 0.2):
                    c = p.representative_point()
                    lista.append((zs[i], p.area, (c.x, c.y)))
        if i == 0:
            continue
        prev = layers[i - 1]
        appoggio = prev.buffer(SBALZO_OK)
        libero = cur.difference(appoggio)
        for p in pezzi_di(libero):
            if p.area < 0.05:
                continue
            # la parte di strato che lo contiene tocca lo strato sotto? allora è ponte/sbalzo, se no isola
            madre = [q for q in pezzi_di(cur) if q.intersects(p)]
            ancorato = any(q.intersects(prev) for q in madre)
            if not ancorato:
                c = p.representative_point()
                isole.append((zs[i], p.area, (c.x, c.y)))
                continue
            dmax, dove = distanza_max(p, appoggio)
            # ponte (appoggiato su due lati o tutto intorno) o sbalzo (un lato solo)?
            tocco = p.exterior.intersection(appoggio.buffer(0.05))
            n_appoggi = len(getattr(tocco, "geoms", [tocco])) if not tocco.is_empty else 0
            quota = tocco.length / p.exterior.length if p.exterior.length > 0 else 0.0
            ponte = n_appoggi >= 2 or quota > 0.4
            ponti.append((zs[i], p.area, dmax, dove, ponte))

    # riepilogo
    if isole:
        per_z = {}
        for z, a, c in isole:
            per_z.setdefault(round(z, 1), []).append((a, c))
        for z, lst in sorted(per_z.items())[:6]:
            a = sum(x[0] for x in lst)
            errori.append(f"isola nel vuoto a z {z:.1f} mm, {a:.1f} mm² (es. x {lst[0][1][0]:.1f} y {lst[0][1][1]:.1f}): servono supporti")
    critici = [b for b in ponti if b[2] > (PONTE_MAX if b[4] else SBALZO_MAX)]
    if ponti:
        peggio = max(ponti, key=lambda b: b[2])
        righe.append(f"materiale senza appoggio sotto: {len(ponti)} tratti su {len(set(round(b[0], 1) for b in ponti))} strati, "
                     f"il più lontano dall'appoggio {peggio[2]:.1f} mm a z {peggio[0]:.1f} (x {peggio[3][0]:.0f} y {peggio[3][1]:.0f})")
    visti = set()
    for z, a, d, (x, y), n in sorted(critici, key=lambda b: -b[2]):
        chiave = (round(x / 5), round(y / 5))
        if chiave in visti:
            continue
        visti.add(chiave)
        tipo = "ponte" if n else "sbalzo"
        avvisi.append(f"{tipo} a z {z:.1f}: {d:.1f} mm dall'appoggio, {a:.1f} mm² (x {x:.0f} y {y:.0f})")
        if len(visti) >= 8:
            break
    if sottili_persi:
        a = sum(s[1] for s in sottili_persi)
        zmin, zmax = min(s[0] for s in sottili_persi), max(s[0] for s in sottili_persi)
        s0 = max(sottili_persi, key=lambda s: s[1])
        avvisi.append(f"pareti sotto {PERSO} mm (lo slicer le perde): {a:.1f} mm² fra z {zmin:.1f} e {zmax:.1f}, "
                      f"la più grande a x {s0[2][0]:.0f} y {s0[2][1]:.0f} z {s0[0]:.1f}")
    if sottili_fragili:
        a = sum(s[1] for s in sottili_fragili)
        zs_f = sorted(set(round(s[0], 1) for s in sottili_fragili))
        righe.append(f"pareti fra {PERSO} e {FRAGILE} mm (una linea sola): {a:.0f} mm² su {len(zs_f)} strati, "
                     f"da z {zs_f[0]:.1f} a {zs_f[-1]:.1f}")
    return righe, errori, avvisi


def autotest():
    """difetti costruiti apposta: ognuno deve essere RILEVATO, il pezzo pulito no"""
    B = trimesh.creation.box
    def a(size, centro):
        m = B(extents=size)
        m.apply_translation(centro)
        return m
    casi = {
        "pezzo pulito": (a((20, 20, 4), (0, 0, 2)), False),
        "isola nel vuoto": (trimesh.util.concatenate([a((20, 20, 2), (0, 0, 1)), a((5, 5, 2), (0, 0, 6))]), True),
        "ponte da 22 mm": (trimesh.boolean.union([a((4, 5, 10), (-13, 0, 5)), a((4, 5, 10), (13, 0, 5)),
                                                 a((30, 5, 2), (0, 0, 11))]), True),
        "sbalzo da 10 mm": (trimesh.boolean.union([a((5, 5, 10), (0, 0, 5)), a((15, 5, 2), (5, 0, 11))]), True),
    }
    for nome, (mesh, difetto) in casi.items():
        _, errori, avvisi = analizza("autotest", mesh)
        trovato = bool(errori or avvisi)
        esito = "ok" if trovato == difetto else "SBAGLIATO"
        print(f"{nome}: {'RILEVATO' if trovato else 'niente'} ({esito}) {(errori + avvisi)[:1]}")


def main():
    if "--autotest" in sys.argv:
        autotest()
        return
    tot_err = 0
    for nome, f in PEZZI.items():
        path = OUT / f
        if not path.exists():
            print(f"{nome}: manca {f} (lancia prima uv run case.py)")
            tot_err += 1
            continue
        mesh = trimesh.load_mesh(path)
        righe, errori, avvisi = analizza(nome, mesh)
        print(f"\n== {nome}")
        for r in righe:
            print("  " + r)
        for a in avvisi:
            print("  AVVISO " + a)
        for e in errori:
            print("  ERRORE " + e)
        tot_err += len(errori)
    print()
    if tot_err:
        print(f"{tot_err} problemi da risolvere prima di stampare.")
        sys.exit(1)
    print(f"OK: {len(PEZZI)} pezzi stampabili senza supporti.")


if __name__ == "__main__":
    main()
