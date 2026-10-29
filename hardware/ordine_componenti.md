# PA-TELAIO — ordine componenti (28/09/2026)

Deciso:
- prima la **veroboard**; la PCB dopo le prove a banco;
- operazionali **TLC2272 in DIP-8**, niente adattatori SOIC;
- il **Seed3 c'è già** (`docs/storico/PA_ordine_125b_Seed3.xlsx`, "Già acquistato").

**Tutte le strade restano aperte** (vedi `../CLAUDE.md`, Stato). Il contenitore decide jack da 6,35, jack DC,
cappucci dei tasti e minuteria; il resto è uguale per tutte. Niente è ancora ordinato.

Prezzi letti il 28/09 sulle pagine prodotto. "n.v." = non verificato su una pagina. Tayda in dollari: al
cambio di circa 0,86 € per dollaro (da ricontrollare).

| Strada | Ordini | Totale indicativo |
|---|---|---|
| Scatola 1590DD da Tayda, forata a macchina | Tayda, Musikding, TME, Amazon, Exploding Shed | circa 150-170 € |
| Scatola 1590DD da Musikding, forata a mano con la dima | Musikding, TME, Amazon, Exploding Shed | circa 170-180 € (stima) |
| Case stampato, in casa o da un servizio, coi pezzi su cui è disegnato | Banzai, TME, Amazon, Exploding Shed, Musikding per la stripboard | circa 190-200 €, più la stampa (servizio: 97-261 €) |

Per tutte le strade c'è anche la **variante AliExpress** (06/10): tutto il generico da AliExpress, e restano solo
TME, l'OLED ed eventualmente Tayda. È nella sezione prima della lista completa.

## Comune a tutte le strade

**TME** (spedizione 7,20 € IVA inclusa; prezzi TME probabilmente IVA esclusa):

| Parte | Q.tà | € |
|---|---|---|
| TLC2272IP, DIP-8 (175 disponibili; il TLC2272CP costa 4,90) | 3 | 12,12 |
| Encoder Bourns PEC11R-4220K-S0024 (657 disponibili) | 1 | 1,68 |
| H11L1M, se non arriva da Tayda (1361 disponibili) | 1 | 0,37 |

**Amazon.it:** OLED Waveshare 2,42" bianco, SKU 25742 (B0CL6WMHJN), 21,99 €; il 28/09 ne restavano 2. Deve
essere proprio il Waveshare: i cloni hanno un altro circuito. Dal sito Waveshare costa 12,99 $ più la
spedizione. Nello stesso ordine va la minuteria M2,5 della strada scelta, e la colla stick se si stampa in casa.

**Exploding Shed** (Germania): jack MIDI Thonkiconn Stereo WQP419GR, filettati M6×0,5 (il successore del
PJ366ST), 3 × 0,57 €, più 20 dadi M6×0,5 zigrinati a 1,10 € (il jack arriva senza dado) e 15 € di spedizione
DHL. In tutto circa 18 €. Tayda, TME e Musikding non li hanno; il Lumberg 1503 09 di TME è a 90° ed esaurito.
Se il MIDI può aspettare, quest'ordine si rimanda. Thonk (Regno Unito) vende anche la versione senza filetto:
da evitare, e ha dogana.

**Rimandato:** lettore microSD Adafruit 4682 (DigiKey 3,00 €). Per il primo collaudo non serve. I moduli "per
Arduino" (AMS1117 + 74LVC125) non vanno: funzionano solo in SPI.

## Strada 1590DD da Tayda, forata a macchina: circa 150-170 €

### Tayda: scatola forata e quasi tutto il resto

| Parte | Codice | Q.tà | $ |
|---|---|---|---|
| Scatola 1590DD verniciata, colore a scelta (nera A-5907) | A-5907 | 1 | 14,99 |
| Foratura CNC con la finestra dell'OLED, dalla dashboard drill.taydakits.com. File `case/out/scatola/coordinate_tayda_verniciata.csv` (+0,4 mm per la verniciatura); con la grezza A-5141 ($9,99) il file è `coordinate_tayda.csv` | servizio | 1 | 4,50 |
| Stampa UV sul pannello (facoltativa) | servizio | 1 | 4,00 |
| Footswitch 3PDT | A-5509 | 1 | 2,30 |
| Pot Alpha RD901F-40-15R1-B10K (179 disponibili) | A-1847 | 6 | 7,74 |
| Manopola Davies 1900H clone, albero 6,35 col grano, Ø 12,7 | A-4564 (bianca) o altro colore | 6 | 2,52 |
| Jack 6,35 stereo PJ-629HAN in metallo: OUT L, OUT R, pedale | A-1121 | 3 | 1,35 |
| Jack DC 2,1 a telaio chiuso | A-2237 | 1 | 0,13 |
| Deviatore mini DPDT on-on | A-4568 | 1 | 0,59 |
| Tasto 12×12×7,3 | A-4812 | 2 | 0,18 |
| Cappuccio tondo nero | A-4814 | 2 | 0,12 |
| LED 3 mm | n.v. | 2 | ~0,10 |
| Optoaccoppiatore H11L1M | A-3697 | 1 | 0,50 |
| Header femmina 20 pin | A-1310 | 2 | 0,28 |
| Zoccoli DIP-8 ×2 e DIP-6 ×1 | n.v. | 3 | ~0,15 |
| Vite M3×12 a testa tonda (veroboard, dal fondo) | A-1253 | 4 | 0,07 |
| Dado M3 | A-1247 | 4 | 0,08 |
| Piedini 12×4 mm, blocco da 64 (facoltativi) | A-7506 | 1 | 5,90 |
| Resistenze, condensatori, 1N5817, 1N4148, filo, cavetto schermato | vedi lista completa | | ~7 (n.v.) |
| **Merce** | | | **~43** (~53 con UV e piedini) |
| **Spedizione DDP**, IVA e dogana comprese (dato dai forum, n.v.) | | | 23-38 |

Totale circa $65-90, cioè circa 56-77 €.

### Musikding: jack d'ingresso, stripboard, manopola dell'encoder

| Parte | Q.tà | € |
|---|---|---|
| Switchcraft 12A, jack 6,35 mono con commutazione sulla punta, per IN L e IN R (poche scorte: se mancano, Banzai SC-12A a 3,25 €) | 2 | 9,80 |
| Stripboard 100×160: dalla foto le strisce corrono lungo il lato da 100, cioè 39 fori × 63 strisce | 1 | 2,75 |
| Rillenknopf 21 mm, a pressione per l'albero 18T dell'encoder | 1 | 2,60 |
| **Merce** | | **15,15** |
| **Spedizione** | | 5,90-6,90 |

Totale circa 21 €. La stripboard serve almeno di 30 fori × 45 strisce (76 × 114 mm): quelle Tayda sono troppo
piccole (la più grande è 110 × 93), TME non ne ha.

### Minuteria M2,5, su Amazon insieme all'OLED

Un kit di viti M2,5 a testa bombata con dadi, che contenga M2,5×8 e M2,5×12 (da scegliere, n.v.):
- 4 viti M2,5×8 per le staffe dell'OLED, avvitate nel PETG (fori pilota da 2,2);
- 2 viti M2,5×12 con 2 dadi per la scheda tasti: dal pannello attraversano il distanziale e la millefori, dado
  sotto.

Su TME le ISO 7380 M2,5×8 ci sono (B2.5X8/BN19, 9600 disponibili, 7,52 € la confezione minima, n.v.), le M2,5×12
no (esaurite). In alternativa per le staffe: le svasate Tayda A-8940 M2,5×10 a 0,06 $, svasando a mano i fori
(punta a 90°, circa 1 mm su 2,5).

### Jack 6,35: le tre combinazioni

La sessione della stampa ha verificato sui datasheet, e nel modello, che nella 1590DD entrano tutti:
- **Switchcraft 12A** (IN L/R): metallo, contatto di commutazione sulla punta, telaio Ø 19,1 × 26,6.
- **Tayda A-1121** (OUT L/R e pedale): stereo in metallo, filetto 3/8"-32, corpo 15,8×15,8, profondo 23,5 più
  3,6 di pin. Entra anche meglio del 12A. Sulle uscite il contatto di commutazione non serve; il pedale vuole
  proprio lo stereo.
- **Tayda A-6042** (PJ-645C, mono commutato, 0,49 $): entra, ma i pin vanno montati verso l'alto o di lato. Il
  filetto è di plastica e corto: su 3,4 mm di parete il dado prende poco (le recensioni Tayda parlano di
  rondelle sulle 1590).

| Combinazione | Costo | Note |
|---|---|---|
| Mista, nel carrello sopra: 12A sugli ingressi, A-1121 sul resto | base | verificata nel modello (112 corpi con i pezzi interni) |
| Tutti Switchcraft da Musikding: 12A ×4 e 12B | circa +13 € | i più robusti |
| Tutti Tayda: A-6042 sugli ingressi | circa -9 € | gli ingressi, i jack più usati, restano i più deboli |

## Strada 1590DD da Musikding, forata a mano: circa 170-180 € (stima)

La scatola "Alu-Gehäuse Typ DD" (16,50 €, poche scorte) e quasi tutti i pezzi da Musikding, forando a mano con
la dima 1:1 (`case/out/scatola/dima_1590DD.pdf`). La finestra dell'OLED, 57 × 30 mm, a mano è il lavoro più
lungo di tutto il montaggio.

Da Musikding, oltre alla scatola: 3PDT 3,90 €; pot 9 mm 10k lineari 2,20 € (albero dichiarato 10 mm, n.v.);
manopole mini a indice 16 mm 0,85 €; Rillenknopf 21 mm 2,60 €; Switchcraft 12A 4,90 € e 12B 4,40 €; jack DC
0,55 € (foro 12); deviatore DPDT 0,80 €; tasti 0,45 € (senza cappucci); LED 0,08 €; zoccoli 0,08/0,06 €;
stripboard 100×160 2,75 €; passivi e filo (~11 €, n.v.). Musikding non ha H11L1M, header femmina 1×20,
cappucci dei tasti, TLC2272 (ha il TLC2262, stessa famiglia ma più lento) né l'encoder: vanno su TME.

### Tayda contro Musikding, stesse parti, con la 1590DD

| Parte | Q.tà | Tayda | Musikding |
|---|---|---|---|
| Scatola 1590DD | 1 | verniciata $14,99; foratura CNC $4,50 con la finestra dell'OLED; stampa UV $4,00 | 16,50 €, da forare a mano |
| Footswitch 3PDT | 1 | A-5509 $2,30 | 3,90 € |
| Pot Alpha 9 mm B10K | 6 | A-1847 $1,29 | 2,20 € |
| Manopole per i pot | 6 | Davies 1900H clone $0,42 | mini a indice 16 mm 0,85 € |
| Manopola encoder | 1 | col grano $0,42 (non centra perfetto sul 18T) | Rillenknopf 21 mm 2,60 € |
| Jack DC 2,1 | 1 | A-2237 $0,13 | 0,55 € |
| Deviatore DPDT on-on | 1 | A-4568 $0,59 | 0,80 € |
| Tasto + cappuccio | 2 + 2 | $0,09 + $0,06 | 0,45 €, cappucci no |
| H11L1M | 1 | $0,50 | no |
| Header femmina 1×20 | 2 | $0,14 | no |
| Stripboard | 1 | troppo piccole | 100×160, 2,75 € |
| Operazionali | 3 | TLC2272CP esaurito | TLC2262 2,50 € |
| Spedizione | | DDP $23-38 (forum, n.v.) | 5,90-6,90 € |

## Strade col case stampato (in casa o da un servizio): circa 190-200 €

Il case stampato è disegnato su pezzi diversi da quelli dei carrelli 1590DD. Due possibilità:
- comprare i pezzi che `case.py` si aspetta (sotto);
- oppure comprare i pezzi dei carrelli 1590DD e **riallineare `case.py` prima di stampare i pannelli**: jack DC
  foro 12, jack 12A/A-1121 più grandi dell'ingombro previsto, cappucci Tayda (vedi `../CLAUDE.md`, Case).

**Banzai** (Germania), parti da pedale che entrano nel case così com'è: 51,14 € + 8,95 € di spedizione =
60,09 €.

| Parte | Prodotto | € |
|---|---|---|
| Jack 6,35 mono con commutazione sulla punta ×4 | Switchcraft 112AX (15,7 × 15,7, profondo 28,0 con le linguette, foro 9,8-10) | 19,48 |
| Jack 6,35 stereo (pedale) | Switchcraft 112BX | 4,51 |
| Jack DC | Lumberg NEB/J 21C: foro a D Ø 12,8 con piatto a 11,8, flangia Ø 16, dado da 14, lungo 18,3 (il modello ha foro tondo da 11: da cambiare) | 1,18 |
| 3PDT, pot Alpha 9 mm ×6 (liscio 6,3, M7 da 5), manopole Ribby-16 ×6, manopola encoder DKN-2101 (Ø 21,5 a pressione), DPDT | | resto |

Più:
- **TME** come sopra, più tasti 12×12×7,3 con cappuccio tondo (DigiKey: Omron B3F-4055 + B32-1610 Ø 9,5, contro
  gli 11,8 previsti dal modello), header, zoccoli, passivi;
- **Musikding** per la stripboard (un ordine in più; Banzai forse ce l'ha, n.v.);
- **Amazon**, minuteria: inserti ruthex M3×5,7 (100 pezzi, 9,99 €), viti M3×14 (20 pezzi, 8,69 €), autofilettanti
  M3×6 e M2,5×8 (due kit, 21,38 €), piedini, colla stick (6,19 €, se in casa);
- **Exploding Shed** per i jack MIDI, come sopra.

Da un servizio si aggiunge la stampa: preventivi del 28/09 da 96,75 € + IVA (Weerg, MJF grigio) a 261 € (MJF
nero prodotto in Europa). Dettagli in `../case/servizio_stampa.md`.

## Da sapere al montaggio nella 1590DD

- **Pot Alpha:** sul pannello da 2,5 mm oltre il dado resta 0,5 mm di filetto. Niente rondella sotto il dado.
- **Jack del pedale (A-1121):** pin verso l'alto, non piegarli verso la scheda. Con i pin è profondo 27,1 mm e
  arriva a 0,9 mm dal bordo posteriore della veroboard.
- **Tasti:** foro da 12,0; la flangia da 12,8 resta sotto il pannello e fa da fermo, il tasto sporge 1,8 mm.
  Scheda tasti su millefori con 2 viti visibili; in alternativa pulsanti da pannello con dado, da ridisegnare
  nella dima.
- **LED:** niente portaLED. Foro da 3,2, il LED entra da dentro e si incolla.
- **OLED:** niente header a pin dritti saldati sul modulo, perché scenderebbero fino al Seed. Fili saldati
  direttamente sulle piazzole, oppure header a 90°.
- **Veroboard:** 4 viti M3×12 dal fondo attraverso le colonnine da 4 mm e la veroboard, dado sopra.
- **Jack MIDI, verifica all'arrivo:** i Thonkiconn sono già alla quota più bassa possibile (centro a 9,8 mm).
  Lì la parete è 3,1 mm sul disegno Hammond: col filetto da 4,5 restano 1,4 mm per il dado, circa 3 giri a passo
  0,5. Dovrebbe tenere, ma la scatola Tayda è un clone e può essere diversa. Se il dado non prende, spiana
  0,2-0,3 mm da dentro intorno al foro, a mano, con una punta a fondo piatto Ø 12. Il Cliff FC681374V non va
  meglio: filetto 4,5 e ghiera 2,0, quindi al massimo 2,5 mm di parete.

Dettagli e punti aperti della scatola: `../case/scatola_1590DD.md`.

## Variante AliExpress (06/10, prezzi non cercati)

Da AliExpress si prende tutto il generico. Restano fuori:
- **TME:** TLC2272IP ×3, encoder Bourns PEC11R ×1 e H11L1M ×1, circa 14 € più 7,20 € di spedizione.
  - Gli operazionali TI su AliExpress sono spesso falsi o rimarcati.
  - L'encoder è quello su cui sono disegnati il case e la scatola.
  - Se mancano, su TME vanno anche i ceramici C0G da 100 pF, 390 pF e 2,2 nF: su AliExpress il dielettrico non è
    garantito.
- **OLED:** solo il Waveshare 2,42" (SKU 25742), perché i cloni hanno un altro circuito. Su AliExpress va bene solo
  dal negozio ufficiale Waveshare, se lo vende (n.v.); altrimenti Amazon.
- **Tayda:** solo per la 1590DD forata a macchina (scatola, foratura, stampa UV).

I pezzi generici cambiano da venditore a venditore. Quindi l'ordine è questo:
1. arriva AliExpress;
2. si misurano i pezzi;
3. si riallineano `case.py` o il file di foratura Tayda;
4. solo dopo si stampa o si ordina la foratura.

### Comandi e connettori

| Parte | Servono | Cerca | Controlla |
|---|---|---|---|
| Pot 9 mm B10K lineare | 6 | `9mm potentiometer B10K` | boccola M7 lunga 5; albero lungo 15 |
| Manopole per i pot | 6 | per lo stesso albero dei pot (6 mm tondo o zigrinato 18T) | Ø al massimo 16: i modelli controllano l'aria fra le manopole su 16 |
| Manopola dell'encoder | 1 | `knob 6mm knurled shaft 18T` | Ø al massimo 22 |
| Footswitch 3PDT, 9 terminali | 1 | `3PDT footswitch 9 pin` | boccola M12, corpo entro 18 × 18 |
| Tasto tattile 12×12×7,3 con cappuccio tondo | 2 + 2 | `12x12x7.3 tactile switch round cap` | cappuccio e altezza: il case vuole Ø 11,8; la 1590DD un cappuccio Ø 11,5 con flangia Ø 12,8 sotto il pannello |
| Deviatore mini DPDT on-on | 1 | `MTS-202 mini toggle` | boccola M6 |
| LED 3 mm | 2 | `3mm LED` | |
| Jack 6,35 mono con commutazione sulla punta (IN L e IN R) | 2 | `6.35 mono jack switch open frame` (tipo Switchcraft 12A) | il contatto che manda l'ingresso a massa a jack scollegato |
| Jack 6,35 stereo in metallo (OUT L, OUT R, pedale) | 3 | `PJ-629HAN` | come il Tayda A-1121 |
| Jack 3,5 stereo per il MIDI | 2 | `PJ366ST` (tipo Thonkiconn) | stereo; filetto M6×0,5 lungo almeno 4,5 mm; coi dadi. Sostituisce l'ordine Exploding Shed |
| Jack DC 5,5×2,1 da pannello | 1 | `DC-022B panel mount` | il foro: il case ne ha uno da 11, la dima 1590DD da 12 |

### Scheda e cablaggio

| Parte | Servono | Cerca | Controlla |
|---|---|---|---|
| Stripboard | 1 | `stripboard uncut 2.54` | strisce intere (non a gruppi di 2-3 fori); almeno 30 fori per striscia e 45 strisce, 76 × 114 mm |
| Header femmina 2,54, alti 8,5 | 2 da 20 | `female header 2.54 single row 40p`, da tagliare | |
| Zoccoli DIP-8 e DIP-6 | 2 + 1 | `DIP IC socket` | |
| Millefori | 2 | `prototype pcb 5x7` | scheda tasti 50 × 25,5 e scheda I/O |
| Filo 24 AWG in 2-3 colori, cavetto schermato mono (2 m), guaina termorestringente | | `silicone wire 24AWG`, `shielded cable single core`, `heat shrink kit` | |
| Passivi che mancano (vedi la lista completa) | | resistenze a film metallico 1/4 W 1 %, elettrolitici 10, 47 e 100 µF ≥ 16 V, 1N5817, 1N4148, film 100 nF | |

### Minuteria

| Strada | Parte | Servono | Cerca |
|---|---|---|---|
| 1590DD | Viti M2,5 a testa bombata: 4 da 8 mm e 2 da 12 con dado; viti M3×12 bombate con dado | 4, 2 + 2, 4 + 4 | `M2.5 M3 button head screw nut kit` (con le lunghezze 8 e 12) |
| 1590DD | Piedini adesivi | 4 | `silicone bumper feet` |
| Case stampato | Inserti a caldo M3 lunghi 5,7, Ø esterno 4,6, per foro da 4,0 (come i ruthex) | 5 | `M3 heat set insert 5.7` |
| Case stampato | Viti M3×14 a brugola | 5 | `M3x14 socket head cap screw` |
| Case stampato | Autofilettanti per plastica, 3×6 e 2,5×8 | 4 + 6 | `self tapping screw plastic kit` |
| Case stampato | Piedini adesivi Ø 12,7 × 3,5 | 4 | `silicone bumper 12.7` |

### Facoltativi

- Scatola 1590DD clone (`1590DD aluminum enclosure`): solo per la strada forata a mano. Le pareti vanno misurate
  all'arrivo.
- PETG nero o grafite da 1 kg, per un case stampato scuro (in casa c'è il bianco).
- Alimentatore 9 V centro negativo, se non c'è già.

## Lista completa

Tutti i componenti, anche quelli che hai già: spunta quello che c'è.

### Scheda (veroboard)

| Parte | Q.tà | Riferimenti |
|---|---|---|
| TLC2272 (CP, ACP o IP), DIP-8 | 2 + 1 di scorta | U1, U2 |
| Zoccolo DIP-8 | 2 | U1, U2 |
| Header femmina 1×20, passo 2,54, alto 8,5 mm | 2 | Seed3 |
| Stripboard, almeno 45 strisce da 30 fori | 1 | |
| Resistenza 1/4 W 3R3 | 1 | R1 |
| 10R | 1 | R2 |
| 100R | 2 | R13, R17 |
| 1K | 2 | R7, R10 |
| 10K | 6 | R3, R4, R11, R12, R15, R16 |
| 100K | 2 | R14, R18 |
| 1M | 4 | R5, R6, R8, R9 |
| Ceramico C0G 100 pF | 2 | C19, C20 |
| Ceramico C0G 390 pF | 2 | C13, C16 |
| Ceramico C0G (o film) 2,2 nF | 2 | C6, C9 |
| Ceramico 100 nF | 3 | C3, C11, C18 |
| Film 100 nF | 2 | C5, C8 |
| Elettrolitico ≥ 16 V 10 µF | 6 | C7, C10, C12, C14, C15, C17 |
| Elettrolitico ≥ 16 V 47 µF | 1 | C4 |
| Elettrolitico ≥ 16 V 100 µF | 2 | C1, C2 |
| Diodo Schottky 1N5817 | 1 | D1 |

### Scheda I/O (MIDI, microSD) e cablaggi

| Parte | Q.tà | Note |
|---|---|---|
| Optoaccoppiatore H11L1M + zoccolo DIP-6 | 1 + 1 | MIDI IN |
| Diodo 1N4148 | 1 | MIDI IN |
| Resistenza 220R | 1 | MIDI IN |
| Resistenza 270R | 1 | MIDI IN, pull-up |
| Resistenza 10R | 2 | MIDI OUT |
| Resistenza 47K | 5 | pull-up microSD |
| Resistenza 10K | 2 | Rs INST/LINE |
| Resistenza 3K3 | 2 | Rsh INST/LINE |
| Resistenza 1K | 2 | LED di stato e LED del bypass |
| Ceramico 100 nF | 2 | opto, manica MIDI IN |
| Jack 3,5 stereo | 2 | MIDI IN, MIDI OUT (vedi sopra) |
| Lettore microSD (Adafruit 4682) | 1 | rimandato |
| Millefori piccola | 2 | scheda I/O e scheda tasti (50 × 25,5 mm) |
| Filo 0,25 mm² in 2-3 colori, cavetto schermato mono (~2 m), guaina termorestringente | | |
| Alimentatore 9 V centro negativo | 1 | |

### Pannelli

| Parte | Q.tà | Note |
|---|---|---|
| OLED Waveshare 2,42" 128×64 SSD1309 | 1 | sposta i due 0 Ω sul modulo per l'I2C |
| Encoder Bourns PEC11R-4220K-S0024 | 1 | pulsante, albero 20 mm zigrinato 18T |
| Pot Alpha 9 mm RD901F-40-15R1-B10K | 6 | boccola M7 da 5 mm, albero tondo 6,35 |
| Manopole per albero tondo 6,35 col grano | 6 | |
| Manopola dell'encoder, a pressione per 18T | 1 | |
| Tasto tattile 12×12×7,3 + cappuccio tondo | 2 + 2 | K1, K2 |
| Footswitch 3PDT 9 terminali, boccola M12 | 1 | true bypass |
| LED 3 mm | 2 | stato e bypass |
| Jack 6,35 con commutazione sulla punta | 2 | IN L, IN R: a jack scollegato l'ingresso va a massa |
| Jack 6,35 (Tayda A-1121, stereo) | 2 | OUT L, OUT R: il contatto di commutazione non serve |
| Jack 6,35 stereo (TRS) | 1 | pedale esterno |
| Jack DC 2,1 centro negativo | 1 | |
| Deviatore mini DPDT on-on | 1 | INST/LINE |

### Minuteria con la 1590DD

| Parte | Q.tà | Note |
|---|---|---|
| Viti M2,5 × 8 a testa bombata | 4 | staffe dell'OLED, nel PETG |
| Viti M2,5 × 12 con dado | 2 | scheda tasti |
| Viti M3 × 12, meglio a testa bombata, con dado | 4 | dal fondo, colonnine e veroboard, dado sopra |
| Piedini adesivi | 4 | sotto il fondo |

### Minuteria col case stampato

| Parte | Q.tà | Note |
|---|---|---|
| Inserti M3 a caldo per foro da 4,0 (ruthex M3×5,7) | 5 | torrette del pannello superiore |
| Viti M3×14 a brugola | 5 | dal fondo |
| Autofilettanti per plastica 3×6 | 4 | veroboard |
| Autofilettanti per plastica 2,5×8 | 6 | staffe OLED e scheda tasti |
| Piedini adesivi Ø 12,7 × 3,5 | 4 | |
| Colla stick | 1 | solo per la stampa in casa |
