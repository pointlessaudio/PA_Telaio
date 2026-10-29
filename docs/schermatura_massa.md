# Schermatura e masse nel case stampato

Progetto (29/10/2026), non costruito né misurato. Il case è di PETG: nessuno schermo. Dentro ci sono il Seed3
(digitale, codec, USB), l'OLED I2C, MIDI e microSD, e il preamp JFET con ingresso da 1 MΩ e fino a +26 dB
(`hardware/preamp/risultati.md`). Il punto debole è il nodo ad alta impedenza dopo il jack d'ingresso (1M di
polarizzazione, gate del J201), sia sulla schedina sia sulla veroboard (R6/R9, 1M, a partire dalla striscia 30)
quando PRE è spento. Coordinate come in `case/case.py` (mm; X da sinistra, Y dal fronte, Z in su, origine sotto
il fondo). Rame da 0,1 mm in tutto: nastro + adesivo.

Regola base: **lo schermo è un pezzo di rame che si collega al circuito in un punto solo** (la massa dei jack
d'ingresso). Se tocca la massa in due punti diventa un anello di massa; se non tocca nulla fa da antenna.

## 1. Nastro: dove, come, a che distanza

**Tipo**: nastro di rame con **adesivo conduttivo** (adesivo acrilico conduttivo, quello da schermatura EMI;
quello da hobby/vetrate ha l'adesivo isolante e fra una striscia e l'altra non passa corrente). Larghezza **20 mm**,
da tagliare alla misura. Spessore totale ~0,1 mm (dato di partenza del progetto; da confermare sul rotolo scelto).
Non si salda sul nastro nel case (il PETG si ammorbidisce sopra ~80 °C): ogni contatto è a pressione, sotto una
vite con capocorda, o per sovrapposizione.

**Sovrapposizioni**: ogni striscia copre la vicina di almeno 3 mm, adesivo contro rame; negli angoli il nastro si
piega (non si taglia) con una piega di 8 mm sulla faccia vicina. Dopo la posa, premere con un'unghia di plastica.

### Vasca (la parte che fa il lavoro)

| Faccia | Rame | Note |
|---|---|---|
| Fondo interno (205 × 129 mm) | tutto, ~8 strisce lungo X | stima 1,7 m. Tagliare intorno alle 5 colonne, alle 4 colonnine della veroboard, alle 2 della schedina, alla torre del footswitch |
| Pareti: fronte, sinistra, destra | una corsia da 20 mm a partire dal fondo (z 2,4-22,4) e, per Y > 60, una seconda corsia sopra (z 21-41) | la prima corsia piega 8 mm sul fondo e si unisce al rame del fondo. Stima 0,6 m. Fermarsi **a 4 mm sotto il bordo** delle pareti: lì entra il labbro del pannello superiore (gioco 0,3 mm, vedi §4) |
| Parete sinistra | niente rame nel riquadro Y 25-100 intorno alla USB-C | vedi distanze sotto: la USB-C è massa digitale (la microSD è sul pannello posteriore dal 29/10) |
| Parete posteriore | niente: la copre il pannello posteriore | |

Colonne (5): anello di nastro attorno al fusto e lungo 8 mm sulla faccia superiore, per portare il rame fino
al giunto con la torretta (§1, pannello superiore).

### Pannello posteriore (faccia interna, quella rivolta alla vasca)

**Una fascia da 12 mm** (nastro da 20 tagliato a lungo), x 120-198, z 30-42, sopra i jack IN L, IN R, OUT L,
OUT R. Il pannello va da z 2,7 a 43,2: la fascia lascia 3 mm sopra i corpi dei jack (z 26,5) e 1 mm sotto
il bordo alto. Si ferma a x 198 perché oltre c'è il montante.

Niente rame intorno a GAIN (x 109, z 33,5), PRE (x 109, z 18,5) e alla fessura microSD con la sua culla (x 23, z 31,5), né sui jack DC, MIDI, PEDALE e sul deviatore
INST/LINE: sono metallo con potenziali che non sono quello dello schermo. Fascia sinistra (x 12-97, z 30-42) solo se
dopo la prima misura resta ronzio; si collegherebbe al capocorda con un filo.

Il **capocorda di massa L0** sta su questa fascia (§2).

### Pannello superiore (faccia inferiore)

Tre pezzi, più 5 anelli:
- **fascia posteriore**: y 108-130 misurata in pianta, x 15-197 (stima 0,18 m); sopra non c'è nessun componente,
  la fila dei pot arriva a y 107;
- **fascia centrale** fra le due file dei pot: x 118-206, y 76-90 (14 mm, 0,09 m); passa sopra la schedina;
- **collegamento destro**: x 197-205, y 90-110, che unisce le due fasce;
- **anelli**: sotto ognuna delle 5 torrette un anello di nastro con foro Ø 3,4 (come la vite passante), largo
  quanto la torretta (Ø 10) e sovrapposto alla fascia dove arriva (le due torrette dietro, a y 120). Gli
  anelli delle altre tre torrette (a y 9,5) restano isolati sul pannello e servono solo al contatto con la colonna:
  collegarli alla fascia con una striscia che sale a y 108 oppure ometterli; ometterli è corretto, il contatto
  col fondo passa dalle due torrette posteriori e dalle pareti.
  Con la vite serrata il giunto colonna-torretta si chiude (c'è 0,3 mm di gioco): l'anello fa da rondella fra il
  fusto in rame della colonna e l'inserto di ottone.

### Distanze minime

| Da | Distanza |
|---|---|
| Piazzole e fili della veroboard e della schedina | 3 mm in aria; sotto di esse Kapton sopra il rame del fondo (vedi sotto) |
| Terminali dei pot e dell'encoder sotto il pannello (4-4,5 mm di piedini) | 3 mm: le fasce del pannello superiore non toccano le zone y 59-71 e y 95-107 dei pot |
| Corpi metallici dei jack OUT, PEDALE, MIDI, deviatore INST/LINE, PRE, GAIN | 3 mm |
| **Jack DC**: il bossolo esterno è **+9 V** (centro negativo) | 5 mm, e lo stesso per il capocorda positivo di VIN: un corto qui brucia D1 |
| Guscio USB-C del Seed, lettore microSD e suo telaio (massa digitale) | 5 mm |
| Viti M3: le 4 della veroboard (punte nei piloti) e le 2 della schedina | niente rame nel cerchio Ø 12 intorno alla colonnina |
| Fori delle 5 viti dal fondo | niente rame nel cerchio Ø 8 sotto la testa (la testa sta fuori dall'impronta) |

**Isolamento sotto le schede**: il rame del fondo sta 4 mm sotto la faccia inferiore delle schede, e i terminali
tagliati sporgono fino a ~2 mm. Sopra il rame, nell'impronta della veroboard (x 4,5-119, y 18,5-95) e della
schedina (x 122-184, y 51-98) steso Kapton (nastro di poliimmide 20 mm, o un foglio di acetato da 0,2 mm).

## 2. Un solo punto di massa

Il rame ha **un solo collegamento al circuito**: il filo F0 da un capocorda sul pannello posteriore al manicotto
(lug) del jack IN L. La massa del circuito è già un nodo unico (`hardware/layout.py`: i manicotti dei cinque jack
arrivano tutti sulla striscia GND, AGND pin 20 e DGND pin 40 si uniscono alla striscia 22 con W2/W3), quindi
legare lo schermo al manicotto di IN L equivale a legarlo alla stella d'ingresso.

```
                         rame: fondo + pareti + colonne -> anelli -> pannello superiore
                                              |
   (nessun altro contatto)               F1 (filo, ~45 mm)
                                              |
  rame posteriore ----------- L0 ----- F0 ------ manicotto IN L  ===  massa del circuito
  (fascia z 30-42)        (capocorda)  (~25 mm)
```

- **L0**: capocorda ad anello M3 sotto una vite M3×8 con dado, nel pannello posteriore a x 135,5, z 32,0 (richiesta
  1, §4). Il dado è fuori, nella finestra, la testa e il capocorda dentro, sopra il nastro della fascia, con
  una rondella dentellata fra capocorda e nastro: l'adesivo conduttivo non basta come unico contatto, la vite lo
  stringe. Su L0 si attestano F0 (a IN L) e F1.
- **F1**: filo verde/giallo 0,5 mm², ~45 mm, da L0 a **L1**, capocorda sul fondo della vasca (torretta `MASSA_L1` in `case/case.py`, 29/10), che
  preme sul nastro del fondo. Così il rame del fondo, delle pareti e (per le colonne) del pannello superiore arriva a L0
  senza altro contatto fra le due parti.
- Niente altro collega il rame ai metalli del circuito. In particolare lo **schermo non tocca**: manicotti dei
  jack OUT, PEDALE, MIDI, DC; guscio USB; telaio microSD; header del Seed; carcasse dei pot; viti M3 (le viti
  dal fondo toccano l'anello dell'inserto, cioè il rame: va bene, è lo schermo).

### Schema delle masse (stella)

```
                     jack IN L/R:  manicotti  --- massa d'ingresso (N_IN)
                       |   calze dei cavi dal jack (un solo lato, §3)
                       |   F0 verso lo schermo (L0)
                       v
veroboard (nodo GND unico, strip 22: AGND pin 20 + DGND pin 40 si uniscono qui, W2/W3)
   |-- manicotti IN L/R, OUT L/R, DC, scheda I/O, OLED, controlli digitali (come layout.py)
   |
   +-- UN filo di massa (con VA: due fili intrecciati ~100 mm) alla schedina,
       sul pad GND (0,8) "stella della scheda"  ---  GND_a (segnale) e GND_b (alimentazione) restano
       separate sulla schedina, si uniscono sul pad (J1/J2/J3, `layout_preamp.py`); GNDc (ritorno 47 uF)
       torna al pad col solo W1/W2
```

Si uniscono:
- **AGND e DGND**: sulla veroboard, strip 22, come già fatto; non si aggiunge un secondo ponte.
- **Schedina e scheda principale**: solo col filo di massa insieme a VA. La calza del segnale sulla schedina
  non è mai una seconda connessione di massa (§3).
- **Schermo e circuito**: solo F0.

**Non** si uniscono:
- lo schermo con alcun jack tranne IN L (via F0);
- la massa digitale (D-GND dell'I/O e dell'OLED) alla schedina se non attraverso la veroboard;
- le calze, fra loro o con lo schermo, fuori dal lato prescelto;
- la carcassa del pot GAIN a nulla di partenza (è a 4-5 mm da GND_a, il reostato è a bassa impedenza, ~24K): se
  a banco toccarla cambia il rumore, un filo dalla carcassa a GND_a della schedina.

Nota: i diretti (OUT L/R e DC) hanno già la massa sulla veroboard; basta che il rame **non li tocchi**.

## 3. Calza dei cavi schermati: un lato solo

Cavetto schermato mono (anima + calza), calza collegata **al lato della sorgente**:

| Tratta | Calza collegata | Lato libero |
|---|---|---|
| jack IN L / IN R -> deviatore PRE o schedina | al manicotto del jack | calza tagliata raso, guaina termorestringente sopra |
| deviatore PRE -> schedina (IN) | alla calza della tratta precedente, sul deviatore (non alla massa del pannello) | lato schedina libero |
| schedina (uscita dopo LEVEL, 1 µF) -> veroboard (JINL/JINR) | al pad GND (0,8) della schedina | lato veroboard libero |
| INST/LINE: tratte dal jack | come le prime | |

La calza non serve da conduttore di ritorno del segnale: il ritorno è il filo di massa del §2. La tratta
cablata come sopra dipende da come passa il PRE nel cablaggio (`case/cablaggio.md`): vale la regola, ogni calza
ha un solo capo a massa e quello è il lato che sta dal jack verso l'interno.

Protezione: 25-30 mm di guaina termorestringente sul capo libero (taglio della calza a 3 mm dal bordo
guaina) e sulle saldature dei manicotti per non toccare il rame.

## 4. Cosa serve nel modello (`case.py`)

1. **Foro di massa L0** nel pannello posteriore, Ø 3,4 + `TOL_FORI`, a x 135,5, z 32,0: fatto il 29/10
   (`MASSA_L0` in `RETRO_PRE`, con ingombro interno 8 × 8 × 6 per capocorda, dado e punta della vite). Rientra
   nel controllo dei 3 mm bordo-bordo fra i fori del retro; mutazione «vite di massa L0 sul jack IN R» RILEVATO.
2. **Torretta di massa L1** sul fondo, Ø 8 × 4 con pilota M3, a x 109,5, y 101,5: fatta il 29/10 (`MASSA_L1`),
   con un ingombro Ø 10 × 7 sopra la torretta per capocorda, testa della vite e mano; mutazione «torretta di
   massa L1 sotto la veroboard» RILEVATO. Fili F0 e F1 in `case/cablaggio.py`.
3. **Gioco per il rame**: nessuna modifica agli incastri. Verifiche richieste nel test, con 0,1 mm per faccia di rame:
   - fondo -> pannello posteriore (gioco 0,3: z 2,4 contro 2,7) e pannello posteriore -> parete (0,3):
     restano ≥ 0,2;
   - colonna -> torretta (0,3 al giunto): l'anello da 0,1 è schiacciato dalla vite, non serve spazio;
   - **labbro del pannello superiore dentro le pareti (gioco 0,3)**: NON si mette rame sul labbro né sulla parete
     dentro la fascia di 4 mm sotto il bordo (0,1 + 0,1 = 0,2 su 0,3 sarebbe al limite; qui il test deve
     poter dire che, anche con 0,1 per faccia, il labbro entra).
4. **Facoltativo, dopo la prima misura (paratia)**: lamina verticale stampata 1,2 mm (+0,1 per faccia di rame) a
   **x ≈ 120,4** fra bordo veroboard (118,8) e schedina (122), y 51-98, alta 24 mm: separa la schedina dal
   digitale. Il gioco è 3,2 mm: restano 0,8 per lato. Da fare solo se il rumore del §5 lo chiede. Non è nel modello.
5. **Facoltativo**: segnare in `case.py` come volume di rispetto i riquadri senza rame (Y 25-100 sulla parete
   sinistra, cerchi Ø 12 e Ø 8 del §1) per un controllo automatico. Non necessario per il rame.

## 5. Verifica a banco

Strumenti: tester (continuità e Ω), interfaccia audio con un visualizzatore di spettro (o oscilloscopio con FFT),
un jack da 6,35 chiuso con **10 kΩ** fra punta e manicotto (la stessa sorgente della simulazione) e uno chiuso
in corto.

### A. Continuità del rame (case aperto, F0 e F1 staccati)

1. Fra due punti qualsiasi del fondo e delle pareti: **≤ 0,5 Ω**. Fra fondo e fascia centrale del pannello
   superiore, a case chiuso (5 viti serrate): ≤ 0,5 Ω.
2. La fascia posteriore del pannello posteriore, da sola: continua, ≤ 0,5 Ω fra le due estremità.
3. Con F0 staccata, **rame isolato da tutto**: fra il rame e ognuno di: manicotto IN L, IN R, OUT L/R, PEDALE;
   DC (sia centro sia bossolo); guscio USB-C; telaio microSD; header GND e VA del Seed; carcasse dei pot e
   dell'encoder; i terminali di PRE e GAIN. Letto > 1 MΩ (portata più alta), Seed e alimentazione spenti.
4. Rimontato F0: fra rame e manicotto IN L ≈ 0 Ω; resto invariato.

Se un punto del punto 3 conduce, è il punto da correggere (distanza, Kapton), non si scrive "sono vicini".

### B. Rumore a ingresso chiuso, GAIN al massimo

Collaudo preamp di base già passato (`hardware/preamp/collaudo.md`, §1-5), LEVEL regolato.
Misura a **banda 20 Hz-20 kHz**, PRE acceso, GAIN al massimo, uscita sull'interfaccia, ingresso su 10 kΩ, nessun
altro cavo; cella dei valori attesi: soffio simulato 2,0-2,4 µV riportato all'ingresso (con GAIN da metà in su),
cioè circa 2,2 µV × 20 = 44 µV = −85 dBu in uscita. Il ronzio non è simulato: va misurato.

| Misura | Con | Registra |
|---|---|---|
| 1 | case aperto, senza rame | livello totale, 50/100/150/250 Hz |
| 2 | case chiuso, senza rame (stesso circuito, nastro non posato) | idem |
| 3 | case chiuso, con rame, F0 collegato | idem |
| 4 | come 3 ma F0 staccata (rame flottante) | idem |
| 5 | come 3, ingresso **in corto** (0 Ω) | solo rumore dell'amplificatore |
| 6 | come 3, avvicinando una mano al pannello posteriore e al pannello superiore | variazione |

Criteri (da confermare alla prima prova, sono ipotesi):
- 3 contro 2: ronzio a 50 e 100 Hz **sceso di almeno 6 dB** o già nel pavimento (dentro 3 dB da quello di 5);
- livello totale di 3 entro **3 dB** dal pavimento simulato (−85 dBu a GAIN max);
- 4 non migliore di 3 (se lo è, la massa dello schermo è da rivedere, non lo schermo);
- 6: nessuna variazione apprezzabile in 3. Se cambia solo toccando il pannello superiore, la fascia centrale
  non è ben collegata (anelli, §1).

Ripetere col GAIN al minimo (punto aperto del preamp: 3,6-3,75 µV) e annotare in `docs/stato.md`.

### C. Rumore digitale

Case chiuso, schermo montato, Seed in marcia con l'OLED acceso e la scheda tasti attiva: ripetere 3 e 5 con la
sola 10 kΩ. Differenza rispetto a una misura con Seed spento (Seed alimentato ma fermo) = contributo digitale. Se
supera 3 dB sul pavimento: richiesta 4 (paratia) e, se non basta, schermare i fili dall'OLED.

### D. Se qualcosa non torna

Un solo cambiamento alla volta, rimisurare dopo ognuno: prima il lato della calza, poi il capocorda L0 (stringerlo,
controllare dentellata e rame sotto), poi la fascia sinistra del pannello posteriore, poi la paratia.

## Non verificato

Tutto: nessuna misura, nessuna prova del nastro sul PETG. Il tipo di nastro e il suo spessore, le quote delle
richieste (collisioni con la schedina e con PRE in particolare), l'ingombro del pot doppio (stimato in
`case.py`) e la posizione del contatto dei jack (flangia o corpo: dipende dal modello comprato) vanno controllati
sul pezzo vero.
