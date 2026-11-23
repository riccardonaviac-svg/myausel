import os
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-23: historias (tip calor, ¿cuál te llevas?, cómo comprar).
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-23")
NAVY, BLUE, SKY, STEEL, YEL = (6, 21, 43), (0, 63, 130), (239, 251, 252), (52, 102, 160), (255, 230, 0)
WHITE, SOFT = (255, 255, 255), (197, 211, 230)
F = lambda name, size: ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
SERIF, BOLD, REG = "Merriweather.ttf", "Lato-Bold.ttf", "Lato-Regular.ttf"
W, H = 1080, 1920
EST = os.path.join(SITE, "img", "estudio", "m11-ventilador-inal-mb")

def center(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

def foto(name, bw, bh):
    f = Image.open(os.path.join(EST, name)).convert("RGB")
    k = max(bw / f.width, bh / f.height)
    f = f.resize((int(f.width * k) + 1, int(f.height * k) + 1), Image.LANCZOS)
    l, t = (f.width - bw) // 2, (f.height - bh) // 2
    return f.crop((l, t, l + bw, t + bh))

def card(img, name, box, r=40):
    x0, y0, x1, y1 = box
    f = foto(name, x1 - x0, y1 - y0)
    m = Image.new("L", f.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, f.width - 1, f.height - 1], radius=r, fill=255)
    img.paste(f, (x0, y0), m)


def fit(name, path, box, r=40):
    x0, y0, x1, y1 = box
    f = Image.open(os.path.join(SITE, path)).convert("RGB")
    bw, bh = x1 - x0, y1 - y0
    k = max(bw / f.width, bh / f.height)
    f = f.resize((int(f.width * k) + 1, int(f.height * k) + 1), Image.LANCZOS)
    l, t = (f.width - bw) // 2, (f.height - bh) // 2
    f = f.crop((l, t, l + bw, t + bh))
    m = Image.new("L", f.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=r, fill=255)
    return f, m

# s1 tip contra el calor
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 270, "Tip para el verano", F(BOLD, 56), STEEL)
center(d, 370, "Aire en la cara", F(SERIF, 86), NAVY)
center(d, 485, "y el cuello", F(SERIF, 86), NAVY)
center(d, 610, "refresca al tiro", F(REG, 56), BLUE)
card(img, "a3.jpg", (160, 720, W - 160, 1300))
center(d, 1350, "Ventilador de mano M11", F(BOLD, 56), NAVY)
center(d, 1430, "Nuevo reel en el perfil 👀".replace(" 👀", ""), F(BOLD, 52), BLUE)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 ¿cuál te llevas?
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 270, "¿Cuál te llevas?", F(SERIF, 92), WHITE)
center(d, 390, "Respóndenos por DM", F(REG, 50), SOFT)
items = [("img/estudio/m11-ventilador-inal-mb/a1.jpg", "Ventilador M11", "$13.990"),
         ("img/estudio/micr-fono-condensador/a1.jpg", "Micrófono", "$15.990"),
         ("img/estudio/kit-teclado-y-rat-n-ga/e1.jpg", "Kit gamer", "$16.990"),
         ("img/estudio/irrigador-bucal-port-t/e1.jpg", "Irrigador", "$21.990")]
for i, (p, n, pr) in enumerate(items):
    x0 = 90 + (i % 2) * 465; y0 = 500 + (i // 2) * 540
    f, m = fit(n, p, (x0, y0, x0 + 435, y0 + 390)); img.paste(f, (x0, y0), m)
    cx = x0 + 217
    for t, fo, c, yy in ((n, F(BOLD, 44), WHITE, y0 + 405), (pr, F(BOLD, 44), YEL, y0 + 460)):
        d.text((cx - d.textlength(t, font=fo) / 2, yy), t, font=fo, fill=c)
center(d, 1560, "www.myausel.com", F(BOLD, 50), SOFT)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 cómo comprar
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 280, "¿Cómo compro?", F(SERIF, 92), WHITE)
center(d, 400, "En 3 pasos", F(BOLD, 56), YEL)
pasos = [("1", ["Entra a www.myausel.com"]), ("2", ["Elige tu producto y te lleva", "a Mercado Libre"]), ("3", ["Paga con Mercado Pago,", "hasta 6 cuotas sin interés"])]
d.rounded_rectangle([100, 560, W - 100, 1260], radius=40, fill=WHITE)
for i, (n, ts) in enumerate(pasos):
    y = 620 + i * 210
    d.ellipse([150, y, 240, y + 90], fill=YEL); fo = F(BOLD, 56)
    d.text((195 - d.textlength(n, font=fo) / 2, y + 10), n, font=fo, fill=NAVY)
    for j, t in enumerate(ts):
        d.text((270, y + 15 + j * 62), t, font=F(REG, 46), fill=NAVY)
center(d, 1340, "Envío a todo Chile", F(BOLD, 60), WHITE)
center(d, 1440, "¿Dudas? Escríbenos por DM", F(BOLD, 52), YEL)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok")
