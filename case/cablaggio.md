# PA-TELAIO: cablaggio del case stampato

Generato da `case/cablaggio.py` (`cd case && uv run cablaggio.py --scrivi-md`). Le coordinate dei capi e le
lunghezze vengono dal modello `case/case.py` e dai layout; se cambiano, rilancia lo script e rileggi questa pagina.
Le posizioni dei terminali dentro i corpi (jack, deviatori, pot, encoder, footswitch, OLED) sono STIME dalle misure
di ingombro: prima di tagliare i fili controllali sul pezzo vero.

## Regole

- **Ingressi schermati**: ogni filo audio d'ingresso (jack IN, nodo INST/LINE, PRE, schedina, bypass) e' un cavetto
  schermato (un conduttore, calza). La calza va a massa **da un solo lato** (colonna `calza`), mai da tutti e due: l'altro
  capo resta tagliato corto e isolato con guaina.
- **Rs 10 kOhm sul jack**: la Rs d'ingresso e' saldata sulla punta del jack IN, cosi il cavo dopo la Rs vede 10 kOhm piu la
  sorgente e non la sorgente nuda. Rsh 3,3 kOhm: fra il terminale LINE del deviatore INST/LINE e il giunto di massa del
  deviatore (stesso giunto del filo `IN x f` e delle calze).
- **Alimentazione intrecciata**: DC (+9 V e massa), VA e massa della schedina, 3V3D e massa di OLED, MIDI e microSD, e i due
  capi di ogni gang del GAIN, intrecciati a coppie (circa 3 giri per cm). Il taglio e' gia maggiorato del 10 %.
- **I2C corto**: SCL e SDA affiancati, il piu corti possibile, lontani dai fili d'ingresso e dai cursori dei pot.
  Cursori dei pot: lontani dall'I2C e dal clock della microSD.
- Piu fili nello stesso foro (massa controlli, 3V3D/GND della scheda I/O, massa OUT): al massimo due per foro; se non
  entrano, un giunto di massa sul filo.
- Sezione: AWG 24-26 per alimentazione, AWG 26-28 per segnali.

## Convenzioni di calcolo

- Lunghezza di taglio = percorso a gambe assiali in 3D (salita sul capo piu basso, tratto orizzontale alla quota piu alta,
  x poi y) piu un margine: **12 mm fissi** (6 per capo: spelatura e saldatura) piu **10%** del percorso per i giri
  intorno ai corpi, piu 10% se intrecciato; arrotondata per eccesso a 5 mm.
- Un filo che incontra un corpo passa da un punto intermedio (colonna `via` nello script) cercato su griglia: il piu corto
  che lo libera. I fili del footswitch escono dalla fessura della torre.
- Per PRE: DPDT, un polo per canale, commuta l'USCITA (comune = piazzola IN della veroboard; OFF = nodo INST/LINE; ON = OUT
  schedina). L'ingresso della schedina resta sempre sul nodo INST/LINE (con un polo per canale non si commutano i due capi):
  con PRE spento la schedina carica comunque il nodo con ~1 MOhm in parallelo e resta alimentata.

## Orientamento della schedina preamp

**Scelta: A identica (provvisoria).** In `case.py` aggiungere `SCHEDINA_ORI = dict(foro=+1, striscia=+1, trasposta=False)`
(`foro=+1`: foro 0 verso x/y minore dell'asse su cui cade; `-1`: verso il maggiore; `trasposta`: i fori corrono lungo Y)
e usare `x0, y0 = (122, 51)`. Colonnine sui fori (21,1) e (21,16):
`(176.61, 54.81)`, `(176.61, 92.91)` (x, y del case).

| Opzione | Origine (x0, y0) | IN b | GAIN | OUT d | Punteggio | Catena IN (mm) | Distanza dai digitali (mm) | Piu vicino |
|---|---|---|---|---|---|---|---|---|
| A identica (provvisoria) **(scelta)** | (122, 51) | 190 | 343 | 249 | 657 | 933 | 3.7 | filo ENC SW |
| B foro 0 verso x maggiore | (122, 51) | 307 | 515 | 132 | 889 | 933 | 4.3 | filo ENC SW |
| C striscia 0 verso y maggiore | (122, 51) | 190 | 343 | 249 | 657 | 933 | 3.7 | filo ENC SW |
| D ruotata 180 | (122, 51) | 307 | 515 | 132 | 889 | 933 | 4.3 | filo ENC SW |
| E trasposta, foro 0 y-, str 0 x- | (122, 35) | 308 | 518 | 134 | 893 | 936 | 4.3 | filo ENC SW |
| F trasposta, foro 0 y-, str 0 x+ | (122, 35) | 309 | 518 | 134 | 894 | 937 | 4.3 | filo ENC SW |
| G trasposta, foro 0 y+, str 0 x- | (122, 35) | 192 | 346 | 251 | 663 | 937 | 3.7 | filo ENC SW |
| H trasposta, foro 0 y+, str 0 x+ | (122, 35) | 192 | 346 | 251 | 663 | 937 | 3.7 | filo ENC SW |

Lunghezze di percorso, L+R. IN b = nodo INST/LINE -> ingresso schedina; GAIN = i 4 fili del pot; OUT d = uscita schedina -> PRE;
punteggio = IN b + GAIN + 0.5 x OUT d (ingresso e GAIN sono i nodi piu sensibili). Provvisoria: IN b 190 mm, GAIN 343 mm;
scelta: IN b 190 mm, GAIN 343 mm. Catena d'ingresso completa (IN a-e, L e R): 933 -> 933 mm di percorso.

## Fili da tagliare

Lunghezza = percorso nominale; taglio = con margine, arrotondato. Colore: suggerimento (L bianco, R rosso, massa nera,
alimentazioni rosso/arancione). Schermato: cavetto con calza, calza a massa dal lato indicato.

| Filo | Da | A | Segnale | Tipo | Colore | Perc. (mm) | Taglio (mm) | Schermato | Calza a massa dal lato | Nota |
|---|---|---|---|---|---|---|---|---|---|---|
| IN L a | JIL:rs | ILS:COM L | IN L | schermato | bianco | 86 | **110** | si | lato INST/LINE | punta (con Rs 10k) -> deviatore INST/LINE (via) |
| IN L b | ILS:COM L | SC:IN L | IN L | schermato | bianco | 119 | **145** | si | lato schedina | nodo INST/LINE -> ingresso schedina (via) |
| IN L c | ILS:COM L | PRE:OFF L | IN L | schermato | bianco | 67 | **90** | si | lato INST/LINE | nodo INST/LINE -> PRE, posizione OFF (via) |
| IN L d | SC:OUT L | PRE:ON L | IN L | schermato | bianco | 131 | **160** | si | lato schedina | uscita schedina -> PRE, posizione ON (via) |
| IN L e | PRE:COM L | VB:IN L | IN L | schermato | bianco | 49 | **70** | si | lato veroboard | PRE comune -> piazzola IN della veroboard (via) |
| IN L f | ILS:GND L | JIL:sleeve | GND | normale | nero | 101 | **125** | no | - | giunto di massa di Rsh/calze -> manicotto IN (via) |
| IN L g | JIL:sleeve | VB:IN L GND | GND | normale | nero | 63 | **85** | no | - | manicotto IN -> piazzola GND (via) |
| BYP L | JIL:tip | FS:A byp | IN L | schermato | bianco | 156 | **185** | si | lato jack | ingresso diretto -> 3PDT, posizione bypass (via) |
| OUT L a | VB:OUT L | FS:A eff | OUT L | normale | bianco | 140 | **170** | no | - | veroboard (100R) -> 3PDT, posizione effetto (via) |
| OUT L b | FS:A com | JOL:tip | OUT L | schermato | bianco | 107 | **135** | si | lato jack | 3PDT comune -> punta jack OUT (in bypass porta il segnale diretto) (via) |
| OUT L c | JOL:sleeve | VB:OUT L GND | GND | normale | nero | 80 | **100** | no | - | manicotto OUT -> piazzola GND (via) |
| IN R a | JIR:rs | ILS:COM R | IN R | schermato | rosso | 101 | **125** | si | lato INST/LINE | punta (con Rs 10k) -> deviatore INST/LINE (via) |
| IN R b | ILS:COM R | SC:IN R | IN R | schermato | rosso | 71 | **90** | si | lato schedina | nodo INST/LINE -> ingresso schedina (via) |
| IN R c | ILS:COM R | PRE:OFF R | IN R | schermato | rosso | 67 | **90** | si | lato INST/LINE | nodo INST/LINE -> PRE, posizione OFF (via) |
| IN R d | SC:OUT R | PRE:ON R | IN R | schermato | rosso | 118 | **145** | si | lato schedina | uscita schedina -> PRE, posizione ON (via) |
| IN R e | PRE:COM R | VB:IN R | IN R | schermato | rosso | 123 | **150** | si | lato veroboard | PRE comune -> piazzola IN della veroboard (via) |
| IN R f | ILS:GND R | JIR:sleeve | GND | normale | nero | 116 | **140** | no | - | giunto di massa di Rsh/calze -> manicotto IN (via) |
| IN R g | JIR:sleeve | VB:IN R GND | GND | normale | nero | 158 | **190** | no | - | manicotto IN -> piazzola GND (via) |
| BYP R | JIR:tip | FS:B byp | IN R | schermato | rosso | 141 | **170** | si | lato jack | ingresso diretto -> 3PDT, posizione bypass (via) |
| OUT R a | VB:OUT R | FS:B eff | OUT R | normale | rosso | 92 | **115** | no | - | veroboard (100R) -> 3PDT, posizione effetto (via) |
| OUT R b | FS:B com | JOR:tip | OUT R | schermato | rosso | 126 | **155** | si | lato jack | 3PDT comune -> punta jack OUT (in bypass porta il segnale diretto) (via) |
| OUT R c | JOR:sleeve | VB:OUT R GND | GND | normale | nero | 175 | **205** | no | - | manicotto OUT -> piazzola GND (via) |
| SC VA | VB:VA EXT | SC:VA | VA | intrecciato | rosso | 38 | **60** | no | - | VA -> schedina (piazzola VA EXT, 29/10) |
| SC GND | VB:PRE GND | SC:GND | GND | intrecciato | nero | 48 | **75** | no | - | massa schedina (piazzola PRE GND, 29/10) |
| GAIN A L | SC:GAIN A L | GAIN:A L | GAIN L | intrecciato | bianco | 106 | **145** | no | - | S1 -> capo A della gang (via) |
| GAIN B L | SC:GAIN B L | GAIN:B L | GAIN L | intrecciato | bianco | 106 | **145** | no | - | 220R -> capo B della gang (via) |
| GAIN A R | SC:GAIN A R | GAIN:A R | GAIN R | intrecciato | rosso | 70 | **100** | no | - | S1 -> capo A della gang (via) |
| GAIN B R | SC:GAIN B R | GAIN:B R | GAIN R | intrecciato | rosso | 60 | **90** | no | - | 220R -> capo B della gang (via) |
| F0 | MASSA:L0 | JIL:sleeve | GND | normale | nero | 36 | **55** | no | - | punto unico di massa -> manicotto IN L |
| F1 | MASSA:L0 | MASSA:L1 | GND | normale | nero | 75 | **95** | no | - | rame del pannello posteriore -> rame del fondo (via) |
| DC +9V | VB:DC +9V | DC:sleeve | +9V | intrecciato | rosso | 59 | **90** | no | - | +9 V al manicotto |
| DC GND | VB:DC GND | DC:center | GND | intrecciato | nero | 69 | **100** | no | - | massa al centrale |
| K1 | VB:FS1 | TASTI:D0 | D0 | normale | giallo | 94 | **120** | no | - | tasto K1 (via) |
| K2 | VB:FS2 | TASTI:D10 | D10 | normale | verde | 80 | **105** | no | - | tasto K2 (via) |
| KGND | VB:CTRL GND | TASTI:GND | GND | normale | nero | 71 | **95** | no | - | massa tasti e LED |
| LED | VB:LED | TASTI:LED+ | LED | normale | viola | 112 | **140** | no | - | LED (1K sulla scheda) |
| PED tip | JP:tip | TASTI:D0 | D0 | normale | giallo | 147 | **175** | no | - | pedale punta, in parallelo a K1 (via) |
| PED ring | JP:ring | TASTI:D10 | D10 | normale | verde | 148 | **175** | no | - | pedale anello, in parallelo a K2 (via) |
| PED sleeve | JP:sleeve | TASTI:GND | GND | normale | nero | 149 | **180** | no | - | pedale manicotto (via) |
| ENC A | VB:ENC A | ENC:A | ENC_A | normale | giallo | 110 | **135** | no | - |  |
| ENC B | VB:ENC B | ENC:B | ENC_B | normale | verde | 95 | **120** | no | - |  |
| ENC SW | VB:ENC SW | ENC:SW | ENC_SW | normale | blu | 104 | **130** | no | - |  |
| ENC GND | VB:CTRL GND | ENC:C | GND | normale | nero | 123 | **150** | no | - | massa encoder |
| ENC ponte | ENC:C | ENC:SW2 | GND | normale | nero | 10 | **25** | no | - | ponticello fra comune e 2o pin del pulsante (sull'encoder) |
| OLED SCL | VB:SCL | OLED:SCL | SCL | normale | giallo | 63 | **85** | no | - | I2C: corto, accanto a SDA (via) |
| OLED SDA | VB:SDA | OLED:SDA | SDA | normale | verde | 63 | **85** | no | - | I2C: corto, accanto a SCL (via) |
| OLED 3V3 | VB:3V3D | OLED:VCC | 3V3D | intrecciato | arancione | 53 | **80** | no | - |  |
| OLED GND | VB:OLED GND | OLED:GND | GND | intrecciato | nero | 58 | **85** | no | - |  |
| MIDI TX | VB:MIDI TX | MIDI:TX | MIDI_TX | normale | blu | 30 | **45** | no | - |  |
| MIDI RX | VB:MIDI RX | MIDI:RX | MIDI_RX | normale | viola | 31 | **50** | no | - |  |
| MIDI 3V3 | VB:IO 3V3D | MIDI:3V3 | 3V3D | intrecciato | arancione | 112 | **150** | no | - |  (via) |
| MIDI GND | VB:IO GND | MIDI:GND | GND | intrecciato | nero | 109 | **145** | no | - |  (via) |
| SD D0 | VB:SD D0 | SD:D0 | SD_D0 | normale | grigio | 37 | **55** | no | - |  |
| SD CMD | VB:SD CMD | SD:CMD | SD_CMD | normale | marrone | 38 | **55** | no | - |  |
| SD CLK | VB:SD CK | SD:CLK | SD_CK | normale | bianco | 38 | **55** | no | - | clock: il piu corto possibile |
| SD 3V3 | VB:IO 3V3D | SD:3V3 | 3V3D | intrecciato | arancione | 84 | **120** | no | - |  (via) |
| SD GND | VB:IO GND | SD:GND | GND | intrecciato | nero | 90 | **125** | no | - |  (via) |
| POT1 W | VB:A0 | POT1:W | A0 | normale | grigio | 136 | **165** | no | - | cursore, lontano dall'I2C (via) |
| POT2 W | VB:A1 | POT2:W | A1 | normale | grigio | 167 | **200** | no | - | cursore, lontano dall'I2C (via) |
| POT3 W | VB:A2 | POT3:W | A2 | normale | grigio | 197 | **230** | no | - | cursore, lontano dall'I2C (via) |
| POT4 W | VB:A3 | POT4:W | A3 | normale | grigio | 102 | **125** | no | - | cursore, lontano dall'I2C |
| POT5 W | VB:A4 | POT5:W | A4 | normale | grigio | 132 | **160** | no | - | cursore, lontano dall'I2C (via) |
| POT6 W | VB:A5 | POT6:W | A5 | normale | grigio | 163 | **195** | no | - | cursore, lontano dall'I2C (via) |
| 3V3A P4 | VB:3V3A | POT4:HI | 3V3A | normale | arancione | 94 | **120** | no | - | catena a margherita |
| 3V3A P5 | POT4:HI | POT5:HI | 3V3A | normale | arancione | 28 | **45** | no | - | catena a margherita |
| 3V3A P6 | POT5:HI | POT6:HI | 3V3A | normale | arancione | 28 | **45** | no | - | catena a margherita |
| 3V3A P3 | POT6:HI | POT3:HI | 3V3A | normale | arancione | 42 | **60** | no | - | catena a margherita |
| 3V3A P2 | POT3:HI | POT2:HI | 3V3A | normale | arancione | 28 | **45** | no | - | catena a margherita |
| 3V3A P1 | POT2:HI | POT1:HI | 3V3A | normale | arancione | 28 | **45** | no | - | catena a margherita |
| AGND P1 | VB:POT GND | POT1:LO | AGND | normale | nero | 105 | **130** | no | - | catena a margherita (via) |
| AGND P2 | POT1:LO | POT2:LO | AGND | normale | nero | 28 | **45** | no | - | catena a margherita |
| AGND P3 | POT2:LO | POT3:LO | AGND | normale | nero | 28 | **45** | no | - | catena a margherita |
| AGND P6 | POT3:LO | POT6:LO | AGND | normale | nero | 42 | **60** | no | - | catena a margherita |
| AGND P5 | POT6:LO | POT5:LO | AGND | normale | nero | 28 | **45** | no | - | catena a margherita |
| AGND P4 | POT5:LO | POT4:LO | AGND | normale | nero | 28 | **45** | no | - | catena a margherita |
| LEDFS + | VB:VA EXT | FS:C com | LEDFS | normale | arancione | 123 | **150** | no | - | VA -> R 4,7k saldata sul lug comune del polo C (~1,5 mA a 8,5 V con LED rosso) (via) |
| LEDFS A | FS:C eff | LEDFS:A | LEDFS | normale | arancione | 48 | **65** | no | - | polo C, posizione effetto -> anodo (via) |
| LEDFS K | LEDFS:K | VB:OUT R GND | GND | normale | nero | 64 | **85** | no | - | catodo -> massa piu vicina (OUT R GND); ~1 mA continui |

### Totali per tipo

| Tipo | Fili | Lunghezza di taglio totale |
|---|---|---|
| intrecciato | 14 | 1510 mm (1.51 m) |
| normale | 50 | 5365 mm (5.37 m) |
| schermato | 14 | 1820 mm (1.82 m) |

Componenti fuori scheda da saldare (non sono fili): Rs 10 kOhm sulla punta di IN L e IN R; Rsh 3,3 kOhm fra LINE e il giunto
di massa del deviatore INST/LINE (due, uno per canale); 1K in serie al LED dei tasti (sulla scheda tasti); 4,7 kOhm sul lug comune del polo C del 3PDT, in serie al LED del bypass;
47 kOhm sui due terminali usati di ogni gang del pot GAIN.

## Problemi aperti

- Fili lunghi (taglio >= 150 mm): POT3 W (230), OUT R c (205), POT2 W (200), POT6 W (195), IN R g (190), BYP L (185), PED sleeve (180), PED tip (175), PED ring (175), OUT L a (170), BYP R (170), POT1 W (165), IN L d (160), POT5 W (160), OUT R b (155), IN R e (150), ENC GND (150), MIDI 3V3 (150), LEDFS + (150).
