# PA-TELAIO — strumento da tavolo su Daisy Seed3

Piattaforma per prototipare effetti su Daisy Seed3: veroboard con 2x TLC2272, stereo in/out
(strumento e linea), MIDI, microSD. Contenitore ancora da scegliere fra tre strade: case stampato in casa,
case stampato da un servizio, scatola in alluminio 1590DD.

- `CLAUDE.md` — stato, decisioni, dove sta cosa, mappa pin, punti aperti. Da leggere per primo.
- `hardware/` — layout veroboard verificato (`layout.py`), pagina di montaggio HTML, `ordine_componenti.md`
  con i carrelli per ogni strada.
- `case/` — case parametrico (`case.py`, build123d) con test di mutazione, e scatola 1590DD (`scatola.py`).
  Una pagina per strada: `stampa_chiron.md`, `servizio_stampa.md`, `scatola_1590DD.md`. Uscite in `out/`,
  G-code in `stampa/`, render in `render/`.
- `firmware/collaudo/` — firmware di collaudo: passthrough, bypass, mono, pot, encoder, OLED, MIDI, DFU da tasti.
- `docs/storico/` — documenti precedenti, superati. Leggere le note in CLAUDE.md prima di usarli.
