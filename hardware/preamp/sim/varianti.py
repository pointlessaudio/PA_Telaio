"""
Carattere della spinta: diagnosi e varianti del preamp (usa sim_preamp.py).

    python3 varianti.py diagnosi    # escursione dei due drain rispetto al riposo, in saturazione
    python3 varianti.py             # ginocchio di ogni variante sui 3 angoli estremi

Ginocchio: si sale con l'ingresso a passi di 1 dB, GAIN fisso; si annota il livello a cui la THD passa l'1 % e
il 10 %. Più dB fra i due = saturazione più graduale. H2-H3 al 3 % e al 10 % di THD: positivo = domina la seconda.
"""
import sys

import sim_preamp as S

# circuito della prima simulazione (V0), da cui partono le varianti
BASE = dict(S.C, Rd1=20e3, Rs1=15e3, Rs2a=8.2e3, Rs2b=6.8e3, Cs2=47e-6)
ESTREMI = ("basso", "modello", "alto")


def drain(nome, gain, vin):
    idss, vp = S.ANGOLI[nome]
    an = ("op\nwrdata @D@/op.dat v(d1) v(d2)\n"
          "tran 2u 40m 0 2u\nlinearize v(d1) v(d2)\nwrdata @D@/tr.dat v(d1) v(d2)")
    out, _ = S.ngspice(S.netlist(idss, vp, gain, 1.0, an, vin))
    q1, q2 = out["op"][0, 1], out["op"][0, 3]
    tr = out["tr"]
    sel = tr[:, 0] >= 0.02
    d1, d2 = tr[sel, 1], tr[sel, 3]
    return (d1.max() - q1, d1.min() - q1, q1), (d2.max() - q2, d2.min() - q2, q2)


def diagnosi(circuito):
    S.C.clear()
    S.C.update(circuito)
    print("Escursione dei drain rispetto al riposo (V): + verso VA (interdizione), - verso il source (ohmico)")
    for nome in ESTREMI:
        for gain, vin in ((0.0, 1.0), (0.5, 0.5), (1.0, 0.25), (1.0, 1.0)):
            a, b = drain(nome, gain, vin)
            print(f"  {nome:8s} GAIN {gain:.1f} Vin {vin:.2f} | D1 riposo {a[2]:.2f}: {a[0]:+.2f}/{a[1]:+.2f}"
                  f" | D2 riposo {b[2]:.2f}: {b[0]:+.2f}/{b[1]:+.2f}")


ginocchio = S.ginocchio


def prova(nome_var, modifiche):
    S.C.clear()
    S.C.update(BASE)
    S.C.update(modifiche)
    righe = []
    for gain in (0.0, 1.0):
        for nome in ESTREMI:
            g = ginocchio(nome, gain)
            righe.append((gain, nome, g))
    gmax = [S.misura(*S.ANGOLI[n], 1.0, 1.0, 0.05)["g1k"] for n in ESTREMI]
    gmin = [S.misura(*S.ANGOLI[n], 0.0, 1.0, 0.05)["g1k"] for n in ESTREMI]
    print(f"\n{nome_var}  {modifiche}")
    print(f"  guadagno: minimo {min(gmin):.1f}...{max(gmin):.1f} dB, massimo {min(gmax):.1f}...{max(gmax):.1f} dB")
    for gain, nome, g in righe:
        if g is None:
            print(f"  GAIN {gain:.0f} {nome:8s}  non arriva al 10 %")
            continue
        print(f"  GAIN {gain:.0f} {nome:8s}  ginocchio 1->10 %: {g[0]:4.1f} dB  (1 % a {g[1]:+5.1f} dBu in)"
              f"  H2-H3: {g[2]:+5.1f} dB al 3 %, {g[3]:+5.1f} dB al 10 %")


VARIANTI = [
    ("V0 base", {}),
    ("V1a drain piu' alto", dict(Rd1=15e3, Rd2=15e3)),
    ("V1b drain piu' alto", dict(Rd1=12e3, Rd2=12e3)),
    ("V2a Rs mai tutta bypassata", dict(Rgmin=1e3)),
    ("V2b Rs mai tutta bypassata", dict(Rgmin=2.2e3)),
    ("V3a secondo stadio lineare", dict(Rs2a=15e3, Rs2b=1.0, Cs2=1e-12)),
    ("V3b secondo stadio lineare", dict(Rd2=12e3, Rs2a=15e3, Rs2b=1.0, Cs2=1e-12)),
    ("V4a V3a + meno corrente nel primo stadio (scelta)", dict(Rs2a=15e3, Rs2b=None, Cs2=None, Rs1=22e3, Rd1=27e3)),
    ("V4b V3a + meno corrente, Rd1 30k", dict(Rs2a=15e3, Rs2b=None, Cs2=None, Rs1=22e3, Rd1=30e3)),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "diagnosi":
        print("V0 (prima simulazione)")
        diagnosi(BASE)
        print("\nV4a (scelta)")
        diagnosi(dict(BASE, **VARIANTI[-2][1]))
    else:
        for nome, mod in VARIANTI:
            prova(nome, mod)
