import io, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-19: solo 3 historias (micrófono, envíos, tips de grabación).
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-19")
NAVY, BLUE, SKY, STEEL, YEL = (6, 21, 43), (0, 63, 130), (239, 251, 252), (52, 102, 160), (255, 230, 0)
WHITE, SOFT = (255, 255, 255), (197, 211, 230)
F = lambda name, size: ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
SERIF, BOLD, REG = "Merriweather.ttf", "Lato-Bold.ttf", "Lato-Regular.ttf"
W, H = 1080, 1920
clp = lambda n: "$" + f"{n:,}".replace(",", ".")

def center(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

def foto(url, maxw, maxh):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    f = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
    k = min(maxw / f.width, maxh / f.height)
    return f.resize((int(f.width * k), int(f.height * k)), Image.LANCZOS)

MIC = foto("https://http2.mlstatic.com/D_748733-MLA114826546260_082026-O.jpg", 760, 580)
PRECIO = 15990

# s1 producto del día
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 280, "Producto del día", F(BOLD, 56), YEL)
center(d, 370, "Micrófono condensador", F(SERIF, 72), WHITE)
d.rounded_rectangle([140, 540, W - 140, 1160], radius=40, fill=WHITE)
img.paste(MIC, ((W - MIC.width) // 2, 540 + (620 - MIC.height) // 2))
center(d, 1210, "Con trípode y filtro anti pop", F(REG, 54), SOFT)
center(d, 1300, clp(PRECIO), F(BOLD, 110), YEL)
center(d, 1450, "www.myausel.com", F(BOLD, 52), SOFT)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 pregunta frecuente
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 280, "Pregunta frecuente", F(BOLD, 56), YEL)
y = 420
for ln in ["¿Hacen envíos", "a regiones?"]:
    center(d, y, ln, F(SERIF, 110), WHITE); y += 140
center(d, 800, "Sí", F(SERIF, 150), YEL)
y = 1030
for ln in ["Enviamos a todo Chile.", "Compras por Mercado Libre", "y pagas con Mercado Pago."]:
    center(d, y, ln, F(REG, 54), WHITE); y += 80
center(d, 1430, "Escríbenos por DM", F(BOLD, 56), SOFT)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 tips para grabar
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 280, "3 tips para que tu voz", F(SERIF, 70), NAVY)
center(d, 380, "suene mejor al grabar", F(SERIF, 70), NAVY)
tips = [("1", "Graba en una pieza con", "cortinas o ropa: menos eco"),
        ("2", "Habla a unos 15 cm", "del micrófono"),
        ("3", "Usa filtro anti pop para", "suavizar la P y la B")]
y = 590
for n, a, b in tips:
    d.ellipse([110, y, 210, y + 100], fill=BLUE)
    d.text((160 - d.textlength(n, font=F(BOLD, 60)) / 2, y + 14), n, font=F(BOLD, 60), fill=WHITE)
    d.text((250, y - 4), a, font=F(BOLD, 50), fill=NAVY)
    d.text((250, y + 58), b, font=F(REG, 48), fill=STEEL)
    y += 230
center(d, 1330, "Compártelo con quien graba", F(BOLD, 52), BLUE)
center(d, 1420, "Síguenos: @auselspa", F(BOLD, 56), NAVY)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
