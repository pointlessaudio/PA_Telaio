# Preamp JFET d'ingresso: simulazione (29/10/2026)

Simulato in ngspice, non ancora costruito né ascoltato. Circuito attuale: **V4a**.

```
cd hardware/preamp/sim
python3 sim_preamp.py controllo   # harness su un circuito a risposta nota: deve dire CONTROLLO OK
python3 sim_preamp.py             # V4a su 5 angoli del J201, tabelle e criteri        -> uscita.txt
python3 varianti.py diagnosi      # escursione dei drain in saturazione, V0 e V4a      -> uscita_varianti.txt
python3 varianti.py               # ginocchio di tutte le varianti (circa 7 minuti)    -> uscita_varianti.txt
```

Il controllo verifica guadagno AC, estrazione delle armoniche (H2/H1 = −38,06 dB atteso e misurato) e rumore
integrato di una 10 kΩ (1,82 µV atteso e misurato).

## Circuito V4a (per canale)

```
sorgente + 10k ─ 47n ─┬─ 1k ─ G  J1  D ─┬─ 27k ─ VA        J2: gate a VG con 1M e 1k di stopper, D ─ 20k ─ VA,
                      1M                │                      S ─ 15k ─ massa (niente bypass)
                      │                 └─ 220n ─ gate J2   uscita: D2 ─ 1µ ─ LEVEL 100k (trimmer) ─ buffer TLC2272 (1M)
                     VG = 1,73 V        S ─┬─ 22k ─ massa
   (39k / 10k da VA, 22µ)                  └─ GAIN: reostato 25k curva A al contrario + 220R ─ 47µ ─ massa
```

- **Gate polarizzati a VG** da un partitore comune: la corrente di riposo è ~(VG − Vgs)/Rs e dipende poco
  dall'esemplare. Sui 5 angoli del J201 (IDSS 0,2-1,0 mA, Vp −0,3…−1,5 V) i drain stanno fra 5,0 e 6,2 V:
  **niente trimmer di drain**, a differenza dello schema Fetzer.
- **Il primo stadio fa il carattere**, il secondo è quasi lineare: Rs da 15k non bypassata, guadagno ~1,3, serve
  da separatore e per pilotare il LEVEL.
- **LEVEL**: trimmer da regolare una volta a ~0,80. Il preamp satura da solo a 4,2 Vpp al massimo: con LEVEL a
  0,80 il codec (3,6 Vpp) non può saturare, qualunque sia il GAIN.

## Risultati V4a (5 angoli del J201, carico 1 MΩ)

| Criterio | Misura | |
|---|---|---|
| Vd senza trimmer fra 4 e 6,5 V | 5,02-6,24 V | PASS |
| Banda 20 Hz-20 kHz entro 0,5 dB | 0,17 dB | PASS |
| GAIN al minimo ≤ +12 dB | +5,1…+6,3 dB (+3,2 dB col LEVEL a 0,80) | PASS |
| GAIN al massimo ≥ +20 dB | +20,1…+25,7 dB | PASS |
| Pulito: GAIN al minimo, 1 Vpp in, THD ≤ 3 % | 0,23 % | PASS |
| Tetto d'uscita, LEVEL per ≤ 3,4 Vpp | 4,24 Vpp → LEVEL 0,80 | PASS |
| Rumore riportato all'ingresso ≤ 3,5 µV (la sola 10k di sorgente fa 1,82 µV) | 2,0-2,4 µV con GAIN da metà in su, **3,6-3,75 µV col GAIN al minimo** | **NO** |
| Spinta: H2 − H3 ≥ +3 dB al 3 % di THD, GAIN a metà e al massimo | +6,5 dB al peggio, fino a +28,6 | PASS |
| Ginocchio col GAIN al massimo: ≥ 10 dB fra THD 1 % e 10 % | 12-21 dB | PASS |

- **Rumore col GAIN al minimo**: lo supera di 0,25 µV. Lì il source del primo stadio è quasi tutto non bypassato
  e la 22k aggiunge il suo rumore termico. Col GAIN al minimo il preamp ha solo +3-6 dB e serve per sorgenti
  forti, quindi pesa poco; non l'ho corretto per non spostare la polarizzazione.
- **Soglia del guadagno massimo abbassata da +23 a +20 dB** rispetto al primo giro: con V4a la spinta parte
  molto prima (THD all'1 % con −30…−38 dBu all'ingresso, cioè 30-35 mVpp), quindi serve meno guadagno.
- Differenza fra esemplari: ±3 dB di guadagno, i due canali si pareggiano col LEVEL.

Come si comporta (angolo «modello»): col GAIN al massimo la THD passa l'1 % a −34 dBu all'ingresso e il 10 % 16 dB
più su, con la seconda armonica 28 dB sopra la terza al 3 %. Oltre il 10 % la saturazione diventa più simmetrica
e la terza armonica cresce: è il limite dell'escursione, a distorsione già alta.

## Pot del GAIN: il doppio C25K non si trova (29/10)

In simulazione il GAIN è un reostato da 25k con curva antilogaritmica (C). Doppio da 9 mm C25K non risulta in
vendita (Cusack/Tayda: curva C doppia solo 50K e 100K; vedi `hardware/ordine_componenti.md`). Tre strade simulate
con lo stesso script (criteri completi su 5 angoli):

| Pot | Guadagno min…max | Rumore al minimo | H2 − H3 al 3 % a metà corsa | Note |
|---|---|---|---|---|
| doppio C25K (V4a) | +5…+26 dB | 3,75 µV | +6,5 dB al peggio | non si trova |
| doppio C50K | +3…+26 dB | 4,3 µV | **−16,5 dB** (angolo «basso») | corsa più regolare |
| doppio C50K con 47k in parallelo per gang | +5…+26 dB | 3,7 µV | **−15,1 dB** (angolo «basso») | estremi come il 25k, metà corsa più bassa |

Nelle due varianti col 50K la metà corsa cade a 12-16 dB di guadagno, e lì i J201 con IDSS bassa (angoli «basso»
e «basso-Vp», 0,2 mA) saturano con la terza armonica sopra. Gli angoli con IDSS ≥ 0,5 mA restano a +4 dB o più.
Il 25K evitava quella zona per caso, non per merito. Rimedio pratico, indipendente dal pot: **scegliere i J201
con IDSS ≥ 0,5 mA** (si misura a banco con gate e source in corto, vedi `collaudo.md`). Scelta del pot aperta.

## Come ci si è arrivati

Prima simulazione (**V0**): secondo stadio con source bypassato, +6 dB. Spinta troppo brusca (da 1 a 10 % di THD
in 4-6 dB col GAIN basso) e terza armonica alla pari della seconda. La diagnosi (`varianti.py diagnosi`) ha
mostrato che a tagliare era il **secondo stadio**: la sua escursione restava ferma qualunque fosse il drive,
mentre quella del primo cresceva.

Ginocchio col GAIN al massimo sui tre angoli estremi (dB fra THD 1 % e 10 %; H2 − H3 al 3 %):

| Variante | Modifica | Ginocchio | H2 − H3 al 3 % | Esito |
|---|---|---|---|---|
| V0 | prima simulazione | 6-13 dB | −28…+7 dB | spinta brusca |
| V1a/b | drain più alti (Rd 15k / 12k) | 15-19 dB | +16…+23 dB | meglio, ma −4/−8 dB di guadagno, H3 domina col GAIN basso |
| V2a/b | Rs mai tutta bypassata (220R → 1k / 2,2k) | 3-6 dB | −9…+4 dB | peggio: scartata |
| V3a | secondo stadio senza bypass | 12-20 dB | +17…+27 dB | buona; col GAIN a metà l'angolo «basso» cede (H2 − H3 = −22 dB) |
| **V4a** | V3a + meno corrente nel primo stadio (Rs1 22k, Rd1 27k) | 12-20 dB | +16…+29 dB | **scelta**: H2 domina anche col GAIN a metà su tutti gli angoli |
| V4b | come V4a con Rd1 30k | 12-19 dB | +16…+28 dB | col GAIN a metà l'angolo «basso» torna a −8 dB |

L'angolo «basso» (IDSS 0,2 mA, Vp −0,3 V) lavorava a Vgs ≈ −0,07 V, troppo vicino a IDSS: con meno corrente nel
primo stadio (V4a) ha margine.

## Limiti della simulazione

La sorgente è una resistenza da 10 kΩ, non un pickup (induttanza e capacità del cavo non ci sono);
l'alimentazione è ideale, senza ripple; il modello J201 di LTspice ha Kf = 0, quindi niente rumore 1/f. Il
giudizio sul carattere è all'ascolto del circuito vero.
