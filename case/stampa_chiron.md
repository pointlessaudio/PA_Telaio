# Case stampato in casa: Anycubic Chiron in PETG

Una delle tre strade per il contenitore (vedi `../CLAUDE.md`, Stato). Il modello è `case.py`; qui stanno solo
le istruzioni di stampa. Stato al 29/09: G-code pronti; **la prima prova, `TELAIO_1`, si è staccata al primo
strato**. Edo non ha la colla stick.

**22/10: setup della macchina in `<progetti>/chiron-setup/`** (`TUTORIAL.md` + G-code di prova del primo strato). Si fa prima di riprovare `TELAIO_1`.

## 29/09: TELAIO_1 staccata al primo strato

- **Cosa si è visto** (foto di Edo): skirt e brim erano linee tonde e separate, con spazi fra una e l'altra, e si
  sono staccate tutte insieme come un anello. Quindi l'ugello era troppo lontano dal vetro: è il criterio del
  README di a4-stand, "Prima di lanciarla", punto 2. La colla non avrebbe cambiato niente.
- **Il G-code è a posto:** strato 1 a Z 0,2; 0,0361 mm di filo per mm su skirt, brim, pareti e fondo, uguale
  all'atteso con linea 0,5 × 0,2 e flusso 0,95; impronta centrata sul piatto (X 113,5-286,5, Y 157,5-242,5).
- **È la terza stampa su questa Chiron che cede al primo strato:** rialzo v2 finito in un groviglio, v3 con la
  punta alzata, ora TELAIO_1. Il problema è l'altezza dell'ugello, non il profilo v4.
- **Prima del prossimo tentativo:**
  1. pulizia di vetro e ugello;
  2. livellamento col piatto a 85 °C;
  3. prova del foglio al centro;
  4. colla;
  5. controllo della skirt nei primi 30 s e del brim: le linee devono essere schiacciate e unite.
  La sessione della stampa ha offerto a Edo un file di prova del primo strato sull'area della vasca.
- **Profili corretti il 29/09:** la CLI di Orca, con la `--datadir` temporanea di `slice_chiron.py`, non
  risolveva l'ereditarietà dei profili e usava i suoi default. I G-code dicevano `filament_type = PLA` col PETG, e
  la macchina aveva ritrazione al cambio strato e wipe spenti (nel profilo Chiron sono accesi). Temperature,
  ventola e piatto erano giusti perché li imposta lo script. Ora `completo()` scrive per esteso tutte le chiavi
  della catena, e lo script controlla nel G-code filament_type, ritrazione al cambio strato, wipe e le altre
  chiavi che si perdevano. Tutti i G-code di `stampa/` sono rifatti così: `gcode_check.py` ora stampa anche
  `filament_type` (PETG su tutti).

Sulla SD di Edo (ricopiati il 29/09 alle 12:54 coi profili completi, verificati con `cmp`, tolti solo i file
`._` della copia):
- `A4_rialzo_v4_1pezzo.gcode` = rialzo per l'Analog Four, v4, un pezzo a 0,3 (2 h 05, 42,7 g), da
  `a4-stand/stampa/2026-09-29/`;
- `TELAIO_1_prova_sopra.gcode` = `prova_superiore` a 0,3 (1 h 30);
- `TELAIO_2_prova_retro.gcode` = `prova_posteriore` a 0,3 (0 h 37);
- `TELAIO_3_vasca.gcode` = `vasca` a 0,2 (8 h 00), con le colonnine ai fori di fissaggio corretti il 29/09.
Restano anche i vecchi rialzi v3 e i file di Edo. I pannelli non ci sono: aspettano i pezzi.

**Prima di stampare i pannelli** `case.py` va riallineato ai pezzi che si comprano davvero: oggi è disegnato
sui pezzi di partenza. Vedi `../hardware/ordine_componenti.md`, sezione "Case stampato". La vasca non dipende
da quei pezzi.

## La macchina e le impostazioni v4

La Chiron di Edo: 400 × 400 × 450, Bowden, ugello 0,4, vetro rivestito, 260 °C al massimo all'ugello, avvio
col G-code di Cura. La pipeline sta nel progetto a4-stand (`<progetti>/a4-stand/README.md`,
script `slice_chiron.py`). Parte dal profilo ufficiale OrcaSlicer della Chiron e ci mette sopra le correzioni
della v4 (28/09).

Le correzioni vengono da due stampe dei rialzi per l'A4, entrambe senza colla:
- la prima è finita in un groviglio;
- la seconda (v3: piatto a 80 °C, ventola dal 6° strato al 40 %) ha alzato un'estremità nei primi strati;
- l'altezza dell'ugello dopo la prima stampa non è nota.

Le impostazioni v4:
- piatto 85 °C;
- colla stick o lacca sul vetro pulito: obbligatoria;
- brim 10 mm, pezzi a 25 mm l'uno dall'altro, così i brim non si toccano;
- ventola spenta nei primi 10 strati, poi fra 10 e 20 %, anche su ponti e sporgenze;
- primo strato lento (15 mm/s) e largo (0,5 mm), ugello a 245 °C, poi 240;
- ritrazione 6 mm a 40 mm/s.

Il primo collaudo della v4: il rialzo v4 da 2 h preparato dalla sessione dello stand (a4-stand, non è sulla SD),
oppure la piastra di prova `TELAIO_1`. La sessione dello stand aspetta anche l'ok di Edo per il commit della v4 e
per spostare lo script in un posto condiviso.

## Regole di disegno che ne derivano (già applicate in case.py)

- niente smussi o raccordi sui lati appoggiati al piatto: Orca li vede come sporgenze e accende la ventola;
- angoli in pianta raccordati;
- niente ponti nei 10 strati a ventola spenta. Restano solo quelli sopra il logo del pannello superiore,
  profondo 0,5 mm e largo al massimo 5,4 mm;
- orecchie sulla vasca (28/09, finché non c'è la colla): 4 dischi Ø 30 × 0,4 mm, due strati, centrati sugli
  spigoli della pianta. Stanno fuori dall'impronta, tranne 0,5 mm sotto il bordo per saldarsi al pezzo: le
  sedi delle viti restano aperte, e `case.py` lo controlla. Allargano la vasca sul piatto a 240 × 164 mm.
  Solo in `out/vasca.stl`; STEP, render, verifiche e `out/servizio/` sono senza.

## Comandi

```
uv run stampabilita.py              # isole nel vuoto, ponti, sbalzi, pareti sottili: "OK ... senza supporti"
uv run stampabilita.py --autotest   # difetti costruiti apposta: devono uscire tutti RILEVATO
uv run piatto_unico.py              # tutti i pezzi su un piatto solo, in out/piatto_unico.stl
python3 <progetti>/a4-stand/slice_chiron.py --stl "$PWD/out/vasca.stl" --out "$PWD/stampa" --bed 85 --brim 10 --copies 1 [--layer 0.2]
python3 gcode_check.py              # rilegge i G-code di stampa/: temperature, ventola, brim, ponti
```

Con `slice_chiron.py`:
- passa sempre `--bed`, `--brim` e `--copies`: i default sono tarati sul rialzo di a4-stand e possono cambiare;
- un STL per volta; le copie le mette lo script, non Orca;
- `--stl` e `--out` vanno con percorsi assoluti.

I G-code pronti per la SD sono in `stampa/`. `gcode_check.py` deve dire per ogni file:
- piatto 85 °C;
- ugello 245 poi 240;
- ventola dallo strato 11;
- brim presente.

Sporgenze attese nella vasca: 3,4-4,0 mm (i due strati a ponte sopra le sedi delle viti), 16 mm (fessura
microSD, 13 mm), 25,6 mm (USB-C). Tutte a ventola accesa.

## Tempi e grammi (OrcaSlicer, v4 coi profili completi, 3 pareti, infill 15 %; tutto rifatto il 29/09)

| Lavoro | Strato | Tempo | PETG |
|---|---|---|---|
| Piastre di prova (superiore + posteriore) | 0,3 | 1 h 30 + 0 h 37 | 23 + 9 g |
| Vasca, con le orecchie | 0,2 | 8 h 00 | 107 g |
| Pannello superiore | 0,3 | 5 h 53 | 92 g |
| Pannello posteriore | 0,3 | 1 h 21 | 21 g |
| Staffe OLED, due | 0,3 | 0 h 16 | 3 g |
| Piatto unico, tutti i pezzi (305 × 325 mm) | 0,3 / 0,2 | 14 h 41 / 16 h 08 | 238 / 206 g |

Il pannello superiore va a 0,3: la profondità del logo (0,5) è tarata su un primo strato da 0,2 più uno da 0,3.

## Ordine consigliato

1. Piastre di prova. Se un foro è stretto o largo, correggi `TOL_FORI` (+0,3 di partenza), riesporta e
   riaffetta.
2. Vasca da sola.
3. Pannello superiore. Se hai già l'OLED, prima prova il vetro nella sede della piastra di prova.
4. Pannello posteriore e staffe.

Il piatto unico solo quando la v4 ha già dato pezzi buoni:
- un distacco a metà butta 15 ore e tutti i pezzi insieme;
- l'impronta copre quasi tutto il vetro, quindi anche la planarità deve reggere su tutto il vetro.

## Prima e durante ogni stampa

- vetro sgrassato con alcool isopropilico, poi niente dita;
- colla su tutta l'impronta, brim compreso;
- qualche minuto di attesa dopo che il piatto segna 85: il vetro arriva in temperatura dopo il sensore;
- niente correnti d'aria sulla macchina.

Durante il primo strato guarda il brim su tutti e quattro i lati: dev'essere schiacciato e uniforme. Se in un
angolo resta tondo o si solleva, ferma e rilivella. Stacca i pezzi a piatto freddo, sotto i 40 °C.

**29/09 pomeriggio, secondo tentativo di TELAIO_1** (G-code coi profili completi): stesso difetto dopo 2 min.
Skirt e brim sono fili tondi e sottili appoggiati sul vetro, trascinati, con grumi: l'ugello è ancora troppo alto,
più dei 0,13 mm stimati la prima volta. Sullo schermo, in pausa, Z 20,20: è lo strato da 0,2 più il sollevamento
della pausa, non un errore del G-code.

**29/09, tentativo successivo** (foto del brim di un pezzo con una curva a U): le linee ora si attaccano, ma
restano tonde e separate, con fessure scure fra una e l'altra. L'ugello è ancora un po' alto, circa 0,05-0,1 mm.
I fili sottili sulla curva sono stringing dei trasferimenti e non c'entrano con la presa.

**29/09, perché il rialzo v3 del 28/09 teneva meglio.** Edo: il 28/09 il piano era storto, dopo il v3 l'ha
raddrizzato. Il primo strato del v3 (a4-stand @206fa22) e quello di TELAIO_1 sono identici:
- Z 0,2;
- 0,0361 mm di filo per mm;
- 15/20 mm/s, ugello a 245 °C;
- stesso avvio;
- stessa zona centrale: v3 X 106-294 e Y 130-270, TELAIO_1 ci sta dentro.

Cambiano solo il piatto (80 → 85 °C) e il brim (5 → 10 mm), ed entrambi aiutano la presa. Quindi è cambiata la
macchina: raddrizzando il piano si è spostata anche l'altezza al centro. Se c'è un livellamento salvato col sensore,
dopo aver girato i dadi va rifatto il PROBE: la mappa corregge ancora la pendenza vecchia.

## Livellamento della Chiron (verificato il 29/09 su manuale e firmware ufficiale)

Fonti: manuale Anycubic Chiron (ManualsLib, pp. 20-28) e firmware ufficiale
(github.com/ANYCUBIC-3D/ANYCUBIC_CHIRON, V1.2.7 su Marlin 1.1.0).
- Il livellamento salvato si applica anche col nostro avvio: in fondo a `gcode_G28()` il firmware ufficiale
  chiama sempre `set_bed_leveling_enabled(true)` (ABL bilineare 5 × 5). Quindi `M420 S1` non serve. Con un
  firmware della comunità va ricontrollato.
- Due modi, di fabbrica è il manuale. Per capire quale: Home, poi prova a spostare la testina a mano; nel modo
  manuale il firmware sblocca i motori X/Y.
- **Manuale:** dadi sotto il piatto, foglio sui 4 angoli e al centro, col piatto a 85 °C (in senso orario il
  piatto scende). Rifare il giro 2-3 volte. Planarità garantita solo entro 0,25 mm. In stampa non si corregge.
- **Assistito:** sensore magnetico sulla testina, ugello sotto i 60 °C, Tools → More → Level → PROBE (25 punti).
  Dopo il PROBE l'ugello resta apposta 2-4 mm alto. Si corregge in stampa: Tools → More → Level, ALL, "−" o "+"
  da 0,05 mm a click, poi OK per salvare.
- `Auto_Leveling.gcode` (M1001) e `Manual_Leveling.gcode` (M1000) cancellano il livellamento salvato e cambiano
  modo: non stamparli se non vuoi cambiare modo.
- Per TELAIO_1 la stima dalla foto era un ugello almeno 0,13 mm troppo alto (3 click o più nel modo assistito).
- Nel modo manuale prova il foglio anche ai quattro angoli dell'area della vasca, oltre agli angoli del piatto e al
  centro: circa 7 cm dai fianchi e 11 cm da davanti e da dietro. Il primo strato della vasca, skirt compresa, va da
  X 68,5 a 331,5 e da Y 106,5 a 293,5 (263 × 187 mm centrati); TELAIO_1 da X 113,5 a 286,5 e da Y 157,5 a 242,5.
  È l'area che deve tenere per le 8 ore.
- Se serve, si può preparare un file di prova del primo strato sulla sola area della vasca (proposto a Edo il
  29/09, nessuna risposta).

Sulla SD (FAT32, volume `NO NAME`) copia senza i file `._` che macOS aggiunge sulle schede FAT (indicazione
della sessione a4-stand):

```
cp -X stampa/vasca_x1_Chiron_PETG_0.2mm.gcode "/Volumes/NO NAME/"
find "/Volumes/NO NAME" -maxdepth 1 -name '._*' -delete
diskutil eject "/Volumes/NO NAME"
```

Dopo la stampa: rifila le orecchie della vasca col cutter, raso al bordo del fondo.
