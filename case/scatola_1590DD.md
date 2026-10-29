# Scatola in alluminio pressofuso 1590DD

Una delle tre strade per il contenitore (vedi `../CLAUDE.md`, Stato). Nata il 28/09 quando la stampa
professionale è sembrata cara. Stato al 28/09 sera: **verifica d'ingombro passata**, dima e coordinate pronte,
nessun acquisto. Pezzi interni stampati disegnati e affettati (39 min).

Fornitori:
- **Musikding** "Alu-Gehäuse Typ DD", 187 × 118 × 38, 16,50 €, poche scorte, senza foratura: si fora a mano con
  la dima;
- **Tayda 1590DD**: grezza 9,99 $, verniciata 14,99 $. Foratura CNC 4,50 $ fino a 40 punti (i rettangoli si
  fanno con 4 linee nel Box Tool), stampa UV 4,00 $, spedizione DDP in Italia circa 23-38 $ (dato dei forum, non
  verificato). Si ordina dalla dashboard drill.taydakits.com.

Il carrello con i pezzi scelti per la scatola è in `../hardware/ordine_componenti.md`.

## Il modello: `scatola.py`

```
PYTHONDONTWRITEBYTECODE=1 uv run scatola.py   # da case/: "OK: 112 corpi nella 1590DD, nessuna collisione."
```

`PYTHONDONTWRITEBYTECODE=1` serve perché con l'ambiente nuovo di uv la scrittura del `.pyc` in Documenti restava
bloccata in `rename()`.

Usa gli stessi corpi di `case.py`. La veroboard arriva da `hardware/layout.py` tramite `case.componenti()`,
traslata in blocco. Uscite in `out/scatola/`:
- `ingombri.png`: vista dall'alto e da dietro;
- `dima_1590DD.html` e `.pdf`: dima 1:1, 3 pagine A4 orizzontali, 34 fori con codici;
- `coordinate_tayda.csv` per la scatola grezza e `coordinate_tayda_verniciata.csv` per la verniciata (+0,4 mm su
  diametri e rettangoli, come chiede Tayda per la verniciatura a polvere).

Il PDF della dima si rigenera dall'HTML con Chrome headless (comando in `servizio_stampa.md`). Il comando si è
bloccato una volta: se non esce, controlla che il PDF sia stato scritto e chiudi il processo.

**Limite:** `scatola.py` non ha test di mutazione. Le sue verifiche (uscita dalla cavità, borchie, collisioni a
coppie) non sono state provate con difetti iniettati.

### Scatola, dal disegno Hammond

Fonte: hammfg.com/files/parts/pdf/1590DD.pdf.
- esterno 188 × 120 × 37; pareti e pannello da 2,5, fondo 1,9;
- dentro 183 × 115 al bordo e 178 × 110 sotto il pannello: è lo sformo, circa 4,4°, ricavato dal disegno;
- altezza interna 32,6 (il disegno dice 32,0);
- borchie: 4 d'angolo Ø 10 con centro a 4,4 dai bordi, 2 a metà dei lati lunghi fino a 9,5;
- bordino del fondo largo 2, alto fino a z 4,0.

La Tayda è un clone e può differire: **all'arrivo misura** la parete ai jack MIDI e lo spessore del pannello
dei pot.

### Disposizione

Coordinate in mm dallo spigolo anteriore sinistro, sotto il fondo. Il fondo (coperchio Hammond) sta sotto; la
faccia chiusa della scatola è il pannello dei comandi.
- veroboard: x 6,0-120,3, y 11,8-88,0, faccia sopra a z 7,5 (colonnine da 4). I più alti: USB-C a z 23,4, Seed a
  22,3, C7 a 20,0. USB-C contro il fianco sinistro;
- pot 3 × 2 a x 116/144/172, y 84/52 (28 mm fra le colonne, 32 fra le file);
- encoder (88, 74);
- OLED: circuito centrato in (44, 88), sopra la zona del Seed; finestra centrata in (44, 90,68), 57,2 × 29,7;
- tasti (24, 26) e (46, 26); LED (64, 26); LED del bypass (146, 24); footswitch (166, 24), in basso a destra
  fuori dalla veroboard;
- retro, tutti con il centro a z 14 salvo i MIDI:
  - MIDI (Thonkiconn) a x 25 e 39, z 9,8;
  - pedale x 68 (A-1121);
  - IN L 109 e IN R 129 (Switchcraft 12A);
  - OUT L 149 e OUT R 169 (A-1121);
- fianco destro: DC a y 72 (ingombro Ø 16 × 18,3), deviatore INST/LINE a y 52 (13 × 13 × 20);
- microSD sul fondo davanti, x 130-156: posizione indicativa, da fissare quando c'è la scheda.

### Esito e note (stampate da scatola.py, ricontrollate il 28/09 alle 21:24)

- 100 corpi, nessuna collisione (112 con i pezzi interni, ricontrollato alle 22 circa);
- filetto oltre il dado: pot 0,5 mm (niente rondella), encoder 2,5;
- tasti: flangia del cappuccio 0,5 mm sotto il pannello, sporgono 1,8;
- parete posteriore: 3,43 mm ai jack da 6,35, 3,11 ai MIDI (il Thonkiconn regge al massimo 3,0; col filetto da
  4,5 restano 1,4 mm per il dado, circa 3 giri);
- aria fra le manopole: pot-pot 12,0, encoder-pot 10,7, footswitch-pot 12,6;
- coda del jack del pedale (A-1121, 27,1 mm con i pin) a 0,87 mm dal bordo della veroboard: pin verso l'alto,
  non piegarli verso la scheda.

Storia dei giri: il primo con 9 collisioni (borchie d'angolo troppo prudenti, jack contro il bordino, IN R contro
la borchia centrale), il secondo con 1 (DC contro OUT R), poi OK.

### Fori

Diametro in mm; +0,4 sulla verniciata.

| Foro | Ø |
|---|---|
| Pot ed encoder | 7,5 |
| Footswitch | 12,0 |
| Tasti (la flangia da 12,8 resta sotto il pannello) | 12,0 |
| LED (niente portaLED: entra da dentro e si incolla) | 3,2 |
| Viti M2,5: 4 per le staffe OLED (S1-S4), 2 per la scheda tasti (T1-T2) | 3,0 |
| Jack 6,35 | 10,0 |
| Thonkiconn | 6,2 |
| Jack DC | 12,0 |
| Deviatore | 6,2 |
| Fondo, viti M3 della veroboard (V1-V4) | 3,2 |
| Asola USB-C, fianco sinistro | 13 × 7 |
| Fessura microSD, fronte (indicativa) | 13 × 2,6 |

Le coordinate partono dal centro di ogni faccia, nella vista descritta in `FACCE`: pannello visto da sopra con
il fronte in basso, retro visto da dietro, destra da destra, sinistra da sinistra, fronte da davanti, fondo
dall'interno.

## Pezzi interni stampati in PETG (28/09 sera)

Tutto in `scatola.py`: `OK: 112 corpi nella 1590DD, nessuna collisione`, contando pezzi stampati, dadi e punte
delle viti. STL in `out/scatola/stampa/`:
- `staffa_oled_1590DD.stl`, da stampare in 2: barra 75 × 4,5 × 2,2 sul piatto, 2 piedini 4 × 4 × 1,5 a ±27,75
  che spingono il circuito dell'OLED; 2 colonne Ø 6 a ±34,5, alte 7,7 fino al pannello, con foro pilota Ø 2,2
  profondo 6,5 per le viti M2,5×8 che scendono dal pannello (fori S1-S4);
- `distanziale_tasti_1590DD.stl`, in 2: tubo Ø 6, foro 3,0, alto 6,2. La vite M2,5×12 passa dal pannello
  (T1-T2) e dalla millefori, dado sotto;
- `colonnina_veroboard_1590DD.stl`, in 4: tubo Ø 7, foro 3,5, alto 4,0 esatti, perché sopra il Seed restano
  1,2 mm prima dei pot. Vite M3×12 dal fondo (V1-V4), dado M3 sopra la scheda;
- `pezzi_interni_1590DD.stl`: piatto unico con tutti gli 8 pezzi a 25 mm.

G-code: `stampa/pezzi_interni_1590DD_x1_Chiron_PETG_0.2mm.gcode`, 39 min, 4,8 g, 38 strati. `gcode_check`:
piatto 85, ugello 245 poi 240, ventola dallo strato 11, brim, niente sporgenze né ponti. Stampabilità: mesh
chiuse, 1 corpo per pezzo (8 sul piatto), nessun avviso.

**Fori della veroboard:** gli stessi del case, dalla lista unica `layout.FORI_FISSAGGIO` =
[(1,1), (28,1), (7,43), (28,37)] (`FORI_SCATOLA = C.L.FORI_FISSAGGIO`). Il controllo elettrico è
`layout.fori_fissaggio_errori()`: foro libero, a un passo dal bordo, nessuna striscia usata spezzata. Viti e dadi
sono modellati contro i componenti. V3 e V4 sul fondo sono su (7,43) e (28,37). Coordinate del fondo sulla
verniciata, dal centro: V1 (-84,15; +24,19), V2 (-84,15; -44,39), V3 (+22,53; +8,95), V4 (+7,29; -44,39), Ø 3,6.
Dima PDF e CSV rigenerati.

Minuteria che ne deriva:
- veroboard: 4 viti M3×12, meglio a testa bombata, con 4 dadi M3. Dal fondo attraversano la colonnina da 4 mm e
  la veroboard, dado sopra;
- scheda tasti: 2 viti M2,5×12 con 2 dadi M2,5. Dal pannello attraversano il distanziale e la millefori, dado
  sotto. La millefori deve avere due fori Ø 2,8 in corrispondenza di T1-T2: x 35, a ±8,75 dalla fila dei tasti;
- staffe dell'OLED: 4 viti M2,5×8, avvitate nel PETG (fori pilota da 2,2).

Montaggio:
- l'OLED si centra a occhio nella finestra prima di stringere le staffe;
- niente header a pin dritti saldati sul modulo OLED, perché scenderebbero fino al Seed: fili saldati
  direttamente sulle piazzole, oppure header a 90°.

## Punti aperti

1. Orientamento della 1590DD nel Box Tool di Tayda (orizzontale o verticale, e come nomina le facce): non
   verificato. Confronta l'anteprima con la dima prima di mandare.
2. USB-C: l'asola 13 × 7 sta in una parete spessa circa 4 mm a quella quota. Serve un cavo con la spina sottile.
3. Posizione della microSD da fissare quando c'è la scheda (Adafruit 4682).
4. Scatola Tayda clone: misurare all'arrivo parete ai MIDI e pannello dei pot (vedi sopra).
