# Case stampato da un servizio professionale

Una delle tre strade per il contenitore (vedi `../docs/stato.md`). Stesso modello del case stampato in casa
(`case.py`), esportato in una variante per le tecnologie a polvere. Stato al 28/09 sera: **preventivi fatti,
giudicati troppo cari da Edo, nessun ordine**.

## Cosa si manda

`out/servizio/` (rigenerato da `uv run case.py`):
- `vasca`, `pannello_superiore`, `pannello_posteriore`, `staffa_oled` in STEP e STL: in piano con la faccia a
  vista in alto, senza orecchie (servono solo sul piatto della Chiron);
- `assieme.step` di riferimento;
- la richiesta in PDF, rev. A: `PA-TELAIO_case_richiesta_stampa_revA.pdf`;
- lo zip da mandare: `PA-TELAIO_case_revA.zip` (PDF, i 4 pezzi in STEP e STL, `assieme.step`; 12 MB). Rifatto il
  29/09 con la vasca corretta (colonnine ai nuovi fori di fissaggio); il PDF rev. A non cambia, perché non elenca
  le posizioni. I preventivi del 28/09 sono stati fatti con la vasca vecchia: la differenza di prezzo è
  trascurabile, ma per ordinare va ricaricata quella nuova.

La rev. A è **per il preventivo**. La rev. B deve portare i fori veri del pannello posteriore, quindi va emessa
quando sono comprati i connettori, e dopo aver riallineato `case.py` a quei pezzi (vedi
`../hardware/ordine_componenti.md`, "Case stampato"). Per esempio il jack DC scelto vuole 12 mm e il modello ne
ha 11.

## Differenze della variante servizio (in case.py)

- `LOGO_SERVIZIO = (48.0, 1.0)`: logo largo 48 mm, inciso 1,0. Le linee guida PA12 MJF (Materialise) chiedono
  tratti di almeno 0,5 e incisioni da 1 mm: a 48 mm il tratto più sottile è 0,50. Il logo di casa resta 42 × 0,5.
- `logo_solido(prof, larghezza=None)` e `pannello_superiore(logo=None)`: il logo è un parametro.
- `controlla_logo(top, larghezza, prof)` raccoglie il controllo del logo; lo usa `verifica()`.
- `per_servizio(nome, s)`: pezzi in piano, faccia a vista in alto.
- `verifica_servizio(top)`, chiamata da `main()`: logo inciso, tratto ≥ 0,5, pannello pieno sotto il logo.
- `test_case.py`, mutazione 13: "logo della variante servizio troppo stretto" (48 → 40 mm).

Esito del 28/09 sera, ricontrollato: `OK: 5 pezzi, 93 componenti controllati, nessuna collisione`. La variante
servizio stampa "logo 48 mm inciso 1, tratto ~0.50 mm, 469 mm³ tolti, sotto pieno al 100%". Tutte e 13 le
mutazioni RILEVATO.

## Materiali consigliati

- HP MJF PA12 tinto nero e sabbiato; levigatura a vapore come opzione;
- in alternativa SLS PA12 o PA11;
- no alle resine SLA/DLP standard: fragili con inserti a caldo e viti.

## Preventivi del 28/09

Caricati sui siti dei servizi, senza ordinare.

**Weerg** (Italia, HP MJF). PA12 grigio grezzo, modalità Fast (-15 %), IVA esclusa:

| Pezzo | € |
|---|---|
| Vasca | 43,02 |
| Pannello superiore | 37,12 |
| Pannello posteriore | 11,42 |
| Staffa OLED (quantità 1, ne servono 2) | 5,19 |

Totale per data di spedizione: 96,75 € il 9/10, 116,11 € il 6/10, 135,46 € il 5/10, 193,52 € l'1/10. Con la
tinta "Nero Top" solo sulla vasca (47,80 €): 101,53 € con spedizione il 12/10. Gli altri pezzi non sono stati
passati a nero.

**Craftcloud**, 5 pezzi, totale con spedizione:
- SLS PA12 da 127,71 € + 14,77 €;
- MJF PA12 grigio 172,77 €; tinto nero 174,13 € (3DPnxt, Cina, possibili dazi) o 174,49 € (Amuse 3D, India);
- levigatura a vapore 215,65 €;
- producendo solo in Europa: 261,17 € (STURM, Germania, 14-19/10), 291,88 € (3D Center, Polonia), Svezia da
  321 €.

## La pagina della richiesta

Sorgente `richiesta_stampa.html`. Per la rev. B: correggi il sorgente, rifai PDF e zip.

Rigenerare il PDF: il sorgente non ha `html`/`head`/`body` (è un frammento). Avvolgilo in
`<!doctype html><html lang=it><head><meta charset=utf-8></head><body>…</body></html>` e stampalo con Chrome
headless. Serve una `--user-data-dir` separata, altrimenti Chrome, già aperto, si blocca:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-first-run \
  --user-data-dir=<cartella temporanea> --virtual-time-budget=8000 --no-pdf-header-footer \
  --print-to-pdf=<pdf> file://<html>
```

Lo zip: `zip -X` con il PDF, gli 8 file dei pezzi e `assieme.step`.
