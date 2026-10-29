"""Genera montaggio_preamp.html dal layout_preamp.py (vista dall'alto, lato componenti, strisce sotto).
    python3 montaggio_preamp.py
Righe numerate da 1, fori numerati da 1 (come hardware/page.py)."""
import html
import os
import sys

import layout_preamp as L

if L.errors:
    sys.exit("layout_preamp.py ha errori: niente pagina")

esc = html.escape
K = 30            # px per foro
M = 24
COL = {"res": "#d8b878", "film": "#c2452d", "elco": "#2f4f7a", "mlcc": "#8a6a2a", "jfet": "#333", "trimmer": "#1f6f78"}
svg = []
Wp, Hp = L.W * K + 2 * M, L.H * K + 2 * M
svg.append(f'<svg viewBox="0 0 {Wp} {Hp}" class="board" xmlns="http://www.w3.org/2000/svg">')
svg.append(f'<rect x="{M-12}" y="{M-12}" width="{L.W*K+24-K+K}" height="{L.H*K+24}" fill="#e8dfc8" stroke="#8c7d58"/>')


def cx(x):
    return M + x * K + K / 2


def cy(y):
    return M + y * K + K / 2


for y in range(L.H):                       # strisce
    xs = [x for x in range(L.W) if (x, y) not in L.CUTS]
    svg.append(f'<rect x="{M}" y="{cy(y)-9}" width="{L.W*K}" height="18" fill="#c9a24a" opacity=".55"/>')
    svg.append(f'<text x="2" y="{cy(y)+4}" class="gl">{y+1}</text>')
for x in range(L.W):
    svg.append(f'<text x="{cx(x)-4}" y="{M-6}" class="gl">{x+1}</text>')
for y in range(L.H):
    for x in range(L.W):
        if (x, y) in L.CUTS:
            svg.append(f'<rect x="{cx(x)-K/2}" y="{cy(y)-10}" width="{K}" height="20" fill="#e8dfc8"/>')
            svg.append(f'<path d="M{cx(x)-6} {cy(y)-6}L{cx(x)+6} {cy(y)+6}M{cx(x)+6} {cy(y)-6}L{cx(x)-6} {cy(y)+6}" stroke="#b3261e" stroke-width="2"/>')
        else:
            svg.append(f'<circle cx="{cx(x)}" cy="{cy(y)}" r="3.2" fill="#2b2418"/>')
for p in L.P:                              # corpi
    x0, y0, x1, y1 = p["rect"]
    col = COL[p["kind"]]
    svg.append(f'<rect x="{cx(x0)-10}" y="{cy(y0)-10}" width="{(x1-x0)*K+20}" height="{(y1-y0)*K+20}" rx="8" fill="{col}" opacity=".78" stroke="#111"/>')
    for (x, y, net, pn) in p["pins"]:
        svg.append(f'<circle cx="{cx(x)}" cy="{cy(y)}" r="5" fill="#f4f4f4" stroke="#111"/>')
        if pn in ("+", "-"):
            svg.append(f'<text x="{cx(x)-3}" y="{cy(y)+4}" class="pm">{pn}</text>')
    mx, my = (cx(x0) + cx(x1)) / 2, (cy(y0) + cy(y1)) / 2
    svg.append(f'<text x="{mx}" y="{my+3}" class="cl" text-anchor="middle">{esc(p["ref"])}</text>')
for name, a, b, net, lab in L.LINKS + L.WIRES:
    svg.append(f'<line x1="{cx(a[0])}" y1="{cy(a[1])}" x2="{cx(b[0])}" y2="{cy(b[1])}" stroke="#0b8a3c" stroke-width="3" stroke-dasharray="7 4"/>')
    for h in (a, b):
        svg.append(f'<circle cx="{cx(h[0])}" cy="{cy(h[1])}" r="5" fill="#0b8a3c"/>')
    svg.append(f'<text x="{(cx(a[0])+cx(b[0]))/2+4}" y="{(cy(a[1])+cy(b[1]))/2}" class="jl">{name}</text>')
for name, h, net, d in L.PADS:
    svg.append(f'<rect x="{cx(h[0])-8}" y="{cy(h[1])-8}" width="16" height="16" fill="#fff" stroke="#b3261e" stroke-width="2"/>')
    tx = cx(h[0]) + 12 if h[0] < L.W / 2 else cx(h[0]) - 12
    svg.append(f'<text x="{tx}" y="{cy(h[1])-9}" class="pl" text-anchor="{"start" if h[0] < L.W/2 else "end"}">{esc(name)}</text>')
for (x, y) in L.FORI_FISSAGGIO:
    svg.append(f'<circle cx="{cx(x)}" cy="{cy(y)}" r="13" fill="none" stroke="#111" stroke-width="3"/>')
    svg.append(f'<text x="{cx(x)+15}" y="{cy(y)+4}" class="pl">M3</text>')
svg.append("</svg>")

bom = {}
for p in L.P:
    key = (p["kind"], p["label"], p["mount"])
    bom.setdefault(key, []).append(p["ref"])
bom_html = "\n".join(f"<tr><td>{esc(', '.join(refs))}</td><td>{len(refs)}</td><td>{esc(k[1])}</td><td>{esc(k[2])}</td></tr>"
                     for k, refs in bom.items())
cut_html = "\n".join(f"<tr><td>riga {y+1}</td><td>foro {x+1}</td></tr>" for (x, y) in sorted(L.CUTS, key=lambda t: (t[1], t[0])))
link_html = "\n".join(f"<tr><td>{n}</td><td>riga {a[1]+1} foro {a[0]+1} &rarr; riga {b[1]+1} foro {b[0]+1}</td><td>{esc(lab)}</td></tr>"
                      for n, a, b, net, lab in L.LINKS + L.WIRES)
pad_html = "\n".join(f"<tr><td>{esc(n)}</td><td>riga {h[1]+1} foro {h[0]+1}</td><td>{esc(d)}</td></tr>" for n, h, net, d in L.PADS)
fori = "; ".join(f"riga {y+1} foro {x+1}" for x, y in L.FORI_FISSAGGIO)

doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preamp JFET stripboard</title>
<style>
:root{{--bg:#eef2f4;--ink:#16232b;--muted:#4d5d67;--rule:#b9c6ce;--accent:#0b5d63}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#172026;--ink:#e3eaee;--muted:#9fb0ba;--rule:#34444e;--accent:#6fc3c9}}}}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;margin:0;padding:16px;max-width:900px;margin:auto}}
svg.board{{width:100%;height:auto}} .gl{{font:9px sans-serif;fill:#555}} .cl{{font:700 10px sans-serif;fill:#fff;paint-order:stroke;stroke:#000;stroke-width:2px}}
.pl{{font:700 11px sans-serif;fill:#b3261e;paint-order:stroke;stroke:#fff;stroke-width:3px}} .jl{{font:700 10px sans-serif;fill:#0b8a3c;paint-order:stroke;stroke:#fff;stroke-width:3px}}
.pm{{font:700 8px sans-serif;fill:#000}}
table{{border-collapse:collapse;width:100%;margin:8px 0 20px}} td,th{{border-bottom:1px solid var(--rule);padding:4px 8px;text-align:left}}
h1,h2{{color:var(--accent)}} .n{{color:var(--muted)}}
</style></head><body>
<h1>Preamp JFET d'ingresso su stripboard</h1>
<p class="n">Circuito V4a (risultati.md). Scheda {L.W} &times; {L.H} fori ({L.W*L.PASSO:.1f} &times; {L.H*L.PASSO:.1f} mm), vista dai componenti: le strisce di rame sono sotto,
orizzontali. X rossa = taglio della striscia, tratteggio verde = ponticello/cavo isolato, quadrato rosso = piazzola per filo esterno.
Canale L in alto (righe 1-9), R in basso (righe 10-18, specchiato).</p>
{''.join(svg)}
<h2>J201 (TO-92)</h2>
<p>Piedini: 1 = drain, 2 = source, 3 = gate (Central Semiconductor J201, lead code). Sulla scheda i tre piedi stanno su tre strisce
consecutive: D, S, G (nel canale L dal basso verso l'alto; nel R dall'alto verso il basso, quindi il componente va girato di 180&deg;).
Verificare con il tester prima di saldare.</p>
<h2>Componenti</h2><table><tr><th>Riferimenti</th><th>N.</th><th>Valore</th><th>Montaggio</th></tr>{bom_html}</table>
<h2>Piazzole esterne</h2><p>GAIN: pot doppio 9 mm C50K usato come reostato (cursore e un capo), con una 47k saldata direttamente sui due terminali usati di ogni gang. A GAIN al massimo la resistenza va a zero: se il guadagno sale girando a sinistra, usare l'altro capo.</p><table>{pad_html}</table>
<h2>Ponticelli e cavi</h2><table>{link_html}</table>
<h2>Tagli ({len(L.CUTS)})</h2><table>{cut_html}</table>
<h2>Fori di fissaggio M3 (3,2 mm)</h2><p>{fori}. Forare prima di montare.</p>
</body></html>"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "montaggio_preamp.html")
open(out, "w").write(doc)
print("scritto", out, len(doc), "byte")
