import io, json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-26 (reusa el FAQ del 24, que no alcanzó a publicarse): carrusel "5 dudas antes de comprar online, resueltas" (FAQ) + 3 historias
# (adelanto del post, producto del día irrigador, tip escritorio -> kit gamer).
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-26")
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

P = {p["nombre"]: p for p in json.load(open(os.path.join(SITE, "products.json"), encoding="utf-8"))}
def prod(parte):
    return next(v for k, v in P.items() if parte.lower() in k.lower())

_cache = {}
def foto(url, maxw, maxh):
    if url not in _cache:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        _cache[url] = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
    f = _cache[url]
    k = min(maxw / f.width, maxh / f.height)
    return f.resize((int(f.width * k), int(f.height * k)), Image.LANCZOS)

def foto_prod(p, maxw, maxh):
    if "Kit Teclado" not in p["nombre"] or len(p.get("fotos", [])) < 2:
        return foto(p["img"], maxw, maxh)
    kb = foto(p["fotos"][1], maxw, int(maxh * 0.62))
    ms = foto(p["img"], maxw, maxh - kb.height - 10)
    c = Image.new("RGB", (maxw, kb.height + 10 + ms.height), WHITE)
    c.paste(kb, ((maxw - kb.width) // 2, 0))
    c.paste(ms, ((maxw - ms.width) // 2, kb.height + 10))
    return c

def estudio(path, bw, bh, r=40):
    f = Image.open(os.path.join(SITE, path)).convert("RGB")
    k = max(bw / f.width, bh / f.height)
    f = f.resize((int(f.width * k) + 1, int(f.height * k) + 1), Image.LANCZOS)
    l, t = (f.width - bw) // 2, (f.height - bh) // 2
    f = f.crop((l, t, l + bw, t + bh))
    m = Image.new("L", f.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=r, fill=255)
    return f, m

IRR, KIT = prod("Irrigador"), prod("Kit Teclado")

# --- Post 1080x1350 ---
H = 1350
def faq(num, pregunta, respuesta_grande, lineas, nombre):
    img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 90, 300, 160], radius=35, fill=BLUE)
    t = f"Duda {num}/5"; fb = F(BOLD, 40)
    d.text((195 - d.textlength(t, font=fb) / 2, 102), t, font=fb, fill=WHITE)
    y = 230
    for ln in pregunta:
        center(d, y, ln, F(SERIF, 80), NAVY); y += 110
    y += 30
    d.rounded_rectangle([90, y, W - 90, y + 560], radius=40, fill=WHITE)
    center(d, y + 50, respuesta_grande, F(SERIF, 96), BLUE)
    yy = y + 220
    for ln in lineas:
        center(d, yy, ln, F(REG, 46), STEEL); yy += 72
    d.rectangle([0, H - 110, W, H], fill=NAVY)
    center(d, H - 82, "www.myausel.com", F(BOLD, 44), WHITE)
    img.save(os.path.join(OUT, nombre), quality=92)

# 1 portada
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
paste_logo(img, 280, 100)
center(d, 300, "Antes de comprar online", F(BOLD, 52), YEL)
center(d, 410, "¿Te da", F(SERIF, 110), WHITE)
center(d, 540, "desconfianza?", F(SERIF, 110), WHITE)
center(d, 730, "Las 5 dudas que más", F(SERIF, 66), LIGHT)
center(d, 820, "nos hacen, resueltas", F(SERIF, 66), LIGHT)
d.rounded_rectangle([290, 980, 790, 1070], radius=45, fill=YEL)
center(d, 995, "Desliza  →", F(BOLD, 46), NAVY)
center(d, 1180, "Guárdalo para Black Friday y Navidad", F(REG, 38), SOFT)
img.save(os.path.join(OUT, "1.jpg"), quality=92)

faq(1, ["¿Es seguro", "pagar?"], "Sí",
    ["Compras por Mercado Libre", "y pagas con Mercado Pago,", "así tu pago queda protegido."], "2.jpg")
faq(2, ["¿Llega a", "regiones?"], "Sí",
    ["Enviamos a todo Chile,", "de Arica a Punta Arenas.", "Te llega a la puerta de tu casa."], "3.jpg")
faq(3, ["¿Puedo pagar", "en cuotas?"], "Hasta 6",
    ["cuotas sin interés.", f"Ej: irrigador bucal {clp(IRR['precio'])}", f"= 6 cuotas de {clp(round(IRR['precio'] / 6))}"], "4.jpg")
faq(4, ["¿Cómo", "compro?"], "3 pasos",
    ["1. Entra a www.myausel.com", "2. Elige y toca Comprar", "3. Pagas en Mercado Libre y listo"], "5.jpg")
faq(5, ["¿Y si tengo una", "duda antes?"], "Pregúntanos",
    ["Te respondemos por", "WhatsApp +56 9 4503 7484", "o por DM en @auselspa"], "6.jpg")

# 7 cierre
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 140, "¿Te sirvió?", F(SERIF, 90), WHITE)
center(d, 270, "Guárdalo y compártelo", F(BOLD, 64), YEL)
center(d, 360, "con quien siempre pregunta esto", F(REG, 44), SOFT)
cw, ch, gap = 205, 260, 25
x0 = (W - 4 * cw - 3 * gap) // 2
for k, p in enumerate([prod("Irrigador"), prod("Kit Teclado"), prod("Micrófono"), prod("Ventilador")]):
    x, y = x0 + k * (cw + gap), 470
    d.rounded_rectangle([x, y, x + cw, y + ch], radius=24, fill=WHITE)
    ph = foto_prod(p, cw - 30, 170)
    img.paste(ph, (x + (cw - ph.width) // 2, y + 15 + (170 - ph.height) // 2))
    fp = F(BOLD, 36)
    d.text((x + (cw - d.textlength(clp(p["precio"]), font=fp)) / 2, y + 200), clp(p["precio"]), font=fp, fill=BLUE)
center(d, 800, "www.myausel.com", F(BOLD, 60), YEL)
center(d, 890, "WhatsApp +56 9 4503 7484", F(BOLD, 44), WHITE)
center(d, 990, "Síguenos: @auselspa", F(BOLD, 50), WHITE)
center(d, 1060, "para más datos útiles", F(REG, 40), SOFT)
paste_logo(img, 240, 1180)
img.save(os.path.join(OUT, "7.jpg"), quality=92)

# --- Historias 1080x1920 (texto entre y=250 y 1600) ---
H = 1920
# s1 adelanto del post
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 290, "Nuevo post", F(BOLD, 60), YEL)
y = 420
for ln in ["¿Te da", "desconfianza", "comprar online?"]:
    center(d, y, ln, F(SERIF, 92), WHITE); y += 125
center(d, 880, "Resolvimos las 5 dudas", F(REG, 56), SOFT)
center(d, 960, "que más nos hacen", F(REG, 56), SOFT)
for n, t in enumerate(["¿Es seguro?", "¿Llega a regiones?", "¿Hay cuotas?"]):
    center(d, 1090 + n * 75, t, F(BOLD, 52), LIGHT)
d.rounded_rectangle([240, 1350, 840, 1460], radius=55, fill=YEL)
center(d, 1372, "Míralo en el perfil", F(BOLD, 52), NAVY)
center(d, 1520, "@auselspa", F(BOLD, 52), SOFT)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 producto del día: irrigador
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 270, "Producto del día", F(BOLD, 56), BLUE)
center(d, 360, "Irrigador bucal", F(SERIF, 90), NAVY)
f, m = estudio("img/estudio/irrigador-bucal-port-t/e1.jpg", 800, 640)
img.paste(f, ((W - 800) // 2, 500), m)
y = 1180
for t in ["Inalámbrico y portátil", "Trae 4 boquillas"]:
    center(d, y, t, F(BOLD, 50), STEEL); y += 70
center(d, 1330, clp(IRR["precio"]), F(BOLD, 100), BLUE)
center(d, 1460, f"6 cuotas de {clp(round(IRR['precio'] / 6))} sin interés", F(REG, 46), GREEN)
center(d, 1530, "www.myausel.com", F(BOLD, 52), NAVY)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 tip escritorio -> kit gamer
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 270, "Tip para tu escritorio", F(BOLD, 56), YEL)
center(d, 370, "3 cambios simples", F(SERIF, 84), WHITE)
tips = [("Pantalla a la altura", "de tus ojos"), ("Luz de costado, no", "detrás de la pantalla"), ("Teclado y mouse", "cerca, sin estirar el brazo")]
y = 540
for n, (a, b) in enumerate(tips, 1):
    d.ellipse([110, y, 200, y + 90], fill=YEL)
    fn = F(BOLD, 54); d.text((155 - d.textlength(str(n), font=fn) / 2, y + 12), str(n), font=fn, fill=NAVY)
    d.text((240, y - 2), a, font=F(BOLD, 50), fill=WHITE)
    d.text((240, y + 62), b, font=F(REG, 46), fill=SOFT)
    y += 190
d.rounded_rectangle([140, 1110, W - 140, 1420], radius=36, fill=WHITE)
ph = foto_prod(KIT, 380, 270)
img.paste(ph, (170 + (380 - ph.width) // 2, 1130 + (270 - ph.height) // 2))
d.text((590, 1170), "Kit teclado", font=F(BOLD, 44), fill=NAVY)
d.text((590, 1225), "+ mouse gamer", font=F(BOLD, 44), fill=NAVY)
d.text((590, 1300), clp(KIT["precio"]), font=F(BOLD, 64), fill=BLUE)
center(d, 1490, "Escríbenos por DM", F(BOLD, 54), YEL)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
