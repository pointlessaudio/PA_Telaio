# Schema KiCad (29/10/2026)

Schema elettrico completo di PA-TELAIO per KiCad 10, **generato da script**, non disegnato a mano. Comprende
la veroboard principale, la schedina del preamp JFET, le parti fuori scheda (jack, deviatori, footswitch, pot,
encoder, OLED, scheda tasti), la scheda MIDI e la microSD: 127 componenti, 94 reti.

È la base per le due strade a circuito stampato di `../strade_circuito.md` (JLCPCB e fresatura CNC). La PCB
non è ancora disegnata.

## Comandi

```bash
uv run genera_schema.py      # scrive pa-telaio.kicad_sch, PA.kicad_sym, sym-lib-table, reti_attese.json (~1 min)
python3 verifica_schema.py   # "OK: netlist di KiCad uguale a quella attesa ..., ERC senza errori"
python3 test_schema.py       # 6 mutazioni dello schema, ogni riga RILEVATO
```

Serve KiCad 10 (`kicad-cli`), in `/Applications/KiCad` o `~/Applications/KiCad`. Per aprire lo schema:
`pa-telaio.kicad_pro`.

## Da dove vengono le reti

| Parte | Fonte |
|---|---|
| veroboard (Seed3, TLC2272, alimentazione, ingressi, uscite) | `hardware/layout.py` |
| schedina preamp | `hardware/preamp/layout_preamp.py`, riferimenti rinumerati da 101 (originale nel campo `Layout`) |
| terminali fuori scheda e fili | `case/cablaggio.py` |
| parti fuori scheda, scheda MIDI, microSD | tabella `FUORI` in `genera_schema.py`, dalla pagina `prototipo-veroboard-seed3.html` e da `cablaggio.py` |

Le reti si calcolano come nel montaggio vero: ogni scheda ha le sue, ogni terminale fuori scheda (un lug di
jack, un pin del deviatore) è un nodo a sé, e solo i fili di `cablaggio.py` li uniscono. Un filo che manca
lascia una rete divisa (`GND_2`) e il generatore lo segnala come errore; un terminale senza parte o una rete
con un solo piedino anche.

## Come è fatto lo schema

Un foglio A0, un blocco per scheda. Ogni piedino porta un'etichetta col nome della sua rete; non ci sono fili
disegnati. Si legge meno bene di uno schema disegnato a mano, ma è corretto per costruzione e si rigenera a ogni
modifica delle fonti: **non va modificato a mano** (le modifiche si perdono alla rigenerazione).

I simboli sono nella libreria di progetto `PA.kicad_sym` (scritta dal generatore). Le impronte sono quelle
delle librerie ufficiali di KiCad 10, solo per i componenti delle due schede; le parti montate sul pannello non
ne hanno. Al primo avvio KiCad crea le tabelle globali delle librerie: prima di allora l'ERC dà 78 avvisi
`footprint_link_issues`, che non sono errori.

## Cosa controlla la verifica

`verifica_schema.py` fa esportare la netlist a KiCad stesso e la confronta con `reti_attese.json`, rete per
rete e piedino per piedino (quali piedini stanno insieme, non i nomi). Poi lancia l'ERC. `test_schema.py`
rovina lo schema in sei modi (etichetta rinominata, due ingressi scambiati, etichetta tolta, simbolo spostato,
segno di non collegato tolto, massa staccata) e la verifica deve accorgersene ogni volta.

La verifica prova che lo schema riproduce le fonti, non che le fonti siano giuste: quelle sono verificate dai
loro script (`layout.py`, `layout_preamp.py`, `cablaggio.py`).

## Scostamenti trovati trascrivendo

- **Polo C del 3PDT (LED del bypass):** la pagina `prototipo-veroboard-seed3.html` ha ancora la versione vecchia
  (catodo sul comune, anodo con 1 kΩ a 3V3D). Lo schema segue `cablaggio.py` (29/10): R 4,7 kΩ da VA sul comune,
  posizione effetto all'anodo, catodo a massa.
- **Contatto della punta dei jack d'ingresso:** la pagina chiede che vada a massa (a jack scollegato l'ingresso
  non fruscia), ma in `cablaggio.py` quel filo non c'è. Nello schema è un ponticello sul jack, fra contatto e
  manicotto (J201, J202): da aggiungere al cablaggio.
- **GAIN:** ogni gang del pot doppio è usata come reostato, cursore e un capo (pagina di montaggio del preamp);
  il terzo capo resta libero.
