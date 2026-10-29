"""
Struttura per disegnare a mano, da codice, i fogli dello schema di PA-TELAIO (usata da disegna_schema.py e dai
moduli in fogli/). Ogni foglio è un A3; le coordinate sono in mm sul foglio, x verso destra, y verso il BASSO
(come in KiCad), sempre sulla griglia da 2,54.

    f.parte("R1", x, y, rot=0, unit=1)      piazza un'unità di un componente di componenti.json; rot in gradi, antiorario
    p = f.parte(...); p.pin("2")            punto di collegamento di un piedino (oggetto Pin, .x .y)
    f.filo(a, b, c, ...)                    filo per punti (Pin o (x, y)); ogni tratto orizzontale o verticale
    f.porta(pin)                            tratto di filo verso l'esterno + etichetta globale col nome della rete del
                                            piedino (o simbolo di alimentazione/massa se la rete è GND, VA, ...)
    f.etichetta(nome, punto, verso)         etichetta globale su un punto di filo; verso "dx", "sx", "su", "giu"
    f.alim(nome, punto)                     simbolo di alimentazione o massa su un punto di filo
    f.nc(pin)                               piedino non collegato (solo se in componenti.json è NC)
    f.testo("...", x, y)                    nota

Alla scrittura il foglio controlla da solo che ogni gruppo di piedini uniti da fili ed etichette abbia la rete
attesa (componenti.json), che nessun piedino resti scollegato e che i componenti non si sovrappongano.
"""
import json
import math
import re
from pathlib import Path

import simboli
from genera_uuid import uid

QUI = Path(__file__).resolve().parent
G = 2.54
DATI = json.loads((QUI / "componenti.json").read_text())
COMP = DATI["componenti"]
SIMB = simboli.catalogo(DATI["seed_nomi"])
PROGETTO = "pa-telaio"
FORMATI = {"A3": (420.0, 297.0), "A4": (297.0, 210.0)}


def fx(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def sulla_griglia(v):
    return abs(v / 1.27 - round(v / 1.27)) < 1e-6


class Pin:
    def __init__(self, parte, num, x, y, fuori):
        self.parte, self.num, self.x, self.y, self.fuori = parte, num, x, y, fuori

    @property
    def xy(self):
        return (round(self.x, 3), round(self.y, 3))

    @property
    def rete(self):
        return COMP[self.parte.ref]["pins"][self.num] if self.parte.ref in COMP else self.parte.rete

    def __repr__(self):
        return f"{self.parte.ref}.{self.num}"


class Parte:
    def __init__(self, foglio, ref, sim, unit, x, y, rot, valore, rete=None, power=False, scritte=None):
        self.foglio, self.ref, self.sim, self.unit, self.x, self.y, self.rot = foglio, ref, sim, unit, x, y, rot
        self.valore, self.rete, self.power = valore, rete, power
        self.scritte = scritte or ("dx" if rot in (90, 270) else "su")
        u = SIMB[sim]["units"][unit]
        c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
        self.pins = {}
        for p in u["pins"]:
            rx, ry = p["x"] * c - p["y"] * s, p["x"] * s + p["y"] * c
            a = math.radians(p["ang"] + rot + 180)          # verso l'esterno, y in su
            self.pins[p["num"]] = Pin(self, p["num"], x + rx, y - ry, (round(math.cos(a)), -round(math.sin(a))))
        # ingombro: piedini e grafica, ruotati
        pts = [(p["x"], p["y"]) for p in u["pins"]]
        for g in u["gr"]:
            nums = [float(v) for v in re.findall(r"\((?:xy|start|end|center) ([-\d.]+) ([-\d.]+)\)", g) for v in v]
            pts += list(zip(nums[0::2], nums[1::2]))
            m = re.search(r"\(radius ([\d.]+)\)", g)
            if m:
                cx, cy, r = nums[0], nums[1], float(m.group(1))
                pts += [(cx - r, cy - r), (cx + r, cy + r)]
        sx = [x + px * c - py * s for px, py in pts]
        sy = [y - (px * s + py * c) for px, py in pts]
        self.bb = (min(sx), min(sy), max(sx), max(sy))

    def pin(self, num):
        num = str(num)
        if num not in self.pins:
            raise KeyError(f"{self.ref} unità {self.unit}: nessun piedino {num} (ci sono {sorted(self.pins)})")
        return self.pins[num]


class Foglio:
    def __init__(self, file, titolo, formato="A3"):
        self.file, self.titolo, self.formato = file, titolo, formato
        self.W, self.H = FORMATI[formato]
        self.parti, self.fili, self.etichette, self.ncs, self.testi = [], [], [], [], []
        self.uuid = uid("foglio", file)
        self.errori = []

    # ------------------------------------------------------------------ costruzione
    def parte(self, ref, x, y, rot=0, unit=1, valore=None, scritte=None):
        """scritte: dove vanno riferimento e valore, "su" (sopra e sotto) o "dx"/"sx" (a lato)"""
        if ref not in COMP:
            raise KeyError(f"{ref} non è in componenti.json")
        sim = COMP[ref]["sim"]
        if unit not in SIMB[sim]["units"]:
            raise KeyError(f"{ref} ({sim}) non ha l'unità {unit}")
        if not (sulla_griglia(x) and sulla_griglia(y)):
            self.errori.append(f"{ref}: posizione ({x}, {y}) fuori griglia")
        p = Parte(self, ref, sim, unit, x, y, rot % 360, valore or COMP[ref]["val"], scritte=scritte)
        self.parti.append(p)
        return p

    def _punto(self, a):
        return a.xy if isinstance(a, Pin) else (round(a[0], 3), round(a[1], 3))

    def filo(self, *punti):
        pts = [self._punto(a) for a in punti]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            if a[0] != b[0] and a[1] != b[1]:
                self.errori.append(f"filo obliquo da {a} a {b}: usa tratti orizzontali e verticali")
            self.fili.append((a, b))
        return pts[-1]

    def alim(self, nome, punto, verso=None):
        """simbolo di rete su un punto; verso = dove punta: massa "giu" di serie, alimentazioni "su" di serie"""
        x, y = self._punto(punto)
        if nome == "GND":
            rot = {None: 0, "giu": 0, "dx": 90, "su": 180, "sx": 270}[verso]
        else:
            rot = {None: 0, "su": 0, "sx": 90, "giu": 180, "dx": 270}[verso]
        n = sum(1 for p in self.parti if p.power) + 1
        ref = ("#FLG" if nome == "PWR_FLAG" else "#PWR") + f"{self.file[:3]}{n:02d}"
        p = Parte(self, ref, nome, 1, x, y, rot, nome, rete=nome if nome != "PWR_FLAG" else None, power=True)
        self.parti.append(p)
        return p

    def etichetta(self, nome, punto, verso):
        x, y = self._punto(punto)
        self.etichette.append((nome, x, y, verso))

    def porta(self, pin, nome=None, lung=2 * G, verso=None):
        nome = nome or pin.rete
        dx, dy = pin.fuori
        fine = (pin.x + dx * lung, pin.y + dy * lung)
        self.filo(pin, fine)
        if nome in SIMB and SIMB[nome].get("power"):
            self.alim(nome, fine, {(1, 0): "dx", (-1, 0): "sx", (0, -1): "su", (0, 1): "giu"}[(dx, dy)])
        else:
            v = verso or {(1, 0): "dx", (-1, 0): "sx", (0, -1): "su", (0, 1): "giu"}[(dx, dy)]
            self.etichetta(nome, fine, v)
        return fine

    def nc(self, pin):
        self.ncs.append(pin)

    def testo(self, s, x, y, size=1.8, grassetto=False):
        self.testi.append((s, x, y, size, grassetto))

    # ------------------------------------------------------------------ controlli
    def nodi(self):
        """punti di collegamento: piedini, estremi dei fili, etichette; ritorna gruppi di punti connessi"""
        par = {}

        def f(a):
            par.setdefault(a, a)
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a

        def u(a, b):
            par[f(a)] = f(b)

        punti = set()
        for p in self.parti:
            for q in p.pins.values():
                punti.add(q.xy)
        for a, b in self.fili:
            punti |= {a, b}
        for e in self.etichette:
            punti.add((round(e[1], 3), round(e[2], 3)))
        for a, b in self.fili:
            u(a, b)
            for q in punti:
                if self._dentro(q, a, b):
                    u(q, a)
        for q in punti:
            f(q)
        return f

    @staticmethod
    def _dentro(q, a, b):
        """q sul tratto a-b, estremi esclusi"""
        if q in (a, b):
            return False
        if a[0] == b[0] == q[0]:
            return min(a[1], b[1]) < q[1] < max(a[1], b[1])
        if a[1] == b[1] == q[1]:
            return min(a[0], b[0]) < q[0] < max(a[0], b[0])
        return False

    def controlla(self):
        err = list(self.errori)
        f = self.nodi()
        gruppi = {}
        for p in self.parti:
            for q in p.pins.values():
                gruppi.setdefault(f(q.xy), []).append(q)
        nomi = {}
        for nome, x, y, _ in self.etichette:
            nomi.setdefault(f((round(x, 3), round(y, 3))), set()).add(nome)
        nc = {(q.parte.ref, q.num) for q in self.ncs}
        filo_su = {f(a) for a, b in self.fili}
        for r, qs in gruppi.items():
            attese = {q.rete for q in qs if q.rete is not None}
            nomi_r = nomi.get(r, set()) | {q.parte.rete for q in qs if q.parte.power and q.parte.rete}
            tutte = attese | nomi_r
            if "NC" in attese and len(qs) > 1:
                err.append(f"piedino NC collegato: {qs}")
            elif len(tutte) > 1:
                err.append(f"reti diverse unite: {sorted(tutte)} su {qs}")
            for q in qs:
                if q.parte.power:
                    continue
                if q.rete == "NC":
                    if (q.parte.ref, q.num) not in nc:
                        err.append(f"{q} è NC: segnalo con f.nc()")
                elif (q.parte.ref, q.num) in nc:
                    err.append(f"{q} segnato NC ma la rete è {q.rete}")
                elif len(qs) == 1 and r not in nomi and r not in filo_su:
                    err.append(f"{q} scollegato (rete {q.rete})")
                elif len(qs) == 1 and r in filo_su and r not in nomi:
                    err.append(f"{q} su un filo che non va da nessuna parte (rete {q.rete})")
        # etichette e fili appesi
        for nome, x, y, _ in self.etichette:
            if f((round(x, 3), round(y, 3))) not in filo_su and f((round(x, 3), round(y, 3))) not in gruppi:
                err.append(f"etichetta {nome} in ({x}, {y}) non tocca né fili né piedini")
        # ingombri sovrapposti
        corpi = [p for p in self.parti if not p.power]
        for i, a in enumerate(corpi):
            for b in corpi[i + 1:]:
                if a.bb[0] < b.bb[2] - 0.3 and b.bb[0] < a.bb[2] - 0.3 and a.bb[1] < b.bb[3] - 0.3 and b.bb[1] < a.bb[3] - 0.3:
                    err.append(f"{a.ref}/{a.unit} e {b.ref}/{b.unit} si sovrappongono")
            if a.bb[0] < 12 or a.bb[1] < 12 or a.bb[2] > self.W - 12 or a.bb[3] > self.H - 12:
                err.append(f"{a.ref} fuori dal foglio o sul bordo")
            if a.bb[2] > self.W - 120 and a.bb[3] > self.H - 45:
                err.append(f"{a.ref} sul cartiglio in basso a destra")
        # fili sovrapposti
        for i, (a, b) in enumerate(self.fili):
            for c, d in self.fili[i + 1:]:
                if (a[0] == b[0] == c[0] == d[0] and max(min(a[1], b[1]), min(c[1], d[1])) < min(max(a[1], b[1]), max(c[1], d[1]))) or \
                   (a[1] == b[1] == c[1] == d[1] and max(min(a[0], b[0]), min(c[0], d[0])) < min(max(a[0], b[0]), max(c[0], d[0]))):
                    err.append(f"fili sovrapposti: {a}-{b} e {c}-{d}")
        return err

    # ------------------------------------------------------------------ scrittura
    def kicad(self, radice, sheet_uuid, pagina):
        f = self.nodi()
        punti_nodo = set()
        for p in self.parti:
            punti_nodo |= {q.xy for q in p.pins.values()}
        for a, b in self.fili:
            punti_nodo |= {a, b}
        punti_nodo |= {(round(e[1], 3), round(e[2], 3)) for e in self.etichette}
        # tratti spezzati sui punti interni, giunzioni dove si incontrano 3 o più capi
        segmenti = []
        for a, b in self.fili:
            interni = sorted([q for q in punti_nodo if self._dentro(q, a, b)], key=lambda q: abs(q[0] - a[0]) + abs(q[1] - a[1]))
            pts = [a] + interni + [b]
            segmenti += list(zip(pts, pts[1:]))
        grado = {}
        for a, b in segmenti:
            for q in (a, b):
                grado[q] = grado.get(q, 0) + 1
        for p in self.parti:
            for q in p.pins.values():
                if q.xy in grado:
                    grado[q.xy] += 1
        giunzioni = sorted(q for q, n in grado.items() if n >= 3)
        usati = sorted({p.sim for p in self.parti})
        out = [f'(kicad_sch (version 20231120) (generator "pa_telaio_disegna_schema") (generator_version "8.0") '
               f'(uuid "{self.uuid}") (paper "{self.formato}")',
               f'(title_block (title "PA-TELAIO: {self.titolo}") (date "") (rev "") '
               f'(comment 1 "generato da hardware/kicad/disegna_schema.py: non modificare a mano"))',
               "(lib_symbols"]
        out += [lib_symbol(n, SIMB[n]) for n in usati]
        out.append(")")
        for q in giunzioni:
            out.append(f'(junction (at {fx(q[0])} {fx(q[1])}) (diameter 0) (color 0 0 0 0) (uuid "{uid("j", self.file, q)}"))')
        for q in self.ncs:
            out.append(f'(no_connect (at {fx(q.x)} {fx(q.y)}) (uuid "{uid("nc", self.file, q.parte.ref, q.num)}"))')
        for a, b in segmenti:
            out.append(f'(wire (pts (xy {fx(a[0])} {fx(a[1])}) (xy {fx(b[0])} {fx(b[1])})) '
                       f'(stroke (width 0) (type default)) (uuid "{uid("w", self.file, a, b)}"))')
        for nome, x, y, v in self.etichette:
            ang, gius = {"dx": (0, "left"), "sx": (180, "right"), "su": (90, "left"), "giu": (270, "right")}[v]
            out.append(f'(global_label "{nome}" (shape passive) (at {fx(x)} {fx(y)} {ang}) (fields_autoplaced yes) '
                       f'(effects (font (size 1.27 1.27)) (justify {gius})) (uuid "{uid("g", self.file, nome, x, y)}") '
                       f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {fx(x)} {fx(y)} 0) '
                       f'(effects (font (size 1.27 1.27)) hide)))')
        for s, x, y, size, b in self.testi:
            out.append(f'(text "{s}" (exclude_from_sim no) (at {fx(x)} {fx(y)} 0) '
                       f'(effects (font (size {size:g} {size:g}){" bold" if b else ""}) (justify left bottom)) (uuid "{uid("t", self.file, s, x, y)}"))')
        for p in self.parti:
            out.append(istanza(p, radice, sheet_uuid))
        out.append(")")
        return "\n".join(out) + "\n"


def lib_symbol(nome, s, prefisso="PA:"):
    righe = []
    for n, u in sorted(s["units"].items()):
        pins = []
        for p in u["pins"]:
            pins.append(f'(pin {p["tipo"]} line (at {fx(p["x"])} {fx(p["y"])} {p["ang"]}) (length {fx(p["lun"])})'
                        f'{" hide" if p["nascosto"] else ""} '
                        f'(name "{p["nome"]}" (effects (font (size 1.016 1.016)))) '
                        f'(number "{p["num"]}" (effects (font (size 1.016 1.016)))))')
        righe.append(f'  (symbol "{nome}_{n}_1" {" ".join(u["gr"])} {" ".join(pins)})')
    nomi = "(pin_names (offset 0.508))" if s["nomi"] else "(pin_names (offset 0) hide)"
    rif = "#PWR" if s["power"] else "X"
    return (f'(symbol "{prefisso}{nome}"{" (power)" if s["power"] else ""} (pin_numbers hide) {nomi} '
            f'(exclude_from_sim no) (in_bom {"no" if s["power"] else "yes"}) (on_board {"no" if s["power"] else "yes"})\n'
            f'  (property "Reference" "{rif}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Value" "{nome}" (at 0 0 0) (effects (font (size 1.27 1.27))))\n'
            f'  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            + "\n".join(righe) + ")")


def istanza(p, radice, sheet_uuid):
    x0, y0, x1, y1 = p.bb
    if p.power:
        # il valore oltre la punta del simbolo, nel verso in cui punta
        punta = {0: (0, 1), 90: (1, 0), 180: (0, -1), 270: (-1, 0)} if p.sim == "GND" else \
            {0: (0, -1), 90: (-1, 0), 180: (0, 1), 270: (1, 0)}
        ux, uy = punta[p.rot]
        d = 4.2 if uy > 0 else 3.6
        rif_at, val_at = (p.x, p.y, 0), (p.x + ux * (d + 1.5), p.y + uy * d, 0)
        gv = "center"
        hide_ref, hide_val = True, p.sim == "PWR_FLAG"
    elif p.scritte == "su":
        rif_at, val_at, gv = (p.x, y0 - 1.0, 0), (p.x, y1 + 2.2, 0), "center"
        hide_ref = hide_val = False
    elif p.scritte == "dx":
        rif_at, val_at, gv = (x1 + 1.0, p.y - 0.8, 0), (x1 + 1.0, p.y + 1.6, 0), "left"
        hide_ref = hide_val = False
    else:
        rif_at, val_at, gv = (x0 - 1.0, p.y - 0.8, 0), (x0 - 1.0, p.y + 1.6, 0), "right"
        hide_ref = hide_val = False
    # KiCad ruota i campi insieme al simbolo: su un simbolo verticale l'angolo 90 li rimette orizzontali
    fa = 90 if p.rot in (90, 270) else 0
    if p.rot in (90, 180) and gv != "center":
        gv = "right" if gv == "left" else "left"     # con rot 90 e 180 KiCad gira anche la giustificazione
    gius = "" if gv == "center" else f" (justify {gv})"
    pins = " ".join(f'(pin "{n}" (uuid "{uid("p", p.ref, p.unit, n)}"))' for n in p.pins)
    c = COMP.get(p.ref, {})
    return (f'(symbol (lib_id "PA:{p.sim}") (at {fx(p.x)} {fx(p.y)} {p.rot}) (unit {p.unit}) (exclude_from_sim no) '
            f'(in_bom {"no" if p.power else "yes"}) (on_board {"no" if p.power else "yes"}) (dnp no) (uuid "{uid("s", p.ref, p.unit)}")\n'
            f'  (property "Reference" "{p.ref}" (at {fx(rif_at[0])} {fx(rif_at[1])} {fa}) (effects (font (size 1.27 1.27)){gius}{" hide" if hide_ref else ""}))\n'
            f'  (property "Value" "{p.valore}" (at {fx(val_at[0])} {fx(val_at[1])} {fa}) (effects (font (size 1.27 1.27)){gius}{" hide" if hide_val else ""}))\n'
            f'  (property "Footprint" "{c.get("fp", "")}" (at {fx(p.x)} {fx(p.y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Datasheet" "" (at {fx(p.x)} {fx(p.y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Description" "" (at {fx(p.x)} {fx(p.y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  (property "Layout" "{c.get("layout", "")}" (at {fx(p.x)} {fx(p.y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  {pins}\n'
            f'  (instances (project "{PROGETTO}" (path "/{radice}/{sheet_uuid}" (reference "{p.ref}") (unit {p.unit})))))')
