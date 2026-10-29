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
  Le strade 1 e 2 usano lo stesso modello (`case/case.py`), che va riallineato ai pezzi comprati prima di
  stampare i pannelli.
- **Componenti:** lista completa e carrelli per ogni strada in `hardware/ordine_componenti.md`. Nessun ordine
  fatto.
- **Firmware:** `firmware/collaudo` aggiornato il 28/09, **non compilato**: su questo Mac manca la toolchain
  ARM (`arm-none-eabi-gcc`); la versione precedente compilava.

Decisioni aperte, per Edo:
1. contenitore (una delle tre strade);
2. jack da 6,35: combinazione mista, tutti Switchcraft o tutti Tayda (vedi `hardware/ordine_componenti.md`);
3. jack MIDI e lettore microSD: subito o dopo il primo collaudo;
4. per la 1590DD: grezza o verniciata (e colore), stampa UV sì o no.

## Punti aperti (29/09)

- **Chiron:** `TELAIO_1` (29/09) si è staccata al primo strato, la terza stampa su questa macchina che cede lì:
  il problema è l'altezza dell'ugello. Prima di riprovare: pulizia, livellamento a 85 °C nel modo giusto (manuale
  o assistito), prova del foglio, colla (Edo non ce l'ha), controllo della skirt; tutto in `case/stampa_chiron.md`.
  I profili di `slice_chiron.py` sono corretti dal 29/09 (prima `filament_type = PLA`, ritrazione al cambio strato
  e wipe spenti); lo script è nel progetto a4-stand (esterno), con la v4 ancora da committare.
- **Case stampato:** riallineare `case.py` ai pezzi comprati prima di stampare i pannelli (vedi `progetto.md`, Case).
- **Servizio di stampa:** la rev. B della richiesta va emessa dopo aver comprato i connettori.
- **1590DD:** pezzi interni disegnati e affettati (39 min, non stampati); orientamento della scatola nel Box Tool di Tayda da
  verificare con la dima; misurare all'arrivo le pareti della scatola clone; cavo USB-C con la spina sottile;
  posizione della microSD da fissare.
- **Firmware:** installare la toolchain ARM e compilare il collaudo.
