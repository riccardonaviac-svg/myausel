import os
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-18: reel kit teclado + mouse gamer + 3 historias.
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-18")
NAVY, BLUE, SKY, STEEL, YEL = (6, 21, 43), (0, 63, 130), (239, 251, 252), (52, 102, 160), (255, 230, 0)
WHITE, SOFT = (255, 255, 255), (197, 211, 230)
F = lambda name, size: ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
SERIF, BOLD, REG = "Merriweather.ttf", "Lato-Bold.ttf", "Lato-Regular.ttf"
W, H = 1080, 1920
clp = lambda n: "$" + f"{n:,}".replace(",", ".")

def center(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

def foto(path, maxw, maxh):
    f = Image.open(os.path.join(SITE, path)).convert("RGB")
    k = min(maxw / f.width, maxh / f.height)
    return f.resize((int(f.width * k), int(f.height * k)), Image.LANCZOS)

_k = Image.open(os.path.join(SITE, "img/estudio/kit-teclado-y-rat-n-ga/e4.jpg")).convert("RGB").crop((140, 560, 940, 1200))
KIT = _k.resize((840, 672), Image.LANCZOS)  # teclado recortado, llena el recuadro
KIT2 = foto("img/estudio/kit-teclado-y-rat-n-ga/e2.jpg", 400, 460)
MIC = foto("img/estudio/micr-fono-condensador/e4.jpg", 400, 460)
PRECIO = 16990

# s1 producto del día
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 280, "Producto del día", F(BOLD, 56), YEL)
center(d, 370, "Kit teclado + mouse", F(SERIF, 78), WHITE)
m = Image.new("L", KIT.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, KIT.width - 1, KIT.height - 1], radius=40, fill=255)
img.paste(KIT, ((W - KIT.width) // 2, 510), m)
center(d, 1220, "Gamer · con luces LED", F(REG, 54), SOFT)
center(d, 1310, clp(PRECIO), F(BOLD, 110), YEL)
center(d, 1460, "www.myausel.com", F(BOLD, 52), SOFT)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 ¿cuál te llevas? (setup gamer vs setup streamer)
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 280, "¿Cuál le falta", F(SERIF, 84), NAVY)
center(d, 390, "a tu setup?", F(SERIF, 84), NAVY)
for i, (ph, name, pr) in enumerate([(KIT2, "Kit gamer", 16990), (MIC, "Micrófono", 15990)]):
    x0 = 70 + i * 500
    d.rounded_rectangle([x0, 560, x0 + 440, 1060], radius=36, fill=WHITE)
    t = ph.copy(); t.thumbnail((400, 460))
    img.paste(t, (x0 + (440 - t.width) // 2, 560 + (500 - t.height) // 2))
    f = F(BOLD, 50); d.text((x0 + (440 - d.textlength(name, font=f)) / 2, 1100), name, font=f, fill=NAVY)
    f = F(BOLD, 64); d.text((x0 + (440 - d.textlength(clp(pr), font=f)) / 2, 1170), clp(pr), font=f, fill=BLUE)
center(d, 1360, "Respóndenos por DM", F(BOLD, 56), STEEL)
center(d, 1450, "@auselspa", F(BOLD, 56), BLUE)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 adelanto del reel
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 300, "Nuevo reel", F(BOLD, 64), YEL)
y = 460
for ln in ["Tu setup se ve", "aburrido"]:
    center(d, y, ln, F(SERIF, 100), WHITE); y += 140
y = 840
for ln in ["Teclado viejo, mouse cualquiera", "y un escritorio sin onda"]:
    center(d, y, ln, F(REG, 54), SOFT); y += 76
d.rounded_rectangle([240, 1120, 840, 1230], radius=55, fill=YEL)
center(d, 1140, "Míralo en el perfil", F(BOLD, 52), NAVY)
center(d, 1420, "Síguenos: @auselspa", F(BOLD, 56), WHITE)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
