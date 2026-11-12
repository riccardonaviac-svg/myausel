# Genera un reel vertical 1080x1920 (MP4) con los productos de products.json, con la marca Ausel.
# Uso: python scripts/ig_reel.py <carpeta_salida> "<gancho línea 1>" "<gancho línea 2>"
# Requiere Pillow, numpy y ffmpeg (en Linux: apt install ffmpeg python3-numpy; en Windows: pip install imageio-ffmpeg).
import io, json, os, subprocess, sys, urllib.request
import shutil
from musica import pista
from PIL import Image, ImageDraw, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SITE, "ig", "reel")
HOOK = sys.argv[2:4] if len(sys.argv) > 3 else ["4 cosas útiles", "que cuestan menos de $22 mil"]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
NAVY, BLUE, SKY, YEL, WHITE = (6, 21, 43), (0, 63, 130), (239, 251, 252), (255, 230, 0), (255, 255, 255)

def F(name, size):
    f = ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
    if name == "Merriweather.ttf":
        f.set_variation_by_axes([700 if a.get("name") == b"Weight" else a["default"] for a in f.get_variation_axes()])
    return f
SERIF, BOLD, REG = "Merriweather.ttf", "Lato-Bold.ttf", "Lato-Regular.ttf"
clp = lambda n: "$" + f"{round(n):,}".replace(",", ".")
logo = Image.open(os.path.join(SITE, "img", "logo-dark.png")).convert("RGBA")
logo = logo.resize((300, int(logo.height * 300 / logo.width)), Image.LANCZOS)

def center(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

def short(nombre):
    # Nombre corto y legible para pantalla: primeras palabras hasta ~24 caracteres.
    out = ""
    for w in nombre.split():
        if len(out) + len(w) > 24: break
        out = (out + " " + w).strip()
    while out.split()[-1].lower() in {"con", "y", "de", "para", "en", "el", "la", "del"}:
        out = out.rsplit(" ", 1)[0]
    return out

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")

productos = json.load(open(os.path.join(SITE, "products.json"), encoding="utf-8"))
fotos = [fetch(p["img"]) for p in productos]
ease = lambda t: t * t * (3 - 2 * t)

def bg():
    img = Image.new("RGB", (W, H), NAVY)
    img.paste(logo, ((W - logo.width) // 2, 230), logo)
    return img

def hook_frame(t):  # 0..1
    img = bg(); d = ImageDraw.Draw(img)
    a = ease(min(1, t * 2.5))
    y = int(760 + (1 - a) * 60)
    center(d, y, HOOK[0], F(SERIF, 96), WHITE)
    center(d, y + 130, HOOK[1], F(SERIF, 64), (143, 195, 255))
    if t > .45: center(d, 1200, "Mira hasta el final", F(BOLD, 48), YEL)
    return img

def product_frame(i, t):
    p, foto = productos[i], fotos[i]
    img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img)
    center(d, 250, f"{i + 1}/{len(productos)}", F(BOLD, 44), BLUE)
    d.rounded_rectangle([90, 340, W - 90, 1240], radius=48, fill=WHITE)
    z = 1 + .08 * t  # zoom lento
    k = min(820 / foto.width, 820 / foto.height) * z
    f = foto.resize((int(foto.width * k), int(foto.height * k)), Image.LANCZOS)
    box = Image.new("RGB", (860, 860), WHITE)
    box.paste(f, ((860 - f.width) // 2, (860 - f.height) // 2))
    img.paste(box, ((W - 860) // 2, 360))
    a = ease(min(1, t * 3))
    center(d, int(1300 + (1 - a) * 40), short(p["nombre"]), F(SERIF, 66), NAVY)
    if t > .25:
        center(d, 1410, clp(p["precio"]), F(BOLD, 120), BLUE)
        center(d, 1560, f"o 6 cuotas de {clp(p['precio'] / 6)} sin interés", F(REG, 42), (0, 140, 70))
    return img

def end_frame(t):
    img = bg(); d = ImageDraw.Draw(img)
    center(d, 720, "¿Cuál te llevas?", F(SERIF, 96), WHITE)
    center(d, 860, "Comenta tu favorito", F(REG, 50), (197, 211, 230))
    d.rounded_rectangle([170, 1040, 910, 1160], radius=60, fill=YEL)
    center(d, 1066, "Síguenos @auselspa", F(BOLD, 58), (45, 50, 119))
    center(d, 1240, "www.myausel.com", F(BOLD, 56), WHITE)
    center(d, 1320, "Envío a todo Chile · Compra protegida", F(REG, 40), (197, 211, 230))
    return img

escenas = [(hook_frame, 2.0)] + [((lambda i: lambda t: product_frame(i, t))(i), 2.6) for i in range(len(productos))] + [(end_frame, 3.0)]
mp4 = os.path.join(OUT, "reel.mp4")
# Música original generada para este reel (sin derechos de autor); la semilla cambia el tema cada vez.
wav = os.path.join(OUT, "musica.wav")
duracion = sum(d for _, d in escenas)
pista(duracion + .5, wav, semilla=int.from_bytes(os.urandom(2), "big"))
ff = shutil.which("ffmpeg")
if not ff:
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
proc = subprocess.Popen([ff, "-y", "-loglevel", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", wav, "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
for escena, dur in escenas:
    n = int(dur * FPS)
    for k in range(n):
        proc.stdin.write(escena(k / (n - 1)).tobytes())
proc.stdin.close(); proc.wait()
end_frame(1).save(os.path.join(OUT, "portada.jpg"), quality=92)
product_frame(0, .6).convert("RGB").save(os.path.join(OUT, "preview.jpg"), quality=85)
os.remove(wav)
print("ok", mp4, round(os.path.getsize(mp4) / 1e6, 1), "MB")
