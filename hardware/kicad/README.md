# Schema KiCad (29/10/2026)

Schema elettrico completo di PA-TELAIO per KiCad 10, **disegnato da codice e verificato contro le netlist del
progetto**. Dieci pagine A3: un indice e un foglio per blocco. In tutto 127 componenti e 94 reti: veroboard,
schedina del preamp JFET, jack, deviatori, footswitch, pot, encoder, OLED, tasti, scheda MIDI e microSD.

**Da leggere o stampare:** [`pa-telaio_schema.pdf`](pa-telaio_schema.pdf). Per aprirlo in KiCad: `pa-telaio.kicad_pro`.

| Pagina | Foglio | Contenuto |
|---|---|---|
| 1 | `pa-telaio.kicad_sch` | indice |
| 2 | `fogli/f01_alimentazione.py` | 9 V, VIN del Seed, VA, VB, alimentazione degli operazionali, massa del telaio |
| 3 | `fogli/f02_ingressi.py` | jack d'ingresso, Rs, INST/LINE, deviatore PRE |
| 4 | `fogli/f03_preamp.py` | preamp JFET, due canali, GAIN, partitore VG |
| 5 | `fogli/f04_buffer_ingresso.py` | buffer d'ingresso verso il codec |
| 6 | `fogli/f05_buffer_uscita.py` | buffer d'uscita invertente |
| 7 | `fogli/f06_uscite.py` | jack d'uscita, true bypass 3PDT, LED |
| 8 | `fogli/f07_seed.py` | Daisy Seed3 e mappa dei piedini |
| 9 | `fogli/f08_controlli.py` | pot, encoder, OLED, tasti K1/K2, pedale |
| 10 | `fogli/f09_midi_sd.py` | MIDI IN/OUT e microSD |

La PCB non è ancora disegnata. Lo schema è la base per le due strade a circuito stampato di
`../strade_circuito.md`, cioè JLCPCB e fresatura CNC.

## Comandi

```bash
uv run genera_schema.py      # reti attese dalle fonti -> reti_attese.json, componenti.json (~1 min)
python3 disegna_schema.py    # scrive i fogli .kicad_sch, PA.kicad_sym, sym-lib-table: ogni foglio "OK"
python3 verifica_schema.py   # "OK: netlist di KiCad uguale a quella attesa ..., ERC senza errori"
python3 test_schema.py       # 6 mutazioni dello schema, ogni riga RILEVATO
```

Serve KiCad 10 (`kicad-cli`), installato in `/Applications/KiCad` o in `~/Applications/KiCad`. Il PDF si rifà con
`kicad-cli sch export pdf -o pa-telaio_schema.pdf pa-telaio.kicad_sch`.

## Come è fatto

- **`genera_schema.py`** calcola le reti attese dalle fonti, come nel montaggio vero. Ogni scheda ha le sue
  reti, ogni terminale fuori scheda (un lug di jack, un pin di deviatore) è un nodo a sé, e solo i fili di
  `case/cablaggio.py` li uniscono. Se manca un filo, la rete resta divisa (`GND_2`) e il generatore lo segnala.
  Le fonti:

  | Parte | Fonte |
  |---|---|
  | veroboard | `hardware/layout.py` |
  | schedina preamp | `hardware/preamp/layout_preamp.py`, riferimenti rinumerati da 101 (originale nel campo `Layout`) |
  | terminali e fili | `case/cablaggio.py` |
  | parti fuori scheda, MIDI, microSD | tabella `FUORI` in `genera_schema.py` |

- **`fogli/fNN_*.py`** disegnano ogni foglio a mano, da codice: posizione di ogni simbolo e percorso di ogni filo,
  con l'API di `disegno.py`. I simboli sono in `simboli.py`.
- **`disegna_schema.py`** scrive i file KiCad. Prima controlla ogni foglio:
  - i piedini uniti da fili ed etichette devono avere la stessa rete attesa;
  - nessun piedino può restare scollegato;
  - i componenti non devono sovrapporsi.

  Fra un foglio e l'altro le reti passano per etichette globali con lo stesso nome, e massa e alimentazioni per
  simboli di rete.
- **`verifica_schema.py`** fa esportare la netlist a KiCad stesso e la confronta con `reti_attese.json`, piedino
  per piedino: guarda quali piedini stanno insieme, non i nomi. Poi lancia l'ERC.
  - `--fogli f03` limita il controllo ai piedini di alcuni fogli, per il lavoro su un foglio solo.
  - `reti.py R101` elenca le reti dei componenti indicati.
- **`test_schema.py`** rovina lo schema in sei modi e la verifica deve accorgersene ogni volta: etichetta
  rinominata, due etichette scambiate, simbolo spostato, filo tolto, segno di non collegato tolto, massa
  cambiata in VB.

I `.kicad_sch` sono generati: **non vanno modificati a mano**, perché alla rigenerazione le modifiche si perdono.
Se il circuito cambia nelle fonti, la verifica segnala le differenze e il foglio interessato va ridisegnato nel
suo modulo in `fogli/`.

La verifica prova che lo schema riproduce le fonti, non che le fonti siano giuste. Le fonti sono verificate dai
loro script: `layout.py`, `layout_preamp.py`, `cablaggio.py`.

Le impronte vengono dalle librerie ufficiali di KiCad 10, solo per i componenti delle due schede; le parti
montate sul pannello non ne hanno. Al primo avvio KiCad crea le tabelle globali delle librerie. Prima di allora
l'ERC dà circa 80 avvisi `footprint_link_issues`, che non sono errori.

## Scostamenti trovati trascrivendo (sistemati il 29/10)

- **Polo C del 3PDT (LED del bypass):** la pagina `prototipo-veroboard-seed3.html` aveva la versione vecchia
  (catodo sul comune, anodo con 1 kΩ a 3V3D). Ora pagina e schema seguono `cablaggio.py`: R 4,7 kΩ da VA sul
  comune, posizione effetto all'anodo, catodo a massa.
- **Contatto della punta dei jack d'ingresso:** va a massa, così a jack scollegato l'ingresso tace. In
  `cablaggio.py` il filo mancava; ora c'è: terminale `JIL:tn` / `JIR:tn` e ponticello `IN L h` / `IN R h` verso
  il manicotto.
- **GAIN:** ogni gang del pot doppio è usata come reostato, cursore e un capo (pagina di montaggio del preamp);
  il terzo capo resta libero.
