"""
Preamp JFET d'ingresso di PA-TELAIO: simulazione ngspice.

    python3 sim_preamp.py controllo   # harness su un circuito a risposta nota: deve dire OK
    python3 sim_preamp.py             # preamp su tutti gli angoli del J201, tabella e criteri

Topologia per canale (vedi risultati.md):
  sorgente + 10k serie -> C1 -> gate J1 (1M a massa) -> stadio 1 a source comune, guadagno fisso
  -> C2 -> DRIVE (pot log 100k, partitore) -> gate J2 (1M) -> stadio 2 a source comune, Rs bypassata
  -> C3 -> LEVEL (trimmer 100k, partitore) -> uscita, caricata da 1M (ingresso del buffer TLC2272).
I trimmer di drain Rd1/Rd2 si regolano a banco per Vd = (VA + Vs)/2: qui li calcola lo script dal punto
di lavoro di ogni angolo.
"""
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
VA = 8.5            # alimentazione analogica sulla scheda (V)
CODEC_VPP = 3.6     # ingresso massimo del codec (Vpp)
USCITA_MAX = 3.4    # obiettivo con margine
F0 = 1000.0

# J201: datasheet IDSS 0,2-1,0 mA, VGS(off) -0,3...-1,5 V. Il modello LTspice (Linear Systems)
# ha Beta=1.07m Vto=-0.93, IDSS = Beta*Vto^2 = 0,93 mA. Gli angoli cambiano solo Beta e Vto.
J201_BASE = ("Betatce=-0.5 Vtotc=-2.5m Lambda=6.75m Is=1.72f Xti=0 Rd=10 Rs=12 "
             "Cgd=1p Cgs=1p Fc=0.5 M=500m Pb=0.8 Kf=0 Af=1")
ANGOLI = {           # nome: (IDSS A, Vp V)
    "basso":    (0.2e-3, -0.3),
    "basso-Vp": (0.2e-3, -0.6),
    "medio":    (0.5e-3, -0.6),
    "modello":  (1.07e-3 * 0.93 ** 2, -0.93),
    "alto":     (1.0e-3, -1.5),
}

# valori del circuito (si iterano qui). Gate polarizzati a VG da un partitore: Id ~ (VG - Vgs)/Rs dipende poco
# dall'esemplare, quindi niente trimmer di drain.
C = dict(
    Rsrc=10e3, C1=47e-9, Rg=1e6, Rstop=1e3,
    Rvg_top=39e3, Rvg_bot=10e3, Cvg=22e-6,
    Rd1=27e3, Rs1=22e3, Pgain=25e3, Rgmin=220.0, Cs1=47e-6,     # stadio 1: GAIN = reostato + Cs1 su Rs1
    C2=220e-9,
    Rd2=20e3, Rs2a=15e3, Rs2b=None, Cs2=None,                    # stadio 2: Rs non bypassata, quasi lineare
    C3=1e-6, Plevel=100e3, Rload=1e6,
)


def log_taper(p):
    """Pot audio (curva A): 10 % a metà corsa. p in [0, 1] -> frazione di resistenza verso massa."""
    return (10 ** (2 * p) - 1) / 99


def ngspice(netlist):
    with tempfile.TemporaryDirectory() as d:
        cir = os.path.join(d, "c.cir")
        with open(cir, "w") as f:
            f.write(netlist.replace("@D@", d))
        r = subprocess.run(["ngspice", "-b", cir], capture_output=True, text=True)
        if r.returncode != 0 or "error" in r.stdout.lower() and "no error" not in r.stdout.lower():
            pass
        out = {}
        for fn in os.listdir(d):
            if fn.endswith(".dat"):
                out[fn[:-4]] = np.loadtxt(os.path.join(d, fn), ndmin=2)
        if not out:
            raise RuntimeError(r.stdout[-3000:] + r.stderr[-3000:])
        return out, r.stdout


def armoniche(t, v, f0=F0, n=9):
    """Ampiezze H1..Hn su un numero intero di periodi (segnale già linearizzato, passo uniforme)."""
    periodo = 1 / f0
    t_fine = t[-1]
    k = int((t_fine - 0.01) / periodo)          # salta i primi 10 ms
    sel = t >= t_fine - k * periodo
    x = v[sel] - np.mean(v[sel])
    x = x[:len(x) - 1] if len(x) % 2 else x
    spec = np.abs(np.fft.rfft(x)) * 2 / len(x)
    return np.array([spec[k * h] for h in range(1, n + 1)]), np.ptp(v[sel])


def onoise(log):
    m = re.search(r"onoise_total\s*=\s*([-+0-9.eE]+)", log)
    if not m:
        raise RuntimeError(log[-2000:])
    return float(m.group(1))


def db(x):
    return 20 * math.log10(max(x, 1e-30))


# ------------------------------------------------------------------ controllo a risposta nota
def controllo():
    """Sorgente non lineare nota: V(out) = 2 V(in) + 0,5 V(in)^2, Vin = 0,1 V di picco a 1 kHz.
    Atteso: H1 = 0,2 V, H2 = 0,5*0,01/2 = 2,5 mV (H2/H1 = -38,06 dB), guadagno AC 6,02 dB.
    Rumore di 10 kOhm a 27 C in 20 Hz-20 kHz: sqrt(4kTRB) = 1,82 uV."""
    net = f"""controllo
V1 in 0 dc 0 ac 1 sin(0 0.1 {F0})
B1 out 0 V=2*V(in)+0.5*V(in)*V(in)
R1 out 0 1k
Vn nin 0 dc 0 ac 1
Rn nin nout 10k
Rl nout 0 1e12
.control
op
ac dec 20 10 100k
wrdata @D@/ac.dat vdb(out)
tran 2u 30m 0 2u
linearize v(out)
wrdata @D@/tr.dat v(out)
noise v(nout) Vn dec 50 20 20k
print onoise_total
.endc
.end
"""
    out, log = ngspice(net)
    ac = out["ac"]
    g = ac[np.argmin(abs(ac[:, 0] - 1000)), 1]
    h, _ = armoniche(out["tr"][:, 0], out["tr"][:, 1])
    nz = onoise(log)
    righe = [
        ("guadagno AC a 1 kHz (dB)", g, 6.0206, 0.01),
        ("H1 (V)", h[0], 0.2, 0.002),
        ("H2/H1 (dB)", db(h[1] / h[0]), -38.06, 0.2),
        ("H3/H1 (dB, atteso < -100)", db(h[2] / h[0]), None, None),
        ("rumore 10k 20Hz-20kHz (uV)", nz * 1e6, 1.82, 0.03),
    ]
    ok = True
    for nome, val, atteso, tol in righe:
        if atteso is None:
            esito = "OK" if val < -100 else "NO"
        else:
            esito = "OK" if abs(val - atteso) <= tol else "NO"
        ok &= esito == "OK"
        print(f"  {nome:34s} {val:10.4f}   atteso {atteso if atteso is not None else '< -100'}   {esito}")
    print("CONTROLLO", "OK" if ok else "FALLITO")
    return ok


# ------------------------------------------------------------------ preamp
def modello(idss, vp):
    beta = idss / vp ** 2
    return f".model JX NJF(Beta={beta:.6g} Vto={vp:.6g} {J201_BASE})"


def netlist(idss, vp, gain, level, analisi, vin_pk=0.1):
    """gain in [0, 1]: reostato con curva A montato al contrario (a 1 resta solo Rgmin)."""
    p = C
    rpot = p["Pgain"] * log_taper(1 - gain) + p["Rgmin"]
    rlv_bot = max(p["Plevel"] * level, 1.0)
    rlv_top = max(p["Plevel"] - rlv_bot, 1.0)
    return f"""preamp
{modello(idss, vp)}
VA va 0 dc {VA}
Rvt va vg {p['Rvg_top']}
Rvb vg 0 {p['Rvg_bot']}
Cvg vg 0 {p['Cvg']}
Vin src 0 dc 0 ac 1 sin(0 {vin_pk} {F0})
Rsrc src a {p['Rsrc']}
C1 a g1a {p['C1']}
Rg1 g1a vg {p['Rg']}
Rst1 g1a g1 {p['Rstop']}
J1 d1 g1 s1 JX
Rd1 va d1 {p['Rd1']}
Rs1 s1 0 {p['Rs1']}
Rp1 s1 sp {rpot}
Cs1 sp 0 {p['Cs1']}
C2 d1 g2a {p['C2']}
Rg2 g2a vg {p['Rg']}
Rst2 g2a g2 {p['Rstop']}
J2 d2 g2 s2 JX
Rd2 va d2 {p['Rd2']}
{stadio2_source(p)}
C3 d2 lv {p['C3']}
Rlt lv out {rlv_top}
Rlb out 0 {rlv_bot}
Rload out 0 {p['Rload']}
.control
{analisi}
.endc
.end
"""


def stadio2_source(p):
    if p["Rs2b"] is None:
        return f"Rs2a s2 0 {p['Rs2a']}"
    return f"Rs2a s2 s2b {p['Rs2a']}\nRs2b s2b 0 {p['Rs2b']}\nCs2 s2b 0 {p['Cs2']}"


def punto_di_lavoro(idss, vp):
    an = "op\nwrdata @D@/op.dat v(s1) v(d1) v(s2) v(d2) v(vg)"
    out, _ = ngspice(netlist(idss, vp, 0.5, 1.0, an))
    vs1, vd1, vs2, vd2, vg = (out["op"][0, k] for k in (1, 3, 5, 7, 9))
    return dict(vg=vg, vs1=vs1, vd1=vd1, id1=vs1 / C["Rs1"], vs2=vs2, vd2=vd2,
                id2=vs2 / (C["Rs2a"] + (C["Rs2b"] or 0)))


def misura(idss, vp, gain, level, vin_pk):
    an = (f"ac dec 20 10 100k\nwrdata @D@/ac.dat vdb(out)\n"
          f"tran 2u 40m 0 2u\nlinearize v(out)\nwrdata @D@/tr.dat v(out)")
    out, _ = ngspice(netlist(idss, vp, gain, level, an, vin_pk))
    ac = out["ac"]
    f = ac[:, 0]
    g1k = ac[np.argmin(abs(f - 1000)), 1]
    banda = ac[(f >= 20) & (f <= 20e3), 1]
    h, vpp = armoniche(out["tr"][:, 0], out["tr"][:, 1])
    thd = math.sqrt(sum(h[1:] ** 2)) / h[0]
    return dict(g1k=g1k, piatt=(banda.min() - g1k, banda.max() - g1k),
                vpp=vpp, thd=thd, h2=db(h[1] / h[0]), h3=db(h[2] / h[0]))


def rumore(idss, vp, gain):
    """Rumore in uscita 20 Hz-20 kHz riportato all'ingresso col guadagno a 1 kHz, sorgente 10k inclusa."""
    an = "op\nwrdata @D@/op.dat v(d1)\nnoise v(out) Vin dec 50 20 20k\nprint onoise_total"
    _, log = ngspice(netlist(idss, vp, gain, 1.0, an))
    return onoise(log)


def ginocchio(nome, gain):
    """Ingresso a passi di 1 dB, GAIN fisso. Ritorna (dB fra THD 1 % e 10 %, livello d'ingresso all'1 % in dBu,
    H2-H3 in dB al 3 % di THD, H2-H3 al 10 %). Positivo = domina la seconda armonica."""
    idss, vp = ANGOLI[nome]
    l1 = d3 = None
    for v in 0.01 * 10 ** (np.arange(0, 47) / 20):        # 10 mV ... 2,2 V di picco
        an = "tran 2u 30m 0 2u\nlinearize v(out)\nwrdata @D@/tr.dat v(out)"
        out, _ = ngspice(netlist(idss, vp, gain, 1.0, an, v))
        h, _ = armoniche(out["tr"][:, 0], out["tr"][:, 1])
        thd = math.sqrt(sum(h[1:] ** 2)) / h[0]
        d = db(h[1] / h[0]) - db(h[2] / h[0])
        if l1 is None and thd >= 0.01:
            l1 = v
        if d3 is None and thd >= 0.03:
            d3 = d
        if thd >= 0.10:
            return db(v / l1), db(l1 * 0.7071 / 0.7746), d3, d
    return None


GAINS = (0.0, 0.5, 1.0)
VINS = (0.05, 0.25, 0.5, 1.0)


def preamp():
    print(f"VA = {VA} V, codec {CODEC_VPP} Vpp, obiettivo uscita <= {USCITA_MAX} Vpp\n")
    print("Punto di lavoro (nessun trimmer):")
    print(f"  {'angolo':9s} {'IDSS mA':>7s} {'Vp':>6s} | {'Id1 mA':>7s} {'Vs1':>5s} {'Vd1':>5s} | "
          f"{'Id2 mA':>7s} {'Vs2':>5s} {'Vd2':>5s}")
    for nome, (idss, vp) in ANGOLI.items():
        o = punto_di_lavoro(idss, vp)
        print(f"  {nome:9s} {idss*1e3:7.2f} {vp:6.2f} | {o['id1']*1e3:7.3f} {o['vs1']:5.2f} {o['vd1']:5.2f} | "
              f"{o['id2']*1e3:7.3f} {o['vs2']:5.2f} {o['vd2']:5.2f}")
    print(f"  VG = {o['vg']:.2f} V")

    print("\nGuadagno, banda e distorsione (LEVEL al massimo, carico 1M):")
    print(f"  {'angolo':9s} {'GAIN':>5s} {'Vin pk':>6s} | {'G 1k dB':>7s} {'20-20k dB':>12s} | "
          f"{'Vpp out':>7s} {'THD %':>6s} {'H2 dB':>6s} {'H3 dB':>6s}")
    res = {}
    for nome, (idss, vp) in ANGOLI.items():
        for gain in GAINS:
            for vin in VINS:
                m = misura(idss, vp, gain, 1.0, vin)
                res[(nome, gain, vin)] = m
                print(f"  {nome:9s} {gain:5.2f} {vin:6.2f} | {m['g1k']:7.1f} "
                      f"{m['piatt'][0]:+5.1f}/{m['piatt'][1]:+4.1f} | "
                      f"{m['vpp']:7.2f} {m['thd']*100:6.2f} {m['h2']:6.1f} {m['h3']:6.1f}")
        print()

    print("Rumore riportato all'ingresso, 20 Hz-20 kHz (la sola 10k di sorgente fa 1,82 uV):")
    nz_max = 0.0
    for nome, (idss, vp) in ANGOLI.items():
        riga = []
        for gain in GAINS:
            nz = rumore(idss, vp, gain)
            g = 10 ** (res[(nome, gain, 0.05)]["g1k"] / 20)
            nz_max = max(nz_max, nz / g)
            riga.append(f"GAIN {gain:.1f}: {nz/g*1e6:5.2f} uV")
        print(f"  {nome:9s} " + "   ".join(riga))
    criteri(res, nz_max)
    return res


def criteri(res, nz_max):
    pl = [punto_di_lavoro(*v) for v in ANGOLI.values()]
    vd = [x for o in pl for x in (o["vd1"], o["vd2"])]
    piatt = max(max(abs(m["piatt"][0]), abs(m["piatt"][1])) for m in res.values())
    gmin = [res[(n, 0.0, 0.05)]["g1k"] for n in ANGOLI]
    gmax = [res[(n, 1.0, 0.05)]["g1k"] for n in ANGOLI]
    pulito = max(res[(n, 0.0, 0.5)]["thd"] for n in ANGOLI)
    tetto = max(m["vpp"] for m in res.values())
    level = USCITA_MAX / tetto
    gin = {(n, g): ginocchio(n, g) for n in ANGOLI for g in (0.5, 1.0)}
    h2_3 = [v[2] for v in gin.values() if v]
    knee = [gin[(n, 1.0)][0] for n in ANGOLI if gin[(n, 1.0)]]
    print("\nGinocchio (dB fra THD 1 % e 10 %; H2-H3 al 3 % e al 10 % di THD):")
    for (n, g), v in gin.items():
        print(f"  {n:9s} GAIN {g:.1f}: " + (f"{v[0]:4.1f} dB, 1 % a {v[1]:+5.1f} dBu in, "
                                            f"H2-H3 {v[2]:+5.1f} / {v[3]:+5.1f} dB" if v else "non arriva al 10 %"))
    righe = [
        ("Vd senza trimmer fra 4 e 6,5 V", f"{min(vd):.2f}-{max(vd):.2f} V", 4 <= min(vd) and max(vd) <= 6.5),
        ("banda 20 Hz-20 kHz entro 0,5 dB", f"{piatt:.2f} dB", piatt <= 0.5),
        ("GAIN al minimo <= +12 dB", f"{min(gmin):.1f}...{max(gmin):.1f} dB", max(gmin) <= 12),
        ("GAIN al massimo >= +20 dB", f"{min(gmax):.1f}...{max(gmax):.1f} dB", min(gmax) >= 20),
        ("pulito: GAIN 0, 1 Vpp in, THD <= 3 %", f"{pulito*100:.2f} %", pulito <= 0.03),
        ("tetto d'uscita -> LEVEL per <= 3,4 Vpp", f"{tetto:.2f} Vpp, LEVEL {level:.2f}", level >= 0.5),
        ("rumore all'ingresso <= 3,5 uV", f"{nz_max*1e6:.2f} uV", nz_max <= 3.5e-6),
        ("spinta: H2-H3 >= +3 dB al 3 % (GAIN 0,5 e 1)", f"{min(h2_3):+.1f} dB al peggio",
         len(h2_3) == 2 * len(ANGOLI) and min(h2_3) >= 3),
        ("ginocchio GAIN 1: >= 10 dB fra 1 e 10 %", f"{min(knee):.0f}...{max(knee):.0f} dB",
         len(knee) == len(ANGOLI) and min(knee) >= 10),
    ]
    print("\nCriteri:")
    for nome, val, ok in righe:
        print(f"  {'PASS' if ok else 'NO  '}  {nome:40s} {val}")
    print(f"  (con LEVEL a {level:.2f} il guadagno minimo diventa {min(gmin) + db(level):.1f} dB)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "controllo":
        sys.exit(0 if controllo() else 1)
    preamp()
