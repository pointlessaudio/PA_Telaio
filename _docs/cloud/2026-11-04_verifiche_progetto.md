# Verifiche del progetto (da CLAUDE.md) — 2026-11-04

Stato: **parziale**. Il file viene aggiornato e ripushato dopo ogni punto completato.

- Commit misurato: `613ab6a` (`main`). Il repo non ha modifiche dopo le verifiche (`git status` pulito).
- Macchina: container cloud Linux x86_64; Python di sistema 3.13.18, uv con 3.11.18 / 3.12.3 / 3.13.18 disponibili.

## Riepilogo

| Verifica | Esito |
|---|---|
| `hardware/layout.py` | PASS: «42 gruppi componenti, 13 ponticelli, 7 cavi, 38 piazzole, 57 tagli, 61 isole, 61 net, nessun corto, nessun aperto» |
| `hardware/test_layout.py` | PASS: ogni riga RILEVATO |
| `hardware/page.py` | PASS: «pagina ok» |
| `case/case.py` | PASS: «5 pezzi, 106 componenti controllati, nessuna collisione» |
| `case/test_case.py` | PASS: ogni riga RILEVATO (oltre 10 minuti di esecuzione) |
| `case/cablaggio.py` | FAIL con Python 3.11 (scelto da uv), PASS con 3.12: «80 fili, reti coerenti ai due capi, ogni piazzola dei layout cablata, percorsi liberi» |
| `case/test_cablaggio.py` | FAIL con 3.11, PASS con 3.12: 6 righe RILEVATO, nessuna NON RILEVATO (oltre 10 minuti) |
| `case/stampabilita.py` | PASS: «6 pezzi stampabili senza supporti» |
| `hardware/kicad/genera_schema.py` | FAIL con 3.11 (importa `cablaggio`), PASS con 3.12: «127 componenti, 94 reti, 21 piedini NC» |
| `hardware/kicad/disegna_schema.py` | PASS: «fogli scritti» |
| `hardware/kicad/verifica_schema.py` | NON ESEGUITA: manca `kicad-cli` (in corso: tentativo di installare KiCad) |
| `hardware/kicad/test_schema.py` | NON ESEGUITA: manca `kicad-cli` (in corso) |

## Comandi

```bash
cd hardware && python3 layout.py && python3 test_layout.py && python3 page.py
```

```bash
cd case && uv run case.py && uv run test_case.py && uv run stampabilita.py
```

```bash
cd case && UV_PYTHON=3.12 uv run cablaggio.py && UV_PYTHON=3.12 uv run test_cablaggio.py
```

```bash
cd hardware/kicad && UV_PYTHON=3.12 uv run genera_schema.py && python3 disegna_schema.py
```

## Problemi

### 1. `case/cablaggio.py:959`: sintassi valida solo da Python 3.12, requisito dichiarato `>=3.11`

- Gravità: media.
- Cosa succede: la riga 959 usa una f-string con apici uguali annidati (`f'({v['org'][0]:.0f},...)'`), che Python accetta solo dalla 3.12. L'intestazione dello script (riga 2) dichiara `requires-python = ">=3.11,<3.13"`, e lo stesso vale per `hardware/kicad/genera_schema.py`, che importa `cablaggio`. Dove uv trova Python 3.11 lo sceglie, e `uv run cablaggio.py` si ferma con `SyntaxError: f-string: unmatched '['`. Così cadono anche `test_cablaggio.py` e `genera_schema.py`.
- Effetto: le verifiche di «fatto» falliscono su una macchina con 3.11 anche se il modello è corretto. Sul Mac probabilmente non si vede perché uv trova la 3.12.
- Fix proposto (non applicato), una delle due strade:
  - alzare `requires-python` a `">=3.12,<3.13"` in `cablaggio.py` e `genera_schema.py`;
  - oppure riscrivere la riga 959 con apici diversi (es. `{v["org"][0]:.0f}`), così funziona anche su 3.11.

### 2. `kicad-cli` non disponibile nel container

- Gravità: informativa (limite dell'ambiente, non del repo).
- `verifica_schema.py:18-20` cerca `kicad-cli` nell'app KiCad del Mac, poi nel `PATH`. Qui non c'è.

## Cosa non è stato fatto

- `verifica_schema.py` e `test_schema.py`: in attesa di KiCad.
