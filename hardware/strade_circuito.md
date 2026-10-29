# Circuito: tre strade a confronto (29/10/2026)

Nessuna scelta presa. Prezzi JLCPCB dalla stima del 28/09 in `docs/progetto.md`; gli altri costi sono stime da verificare
prima di ordinare.

| | Veroboard | PCB montata da JLCPCB | PCB fresata in casa (CNC) |
|---|---|---|---|
| Pronta da costruire | sì: `layout.py` verificato, 57 tagli | no: lo schema KiCad c'è (`kicad/`, 29/10), manca il disegno della PCB | no: stesso schema e stessa PCB, poi gerber → G-code (FlatCAM o simili) |
| Costo | solo componenti | circa 65-100 € (5 circuiti, 2 montati, scheda I/O inclusa) | lastra ramata 2-5 €, frese a V; se la CNC non c'è, una 3018 costa 150-250 € |
| Tempi | una sera di montaggio | 1-2 settimane di disegno + 1-2 di spedizione | disegno come JLCPCB, poi un pomeriggio di prove di fresatura |
| Operazionali | TLC2272 DIP | OPA1652 SMD (montato da loro), quello dei circuiti del datasheet Seed3 | TLC2272 DIP, o OPA1652 su SOIC se te la senti di saldarlo |
| Massa e rumore | strisce e ponticelli: la parte più debole | piano di massa pieno su un lato: la migliore | piano di massa sul lato rame, una sola faccia: buona |
| Fori metallizzati, solder mask | no | sì | no (si stagna o si vernicia); doppia faccia difficile da allineare |
| Sagoma e fori nel case | 76 × 114, fori in `layout.py` | stessa sagoma, entra senza cambiare `case.py` | stessa sagoma |
| Ripetibilità | una unità | 5 circuiti, rifabbricabili | ogni scheda si rifresa |
| Rischio | errore di taglio o ponticello, trovabile col tester | errore di schema = giro da rifare (settimane, soldi) | isolamenti stretti, piste strappate; FR4 fa polvere di vetro (usare FR1 o aspirazione) |

## Lettura

- **Veroboard**: la strada per provare subito il circuito, che non è mai stato acceso. Il limite è la massa,
  e conta proprio negli stadi analogici sensibili come un preamp ad alto guadagno.
- **JLCPCB**: la strada per la versione buona, a circuito provato. Lo schema KiCad è in `kicad/`, generato
  dalle netlist di `layout.py`, `layout_preamp.py` e `cablaggio.py` e verificato contro di esse (29/10).
- **CNC**: sta in mezzo. Ha senso solo se la macchina c'è già o la vuoi per altri lavori; si fa con lo
  stesso KiCad della PCB, quindi il disegno vale per entrambe.

Ordine naturale: veroboard per il collaudo → KiCad dalla netlist → CNC per le iterazioni rapide di uno stadio
(per esempio il preamp) → JLCPCB per la versione finale.
