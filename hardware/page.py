import html
import layout as L
import render as R

esc = html.escape

bom = R.bom_rows()
cuts = R.cuts_rows()

# fori di fissaggio, numerati da 1 come nella pagina: "riga 2, fori 2 e 29; ..."
_per_riga = {}
for _x, _y in L.FORI_FISSAGGIO:
    _per_riga.setdefault(_y + 1, []).append(_x + 1)
fori_txt = "; ".join(
    f"riga {r}, " + (f"fori {' e '.join(map(str, sorted(f)))}" if len(f) > 1 else f"foro {f[0]}")
    for r, f in sorted(_per_riga.items()))

bom_html = "\n".join(
    f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class='n'>{c}</td><td>{esc(d)}</td></tr>"
    for a, b, c, d in bom)

# tagli raggruppati per righe con lo stesso schema
cut_groups = []
prev = None
for row, holes in cuts.items():
    key = tuple(holes)
    if prev and prev[0] == key and prev[2] == row - 1:
        prev[2] = row
    else:
        prev = [key, row, row]
        cut_groups.append(prev)
cuts_html = "\n".join(
    f"<tr><td>{a if a == b else f'{a}–{b}'}</td><td>{', '.join(map(str, k))}</td>"
    f"<td>{'tra le due file del Seed, e accorcia le strisce di destra' if k == (7, 15) else ''}"
    f"{'isola jack DC, V9 e VIN' if k == (5, 16) else ''}"
    f"{'centro dello zoccolo, separa canale sinistro e destro' if k == (14,) else ''}</td></tr>"
    for k, a, b in cut_groups)

pads_html = "\n".join(
    f"<tr><td>{esc(n)}</td><td>riga {y+1}, foro {x+1}</td><td>{esc(d)}</td></tr>"
    for n, (x, y), net, d in L.PADS)

links_html = "\n".join(
    f"<tr><td>{n}</td><td>{a[1]+1}/{a[0]+1} → {b[1]+1}/{b[0]+1}</td><td>{'nudo' if bare else net}</td></tr>"
    for n, a, b, net, bare in L.LINKS) + "\n" + "\n".join(
    f"<tr><td>{n}</td><td>{a[1]+1}/{a[0]+1} → {b[1]+1}/{b[0]+1}</td><td>{esc(lab)}</td></tr>"
    for n, a, b, net, lab in L.WIRES)

CSS = r"""
:root{
  --bg:#dfe6ea; --paper:#eef2f4; --ink:#16232b; --muted:#4d5d67; --rule:#b9c6ce;
  --accent:#0b5d63; --warn:#b3261e; --warnbg:#f6dcd8;
  --sch-line:#16232b; --sch-fill:#eef2f4;
  box-sizing:border-box;
  padding-top:env(safe-area-inset-top,0px);
  padding-bottom:env(safe-area-inset-bottom,0px);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#172026; --paper:#1f2b33; --ink:#e3eaee; --muted:#9fb0ba; --rule:#34444e;
    --accent:#5fc2c9; --warn:#ff8a80; --warnbg:#3a2220;
    --sch-line:#e3eaee; --sch-fill:#1f2b33;
  }
}
:root[data-theme="dark"]{
  --bg:#172026; --paper:#1f2b33; --ink:#e3eaee; --muted:#9fb0ba; --rule:#34444e;
  --accent:#5fc2c9; --warn:#ff8a80; --warnbg:#3a2220;
  --sch-line:#e3eaee; --sch-fill:#1f2b33;
}
*,*::before,*::after{box-sizing:inherit}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Barlow",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  font-size:17px;line-height:1.55}
main{max-width:980px;margin:0 auto;padding:40px 20px 80px}
header{max-width:62ch}
h1{font-size:2.35rem;line-height:1.1;font-weight:600;margin:0 0 .4em;letter-spacing:-.01em}
.lede{color:var(--muted);font-size:1.08rem;margin:0}
h2{font-size:1.35rem;font-weight:600;margin:2.6em 0 .5em}
h3{font-size:1.05rem;font-weight:600;margin:1.8em 0 .3em}
p,li{max-width:70ch}
.warn{background:var(--warnbg);border-left:4px solid var(--warn);padding:14px 18px;margin:28px 0;max-width:72ch}
.warn strong{color:var(--warn)}
.warn ol{margin:.4em 0 0;padding-left:1.2em}
.fig{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:14px;margin:14px 0}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.fig svg{display:block;margin:0 auto;width:100%;height:auto}
svg.board{max-width:834px}
svg.sch{max-width:780px}
.cap{color:var(--muted);font-size:.93rem;margin:.6em 2px 0;max-width:80ch}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;margin:10px 2px 0;font-size:.92rem;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:7px}
.sw{width:22px;height:5px;border-radius:3px;display:inline-block}
.tbl{overflow-x:auto;border:1px solid var(--rule);border-radius:10px;background:var(--paper)}
table{border-collapse:collapse;width:100%;font-size:.94rem}
th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-weight:600;color:var(--muted)}
tr:last-child td{border-bottom:none}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media (max-width:760px){.two{grid-template-columns:1fr}h1{font-size:1.9rem}}
ol.steps li{margin:.35em 0}
svg .gl{font:500 10px "Barlow",sans-serif;fill:var(--muted)}
svg .pn{font:500 8.5px "Barlow",sans-serif;fill:#e9e9e9}
svg .seedt{font:600 15px "Barlow",sans-serif;fill:#9aa3a8;letter-spacing:.08em}
svg .ict{font:600 13px "Barlow",sans-serif;fill:#f2f2f2}
svg .icv{font:500 10px "Barlow",sans-serif;fill:#bdbdbd}
svg .icp{font:600 8px "Barlow",sans-serif;fill:#f2f2f2}
svg .cl{font:600 9.5px "Barlow",sans-serif;fill:#2c1e0c;paint-order:stroke;stroke:#d8bb82;stroke-width:3px}
svg .jl{font:600 9px "Barlow",sans-serif;paint-order:stroke;stroke:#d8bb82;stroke-width:3px}
svg .pl{font:600 10.5px "Barlow",sans-serif;fill:var(--accent)}
svg .plc{font:700 10.5px "Barlow",sans-serif;fill:#fff;paint-order:stroke;stroke:#3b2410;stroke-width:3.5px}
svg .plus{font:700 11px "Barlow",sans-serif;fill:#274f86;paint-order:stroke;stroke:#d8bb82;stroke-width:3px}
svg.sch .w{fill:none;stroke:var(--sch-line);stroke-width:1.6}
svg.sch .w2{fill:none;stroke:var(--sch-line);stroke-width:2.4}
svg.sch .sym{fill:var(--sch-fill);stroke:var(--sch-line);stroke-width:1.6}
svg.sch .dot{fill:var(--sch-line)}
svg.sch .term{fill:var(--sch-fill);stroke:var(--sch-line);stroke-width:1.6}
svg.sch .st{font:500 11px "Barlow",sans-serif;fill:var(--ink)}
svg.sch .stb{font:600 12px "Barlow",sans-serif;fill:var(--ink)}
svg.sch .sts{font:500 11px "Barlow",sans-serif;fill:var(--muted)}
svg.sch .stp{font:700 14px "Barlow",sans-serif;fill:var(--ink)}
"""

page = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Prototipo veroboard Seed3 con TLC2272</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>
<header>
<h1>Prototipo su veroboard</h1>
<p class="lede">Daisy Seed3 su zoccolo, due TLC2272 in DIP-8 a 9 V, ingresso e uscita stereo a livello strumento.
Bypass in DSP su K1 e true bypass con footswitch 3PDT; i controlli sono cablati fuori scheda. Layout verificato da script: ogni net elettrica
corrisponde a una sola isola di rame, nessun corto, nessun aperto.</p>
</header>

<div class="warn">
<strong>Prima di saldare</strong>
<ol>
<li>Fai tutti i {len(L.CUTS)} tagli e controllali con il tester in continuità. Il taglio sulla colonna 7, righe 1–20, è quello
che separa le due file del Seed: senza, il 3V3A va in corto con AGND e i 9 V finiscono su un GPIO.</li>
<li>Verifica sulla serigrafia del Seed3 dove sta il pin 1 e orienta gli header di conseguenza.
Il puntino rosso nel disegno indica il pin 1.</li>
<li>Primo collaudo senza Seed e senza integrati negli zoccoli: misura VA, VB e VIN.</li>
</ol>
</div>

<h2>Lato componenti</h2>
<div class="fig">{R.board_svg()}
<div class="legend">
<span><i class="sw" style="background:#b3245f"></i>VA, alimentazione operazionali</span>
<span><i class="sw" style="background:#d9822b"></i>VB, bias a metà rail</span>
<span><i class="sw" style="background:#2a2d2f"></i>massa</span>
<span><i class="sw" style="background:#6a4bb5"></i>VIN Seed</span>
<span><i class="sw" style="background:#11808a"></i>audio</span>
<span><i class="sw" style="background:#9aa3a8"></i>ponticello nudo</span>
<span><i class="sw" style="background:#c62f2f"></i>taglio</span>
<span><i class="sw" style="background:#1f6fb2"></i>foro di fissaggio Ø 3,2</span>
</div>
<p class="cap">Strisce orizzontali viste in trasparenza. Linee continue: ponticelli sulla scheda, isolati tranne J1 e J2.
Linee tratteggiate: cavetti isolati verso i pin del Seed, disegnati dritti per leggibilità: nella realtà falli girare intorno ai componenti. Cerchi verdi: piazzole per i fili che escono dalla scheda.
Le resistenze che scavalcano una sola striscia vanno montate in piedi. D1 e R1 stanno sdraiati lungo la riga 22,
a cavallo di un taglio.</p>
</div>

<h2>Lato rame, per i tagli</h2>
<div class="fig">{R.copper_svg()}
<p class="cap">Vista dal lato rame, quindi specchiata: il foro 1 è a destra. I cerchi rossi sono i tagli, i fori chiari
quelli dove va un terminale.</p>
<p class="cap"><b>Fori di fissaggio</b>, in blu nei due disegni: {fori_txt}. Da forare a 3,2 mm per viti M3, prima di
montare i componenti. Stanno ad almeno un foro dal bordo e non spezzano strisce usate: <code>layout.py</code> lo
controlla. Non usare la riga 45, l'ultima: la sua striscia porta la massa a R18 e alle masse delle uscite, e un
foro lì sfonda il bordo.</p></div>

<div class="tbl"><table>
<thead><tr><th>Righe</th><th>Fori da tagliare</th><th>Perché</th></tr></thead>
<tbody>{cuts_html}</tbody></table></div>

<h2>Schema</h2>
<h3>Alimentazione</h3>
<div class="fig scroll">{R.sch_power()}</div>
<h3>Ingresso, uno per canale</h3>
<div class="fig scroll">{R.sch_input()}</div>
<p class="cap">Tra parentesi i riferimenti del canale destro. Il guadagno è unitario: con una chitarra resti lontano
dal fondo scala del Seed3, ma con 32 bit e il rumore di fondo del codec il margine perso non si sente.</p>
<h3>Uscita, una per canale</h3>
<div class="fig scroll">{R.sch_output()}</div>
<p class="cap">Lo stadio è invertente: in firmware moltiplica l'uscita per −1 per rimettere la fase in ordine.</p>

<h2>Componenti</h2>
<div class="tbl"><table>
<thead><tr><th>Tipo</th><th>Valore</th><th>Q.tà</th><th>Riferimenti</th></tr></thead>
<tbody>{bom_html}</tbody></table></div>

<h2>Cablaggio</h2>
<div class="two">
<div>
<h3>Piazzole verso l'esterno</h3>
<div class="tbl"><table>
<thead><tr><th>Piazzola</th><th>Posizione</th><th>Cosa collegare</th></tr></thead>
<tbody>{pads_html}</tbody></table></div>
</div>
<div>
<h3>Ponticelli e cavetti</h3>
<div class="tbl"><table>
<thead><tr><th>Nome</th><th>Riga/foro</th><th>Net</th></tr></thead>
<tbody>{links_html}</tbody></table></div>
<p class="cap">Encoder e tasti chiudono verso massa: attiva i pull-up interni in firmware. Le masse dei controlli
digitali si uniscono fuori scheda e arrivano tutte alla piazzola CTRL.</p>
</div>
</div>

<h2>Scheda I/O posteriore e cablaggi esterni</h2>
<p>Non è sulla veroboard: cablaggi per la schedina che porta MIDI, microSD, il deviatore INST/LINE e il jack pedale.
Alimentazione dalle piazzole IO 3V3D / IO GND.</p>

<h3>MIDI IN — jack TRS 3,5 mm tipo A</h3>
<div class="tbl"><table>
<thead><tr><th>Nodo</th><th>Collegato a</th></tr></thead>
<tbody>
<tr><td>Anello (pin 4 DIN)</td><td>220 Ω → anodo LED optoaccoppiatore H11L1M (pin 1)</td></tr>
<tr><td>Punta (pin 5 DIN)</td><td>catodo LED opto H11L1M (pin 2)</td></tr>
<tr><td>1N4148</td><td>antiparallelo sul LED, catodo verso il pin 1</td></tr>
<tr><td>H11L1M pin 6</td><td>+3V3D (piazzola IO 3V3D)</td></tr>
<tr><td>H11L1M pin 5</td><td>GND (piazzola IO GND)</td></tr>
<tr><td>H11L1M pin 4 (uscita)</td><td>piazzola "MIDI RX", pull-up 270 Ω a +3V3D</td></tr>
<tr><td>100 nF</td><td>tra +3V3D e GND, vicino all'opto</td></tr>
<tr><td>Manica jack</td><td>GND tramite 100 nF, non diretto</td></tr>
</tbody></table></div>
<p class="cap">Come da datasheet Seed3, fig. 7.1 e 7.3. L'opto isola la massa MIDI dalla massa audio; il diodo protegge
il LED dalla polarità inversa del loop di corrente MIDI.</p>

<h3>MIDI OUT — jack TRS 3,5 mm tipo A</h3>
<div class="tbl"><table>
<thead><tr><th>Nodo</th><th>Collegato a</th></tr></thead>
<tbody>
<tr><td>Piazzola "MIDI TX"</td><td>10 Ω → punta</td></tr>
<tr><td>+3V3D</td><td>10 Ω → anello</td></tr>
<tr><td>Manica jack</td><td>GND</td></tr>
</tbody></table></div>
<p class="cap">Come da datasheet Seed3, fig. 7.5: uscita a livello logico 3,3 V, senza opto, solo i due resistori
di corrente.</p>

<h3>microSD, modalità 1-bit</h3>
<div class="tbl"><table>
<thead><tr><th>Pin Seed</th><th>Pin scheda SD</th><th>Pull-up a +3V3D</th></tr></thead>
<tbody>
<tr><td>D4 (piazzola "SD D0")</td><td>DAT0</td><td>47 kΩ</td></tr>
<tr><td>D5 (piazzola "SD CMD")</td><td>CMD</td><td>47 kΩ</td></tr>
<tr><td>D6 (piazzola "SD CK")</td><td>CLK</td><td>nessuno</td></tr>
<tr><td>— (non collegato)</td><td>DAT1</td><td>47 kΩ</td></tr>
<tr><td>— (non collegato)</td><td>DAT2</td><td>47 kΩ</td></tr>
<tr><td>— (non collegato)</td><td>DAT3</td><td>47 kΩ</td></tr>
</tbody></table></div>
<p class="cap">Come da datasheet Seed3, fig. 5.1. Alimentazione dalle piazzole IO 3V3D / IO GND. DAT1-DAT3 restano
con pull-up sulla scheda SD ma non arrivano al Seed: modalità 1-bit, si leggono solo DAT0/CMD/CLK.</p>

<h3>Deviatore INST/LINE</h3>
<p>DPDT sul pannello posteriore, un polo per canale. In serie tra la punta del jack d'ingresso e la piazzola IN L / IN R
della scheda: Rs = 10 kΩ, sempre inserita. Dal lato scheda di Rs, Rsh = 3,3 kΩ verso GND attraverso il polo del
deviatore.</p>
<div class="tbl"><table>
<thead><tr><th>Deviatore</th><th>Modo</th><th>Attenuazione</th><th>Impedenza d'ingresso</th></tr></thead>
<tbody>
<tr><td>chiuso</td><td>LINE</td><td>−12 dB</td><td>~13 kΩ</td></tr>
<tr><td>aperto</td><td>INST</td><td>0 dB</td><td>~1 MΩ</td></tr>
</tbody></table></div>
<p class="cap">I due poli restano separati: un solo polo su entrambi i canali metterebbe in diafonia i due ingressi a
deviatore aperto. Il jack d'ingresso deve avere il contatto di commutazione della punta verso GND, così a jack
scollegato l'ingresso non fruscia.</p>

<h3>Jack TRS 6,35 mm "pedale"</h3>
<p>In parallelo ai tasti K1 e K2 sul pannello (vedi Piazzole verso l'esterno, FS1/FS2): punta = D0 (K1, bypass),
anello = D10 (K2, mono), manica = GND.</p>

<h3>True bypass stereo — footswitch 3PDT</h3>
<p>Sul pannello superiore, in basso a destra. Due poli scambiano le uscite fra effetto e ingresso diretto, il terzo
accende il LED accanto al footswitch. I nomi dei terminali seguono la funzione: sul 3PDT la fila centrale sono i
comuni, le due file esterne le due posizioni.</p>
<div class="tbl"><table>
<thead><tr><th>Polo</th><th>Comune</th><th>Posizione "effetto"</th><th>Posizione "bypass"</th></tr></thead>
<tbody>
<tr><td>A (sinistro)</td><td>punta jack OUT L</td><td>piazzola OUT L</td><td>punta jack IN L, prima di Rs</td></tr>
<tr><td>B (destro)</td><td>punta jack OUT R</td><td>piazzola OUT R</td><td>punta jack IN R, prima di Rs</td></tr>
<tr><td>C (LED)</td><td>catodo LED bypass</td><td>GND</td><td>libero</td></tr>
</tbody></table></div>
<p class="cap">Anodo del LED bypass tramite 1 kΩ a +3V3D, dalla scheda I/O: acceso a effetto inserito. In bypass
l'ingresso resta collegato anche al buffer da 1 MΩ, che non carica il segnale; il deviatore INST/LINE agisce solo
sul ramo effetto. R14/R18 da 100 kΩ tengono a massa i condensatori d'uscita: niente colpo alla commutazione.
Il bypass in DSP su K1 resta, per gli effetti con code che devono sfumare. Se vuoi che il firmware conosca lo
stato del 3PDT, collega il comune del polo C a D1 (libero, 5V-tollerante) invece che al LED.</p>

<h3>Componenti fuori scheda</h3>
<div class="tbl"><table>
<thead><tr><th>Tipo</th><th>Valore</th><th>Q.tà</th><th>Note</th></tr></thead>
<tbody>
<tr><td>OLED I2C</td><td>2,42", 128×64, SSD1309</td><td>1</td><td>molti moduli escono in SPI: sposta il ponticello I2C sul modulo</td></tr>
<tr><td>Tasto tattile 12×12</td><td>cappuccio tondo</td><td>2</td><td>K1, K2</td></tr>
<tr><td>Encoder</td><td>Bourns PEC11R</td><td>1</td><td>con pulsante</td></tr>
<tr><td>Potenziometro</td><td>Alpha 9 mm, 10K lineare</td><td>6</td><td></td></tr>
<tr><td>Optoaccoppiatore</td><td>H11L1M</td><td>1</td><td>MIDI IN</td></tr>
<tr><td>Diodo</td><td>1N4148</td><td>1</td><td>MIDI IN, antiparallelo al LED</td></tr>
<tr><td>Resistenza</td><td>220 Ω</td><td>1</td><td>MIDI IN, serie LED</td></tr>
<tr><td>Resistenza</td><td>270 Ω</td><td>1</td><td>MIDI IN, pull-up uscita opto</td></tr>
<tr><td>Resistenza</td><td>10 Ω</td><td>2</td><td>MIDI OUT</td></tr>
<tr><td>Resistenza</td><td>47 kΩ</td><td>5</td><td>pull-up microSD: DAT0, DAT1, DAT2, DAT3, CMD</td></tr>
<tr><td>Resistenza</td><td>10 kΩ</td><td>2</td><td>Rs deviatore INST/LINE, un canale ciascuna</td></tr>
<tr><td>Resistenza</td><td>3,3 kΩ</td><td>2</td><td>Rsh deviatore INST/LINE, un canale ciascuna</td></tr>
<tr><td>Condensatore ceramico</td><td>100 nF</td><td>2</td><td>decoupling opto, manica MIDI IN</td></tr>
<tr><td>Deviatore</td><td>DPDT</td><td>1</td><td>INST/LINE, pannello posteriore</td></tr>
<tr><td>Jack TRS 3,5 mm</td><td></td><td>2</td><td>MIDI IN, MIDI OUT</td></tr>
<tr><td>Jack TRS 6,35 mm</td><td></td><td>1</td><td>pedale esterno, in parallelo a K1/K2</td></tr>
<tr><td>Lettore microSD</td><td></td><td>1</td><td>slot o modulo breakout</td></tr>
<tr><td>Footswitch</td><td>3PDT, 9 terminali, boccola M12</td><td>1</td><td>true bypass stereo, pannello superiore</td></tr>
<tr><td>LED</td><td>3 mm</td><td>1</td><td>stato del bypass, accanto al footswitch</td></tr>
<tr><td>Resistenza</td><td>1 kΩ</td><td>1</td><td>LED bypass, da +3V3D</td></tr>
</tbody></table></div>

<h2>Collaudo</h2>
<ol class="steps">
<li>Continuità: ogni taglio aperto, nessun corto tra VA, VB, VIN e massa.</li>
<li>Alimenta a 9 V senza integrati e senza Seed. VA intorno a 8,6 V, VB metà di VA, VIN uguale a VA meno qualche decimo.</li>
<li>Inserisci U1 e U2. Le uscite dei quattro operazionali a riposo devono stare su VB.</li>
<li>Inserisci il Seed3 e carica un passthrough. Segnale in, segnale out, niente altro.</li>
<li>Solo dopo, collega pot, encoder, OLED, tasti e footswitch, uno alla volta.</li>
</ol>

<h2>Limiti da conoscere</h2>
<p>U1 e U2 sono TLC2272 al posto del TL072: il TL072 ha il modo comune d'ingresso che parte
~3 V sopra la massa, quindi l'inseguitore d'ingresso a VB ≈ 4,3 V arrivava solo a ~2,6 Vpp contro i 3,6 Vpp di fondo
scala del codec; il TLC2272 accetta da 0 V a 1,5 V sotto il positivo, ~5,5 Vpp intorno a VB. Rumore 9 nV/√Hz, il doppio
dell'OPA1652 dei circuiti del datasheet Seed3 (che è solo SMD): con una chitarra collegata domina il rumore dei pickup. Con una sorgente di linea molto calda il segnale può comunque superare il fondo scala del Seed3 attraverso
il buffer a guadagno unitario: in quel caso metti un partitore prima di J IN.</p>
<p>Il rumore sarà peggiore di un PCB a quattro strati con piano di massa. Cavetto schermato su ingressi e uscite, fili dei
pot corti e lontani dal Seed, e hai fatto quello che il veroboard permette.</p>
</main>
</body>
</html>
"""
open("prototipo-veroboard-seed3.html", "w").write(page)
print("pagina ok", len(page))
