# PA-TELAIO

*[English version](README.en.md)*

Strumento da tavolo per prototipare effetti audio su [Daisy Seed3](https://electro-smith.com/) di
Electro-Smith. Un solo hardware, tanti effetti: si cambia il firmware, non la scatola. L'idea viene da norns e
dal Torso S-4. Progetto di Pointless Audio, parallelo ai plugin.

- ingresso e uscita stereo da 6,35 mm, strumento (1 MΩ) o linea (deviatore INST/LINE, −12 dB);
- stadi d'ingresso e d'uscita con due operazionali TLC2272, su veroboard;
- 6 potenziometri, un encoder con pulsante, 2 tasti, un jack per doppio pedale esterno;
- OLED 2,42" 128×64;
- MIDI TRS tipo A in e out, microSD (scheda I/O a parte);
- true bypass stereo con footswitch 3PDT, più bypass in DSP per le code;
- contenitore: case stampato in 3D (parametrico) o scatola in alluminio 1590DD.

## Stato

**Niente è ancora comprato, costruito o stampato.** Il circuito è progettato e verificato da script, non provato
a banco. Il case è modellato e verificato, una prima stampa di prova non è riuscita (problema della stampante,
non del modello). Il firmware di collaudo è scritto; la versione attuale non è ancora stata compilata.

Stato dettagliato, decisioni aperte e punti aperti: [`docs/stato.md`](docs/stato.md).

## Struttura

| Cartella | Cosa c'è |
|---|---|
| `hardware/` | circuito e veroboard: `layout.py` (sorgente di verità: componenti, tagli, ponticelli, netlist attesa), pagina di montaggio `prototipo-veroboard-seed3.html`, lista componenti e carrelli `ordine_componenti.md`, confronto veroboard / PCB `strade_circuito.md` |
| `case/` | case stampato parametrico `case.py` (build123d) con test di mutazione `test_case.py`, stampabilità strato per strato, scatola 1590DD `scatola.py`; una pagina per strada: `stampa_chiron.md`, `servizio_stampa.md`, `scatola_1590DD.md` |
| `firmware/collaudo/` | firmware di collaudo: passthrough, bypass, mono, pot, encoder, OLED, MIDI, DFU da tasti |
| `docs/` | `progetto.md` (decisioni e perché, mappa pin, case, montaggio, firmware, verifiche a banco), `stato.md`; in `storico/` documenti superati, con errori noti (vedi `progetto.md`) |

Tutta la documentazione è in italiano.

## Verificare il circuito

Serve solo Python 3, senza dipendenze.

```bash
cd hardware
python3 layout.py        # deve stampare "OK ... nessun corto, nessun aperto"
python3 test_layout.py   # test di mutazione: ogni riga deve dire RILEVATO
python3 page.py          # rigenera prototipo-veroboard-seed3.html
```

Convenzioni: `x` = foro lungo la striscia (0..29), `y` = striscia (0..44), strisce orizzontali; nella pagina HTML
righe e fori sono numerati da 1. Lo script verifica i collegamenti, non la meccanica: passo dei componenti e
percorso dei cavi vanno controllati a mano.

## Rigenerare il case

Serve [uv](https://docs.astral.sh/uv/): ogni script dichiara in testa le sue dipendenze (build123d 0.13,
Python 3.12), niente venv a mano. Gli output non sono nel repository e si rigenerano:

```bash
cd case
uv run case.py            # costruisce, verifica, esporta in out/: "OK ... nessuna collisione"
uv run test_case.py       # 16 mutazioni, ogni riga RILEVATO (qualche minuto)
uv run stampabilita.py    # stampabilità strato per strato, senza supporti
uv run scatola.py         # scatola 1590DD: modello, dima e coordinate di foratura
uv run piatto_unico.py    # tutti i pezzi su un piatto solo
uv run render/esporta.py && blender -b -P render/scena_blender.py   # render in render/
```

- `case/out/`: STL già orientati per la stampa, STEP, `assieme.step` e `assieme.glb`; `out/servizio/` è la variante
  per i servizi di stampa a polvere (MJF/SLS);
- `case/stampa/`: G-code. Lo slicing usa uno script esterno, non incluso (vedi `case/stampa_chiron.md`);
- `case/render/`: PNG.

La verifica legge `hardware/layout.py` e trasforma ogni componente della veroboard in un ingombro, poi controlla
collisioni, allineamento della USB-C, spessori di pannello per le boccole, aria fra le manopole, incisione del
logo e finestra dell'OLED. Gli ingombri dei pezzi comprati stanno nei dizionari in testa a `case.py`: il modello è
disegnato sui pezzi di partenza, e prima di stampare i pannelli va riallineato a quelli comprati davvero
(dettagli in `docs/progetto.md`).

## Compilare il firmware di collaudo

Serve la toolchain ARM (`arm-none-eabi-gcc`, provato con 13.2.1; si installa con la
[Daisy Toolchain](https://github.com/electro-smith/DaisyToolchain)). libDaisy va clonata in `firmware/libDaisy`
(commit `facb66c` o successivo, per il supporto al Seed3):

```bash
cd firmware
git clone --recurse-submodules https://github.com/electro-smith/libDaisy.git
cd libDaisy && make -j && cd ..
cd collaudo && make
make program-dfu
```

Per entrare in DFU a case chiuso si tengono premuti K1 e K2 all'accensione; a case aperto BOOT + RESET sul Seed.
Il collaudo prova passthrough, bypass (K1), mono (K2), pot ed encoder a schermo, MIDI in e out, picchi d'ingresso e
versione della scheda. Mappa pin e cose da verificare a banco: `docs/progetto.md`.

## Licenza

- hardware (circuito, case, scatola, documentazione): [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt);
- firmware e script di supporto: [MIT](LICENSES/MIT.txt);
- il nome e il logo Pointless Audio sono esclusi da entrambe: chi distribuisce o produce il case toglie o
  sostituisce il logo (`LOGO_SVG` in `case/case.py`).

Quale file sta sotto quale licenza: [`LICENSE`](LICENSE).
