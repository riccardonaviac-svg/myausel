import io, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-12 am: carrusel "trucos para el calor" + 3 historias.
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-12-am")
os.makedirs(OUT, exist_ok=True)
NAVY, BLUE, SKY, STEEL, YEL = (6, 21, 43), (0, 63, 130), (239, 251, 252), (52, 102, 160), (255, 230, 0)
WHITE, SOFT, LIGHT = (255, 255, 255), (197, 211, 230), (143, 195, 255)
F = lambda name, size: ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
SERIF, BOLD, REG = "georgiab.ttf", "segoeuib.ttf", "segoeui.ttf"
W = 1080
logo_white = Image.open(os.path.join(SITE, "img/logo-dark.png")).convert("RGBA")
clp = lambda n: "$" + f"{n:,}".replace(",", ".")

def center(d, y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)

def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = word
    return lines + [cur]

def paste_logo(img, width, y):
    l = logo_white.resize((width, int(logo_white.height * width / logo_white.width)), Image.LANCZOS)
    img.paste(l, ((W - width) // 2, y), l)

def foto(url, maxw, maxh):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    f = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
    k = min(maxw / f.width, maxh / f.height)
    return f.resize((int(f.width * k), int(f.height * k)), Image.LANCZOS)

VENT = foto("https://http2.mlstatic.com/D_642377-MLA114594537013_072026-O.webp", 640, 560)
PRECIO = 13990

# --- Post 1080x1350 ---
H = 1350
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
paste_logo(img, 300, 110)
center(d, 340, "El calor ya llegó", F(SERIF, 92), WHITE)
center(d, 460, "5 trucos para", F(SERIF, 80), LIGHT)
center(d, 560, "aguantarlo mejor", F(SERIF, 80), LIGHT)
center(d, 730, "Sin aire acondicionado y sin gastar de más", F(REG, 40), SOFT)
d.rounded_rectangle([290, 960, 790, 1050], radius=45, fill=YEL)
center(d, 975, "Guárdalo y desliza  →", F(BOLD, 42), NAVY)
center(d, 1190, "Compártelo con quien se derrite en verano", F(REG, 36), SOFT)
img.save(os.path.join(OUT, "1.jpg"), quality=92)

tips = [
    ("Ventila de noche, cierra de día", "Abre las ventanas cuando baja la temperatura y cierra cortinas y persianas apenas pega el sol."),
    ("Hidrátate antes de tener sed", "Lleva una botella contigo. Cuando aparece la sed, el cuerpo ya va atrasado."),
    ("Ropa clara y de algodón", "Los colores claros absorben menos calor y el algodón deja respirar la piel."),
    ("Aire en movimiento", "Una corriente de aire en la cara y el cuello se siente mucho más fresca, aunque la temperatura sea la misma."),
]
for i, (tit, txt) in enumerate(tips, start=2):
    img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
    d.ellipse([440, 170, 640, 370], fill=BLUE)
    center(d, 205, str(i - 1), F(SERIF, 110), WHITE)
    y = 470
    for ln in wrap(d, tit, F(SERIF, 72), 880):
        center(d, y, ln, F(SERIF, 72), NAVY); y += 95
    y += 40
    for ln in wrap(d, txt, F(REG, 46), 860):
        center(d, y, ln, F(REG, 46), STEEL); y += 66
    d.rectangle([0, H - 110, W, H], fill=NAVY)
    center(d, H - 82, "www.myausel.com", F(BOLD, 44), WHITE)
    img.save(os.path.join(OUT, f"{i}.jpg"), quality=92)

# 6. Truco 5 = producto
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 60, "5. Lleva el aire contigo", F(SERIF, 66), NAVY)
d.rounded_rectangle([140, 170, W - 140, 790], radius=40, fill=WHITE)
img.paste(VENT, ((W - VENT.width) // 2, 170 + (620 - VENT.height) // 2))
center(d, 830, "Ventilador de mano M11", F(SERIF, 62), NAVY)
center(d, 920, "Inalámbrico · alta velocidad · cabe en la cartera", F(REG, 38), STEEL)
center(d, 985, clp(PRECIO), F(BOLD, 96), BLUE)
center(d, 1110, f"6 cuotas de {clp(round(PRECIO / 6))} sin interés", F(REG, 36), (0, 140, 70))
d.rectangle([0, H - 110, W, H], fill=NAVY)
center(d, H - 82, "www.myausel.com", F(BOLD, 44), WHITE)
img.save(os.path.join(OUT, "6.jpg"), quality=92)

# 7. Cierre
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 260, "¿Lo quieres?", F(SERIF, 96), WHITE)
center(d, 420, "Comenta CALOR", F(BOLD, 80), YEL)
center(d, 530, "y te mandamos el link", F(REG, 50), WHITE)
for n, t in enumerate(["Envío a todo Chile", "Pago protegido con Mercado Pago", "Hasta 6 cuotas sin interés"]):
    center(d, 720 + n * 80, t, F(BOLD, 44), SOFT)
center(d, 1010, "WhatsApp +56 9 4503 7484", F(BOLD, 46), YEL)
paste_logo(img, 260, 1150)
img.save(os.path.join(OUT, "7.jpg"), quality=92)

# --- Historias 1080x1920 (texto entre y=250 y 1600) ---
H = 1920
# s1 producto del día
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 280, "Producto del día", F(BOLD, 56), YEL)
center(d, 370, "Para el calor", F(SERIF, 100), WHITE)
d.rounded_rectangle([140, 540, W - 140, 1160], radius=40, fill=WHITE)
img.paste(VENT, ((W - VENT.width) // 2, 540 + (620 - VENT.height) // 2))
center(d, 1210, "Ventilador de mano M11", F(SERIF, 64), WHITE)
center(d, 1300, clp(PRECIO), F(BOLD, 110), YEL)
center(d, 1450, "www.myausel.com", F(BOLD, 52), SOFT)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 pregunta frecuente
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 280, "Pregunta frecuente", F(BOLD, 56), YEL)
y = 420
for ln in ["¿Puedo pagar", "en cuotas?"]:
    center(d, y, ln, F(SERIF, 110), WHITE); y += 140
center(d, 800, "Sí", F(SERIF, 150), YEL)
y = 1030
for ln in ["Hasta 6 cuotas sin interés.", "Pagas por Mercado Pago,", "así tu compra queda protegida."]:
    center(d, y, ln, F(REG, 54), WHITE); y += 80
center(d, 1430, "Escríbenos por DM", F(BOLD, 56), SOFT)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 adelanto del post
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 300, "Nuevo post", F(BOLD, 64), BLUE)
y = 460
for ln in ["5 trucos para", "aguantar el calor"]:
    center(d, y, ln, F(SERIF, 100), NAVY); y += 130
y = 820
for ln in ["Sin aire acondicionado", "y sin gastar de más"]:
    center(d, y, ln, F(REG, 56), STEEL); y += 80
d.rounded_rectangle([240, 1120, 840, 1230], radius=55, fill=YEL)
center(d, 1140, "Míralo en el perfil", F(BOLD, 52), NAVY)
center(d, 1420, "@auselspa", F(BOLD, 56), BLUE)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
