"""
Verifica a ciclo chiuso dello schema KiCad: KiCad stesso esporta la netlist di pa-telaio.kicad_sch, e la si
confronta con reti_attese.json (scritto da genera_schema.py dalle fonti del progetto). Poi ERC di KiCad.

    python3 verifica_schema.py [file.kicad_sch]     # "OK ..." se le due netlist coincidono e l'ERC non ha errori

Il confronto è sulla partizione dei piedini (quali piedini stanno insieme), non sui nomi delle reti.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

QUI = Path(__file__).resolve().parent
CLI = next((str(p) for p in (Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
                              Path.home() / "Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli") if p.exists()),
           "kicad-cli")


def sexp(testo):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', testo)
    pila = [[]]
    for t in tok:
        if t == "(":
            pila.append([])
        elif t == ")":
            x = pila.pop()
            pila[-1].append(x)
        else:
            pila[-1].append(t[1:-1] if t.startswith('"') else t)
    return pila[0][0]


def figli(nodo, chiave):
    return [x for x in nodo if isinstance(x, list) and x and x[0] == chiave]


def netlist_kicad(sch, cartella):
    out = Path(cartella) / "netlist.net"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(out), str(sch)],
                   check=True, capture_output=True)
    albero = sexp(out.read_text())
    reti = {}
    for net in figli(figli(albero, "nets")[0], "net"):
        nome = figli(net, "name")[0][1]
        nodi = sorted((figli(n, "ref")[0][1], figli(n, "pin")[0][1]) for n in figli(net, "node"))
        reti[nome] = nodi
    return reti


def erc(sch, cartella):
    out = Path(cartella) / "erc.json"
    subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", str(out), str(sch)],
                   capture_output=True)
    d = json.loads(out.read_text())
    voci = []
    for foglio in d.get("sheets", []):
        for v in foglio.get("violations", []):
            voci.append((v.get("severity"), v.get("type"), v.get("description"),
                         [i.get("description") for i in v.get("items", [])]))
    return voci


def confronta(attese, kicad, nc):
    """differenze fra le due partizioni dei piedini; i piedini NC in KiCad sono reti a un nodo (unconnected-...)"""
    err = []
    gruppi_k = {frozenset(v) for v in kicad.values() if len(v) > 1}
    gruppi_a = {frozenset(tuple(p) for p in v) for v in attese.values()}
    for g in sorted(gruppi_a - gruppi_k, key=sorted):
        nome = [k for k, v in attese.items() if frozenset(tuple(p) for p in v) == g][0]
        err.append(f"rete attesa {nome} non uguale in KiCad: {sorted(g)[:6]}{' ...' if len(g) > 6 else ''}")
    for g in sorted(gruppi_k - gruppi_a, key=sorted):
        nome = [k for k, v in kicad.items() if frozenset(v) == g][0]
        err.append(f"rete KiCad {nome} non attesa: {sorted(g)[:6]}{' ...' if len(g) > 6 else ''}")
    singoli_k = {v[0] for v in kicad.values() if len(v) == 1}
    nc_set = {tuple(p) for p in nc}
    for p in sorted(singoli_k - nc_set):
        err.append(f"piedino {p[0]}.{p[1]} scollegato in KiCad ma non dichiarato NC")
    for p in sorted(nc_set - singoli_k):
        err.append(f"piedino NC {p[0]}.{p[1]} collegato in KiCad")
    return err


def verifica(sch, attese_json=QUI / "reti_attese.json"):
    d = json.loads(Path(attese_json).read_text())
    with tempfile.TemporaryDirectory() as tmp:
        kicad = netlist_kicad(sch, tmp)
        err = confronta(d["reti"], kicad, d["nc"])
        voci = erc(sch, tmp)
    return err, voci, len(kicad)


def main():
    sch = Path(sys.argv[1]) if len(sys.argv) > 1 else QUI / "pa-telaio.kicad_sch"
    err, voci, n = verifica(sch)
    errori_erc = [v for v in voci if v[0] == "error"]
    avvisi_erc = [v for v in voci if v[0] != "error"]
    for e in err:
        print("NETLIST:", e)
    for v in errori_erc:
        print("ERC errore:", v[1], "-", v[2], v[3])
    tipi = {}
    for v in avvisi_erc:
        tipi[v[1]] = tipi.get(v[1], 0) + 1
    if tipi:
        print("ERC avvisi:", ", ".join(f"{k} {c}" for k, c in sorted(tipi.items())))
    if err or errori_erc:
        print(f"ERRORE: {len(err)} differenze di netlist, {len(errori_erc)} errori ERC")
        return 1
    print(f"OK: netlist di KiCad uguale a quella attesa ({n} reti KiCad, piedini NC compresi), ERC senza errori")
    return 0


if __name__ == "__main__":
    sys.exit(main())
