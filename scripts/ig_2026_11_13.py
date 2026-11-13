import io, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-13: reel irrigador bucal + 3 historias.
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-13")
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

IRR = foto("https://http2.mlstatic.com/D_665212-MLU70646177655_072023-O.jpg", 760, 580)
VENT = foto("https://http2.mlstatic.com/D_642377-MLA114594537013_072026-O.webp", 380, 380)
PRECIO = 21990

# s1 producto del día
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 280, "Producto del día", F(BOLD, 56), YEL)
center(d, 370, "Irrigador bucal", F(SERIF, 90), WHITE)
d.rounded_rectangle([140, 540, W - 140, 1160], radius=40, fill=WHITE)
img.paste(IRR, ((W - IRR.width) // 2, 540 + (620 - IRR.height) // 2))
center(d, 1210, "Inalámbrico · 4 boquillas", F(REG, 54), SOFT)
center(d, 1300, clp(PRECIO), F(BOLD, 110), YEL)
center(d, 1450, "www.myausel.com", F(BOLD, 52), SOFT)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 ¿cuál te llevas?
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 280, "¿Cuál te llevas?", F(SERIF, 90), NAVY)
for i, (ph, name, pr) in enumerate([(IRR, "Irrigador bucal", 21990), (VENT, "Ventilador M11", 13990)]):
    x0 = 70 + i * 500
    d.rounded_rectangle([x0, 500, x0 + 440, 1000], radius=36, fill=WHITE)
    t = ph.copy(); t.thumbnail((400, 460))
    img.paste(t, (x0 + (440 - t.width) // 2, 500 + (500 - t.height) // 2))
    f = F(BOLD, 46); d.text((x0 + (440 - d.textlength(name, font=f)) / 2, 1040), name, font=f, fill=NAVY)
    f = F(BOLD, 64); d.text((x0 + (440 - d.textlength(clp(pr), font=f)) / 2, 1110), clp(pr), font=f, fill=BLUE)
center(d, 1330, "Respóndenos por DM", F(BOLD, 56), STEEL)
center(d, 1420, "@auselspa", F(BOLD, 56), BLUE)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 adelanto del reel
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 300, "Nuevo reel 👀".replace(" 👀", ""), F(BOLD, 64), YEL)
y = 460
for ln in ["Tu cepillo", "no llega aquí"]:
    center(d, y, ln, F(SERIF, 100), WHITE); y += 140
y = 840
for ln in ["Entre los dientes quedan restos", "que el cepillo no saca"]:
    center(d, y, ln, F(REG, 54), SOFT); y += 76
d.rounded_rectangle([240, 1120, 840, 1230], radius=55, fill=YEL)
center(d, 1140, "Míralo en el perfil", F(BOLD, 52), NAVY)
center(d, 1420, "Síguenos: @auselspa", F(BOLD, 56), WHITE)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
