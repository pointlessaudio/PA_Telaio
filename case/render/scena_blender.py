"""
Render del case PA-TELAIO in Blender (Cycles, headless). Legge le parti STL e scena.json
prodotti da render/esporta.py. Ricetta di luce e materiali: skill blender-render-pa
(nodi Principled espliciti, energie piccole, esposizione negativa).

    /Applications/Blender.app/Contents/MacOS/Blender -b -P render/scena_blender.py -- [prova]
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

QUI = Path(__file__).resolve().parent
PARTI = QUI / "parti"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PROVA = "prova" in ARGS
MM = 0.001
SCENA = json.loads((QUI / "scena.json").read_text())
LIFT = (3.5 - SCENA["piedino"][1]) * MM          # piedini in gomma da 3,5 mm nelle sedi

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ------------------------------------------------------------------ materiali
def nuovo(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, nt, bsdf


def setb(bsdf, nome, val):
    if nome in bsdf.inputs:
        try:
            bsdf.inputs[nome].default_value = val
        except Exception:
            pass


def grana(nt, bsdf, scala, forza):
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scala
    tex.inputs["Detail"].default_value = 8.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = forza
    bump.inputs["Distance"].default_value = 0.0002
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def petg():
    m, nt, b = nuovo("PETG grafite opaco")
    setb(b, "Base Color", (0.030, 0.031, 0.034, 1))
    setb(b, "Roughness", 0.58)
    setb(b, "Specular IOR Level", 0.45)
    grana(nt, b, 2600.0, 0.10)
    return m


def semplice(nome, colore, rough, metal=0.0, coat=0.0, emis=None, forza=0.0):
    m, nt, b = nuovo(nome)
    setb(b, "Base Color", (*colore, 1))
    setb(b, "Roughness", rough)
    setb(b, "Metallic", metal)
    setb(b, "Coat Weight", coat)
    if emis:
        setb(b, "Emission Color", (*emis, 1))
        setb(b, "Emission Strength", forza)
    return m


def schermo():
    m, nt, b = nuovo("OLED schermata")
    setb(b, "Base Color", (0.0, 0.0, 0.0, 1))
    setb(b, "Roughness", 0.32)            # polarizzatore semiopaco: niente specchio
    setb(b, "Specular IOR Level", 0.2)
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(QUI / "oled_schermata.png"))
    img.interpolation = "Closest"
    nt.links.new(img.outputs["Color"], b.inputs["Emission Color"])
    setb(b, "Emission Strength", 2.2)
    return m


M_PETG = petg()
M_MANOPOLA = semplice("alluminio anodizzato nero", (0.025, 0.025, 0.028), 0.32, metal=0.85)
M_INDICE = semplice("indice bianco", (0.85, 0.84, 0.80), 0.4)
M_TASTO = semplice("tasto grigio caldo", (0.56, 0.55, 0.52), 0.48)
M_LED = semplice("LED corallo", (0.85, 0.33, 0.18), 0.3, emis=(1.0, 0.36, 0.16), forza=6.0)
M_VETRO = semplice("vetro OLED", (0.003, 0.003, 0.004), 0.30)
M_METALLO = semplice("nichel", (0.62, 0.62, 0.60), 0.28, metal=1.0)
M_CROMO = semplice("cromo", (0.80, 0.80, 0.80), 0.08, metal=1.0)
M_BUIO = semplice("interno", (0.01, 0.01, 0.01), 0.8)
M_GOMMA = semplice("gomma", (0.02, 0.02, 0.02), 0.9)
M_FONDO = semplice("fondale", (0.50, 0.49, 0.47), 0.85)
M_SCHERMO = schermo()


# ------------------------------------------------------------------ geometria
def importa(nome, mat):
    bpy.ops.wm.stl_import(filepath=str(PARTI / f"{nome}.stl"), global_scale=MM)
    o = bpy.context.selected_objects[0]
    o.name = nome
    o.data.materials.append(mat)
    o.location.z += LIFT
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return o


def matrice(info, offset=(0, 0, 0)):
    pos = Vector(info["pos"]) * MM + Vector((0, 0, LIFT))
    rot = Euler([math.radians(a) for a in info["rot"]], "XYZ").to_matrix().to_4x4()
    return Matrix.Translation(pos) @ rot @ Matrix.Translation(Vector(offset) * MM)


def cubo(nome, mat, M, dim):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = nome
    o.matrix_world = M @ Matrix.Diagonal((dim[0] * MM, dim[1] * MM, dim[2] * MM, 1))
    o.data.materials.append(mat)
    return o


def cilindro(nome, mat, M, d, h, lati=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=lati, radius=d / 2 * MM, depth=h * MM)
    o = bpy.context.object
    o.name = nome
    o.matrix_world = M @ o.matrix_world
    o.data.materials.append(mat)
    return o


for nome in ("vasca", "pannello_superiore", "pannello_posteriore"):
    importa(nome, M_PETG)
importa("manopole", M_MANOPOLA)
importa("cappucci", M_TASTO)
importa("led", M_LED)
importa("oled_vetro", M_VETRO)

# indici sulle manopole dei pot, puntino sull'encoder
for i, k in enumerate(SCENA["manopole"]):
    r = k["d"] / 2 * 0.62
    M = matrice(k) @ Matrix.Rotation(math.radians(-k["angolo"]), 4, "Z")
    cubo(f"indice {i}", M_INDICE, M @ Matrix.Translation((0, r * MM, 0.05 * MM)), (1.0, k["d"] * 0.42, 0.12))
e = SCENA["encoder"]
cilindro("puntino encoder", M_INDICE, matrice(e, (0, e["d"] / 2 * 0.72, 0.05)), 1.6, 0.12, 24)

# schermata dell'OLED sull'area attiva
aa = SCENA["oled"]["aa"]
bpy.ops.mesh.primitive_plane_add(size=1)
p = bpy.context.object
p.name = "schermata"
p.matrix_world = matrice(SCENA["oled"]) @ Matrix.Diagonal((aa[0] * MM, aa[1] * MM, 1, 1))
p.data.materials.append(M_SCHERMO)

# dadi e boccole dei connettori sul retro
for j in SCENA["retro"]:
    x, y, z = j["pos"]
    base = Matrix.Translation(Vector((x, y, z)) * MM + Vector((0, 0, LIFT))) @ Matrix.Rotation(math.radians(90), 4, "X")
    if j["tipo"] == "jack635":
        cilindro(f"dado {j['nome']}", M_METALLO, base @ Matrix.Translation((0, 0, -1.2 * MM)), 14.0, 2.4, 6)
        cilindro(f"boccola {j['nome']}", M_METALLO, base @ Matrix.Translation((0, 0, -2.9 * MM)), 9.5, 1.2)
        cilindro(f"foro {j['nome']}", M_BUIO, base @ Matrix.Translation((0, 0, -3.0 * MM)), 6.4, 1.3)
    elif j["tipo"] == "jack35":
        cilindro(f"dado {j['nome']}", M_METALLO, base @ Matrix.Translation((0, 0, -1.0 * MM)), 8.0, 2.0)
        cilindro(f"foro {j['nome']}", M_BUIO, base @ Matrix.Translation((0, 0, -1.6 * MM)), 3.6, 1.3)
    elif j["tipo"] == "dc":
        cilindro(f"dado {j['nome']}", M_METALLO, base @ Matrix.Translation((0, 0, -1.2 * MM)), 13.0, 2.4, 6)
        cilindro(f"foro {j['nome']}", M_BUIO, base @ Matrix.Translation((0, 0, -1.9 * MM)), 6.0, 1.3)
    elif j["tipo"] == "levetta":
        cilindro(f"dado {j['nome']}", M_METALLO, base @ Matrix.Translation((0, 0, -1.0 * MM)), 9.0, 2.0, 6)
        leva = base @ Matrix.Translation((0, 0, -6.5 * MM)) @ Matrix.Rotation(math.radians(18), 4, "X")
        cilindro(f"leva {j['nome']}", M_METALLO, leva, 2.6, 10.0)

# footswitch 3PDT: dado esagonale, rondella e attuatore cromato
fs = SCENA["footswitch"]
(nd, nh), (ad, ah) = fs["dado"], fs["attuatore"]
cilindro("dado footswitch", M_METALLO, matrice(fs, (0, 0, nh / 2)), nd, nh, 6)
cilindro("rondella footswitch", M_METALLO, matrice(fs, (0, 0, 0.3)), nd + 3, 0.6)
cilindro("attuatore footswitch", M_CROMO, matrice(fs, (0, 0, nh + ah / 2)), ad, ah)
bpy.ops.mesh.primitive_uv_sphere_add(radius=ad / 2 * MM, segments=48, ring_count=24)
cupola = bpy.context.object
cupola.matrix_world = matrice(fs, (0, 0, nh + ah)) @ Matrix.Diagonal((1, 1, 0.35, 1)) @ cupola.matrix_world
cupola.data.materials.append(M_CROMO)

# USB-C del Seed, dentro al taglio sul fianco
ux, uy, uz = SCENA["usb"]
cubo("USB-C", M_METALLO, Matrix.Translation(Vector((ux + 3.5, uy, uz)) * MM + Vector((0, 0, LIFT))), (7.0, 8.9, 3.2))

# piedini
for (x, y) in SCENA["piedini"]:
    cilindro("piedino", M_GOMMA, Matrix.Translation(Vector((x, y, 3.5 / 2)) * MM), 12.7, 3.5)

# fondale
PW, PD = SCENA["pianta"]
bpy.ops.mesh.primitive_plane_add(size=4, location=(PW / 2 * MM, PD / 2 * MM, 0))
bpy.context.object.data.materials.append(M_FONDO)

# ------------------------------------------------------------------ luci (scala: case ~0,2 m)
centro = Vector((PW / 2 * MM, PD / 2 * MM, 0.03))


def area(nome, pos, dim, watt, colore):
    d = bpy.data.lights.new(nome, "AREA")
    d.size, d.energy, d.color = dim, watt, colore
    o = bpy.data.objects.new(nome, d)
    scene.collection.objects.link(o)
    o.location = centro + Vector(pos)
    o.rotation_euler = (centro - o.location).to_track_quat("-Z", "Y").to_euler()
    return o


area("key", (0.05, 0.42, 0.50), 0.45, 9.0, (1.0, 0.95, 0.88))       # da nord, caldo
area("fill", (-0.45, -0.35, 0.22), 0.55, 4.0, (0.90, 0.94, 1.0))    # sud-ovest, morbido e freddo
area("rim", (0.40, 0.45, 0.10), 0.20, 3.0, (1.0, 0.98, 0.95))       # controluce radente sul retro
w = bpy.data.worlds.new("mondo")
scene.world = w
w.use_nodes = True
for n in list(w.node_tree.nodes):
    w.node_tree.nodes.remove(n)
bg = w.node_tree.nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.86, 0.84, 0.80, 1)
bg.inputs["Strength"].default_value = 0.12
wo = w.node_tree.nodes.new("ShaderNodeOutputWorld")
w.node_tree.links.new(bg.outputs["Background"], wo.inputs["Surface"])

# ------------------------------------------------------------------ render
scene.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = "GPU"
except Exception:
    scene.cycles.device = "CPU"
scene.cycles.samples = 48 if PROVA else 160
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.3
scene.render.resolution_x, scene.render.resolution_y = (960, 600) if PROVA else (1920, 1200)

cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 70
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.dof.use_dof = not PROVA
cam_data.dof.aperture_fstop = 4.0


def scatta(nome, direzione, distanza, mira=(0, 0, 0)):
    target = centro + Vector(mira)
    cam.location = target + Vector(direzione).normalized() * distanza
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.dof.focus_distance = (target - cam.location).length
    scene.render.filepath = str(QUI / f"{nome}{'_prova' if PROVA else ''}.png")
    bpy.ops.render.render(write_still=True)


scatta("case_fronte", (-0.42, -1.0, 0.78), 0.62)
scatta("case_retro", (0.55, 1.0, 0.50), 0.62)
scatta("case_dettaglio", (0.35, -0.75, 0.80), 0.30, mira=(0.035, -0.02, 0.0))
