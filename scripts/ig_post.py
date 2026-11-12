import io, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Ejemplo de carrusel 1080x1350 con la marca Ausel (usado en ig/c1). Copia y adapta para nuevas publicaciones.
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "c1")
os.makedirs(OUT, exist_ok=True)
NAVY, BLUE, SKY, STEEL, YEL = (6, 21, 43), (0, 63, 130), (239, 251, 252), (52, 102, 160), (255, 230, 0)
# Fuentes libres incluidas en fonts/ para que funcione igual en Windows y Linux.
def F(name, size):
    f = ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
    if name == "Merriweather.ttf":
        f.set_variation_by_axes([700 if a.get("name") == b"Weight" else a["default"] for a in f.get_variation_axes()])
    return f
SERIF, BOLD, REG = "Merriweather.ttf", "Lato-Bold.ttf", "Lato-Regular.ttf"
W, H = 1080, 1350
logo_white = Image.open(os.path.join(SITE, "img/logo-dark.png")).convert("RGBA")
logo_navy = Image.open(os.path.join(SITE, "img/logo.png")).convert("RGB")

def center(d, y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)

def paste_logo(img, logo, width, y):
    l = logo.resize((width, int(logo.height * width / logo.width)), Image.LANCZOS)
    img.paste(l, ((W - width) // 2, y), l if l.mode == "RGBA" else None)

def footer(img, d):
    d.rectangle([0, H - 110, W, H], fill=NAVY)
    center(d, H - 82, "www.myausel.com", F(BOLD, 44), (255, 255, 255))

productos = [
    ("Irrigador bucal inalámbrico", "4 boquillas · limpia donde el cepillo no llega", 21990,
     "https://http2.mlstatic.com/D_665212-MLU70646177655_072023-O.jpg"),
    ("Kit teclado + mouse gamer", "Luces LED RGB · listo para jugar", 16990,
     "https://http2.mlstatic.com/D_612177-MLU70655142179_072023-O.jpg"),
    ("Micrófono condensador", "Con trípode y filtro anti-pop", 15990,
     "https://http2.mlstatic.com/D_748733-MLA114826546260_082026-O.jpg"),
    ("Ventilador de mano M11", "Inalámbrico · alta velocidad", 13990,
     "https://http2.mlstatic.com/D_642377-MLA114594537013_072026-O.webp"),
]
clp = lambda n: "$" + f"{n:,}".replace(",", ".")

# 1. Portada
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
paste_logo(img, logo_white, 420, 150)
center(d, 470, "Lo más buscado", F(SERIF, 96), (255, 255, 255))
center(d, 590, "en Ausel", F(SERIF, 96), (143, 195, 255))
center(d, 760, "4 productos para tu día a día", F(REG, 44), (197, 211, 230))
center(d, 820, "desde " + clp(min(p[2] for p in productos)), F(BOLD, 52), YEL)
d.rounded_rectangle([340, 1020, 740, 1110], radius=45, fill=YEL)
center(d, 1037, "Desliza  →", F(BOLD, 44), (45, 50, 119))
img.save(os.path.join(OUT, "1.jpg"), quality=92)

# 2-5. Productos
for i, (nombre, sub, precio, url) in enumerate(productos, start=2):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    foto = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
    img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 80, W - 90, 800], radius=40, fill=(255, 255, 255))
    k = min(800 / foto.width, 640 / foto.height)
    foto = foto.resize((int(foto.width * k), int(foto.height * k)), Image.LANCZOS)
    img.paste(foto, ((W - foto.width) // 2, 80 + (720 - foto.height) // 2))
    center(d, 850, nombre, F(SERIF, 64), NAVY)
    center(d, 945, sub, F(REG, 38), STEEL)
    center(d, 1010, clp(precio), F(BOLD, 96), BLUE)
    center(d, 1135, f"6 cuotas de {clp(round(precio / 6))} sin interés", F(REG, 36), (0, 140, 70))
    footer(img, d)
    img.save(os.path.join(OUT, f"{i}.jpg"), quality=92)

# 6. Cierre
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 200, "¿Cómo comprar?", F(SERIF, 88), (255, 255, 255))
pasos = ["Entra a www.myausel.com", "Elige tu producto", "Paga protegido con Mercado Pago", "Te llega a la casa, en todo Chile"]
for n, t in enumerate(pasos, 1):
    y = 380 + (n - 1) * 140
    d.ellipse([150, y, 230, y + 80], fill=YEL)
    w = d.textlength(str(n), font=F(BOLD, 48)); d.text((190 - w / 2, y + 6), str(n), font=F(BOLD, 48), fill=NAVY)
    d.text((270, y + 12), t, font=F(BOLD, 46), fill=(255, 255, 255))
center(d, 1000, "¿Dudas? Escríbenos por WhatsApp", F(REG, 42), (197, 211, 230))
center(d, 1060, "+56 9 4503 7484", F(BOLD, 56), YEL)
paste_logo(img, logo_white, 260, 1180)
img.save(os.path.join(OUT, "6.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
