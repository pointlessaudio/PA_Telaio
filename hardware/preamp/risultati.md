# Preamp JFET d'ingresso: simulazione (29/10/2026)

Prima versione simulata in ngspice, non ancora costruita né ascoltata.

```
cd hardware/preamp/sim
python3 sim_preamp.py controllo   # harness su un circuito a risposta nota: deve dire CONTROLLO OK
python3 sim_preamp.py             # preamp su 5 angoli del J201, tabelle e criteri (uscita in uscita.txt)
```

Il controllo verifica guadagno AC, estrazione delle armoniche (H2/H1 = −38,06 dB atteso e misurato) e rumore
integrato di una 10 kΩ (1,82 µV atteso e misurato).

## Circuito (per canale)

```
sorgente + 10k ─ 47n ─┬─ 1k ─ G  J1  D ─┬─ 20k ─ VA          J2 uguale, con Rs = 8k2 + 6k8 (6k8 bypassata da 47µ)
                      1M                │                    uscita: 1µ ─ LEVEL 100k (trimmer) ─ buffer TLC2272 (1M)
                      │                 └─ 220n ─ gate J2 (1M a VG, 1k di stopper)
                     VG = 1,73 V        S ─┬─ 15k ─ massa
   (39k / 10k da VA, 22µ)                  └─ GAIN: reostato 25k curva A al contrario + 220R ─ 47µ ─ massa
```

- **Gate polarizzati a VG** da un partitore comune: la corrente di riposo è ~(VG − Vgs)/Rs e dipende poco
  dall'esemplare. Sui 5 angoli del J201 (IDSS 0,2-1,0 mA, Vp −0,3…−1,5 V) i drain stanno fra 5,0 e 6,1 V:
  **niente trimmer di drain**, a differenza dello schema Fetzer.
- **GAIN sul primo stadio** (bypass variabile del source): il primo stadio dà il guadagno, il secondo (+6 dB)
  porta il segnale al LEVEL. La prima versione aveva il DRIVE fra i due stadi: a metà corsa il rumore riportato
  all'ingresso saliva a 8-36 µV, perché il pot attenuava prima del secondo stadio. Scartata.
- **LEVEL**: trimmer da regolare una volta a ~0,69. Il preamp satura da solo a 4,6-4,9 Vpp: con LEVEL a 0,69
  il codec (3,6 Vpp) non può saturare, qualunque sia il GAIN.

## Risultati (5 angoli del J201, carico 1 MΩ)

| Criterio | Misura | |
|---|---|---|
| Vd senza trimmer fra 4 e 6,5 V | 5,02-6,09 V | PASS |
| Banda 20 Hz-20 kHz entro 0,5 dB | 0,19 dB | PASS |
| GAIN al minimo ≤ +12 dB | +8,9…+10,5 dB (+5,6 dB col LEVEL a 0,69) | PASS |
| GAIN al massimo ≥ +23 dB | +23,4…+29,2 dB | PASS |
| Pulito: GAIN al minimo, 1 Vpp in, THD ≤ 3 % | 2,92 % al peggio (0,7-1 % negli angoli centrali) | PASS |
| Tetto d'uscita, LEVEL per ≤ 3,4 Vpp | 4,92 Vpp → LEVEL 0,69 | PASS |
| Rumore riportato all'ingresso (la sola 10k di sorgente fa 1,82 µV) | 2,0-3,4 µV | PASS |
| Spinta fra 1 e 10 % di THD: H2 > H3 | 6 punti su 11 | **NO** |

La differenza fra esemplari è di ±3 dB di guadagno: due canali vanno pareggiati col LEVEL.

## Aperto: il carattere della spinta

Fino a qualche % di THD domina la seconda armonica, come voluto. Poi la saturazione arriva in fretta (da 1 a
25 % di THD in circa 6 dB) e con la terza armonica alla pari o sopra: più vicina a un taglio netto che alla
spinta morbida cercata. Prossimo giro, da provare uno alla volta in simulazione:
1. spostare il riposo del drain verso l'alto, così il taglio arriva prima dal lato dell'interdizione (morbido)
   che da quello ohmico (duro);
2. lasciare una parte di Rs non bypassata anche col GAIN al massimo, per allungare il ginocchio;
3. tenere il secondo stadio lontano dalla saturazione e far saturare solo il primo.

Fuori dalla simulazione: la sorgente è una resistenza da 10 kΩ, non un pickup (induttanza e capacità del cavo
non ci sono); l'alimentazione è ideale, senza ripple; il modello J201 di LTspice ha Kf = 0, quindi niente
rumore 1/f. Il giudizio finale sul carattere è all'ascolto del circuito vero.
