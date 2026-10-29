# PA-TELAIO: stato e punti aperti

Live state del progetto. La documentazione tecnica (decisioni, mappa pin, case, firmware) sta in
`progetto.md`. Percorsi relativi alla radice del repo.

## Stato attuale (28/09/2026, sera)

Niente è ancora comprato, costruito o stampato. Edo vuole **tenere aperte tutte le strade** finché non decide.

- **Circuito:** veroboard progettata e verificata da script (`hardware/layout.py`), con operazionali TLC2272.
  La PCB è rimandata a dopo le prove a banco (vedi `progetto.md`, Decisioni).
- **Contenitore:** tre strade, nessuna scelta:
  1. **case stampato in casa** sulla Chiron in PETG: G-code v4 coi profili completi, sulla SD le due piastre di
     prova, la vasca e il rialzo v4 dello stand. La prima prova (`TELAIO_1`, 29/09) si è staccata al primo
     strato: ugello troppo lontano dal vetro. Pagina `case/stampa_chiron.md`;
  2. **case stampato da un servizio** (MJF PA12): preventivi da 96,75 € + IVA (Weerg, grigio) a 261 € (Europa,
     nero), giudicati troppo cari. Pagina `case/servizio_stampa.md`;
  3. **scatola in alluminio 1590DD** (Tayda forata a macchina, o Musikding forata a mano): ingombro verificato,
     dima e coordinate pronte, pezzi interni stampati in lavorazione. Pagina `case/scatola_1590DD.md`.
  Le strade 1 e 2 usano lo stesso modello (`case/case.py`).
- **Versione da stampare (29/10):** `case.py` è disegnato sui pezzi dei carrelli Banzai + TME (Switchcraft
  112AX/112BX, DC Lumberg a D, tasti Omron B3F + B32), con dentro veroboard, schedina preamp, scheda MIDI, microSD
  sul pannello posteriore, PRE e GAIN sul retro, vite di massa L0 e torretta L1. `OK: 5 pezzi, 106 componenti
  controllati, nessuna collisione`, 35 mutazioni su 35 RILEVATO; stampabilità: 6 pezzi senza supporti. G-code nuovi
  in `case/stampa/2026-10-29/`. Cablaggio (80 fili, lunghezze di taglio) in `case/cablaggio.md`, schermatura e
  masse in `docs/schermatura_massa.md`. Ancora stimati: pot doppio GAIN, zoccolo microSD, spessore flangia DC.
- **Componenti:** lista completa e carrelli per ogni strada in `hardware/ordine_componenti.md`. Nessun ordine
  fatto.
- **Firmware:** `firmware/collaudo` aggiornato il 28/09, **non compilato**: su questo Mac manca la toolchain
  ARM (`arm-none-eabi-gcc`); la versione precedente compilava.

- **Preamp JFET d'ingresso** (29/10): simulato in ngspice, **non costruito né ascoltato**. Circuito V4a in
  `hardware/preamp/risultati.md`, distinta in `hardware/ordine_componenti.md` (sezione Preamp JFET), procedura a
  banco in `hardware/preamp/collaudo.md`. Criteri della simulazione: 8 su 9 passati (punto di lavoro senza
  trimmer, banda, guadagno minimo e massimo, pulito, tetto d'uscita, spinta, ginocchio). Il nono no: **rumore
  riportato all'ingresso col GAIN al minimo, 3,6-3,75 µV contro il limite di 3,5** (da metà in su 2,0-2,4 µV);
  punto aperto, da giudicare a orecchio. GAIN: doppio C50K con 47k in parallelo per gang (29/10), J201
  con IDSS ≥ 0,5 mA. Schedina su stripboard 24 × 18 fori verificata da
  script (`hardware/preamp/layout_preamp.py`); PRE, GAIN e volume della schedina sono in `case/case.py`.

Decisioni aperte, per Edo:
1. contenitore (una delle tre strade);
2. jack da 6,35: per la versione stampata Switchcraft 112AX/112BX (29/10); per la 1590DD aperta (vedi
   `hardware/ordine_componenti.md`);
3. jack MIDI e lettore microSD: per la versione stampata dentro da subito (29/10); per la 1590DD aperta;
4. per la 1590DD: grezza o verniciata (e colore), stampa UV sì o no.

Decisa (29/10): deviatore PRE resta DPDT. Con PRE spento l'ingresso della schedina resta sul nodo INST/LINE e
la sorgente vede ~500 kΩ invece di 1 MΩ: accettato (con un pickup passivo si perde un filo di acuti; da sentire
al collaudo, la strada di riserva è un 4PDT con due poli per canale).

## Punti aperti (29/09)

- **Schema KiCad (29/10):** in `hardware/kicad/`, disegnato su 10 pagine A3 (`pa-telaio_schema.pdf`) e verificato
  contro le netlist (netlist di KiCad uguale, ERC senza errori, 6/6 mutazioni rilevate). Manca la PCB. I due scostamenti trovati trascrivendo (contatto
  della punta dei jack d'ingresso, polo C del 3PDT nella pagina) sono sistemati (`hardware/kicad/README.md`).
- **Preamp (29/10):** procurarsi J201 genuini e tenere quelli con IDSS ≥ 0,5 mA;
  ingombro vero del pot doppio (in `case.py` è stimato); PRE e GAIN anche in `scatola.py` (1590DD) e nella dima;
  rumore col GAIN al minimo da giudicare a orecchio.
- **Chiron:** `TELAIO_1` (29/09) si è staccata al primo strato, la terza stampa su questa macchina che cede lì:
  il problema è l'altezza dell'ugello. Prima di riprovare: pulizia, livellamento a 85 °C nel modo giusto (manuale
  o assistito), prova del foglio, colla (Edo non ce l'ha), controllo della skirt; tutto in `case/stampa_chiron.md`.
  I profili di `slice_chiron.py` sono corretti dal 29/09 (prima `filament_type = PLA`, ritrazione al cambio strato
  e wipe spenti); lo script è nel progetto a4-stand (esterno), con la v4 ancora da committare.
- **Case stampato:** allineato il 29/10 ai pezzi dei carrelli; prima dei pannelli definitivi stampare le due
  piastre di prova (`stampa/2026-10-29/`) e misurare col pezzo in mano pot doppio e zoccolo microSD.
- **Servizio di stampa:** la rev. B della richiesta va emessa dopo aver comprato i connettori.
- **1590DD:** pezzi interni disegnati e affettati (39 min, non stampati); orientamento della scatola nel Box Tool di Tayda da
  verificare con la dima; misurare all'arrivo le pareti della scatola clone; cavo USB-C con la spina sottile;
  posizione della microSD da fissare.
- **Firmware:** installare la toolchain ARM e compilare il collaudo.
