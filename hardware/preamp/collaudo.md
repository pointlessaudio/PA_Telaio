# Preamp JFET: collaudo a banco (29/10/2026)

Procedura del solo preamp (circuito V4a, `risultati.md`), da fare sulla schedina prima di collegarla alla scheda
principale. I valori attesi vengono dalla simulazione (`sim/uscita.txt`), non da misure: **il circuito non è mai
stato acceso**, quindi ogni scostamento va annotato, non forzato. Se un passo non torna, ci si ferma lì.

Strumenti: tester con ingresso da 10 MΩ, oscilloscopio (o un'interfaccia audio con un visualizzatore), un
generatore di seno a 1 kHz (anche un'app o l'interfaccia) con un attenuatore a partitore per arrivare a
100 mVpp circa, alimentatore a 8,5 V (o la scheda principale, che dà VA).

## 1. Senza JFET (zoccoli vuoti)

Alimentare con VA = 8,5 V. Con i J201 tolti non scorre corrente di canale.

| Dove | Atteso | Se no |
|---|---|---|
| VA sulla schedina | 8,5 V (quello della scheda principale) | controllare alimentazione e diodo |
| **VG**, nodo del partitore 39k/10k | **1,73 V** (8,5 × 10/49) | 39k e 10k invertite o di valore sbagliato; 22 µF al contrario |
| Drain dei due stadi, di entrambi i canali | VA, 8,5 V (nessuna caduta) | corto verso massa o resistenza di drain sbagliata |
| Source dei due stadi | 0 V | |

Misurare VG sul nodo del partitore, non sul gate: attraverso la 1M di polarizzazione e i 10 MΩ del tester si
leggerebbe circa il 9 % in meno (≈ 1,57 V) e sembrerebbe un errore. Controllare con il tester in continuità che la
massa del GAIN (47 µF) e le masse dei due canali siano quelle giuste e che nessun canale sia in corto con l'altro.

## 1b. Scelta dei J201: IDSS ≥ 0,5 mA

In simulazione i J201 con IDSS bassa (0,2 mA) hanno una spinta dura, con la terza armonica sopra la seconda, a
guadagni moderati (12-16 dB); da 0,5 mA in su no (`risultati.md`, §Pot del GAIN). Per ogni esemplare: gate e
source in corto, 9 V fra drain e source con il tester in serie sulla portata mA; la corrente letta è IDSS. Tenere
quelli con IDSS ≥ 0,5 mA (il datasheet dà 0,2-1,0 mA), e per i due stadi dello stesso canale e fra i canali
scegliere esemplari vicini. Annotare IDSS di ognuno.

## 2. Con i JFET: punto di lavoro

Mettere i J201 (attenzione al verso: il layout usa piedino 1 = drain, 2 = source, 3 = gate, dal datasheet
Central Semiconductor; altri produttori possono differire, controllare il datasheet del lotto prima di saldare),
GAIN a metà, nessun segnale.

Attesi, da `uscita.txt` (cinque angoli del J201, IDSS 0,2-1,0 mA):

| Punto | Intervallo atteso | Esemplare «medio» |
|---|---|---|
| **Vd1** (drain stadio 1) | **4,5-6,5 V** senza regolare nulla (simulato 5,0-6,2 V) | 5,6-5,95 V |
| Vs1 (source stadio 1) | 1,8-2,7 V | 2,1-2,35 V |
| Id1 = Vs1 / 22k | 0,08-0,12 mA | 0,09-0,11 mA |
| Vd2 (drain stadio 2) | 5,0-6,1 V | 5,5-5,8 V |
| Vs2 (source stadio 2) | 1,8-2,6 V | 2,0-2,3 V |

Il source del primo stadio si misura con il GAIN: la 22k è in parallelo al reostato solo per il segnale, in
continua il condensatore da 47 µF lo isola, quindi la tensione DC non dipende dal GAIN. Se cambia ruotando il
pot, il 47 µF è perso o al contrario.

**Cosa fare se un J201 sta fuori** (Vd1 sotto 4,5 V o sopra 6,5 V):
1. Vd1 alto (sopra 6,5 V): esemplare debole, poca corrente. Vd1 basso (sotto 4,5 V): troppa corrente o IDSS alta.
2. Non si toccano resistenze né si aggiunge un trimmer: la scelta di progetto è che il punto di lavoro cada nei
   limiti con qualunque J201 genuino.
3. Si cambia esemplare, anche fra i 4 comprati e le scorte. Misurare tutti e tenere i due più vicini.
4. Se la maggior parte dei J201 sta fuori nello stesso verso, il lotto è sospetto (rimarcato o di un altro tipo):
   cambiare fornitore, non circuito.
5. Un drain a VA o a 0 V non è un esemplare fuori misura: JFET morto, piedinatura girata o gate scollegato.

## 3. Passthrough, PRE spento e acceso

Segnale 1 kHz a 100 mVpp all'ingresso, scheda principale collegata (o carico 1 MΩ sul punto d'uscita).

1. **PRE spento**: il segnale passa senza toccare il preamp. Uscita = ingresso, 0 dB (fase invariata). Con il
   preamp scollegato in questa posizione non devono comparire rumore né ronzio in più rispetto alla scheda
   principale da sola.
2. **PRE acceso, GAIN al minimo, LEVEL al massimo** (cursore verso l'uscita): guadagno a 1 kHz di **+5…+6,3 dB**
   (da +5,1 a +6,3 secondo l'esemplare; ×1,8-2,1 in tensione). Con 1 Vpp in, forma d'onda pulita (THD simulata 0,23 %).
3. **GAIN al massimo**: **+20…+25,7 dB**. Per misurarlo riportare l'ingresso a circa 10 mVpp, altrimenti satura.
4. Banda: 50 Hz e 15 kHz entro 0,5 dB da 1 kHz.
5. Il pot GAIN deve dare un aumento continuo e crescente girandolo in senso orario. Se il guadagno è
   massimo a manopola tutta a sinistra, la curva del pot o il senso sono sbagliati (vedi `ordine_componenti.md`,
   Preamp JFET).

## 4. Regolazione del LEVEL (una volta, per canale)

Il LEVEL serve a fare in modo che il preamp non possa dare al codec più di 3,4 Vpp (limite del codec: 3,6 Vpp).

1. PRE acceso, **GAIN al massimo**, LEVEL al massimo.
2. Ingresso forte: 1 Vpp a 1 kHz, abbastanza da portare il preamp in saturazione piena.
3. Misurare sull'oscilloscopio il picco-picco **al punto d'ingresso del codec** (uscita del buffer).
   Senza LEVEL ci si aspetta circa **4,2 Vpp** (simulato 4,24 al massimo).
4. Girare il trimmer finché il picco-picco vale **3,4 Vpp o meno**. Il trimmer finisce intorno a 0,80 del
   percorso verso l'uscita (4,24 × 0,80 = 3,39 Vpp).
5. Toccare il trimmer con un cacciavite isolato: la lettura non deve cambiare mentre si ritira la mano.

## 5. Pareggio dei due canali

Fra due esemplari di J201 la differenza di guadagno arriva a ±3 dB (simulata). Il LEVEL abbassa e basta, quindi:
1. Eseguire il punto 4 su entrambi i canali.
2. Stesso segnale su L e R, GAIN a metà, 100 mVpp: confrontare le due uscite.
3. Se differiscono più di 1 dB, abbassare il LEVEL del canale più forte finché sono pari. Si perde un po' di
   tetto d'uscita su quel canale, ma resta sotto il limite del codec.
4. Ripetere a GAIN al massimo con 10 mVpp: se la differenza è ancora grande (oltre 2 dB) cambiare il J201 più
   lontano dalla media (torna al punto 2).

Si usa un solo pot GAIN per i due canali (sezione doppia), quindi lo scarto fra le sezioni del pot si somma a
quello dei J201: se pesa, annotarlo.

## 6. Rumore e ascolto

- **Rumore**: ingresso chiuso su 10 kΩ verso massa, uscita su oscilloscopio o interfaccia. Simulato, riportato
  all'ingresso: 2,0-2,4 µV con GAIN da metà in su, **3,6-3,75 µV col GAIN al minimo** (la 10k di sorgente da sola
  fa 1,82 µV). È il punto aperto del progetto: col GAIN al minimo il soffio andrà confrontato a orecchio con la
  stessa sorgente senza preamp (PRE spento).
- **Ronzio**: toccare il cavo d'ingresso e la schedina: un ronzio forte indica massa o schermo da rivedere (il
  fondo piano non c'è: veroboard).
- **Ascolto**: chitarra o sintetizzatore sull'ingresso, PRE acceso. GAIN al minimo: suono quasi pulito, appena più
  pieno. Salendo col GAIN la spinta dovrebbe cominciare presto (simulata: THD all'1 % con 30-35 mVpp
  all'ingresso, GAIN al massimo), con la seconda armonica che domina; oltre il 10 % di THD la saturazione si
  fa più simmetrica e più dura. Questo è il giudizio che la simulazione non può dare: se non piace, il circuito
  si ritocca, non si rattoppa.
- Annotare in `docs/stato.md` esito, esemplari usati (Vd1 e Vs1 misurati) e scostamenti dalla simulazione.
