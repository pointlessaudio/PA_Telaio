# PA-TELAIO: progetto

Decisioni prese e perché, sorgenti di verità di circuito e case, montaggio, mappa pin, firmware, verifiche a
banco. Lo stato e i punti aperti stanno in `stato.md`. Percorsi relativi alla radice del repo.

## Decisioni prese, e perché

- **Prima la veroboard, la PCB dopo** (28/09). Serve una sola unità, e il circuito non è mai stato provato a
  banco. Il pedale completo di bkshepherd (125B) costa 150 USD più import: scartato.
  - Stima PCB del 28/09 (JLCPCB, tariffe aggiornate al 9/09/2026): 5 circuiti a 2 strati di 76 × 114 mm (stessa
    sagoma e stessi fori della veroboard, entra nel case senza cambiarlo), 2 montati con i pezzi SMD. Circa
    65-100 € in tutto: circuiti 5-10 $, avvio 8,18 $ + stencil 1,53 $, 3,07 $ per ogni pezzo fuori catalogo
    base, saldature 0,0016 $ a punto, scheda I/O come secondo circuito, spedizione e IVA incassata alla cassa.
  - JLCPCB fa minimo 5 circuiti e ne monta anche solo 2 (verificato il 28/09: prima qui c'era scritto 5
    assemblate).
  - Sulla PCB tornerebbe l'OPA1652 SMD al posto del TLC2272.
- **Da pedale a strumento da tavolo** (28/09). I due footswitch diventano i tasti K1/K2 sul
  pannello; un jack TRS "pedale" sul retro è in parallelo agli stessi pin (punta = D0,
  anello = D10), quindi un doppio pedale esterno funziona senza pin né firmware in più.
- **TLC2272 in DIP-8 al posto del TL072** (28/09). Il TL072 classico accetta in modo comune
  solo da ~3 V sopra la massa (4 V garantiti, datasheet TI): l'inseguitore d'ingresso,
  polarizzato a VB ≈ 4,3 V, faceva ~2,6 Vpp puliti contro i 3,6 Vpp del codec. Il TLC2272
  (datasheet SLOS190H) accetta da 0 V a 1,5 V sotto il positivo su tutta la temperatura: ~5,5 Vpp
  intorno a VB. Uscita rail-to-rail, ingresso CMOS (1 pA), 9 nV/√Hz. Stessa piedinatura: layout
  invariato, niente SMD. Prima c'era l'OPA1652 su adattatore SOIC-8→DIP-8 (4,5 nV/√Hz, è quello
  dei circuiti del datasheet Seed3): tolto il 28/09 per fare la veroboard senza saldature SMD,
  torna buono per un'eventuale PCB. Scartati NE5532 (bipolare: a 8,5 V il modo comune si ferma a
  ~3 V dalle alimentazioni, e la corrente di polarizzazione sposta il punto di lavoro sul 1 MΩ) e
  OPA2134 (garantito fino a 2,5 V dalle alimentazioni: 3,5 Vpp).
- **Niente relè di bypass.** Bypass in DSP, come il Terrarium.
- **Ingresso a guadagno unitario, 1 MΩ**, passa-basso RC ~72 kHz, più 100 pF C0G (C19/C20) che
  con la Rs esterna fanno da filtro RF a ~160 kHz. Per la linea un deviatore INST/LINE sul retro
  inserisce un attenuatore da −12 dB fuori scheda: Rs 10 kΩ in serie (sempre) e Rsh 3,3 kΩ a
  massa, un polo per canale. Il codec satura con un seno a +4 dBu.
- **Uscita invertente a guadagno −1**, passa-basso ~41 kHz. Il firmware inverte la fase per
  compensare. C14/C17 da 10 µF elettrolitici: con 1 µF su un ingresso di linea da 10 kΩ si
  tagliava a 16 Hz.
- **Bias VB da partitore 10K/10K + 47 µF**, senza buffer: alimenta solo nodi ad alta impedenza.
- **Mono senza normalling hardware**: si usa IN L e si duplica in firmware. Il normalling avrebbe
  abbassato l'impedenza d'ingresso a ~250 kΩ.
- **Mappa pin vicina ai DevKit ufficiali Seed3**, dove costa poco: OLED su D11/D12 (pin di
  default dell'I2C1 in libDaisy), MIDI su USART1 D13/D14 come nei DevKit Pedal e Desktop, pot su
  A0-A5 come nel Pedal DevKit.
- **MIDI TRS tipo A e microSD 1-bit** su una scheda I/O esterna: schema e valori nella pagina HTML
  (datasheet Seed3, fig. 5.1, 7.1, 7.3, 7.5).
- **Case, variante A** (28/09): cuneo 210 × 134 mm, alto 25 davanti e 47 dietro (9,3°). Tre pezzi
  (vasca, pannello superiore, pannello posteriore) con viti M3 dal fondo negli inserti a caldo:
  nessuna vite sul pannello. Pot a 28 mm fra le colonne e 36 mm fra le file (12 e 20 mm d'aria
  fra le manopole): la profondità è salita da 118 a 134 mm per allontanare le file senza finire
  sopra i jack posteriori; poi la griglia è salita di altri 8 mm abbassando la fila dei jack (centri
  a 18,5 mm dal fondo), così la fila dietro dei pot passa sopra i corpi dei jack da 6,35. Il pannello posteriore si ristampa da solo se un effetto chiede I/O
  diversi. Niente serigrafia: lo schermo mostra i nomi dei pot nella stessa griglia 3×2. Logo con
  la rondine inciso 0,5 mm al centro della fascia bassa, largo 42 mm: sotto quella misura i tratti
  scendono sotto 0,44 mm, il minimo per un ugello da 0,4.
- **True bypass stereo con footswitch 3PDT** (28/09), in basso a destra: due poli scambiano OUT L/R
  fra effetto e ingresso diretto, il terzo accende il LED accanto. Sotto il pannello una torre
  fino al fondo porta il carico del piede. Il bypass in DSP su K1 resta, per le code.
- **Contenitore**: in origine case stampato sulla Chiron in PETG opaco grafite (il PETG che Edo ha è
  bianco). Dal 28/09 tre strade aperte, vedi `stato.md`.
- **Pannello posteriore piatto** (28/09): lastra di 2,4 mm montata da dentro contro la parete, la
  finestra della vasca le fa da cornice (rientra di 2,4 mm). La prima versione aveva una flangia a U
  che si era staccata dal corpo e sporgeva nel vuoto: l'ha trovato `stampabilita.py`.

## Hardware: la sorgente di verità è `hardware/layout.py`

Contiene posizione di ogni componente, tagli, ponticelli, cavi e piazzole, più una netlist attesa.
Se modifichi qualcosa:

```
cd hardware
python3 layout.py        # deve stampare "OK ... nessun corto, nessun aperto"
python3 test_layout.py   # test di mutazione: ogni riga deve dire RILEVATO
python3 page.py          # rigenera prototipo-veroboard-seed3.html
```

Convenzioni: `x` = foro lungo la striscia (0..29), `y` = striscia (0..44), strisce orizzontali.
Nella pagina HTML righe e fori sono numerati da 1. Lo script verifica collegamenti, non meccanica:
passo dei componenti e percorso dei cavi vanno controllati a mano.

**Fori di fissaggio** (a base 0, da forare a 3,2 mm per viti M3): `FORI_FISSAGGIO = [(1,1), (28,1), (7,43), (28,37)]`
in `layout.py`, l'unica lista. `case.py`, `scatola.py` e la pagina la leggono da lì; nella pagina sono cerchi blu,
riga 2 fori 2 e 29, riga 38 foro 29, riga 44 foro 8.
- `layout.fori_fissaggio_errori()` controlla la parte elettrica: foro libero, ad almeno un foro dal bordo, nessuna
  striscia usata spezzata. `test_layout.py` ha 2 mutanti per questo, 8 su 8 RILEVATO.
- Il controllo meccanico sta nei modelli: `case.py` mette una testa di vite Ø 6 × 2,4 su ogni foro e la controlla
  contro i componenti; `scatola.py` fa lo stesso con viti e dadi.
- Storia: fino al 28/09 c'erano (2,44) e (27,44). Spezzavano la striscia 44, che collega le masse OUT L e OUT R, J13
  ed R18; stavano a 1,27 mm dal bordo, e C12 ed R18 non lasciavano posto alla testa. Il controllo di allora
  guardava solo che il foro fosse libero. Trovato il 28/09 sera lavorando alla scatola, corretto il 29/09:
  colonnine della vasca e G-code rifatti.

## Case: la sorgente di verità è `case/case.py`

```
cd case
uv run case.py            # costruisce, verifica, esporta in case/out/: "OK ... nessuna collisione"
uv run test_case.py       # 16 mutazioni, ogni riga RILEVATO (qualche minuto)
uv run stampabilita.py    # stampabilità strato per strato (vedi stampa_chiron.md)
uv run render/esporta.py && /Applications/Blender.app/Contents/MacOS/Blender -b -P render/scena_blender.py
```

build123d 0.13 con Python 3.12 via `uv`: le dipendenze sono dichiarate in testa ai file, niente
venv a mano. La verifica legge `hardware/layout.py` e trasforma ogni componente della veroboard in
un ingombro (altezze per tipo in `ALTEZZE`). Poi controlla:
- collisioni con pot, encoder, OLED, tasti, jack e pezzi stampati;
- USB-C allineata alla parete e spessori di pannello per le boccole;
- aria fra le manopole;
- logo inciso davvero e finestra dell'OLED aperta su tutti i pixel.

Gli ingombri stanno nei dizionari in testa a `case.py`: se compri un pezzo diverso, cambialo lì e
rilancia. Uscite: `out/` (STL già orientati per la stampa, STEP, `assieme.step` e `.glb`),
`render/` (PNG). Solo `vasca.stl` ha le orecchie di stampa: STEP, render e verifiche usano la vasca
senza.

Il modello serve due delle tre strade: stampa in casa (`stampa_chiron.md`, orecchie della vasca solo per
la Chiron) e stampa da un servizio (`servizio_stampa.md`, variante `out/servizio/` con logo 48 × 1,0 e test
`verifica_servizio()`). La terza strada, la scatola 1590DD, ha il suo modello: `scatola.py`, che riusa i
corpi di questo file (`scatola_1590DD.md`).

Verificato il 29/09: `OK: 5 pezzi, 97 componenti controllati, nessuna collisione` (93 più le 4 teste delle viti
della veroboard). 16 mutazioni su 16 RILEVATO (giro completo del 29/09), comprese le 3 dei fori di fissaggio.

**Il modello è disegnato sui pezzi di partenza, non su quelli dei carrelli.** Prima di stampare i pannelli
va riallineato:
- jack DC: `TIPI_RETRO["dc"]` ha foro 11, i jack DC trovati ne vogliono 12 (o 12,8 a D);
- jack da 6,35: `TIPI_RETRO["jack635"]` è 16 × 17 × 30. Gli Switchcraft 12A sono Ø 19,1 × 26,6 e i Tayda A-1121
  15,8 × 15,8 × 27,1: con quei pezzi la verifica va rifatta. Gli Switchcraft 112AX/112BX (Banzai) entrano così
  come sono;
- tasti: `TASTO` ha cappuccio 11,8 e pila 10,0; il cappuccio Tayda A-4814 è Ø 11,5 con flangia Ø 12,8, pila 10,5.
La vasca non dipende da questi pezzi.

Componenti su cui è disegnato:

| Pezzo | Riferimento | Vincolo |
|---|---|---|
| Footswitch | 3PDT 9 terminali, boccola M12 | corpo 18 × 18 × 22,5 mm dentro la torre; il dado sopra, niente dado sotto |
| Pot | Alpha 9 mm RD901F-40-15R1, 10K lineare | boccola M7 lunga 5: pannello a 2,4 mm con tasca da sotto; staccare il dentino anti-rotazione |
| Encoder | Bourns PEC11R-4220K-S0024 | boccola M7 lunga 7 |
| OLED | Waveshare 2,42" 128×64 SSD1309 | i fori stanno sotto il vetro: sede nel pannello e 2 staffe stampate; spostare i due 0 Ω sul modulo per passare all'I2C |
| Tasti | tattili 12×12×7,3 con cappuccio tondo Ø 11,8 | su millefori 50 × 25,5 mm, 2 viti M2,5 |
| Jack 6,35 | ingombro 16 × 17 × 30 mm, boccola 3/8" | IN L/R, OUT L/R, pedale; centri a 18,5 mm: non alzarli, sopra passano i pot |
| Jack 3,5 | Thonkiconn PJ366ST sulla scheda MIDI | pannello ≤ 3 mm |
| DC | 2,1 mm da pannello, foro 11 mm | |
| Deviatore | mini DPDT, boccola M6 | INST/LINE |
| Header del Seed | femmina standard, 8,5 mm | con header bassi cambia `SEED["header_f"]` |

Minuteria del case stampato:
- 5 inserti M3 a caldo (foro 4,0) e 5 viti M3×14 a brugola, dal fondo;
- 4 viti autofilettanti M3×6 per la veroboard;
- 6 viti autofilettanti M2,5×8 per le staffe dell'OLED e la scheda tasti;
- 4 piedini adesivi Ø 12,7 × 3,5 mm, incollati sul fondo pieno (niente sedi);
- 6 manopole Ø 16 per albero liscio da 6 mm e una manopola Ø 22 per albero zigrinato 18T.

### Montaggio (case stampato)

0. Stampato in casa: rifila le orecchie della vasca col cutter, raso al bordo del fondo.
1. Inserti a caldo nelle 5 torrette del pannello superiore (Ø 10, foro da 4).
2. Veroboard sulle colonnine.
3. Pannello posteriore con i connettori, calato da sopra fra la parete e i montanti: i dadi dei
   jack stanno nella finestra.
4. Sul pannello superiore: OLED (vetro nella sede, 2 staffe), encoder, pot, scheda tasti,
   footswitch (cablato prima: i fili escono dalla fessura in basso della torre), LED del bypass
   incollato nel manicotto.
5. Cablaggio.
6. Chiusura con 5 viti dal fondo.

**Orientamento dell'OLED**: non blocca la stampa del pannello superiore. Il modulo va con la
piattina verso chi suona (`OLED_PIATTINA_DAVANTI = True`). Se a banco il testo esce capovolto, si
raddrizza in firmware. Nel driver SSD130x di libDaisy `transport_` è `protected`: basta una
sottoclasse che dopo `Init()` manda 0xA0 e 0xC0 al posto di 0xA1 e 0xC8 (verificato sul sorgente
di libDaisy master, 28/09). Mettere `False` sposta la finestra di 5,4 mm e chiede una ristampa.

## Mappa pin Seed3

| Pin | Nome | Uso |
|---|---|---|
| 1 | D0 | Tasto K1 (bypass) e pedale esterno, punta |
| 4 | D3 | Encoder A |
| 5 / 6 / 7 | D4 / D5 / D6 | microSD DAT0 / CMD / CLK (SDMMC 1-bit, pull-up 47 kΩ esclusa CLK) |
| 8 | D7 | Encoder B |
| 9 | D8 | Encoder pulsante |
| 10 | D9 | LED (tramite 1K) |
| 11 | D10 | Tasto K2 (mono) e pedale esterno, anello |
| 12 / 13 | D11 / D12 | OLED SCL / SDA (I2C1, pin di default di libDaisy) |
| 14 / 15 | D13 / D14 | MIDI TX / RX (USART1) |
| 16 / 17 | Audio In 1 / 2 | da stadio d'ingresso L / R |
| 18 / 19 | Audio Out 1 / 2 | verso stadio d'uscita L / R |
| 20 | AGND | massa, capo basso dei pot |
| 21 | 3V3A | capo alto dei pot |
| 22–27 | A0–A5 | cursori pot 1–6 |
| 38 | 3V3D | OLED VCC, scheda I/O |
| 39 | VIN | da jack DC tramite D1 e R1 |
| 40 | DGND | massa, masse controlli digitali |

Liberi: D1, D2, A6–A11, D26–D30. D17, D18, D21, D22, D23 non sono 5V-tolleranti.

## Firmware

libDaisy supporta il Seed3 dal 06/08/2026: `759a941` per il riconoscimento della scheda,
`e1f740a` per i 192 kHz nella SAI. Il TAC5242 passa dalla stessa inizializzazione del rev4, senza
un driver dedicato. Il commit `facb66c` del 24/09 aggiunge le classi dei tre DevKit ufficiali
Seed3 (`daisy::pedal_devkit`, `desktop_devkit`, `eurorack_devkit`): servono come riferimento per
la mappa pin, ma al 28/09 i DevKit non risultano in vendita. Usa `facb66c` o successivo.

```
cd firmware
git clone --recurse-submodules https://github.com/electro-smith/libDaisy.git
cd libDaisy && make -j && cd ..
cd collaudo && make
make program-dfu
```

Per entrare in DFU a case chiuso, tieni premuti K1 e K2 all'accensione: il firmware di collaudo
chiama `System::ResetToBootloader()` e lo scrive sullo schermo. A case aperto funziona anche la
via classica, BOOT + RESET sul Seed.

Toolchain: `arm-none-eabi-gcc` (testato con 13.2.1), oggi assente su questo Mac: installare la
DaisyToolchain. Il firmware di collaudo usava circa il 73% dei 128 KB di flash interna; per effetti
più grandi servirà il bootloader Daisy (`APP_TYPE = BOOT_SRAM` o `BOOT_QSPI` nel Makefile).

Cosa prova il collaudo:
- passthrough;
- K1 per il bypass, K2 per il mono;
- pot e encoder a schermo;
- MIDI: il pulsante dell'encoder manda un Do centrale su MIDI OUT, lo schermo mostra l'ultima nota
  o CC ricevuti;
- picchi d'ingresso e versione della scheda.

La microSD non è ancora nel collaudo.

Il framework multi-effetto di bkshepherd (github.com/bkshepherd/DaisySeedProjects,
Software/GuitarPedal) astrae l'hardware con una classe per scheda: è un'opzione per la fase
successiva, scrivendo una classe con la mappa pin qui sopra.

## Da verificare a banco

1. Orientamento del pin 1 sulla serigrafia del Seed3 prima di saldare gli header, e dei TLC2272
   negli zoccoli.
2. Continuità: i 57 tagli, soprattutto la colonna 7 righe 1–20 (separa le file del Seed).
3. Senza Seed e senza integrati: VA ~8,5 V, VB = VA/2, VIN presente.
4. Con gli integrati: le quattro uscite degli operazionali a riposo su VB.
5. Passthrough, fase corretta, rumore di fondo.
6. **Frequenza di campionamento.** La SAI accetta 96 e 192 kHz (`SetAudioSampleRate`), ma che il
   TAC5242 li segua nella configurazione di default non è verificato. Provare prima di progettare
   effetti che ne dipendono.
7. OLED 2,42": che il driver SSD130x di libDaisy inizializzi l'SSD1309 (compatibile, non
   garantito), e l'orientamento del testo (si corregge in firmware, vedi Case).
8. MIDI in e out con la scheda I/O.
9. Deviatore INST/LINE: livello con una sorgente di linea a +4 dBu.
10. True bypass: in bypass continuità punta IN → punta OUT su entrambi i canali, LED spento;
    a effetto inserito uscita dalla scheda e LED acceso; nessun colpo alla commutazione.

## Errori noti nei documenti storici

`docs/storico/PA-TELAIO_schematica.md` e `PA-TELAIO_BOM.xlsx` hanno nello stadio d'ingresso un
4K7 con 33 nF verso massa, cioè un passa-basso a ~1 kHz: sbagliato, non costruire da lì. È una
trascrizione errata della fig. 3.4 del datasheet: lì il 4K7 fa da partitore con il 3K3, e il
33 nF lavora col 100R in uscita (~48 kHz). `PA_ordine_125b_Seed3.xlsx` è la lista d'ordine per il
125B, scartato per il prototipo.

## Idee di effetti già discusse

Sedimento (freeze spettrale con memoria di frame FFT in SDRAM), Simpatiche (banco di corde
simpatiche a waveguide), Nodo (rete di feedback caotica), Catacomba (riverbero FDN più
convoluzione breve), Ancia (modello fisico eccitato dalla chitarra), Palinsesto (looper a
decadimento generazionale), Ombra (sintesi incrociata tra i due ingressi).
