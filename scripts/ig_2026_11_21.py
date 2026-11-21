import io, json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-21: carrusel "¿Qué le regalo? Navidad según cómo es" + 3 historias.
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-21")
os.makedirs(OUT, exist_ok=True)
NAVY, BLUE, SKY, STEEL, YEL = (6, 21, 43), (0, 63, 130), (239, 251, 252), (52, 102, 160), (255, 230, 0)
WHITE, SOFT, LIGHT, GREEN = (255, 255, 255), (197, 211, 230), (143, 195, 255), (0, 140, 70)
F = lambda name, size: ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
SERIF, BOLD, REG = "Merriweather.ttf", "Lato-Bold.ttf", "Lato-Regular.ttf"
W = 1080
logo_white = Image.open(os.path.join(SITE, "img/logo-dark.png")).convert("RGBA")
clp = lambda n: "$" + f"{n:,}".replace(",", ".")

def center(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

def paste_logo(img, width, y):
    l = logo_white.resize((width, int(logo_white.height * width / logo_white.width)), Image.LANCZOS)
    img.paste(l, ((W - width) // 2, y), l)

_cache = {}
def foto(url, maxw, maxh):
    if url not in _cache:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        _cache[url] = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
    f = _cache[url]
    k = min(maxw / f.width, maxh / f.height)
    return f.resize((int(f.width * k), int(f.height * k)), Image.LANCZOS)

P = {p["nombre"]: p for p in json.load(open(os.path.join(SITE, "products.json"), encoding="utf-8"))}
def prod(parte):
    return next(v for k, v in P.items() if parte.lower() in k.lower())

def foto_prod(p, maxw, maxh):
    """Kit gamer: arma teclado + mouse en un mismo recuadro blanco (la foto principal solo muestra el mouse)."""
    if "Kit Teclado" not in p["nombre"] or len(p["fotos"]) < 2:
        return foto(p["img"], maxw, maxh)
    kb = foto(p["fotos"][1], maxw, int(maxh * 0.62))
    ms = foto(p["img"], maxw, maxh - kb.height - 10)
    c = Image.new("RGB", (maxw, kb.height + 10 + ms.height), WHITE)
    c.paste(kb, ((maxw - kb.width) // 2, 0))
    c.paste(ms, ((maxw - ms.width) // 2, kb.height + 10))
    return c

ITEMS = [  # (perfil, línea 2, producto, nombre corto, detalle)
    ("Para el que", "vive jugando", prod("Kit Teclado"), "Kit teclado + mouse gamer", "Con luces LED · teclado y mouse en un solo kit"),
    ("Para el que", "quiere grabar su voz", prod("Micrófono"), "Micrófono condensador", "Con trípode plegable y filtro anti pop"),
    ("Para el que", "siempre tiene calor", prod("Ventilador"), "Ventilador de mano M11", "Inalámbrico · alta velocidad · cabe en la cartera"),
    ("Para el que", "cuida su sonrisa", prod("Irrigador"), "Irrigador bucal portátil", "Inalámbrico · trae 4 boquillas"),
]

# --- Post 1080x1350 ---
H = 1350
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
paste_logo(img, 280, 100)
center(d, 300, "Navidad 2026", F(BOLD, 52), YEL)
center(d, 400, "¿Qué le regalo?", F(SERIF, 100), WHITE)
center(d, 560, "4 ideas según", F(SERIF, 74), LIGHT)
center(d, 660, "cómo es esa persona", F(SERIF, 74), LIGHT)
center(d, 830, "Todas bajo $22.000 y con envío a todo Chile", F(REG, 40), SOFT)
d.rounded_rectangle([250, 960, 830, 1050], radius=45, fill=YEL)
center(d, 975, "Desliza y elige  →", F(BOLD, 44), NAVY)
center(d, 1180, "Etiqueta a quien le regalarías algo", F(REG, 38), SOFT)
img.save(os.path.join(OUT, "1.jpg"), quality=92)

for i, (a, b, p, nom, det) in enumerate(ITEMS, start=2):
    img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
    center(d, 55, a, F(REG, 50), STEEL)
    center(d, 120, b, F(SERIF, 76), NAVY)
    d.rounded_rectangle([140, 250, W - 140, 840], radius=40, fill=WHITE)
    ph = foto_prod(p, 740, 550)
    img.paste(ph, ((W - ph.width) // 2, 250 + (590 - ph.height) // 2))
    center(d, 875, nom, F(SERIF, 58), NAVY)
    center(d, 960, det, F(REG, 38), STEEL)
    center(d, 1020, clp(p["precio"]), F(BOLD, 92), BLUE)
    center(d, 1135, f"6 cuotas de {clp(round(p['precio'] / 6))} sin interés", F(REG, 36), GREEN)
    d.rectangle([0, H - 110, W, H], fill=NAVY)
    center(d, H - 82, "www.myausel.com", F(BOLD, 44), WHITE)
    img.save(os.path.join(OUT, f"{i}.jpg"), quality=92)

img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 200, "¿Ya sabes a quién?", F(SERIF, 84), WHITE)
center(d, 350, "Etiquétalo", F(BOLD, 96), YEL)
center(d, 480, "o compártele este post 🎁".replace(" 🎁", ""), F(REG, 50), WHITE)
for n, t in enumerate(["Envío a todo Chile", "Pago protegido con Mercado Pago", "Hasta 6 cuotas sin interés"]):
    center(d, 650 + n * 80, t, F(BOLD, 44), SOFT)
center(d, 940, "www.myausel.com", F(BOLD, 54), YEL)
center(d, 1020, "WhatsApp +56 9 4503 7484", F(BOLD, 44), WHITE)
center(d, 1110, "Síguenos: @auselspa", F(BOLD, 44), SOFT)
paste_logo(img, 240, 1200)
img.save(os.path.join(OUT, "6.jpg"), quality=92)

# --- Historias 1080x1920 (texto entre y=250 y 1600) ---
H = 1920
# s1 adelanto del post
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 290, "Nuevo post 👀".replace(" 👀", ""), F(BOLD, 60), YEL)
center(d, 400, "¿No sabes qué", F(SERIF, 92), WHITE)
center(d, 520, "regalar esta", F(SERIF, 92), WHITE)
center(d, 640, "Navidad?", F(SERIF, 92), WHITE)
center(d, 820, "Te dejamos 4 ideas", F(REG, 56), SOFT)
center(d, 900, "según cómo es esa persona", F(REG, 56), SOFT)
center(d, 1060, "Todas bajo $22.000", F(BOLD, 64), LIGHT)
d.rounded_rectangle([240, 1240, 840, 1350], radius=55, fill=YEL)
center(d, 1262, "Míralo en el perfil", F(BOLD, 52), NAVY)
center(d, 1460, "@auselspa", F(BOLD, 56), SOFT)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 ¿cuál regalarías? grilla 2x2
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 270, "¿Cuál regalarías?", F(SERIF, 84), WHITE)
cards = [("A", ITEMS[0][2], "Kit gamer"), ("B", ITEMS[1][2], "Micrófono"),
         ("C", ITEMS[2][2], "Ventilador"), ("D", ITEMS[3][2], "Irrigador")]
cw, ch, gap = 430, 500, 40
x0, y0 = (W - 2 * cw - gap) // 2, 440
for k, (letra, p, nom) in enumerate(cards):
    x, y = x0 + (k % 2) * (cw + gap), y0 + (k // 2) * (ch + gap)
    d.rounded_rectangle([x, y, x + cw, y + ch], radius=30, fill=WHITE)
    ph = foto_prod(p, cw - 60, 320)
    img.paste(ph, (x + (cw - ph.width) // 2, y + 20 + (320 - ph.height) // 2))
    fn, fl = F(BOLD, 42), F(BOLD, 38)
    tw = 60 + 14 + d.textlength(nom, font=fn)
    bx = x + (cw - tw) / 2
    d.ellipse([bx, y + 355, bx + 60, y + 415], fill=YEL)
    d.text((bx + 30 - d.textlength(letra, font=fl) / 2, y + 363), letra, font=fl, fill=NAVY)
    d.text((bx + 74, y + 360), nom, font=fn, fill=NAVY)
    fp = F(BOLD, 46)
    d.text((x + (cw - d.textlength(clp(p['precio']), font=fp)) / 2, y + 420), clp(p["precio"]), font=fp, fill=BLUE)
center(d, 1500, "Respóndenos por DM", F(BOLD, 56), YEL)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 pregunta frecuente: envío a regiones
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 280, "Pregunta frecuente", F(BOLD, 56), BLUE)
y = 420
for ln in ["¿Envían a", "regiones?"]:
    center(d, y, ln, F(SERIF, 110), NAVY); y += 140
center(d, 790, "Sí", F(SERIF, 150), BLUE)
y = 1020
for ln in ["Enviamos a todo Chile.", "Compras por Mercado Libre y", "pagas protegido con Mercado Pago."]:
    center(d, y, ln, F(REG, 54), STEEL); y += 80
center(d, 1340, "www.myausel.com", F(BOLD, 60), NAVY)
center(d, 1440, "Escríbenos por DM", F(BOLD, 52), STEEL)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
