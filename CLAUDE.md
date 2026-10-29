# PA-TELAIO — strumento da tavolo per prototipare effetti su Daisy Seed3

Progetto di Edoardo (Pointless Audio), parallelo ai plugin. Piattaforma riusabile su Daisy Seed3
per prototipare più effetti sullo stesso hardware: veroboard più case stampato in 3D, ispirato a
norns e Torso S-4. Questa è la fase prototipo: una sola unità.

## Come lavorare con Edoardo

- Rispondi in italiano, diretto e conciso. Niente emoji, niente introduzioni o riassunti finali inutili.
- Una sola domanda alla volta quando manca un'informazione.
- Task non banali: piano dettagliato, attendi approvazione, poi esegui. Se qualcosa va storto, fermati e torna al piano.
- Nessuna assunzione silenziosa: se manca un dato critico, chiedi.
- Non rattoppare risultati mediocri: riscrivi da zero con quello che hai imparato.
- Chiedi conferma esplicita prima di operazioni rischiose o distruttive.
- Non usare mai `-ffast-math`. Il Makefile core di libDaisy non lo usa: non aggiungerlo.

## Dove sta cosa

| Argomento | File |
|---|---|
| Stato, decisioni aperte, punti aperti (live state) | `docs/stato.md` |
| Decisioni prese, mappa pin, case, montaggio, firmware, verifiche a banco | `docs/progetto.md` |
| Circuito, veroboard, netlist (sorgente di verità) | `hardware/layout.py`, pagina `hardware/prototipo-veroboard-seed3.html` |
| Componenti da comprare, carrelli per ogni strada | `hardware/ordine_componenti.md` |
| Preamp JFET d'ingresso: simulazione, circuito V4a, collaudo a banco | `hardware/preamp/` (`risultati.md`, `collaudo.md`, `sim/`) |
| Tre strade per il circuito (veroboard, PCB JLCPCB, CNC) | `hardware/strade_circuito.md` |
| Case stampato: modello e verifiche (sorgente di verità) | `case/case.py`, `case/test_case.py` |
| Case stampato in casa sulla Chiron | `case/stampa_chiron.md` |
| Cablaggio interno: fili, lunghezze di taglio, orientamento della schedina | `case/cablaggio.py`, `case/cablaggio.md` |
| Schermatura in rame e masse a stella | `docs/schermatura_massa.md` |
| Case stampato da un servizio | `case/servizio_stampa.md` |
| Scatola 1590DD: modello, dima, coordinate Tayda | `case/scatola.py`, `case/scatola_1590DD.md` |
| Firmware di collaudo | `firmware/collaudo/` |
| Documenti vecchi (con errori noti, vedi `docs/progetto.md`) | `docs/storico/` |

## Verifiche prima di dire «fatto»

```
cd hardware && python3 layout.py && python3 test_layout.py && python3 page.py
cd case && uv run case.py && uv run test_case.py
cd case && uv run cablaggio.py && uv run test_cablaggio.py && uv run stampabilita.py
```

`layout.py` deve stampare "OK ... nessun corto, nessun aperto", `case.py` "OK ... nessuna collisione", i test di
mutazione ogni riga RILEVATO. Dettagli in `docs/progetto.md`. Il repo è pubblico: niente dati personali, numeri
d'ordine o di preventivo, link privati, percorsi del Mac.
