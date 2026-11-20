import io, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

# Corrida 2026-11-20: historias (adelanto reel micrófono, ¿qué grabarías?, cómo comprar).
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "ig", "2026-11-20")
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

# s1 adelanto del reel
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
center(d, 280, "Nuevo reel", F(BOLD, 60), YEL)
center(d, 380, "¿Tu voz se", F(SERIF, 90), WHITE)
center(d, 500, "escucha mal?", F(SERIF, 90), WHITE)
d.rounded_rectangle([140, 670, W - 140, 1290], radius=40, fill=WHITE)
img.paste(MIC, ((W - MIC.width) // 2, 670 + (620 - MIC.height) // 2))
center(d, 1350, "Te mostramos cómo arreglarlo", F(REG, 54), SOFT)
center(d, 1450, "Míralo en nuestro perfil", F(BOLD, 56), YEL)
img.save(os.path.join(OUT, "s1.jpg"), quality=92)

# s2 pregunta: ¿qué grabarías?
img = Image.new("RGB", (W, H), BLUE); d = ImageDraw.Draw(img)
center(d, 280, "Pregunta del día", F(BOLD, 56), YEL)
center(d, 390, "Si tuvieras micrófono,", F(SERIF, 76), WHITE)
center(d, 490, "¿qué grabarías?", F(SERIF, 76), WHITE)
y = 680
for letra, txt in [("A", "Un podcast"), ("B", "Canciones"), ("C", "Clases o tutoriales"), ("D", "Streams de juegos")]:
    d.rounded_rectangle([150, y, W - 150, y + 130], radius=65, fill=WHITE)
    d.ellipse([170, y + 15, 270, y + 115], fill=YEL)
    d.text((220 - d.textlength(letra, font=F(BOLD, 56)) / 2, y + 30), letra, font=F(BOLD, 56), fill=NAVY)
    d.text((310, y + 34), txt, font=F(BOLD, 54), fill=NAVY)
    y += 170
center(d, 1400, "Respóndenos por DM", F(BOLD, 56), YEL)
img.save(os.path.join(OUT, "s2.jpg"), quality=92)

# s3 cómo comprar
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
center(d, 280, "¿Cómo comprar?", F(SERIF, 90), NAVY)
center(d, 400, "Fácil, en 3 pasos", F(REG, 56), STEEL)
pasos = [("1", "Entra a", "www.myausel.com"),
         ("2", "Elige tu producto y", "te lleva a Mercado Libre"),
         ("3", "Paga con Mercado Pago,", "hasta 6 cuotas sin interés")]
y = 590
for n, a, b in pasos:
    d.ellipse([110, y, 210, y + 100], fill=BLUE)
    d.text((160 - d.textlength(n, font=F(BOLD, 60)) / 2, y + 14), n, font=F(BOLD, 60), fill=WHITE)
    d.text((250, y - 4), a, font=F(BOLD, 50), fill=NAVY)
    d.text((250, y + 58), b, font=F(REG, 48), fill=STEEL)
    y += 230
center(d, 1330, "Envío a todo Chile", F(BOLD, 56), BLUE)
center(d, 1420, "Síguenos: @auselspa", F(BOLD, 56), NAVY)
img.save(os.path.join(OUT, "s3.jpg"), quality=92)
print("ok", sorted(os.listdir(OUT)))
