# Reel de marketing 1080x1920 (MP4) para UN producto, a partir de un guion JSON:
#   gancho -> problema -> solución -> 3 beneficios -> precio -> llamado a la acción
# Cortes al ritmo de la música, zoom en cada corte, subtítulos en cajas estilo TikTok y barra de progreso.
#
# Uso: python3 scripts/ig_reel.py <carpeta_salida> <guion.json>
# guion.json:
# {"producto": "irrigador",                       (parte del nombre en products.json)
#  "gancho": "Tu cepillo no llega aquí",          (corto, 3-6 palabras, que dé curiosidad)
#  "problema": "Restos de comida entre los dientes...",
#  "solucion": "Irrigador bucal inalámbrico",
#  "beneficios": ["Limpia con agua a presión", "4 boquillas", "Recargable por USB"],
#  "cta": "Comenta QUIERO y te mando el link"}
# Requiere Pillow, numpy y ffmpeg. Música: MUSICA_DIR con temas de scripts/musica_descargar.py (si no, sintetiza una).
import io, json, os, random, shutil, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from musica import pista

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, GUION = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
NAVY, BLUE, YEL, WHITE, GREEN = (6, 21, 43), (0, 63, 130), (255, 230, 0), (255, 255, 255), (0, 140, 70)

def F(name, size):
    return ImageFont.truetype(os.path.join(SITE, "fonts", name), size)
BOLD, REG = "Lato-Bold.ttf", "Lato-Regular.ttf"
clp = lambda n: "$" + f"{round(n):,}".replace(",", ".")
def back(t):  # rebote suave para que el texto "salte" al entrar
    c = 1.7; t = min(1, max(0, t)); return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

# ---------- producto y fotos ----------
productos = json.load(open(os.path.join(SITE, "products.json"), encoding="utf-8"))
p = next((x for x in productos if GUION["producto"].lower() in x["nombre"].lower()), productos[0])
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
ruta_est = os.path.join(SITE, "img", "estudio", "estudio.json")
estudio = json.load(open(ruta_est, encoding="utf-8")) if os.path.exists(ruta_est) else {}
# Primero fotos de estudio (e) y ambientadas (a); los detalles (d) quedan al final, para los beneficios.
rutas = estudio.get(p["nombre"], [])
random.shuffle(rutas)
rutas.sort(key=lambda r: os.path.basename(r).startswith("d"))
fotos = [Image.open(os.path.join(SITE, f)).convert("RGB") for f in rutas] or [fetch(u) for u in (p.get("fotos") or [p["img"]])]
foto = lambda i: fotos[i % len(fotos)]

# ---------- música (define el ritmo de los cortes) ----------
MUSICA = os.environ.get("MUSICA_DIR", "")
credito, wav, tema, bpm = "", None, None, 115
if MUSICA and os.path.exists(os.path.join(MUSICA, "catalogo.json")):
    catalogo = json.load(open(os.path.join(MUSICA, "catalogo.json"), encoding="utf-8"))
    ruta_usados = os.path.join(MUSICA, "usados.json")
    usados = json.load(open(ruta_usados, encoding="utf-8")) if os.path.exists(ruta_usados) else []
    libres = [f for f in catalogo if f not in usados[-15:] and os.path.exists(os.path.join(MUSICA, f))] or list(catalogo)
    tema = random.choice(libres)
    bpm = catalogo[tema].get("bpm") or 115
    json.dump((usados + [tema])[-50:], open(ruta_usados, "w", encoding="utf-8"), ensure_ascii=False)
    credito = f"Música: {catalogo[tema]['titulo']} - Kevin MacLeod (incompetech.com), licencia CC BY 4.0"
beat = 60 / bpm
while beat < .42: beat *= 2   # cortes ni muy rápidos...
while beat > .8: beat /= 2    # ...ni muy lentos

# ---------- dibujo ----------
def cubrir(img, zoom, foco=(.5, .5)):
    """Foto a pantalla completa con zoom lento (efecto Ken Burns)."""
    k = max(W / img.width, H / img.height) * zoom
    r = img.resize((int(img.width * k) + 1, int(img.height * k) + 1), Image.BILINEAR)
    x = int((r.width - W) * foco[0]); y = int((r.height - H) * foco[1])
    return r.crop((x, y, x + W, y + H))

def oscurecer(img, fuerza, y0, y1):
    """Banda oscura degradada detrás del texto para que siempre se lea."""
    capa = Image.new("L", (1, H), 0)
    for y in range(y0, y1):
        m = (y0 + y1) / 2; capa.putpixel((0, y), int(fuerza * (1 - ((y - m) / ((y1 - y0) / 2)) ** 2)))
    return Image.composite(Image.new("RGB", (W, H), NAVY), img, capa.resize((W, H)))

def envolver(d, texto, fuente, ancho):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if d.textlength(prueba, font=fuente) <= ancho: actual = prueba
        else: lineas.append(actual); actual = palabra
    return lineas + ([actual] if actual else [])

def cajas(img, texto, y, tam=74, fondo=WHITE, color=NAVY, t=1.0, ancho=860):
    """Subtítulo en cajas por línea (estilo TikTok) que entra con un pequeño salto. Devuelve el y siguiente."""
    d = ImageDraw.Draw(img); f = F(BOLD, tam)
    lineas = envolver(d, texto, f, ancho); alto = int(tam * 1.3)
    fin = y + len(lineas) * (alto + 12)
    s = back(t * 3.5)
    if s <= 0.02: return fin
    capa = Image.new("RGBA", (W, fin - y + 40), (0, 0, 0, 0)); dc = ImageDraw.Draw(capa)
    for i, linea in enumerate(lineas):
        w = d.textlength(linea, font=f); x = (W - w) / 2; yy = 20 + i * (alto + 12)
        dc.rounded_rectangle([x - 26, yy - 6, x + w + 26, yy + alto - 2], radius=18, fill=fondo + (255,))
        dc.text((x, yy + tam * .07), linea, font=f, fill=color)
    if abs(s - 1) > .01:
        nw, nh = max(1, int(capa.width * s)), max(1, int(capa.height * s))
        capa = capa.resize((nw, nh), Image.BILINEAR)
    img.paste(capa, ((W - capa.width) // 2, y - 20 + (fin - y + 40 - capa.height) // 2), capa)
    return fin

LOGO = Image.open(os.path.join(SITE, "img", "logo-dark.png")).convert("RGBA")
def logo_blanco(img, ancho, y):
    lg = LOGO.resize((ancho, int(LOGO.height * ancho / LOGO.width)), Image.LANCZOS)
    img.paste(lg, ((W - ancho) // 2, y), lg)

# ---------- escenas (texto siempre entre y=260 y y=1450, fuera de lo que tapa Instagram) ----------
def esc_gancho(t):
    img = oscurecer(cubrir(foto(0), 1.25 - .12 * t), 190, 300, 1150)
    cajas(img, GUION["gancho"].upper(), 560, tam=98, fondo=YEL, color=NAVY, t=t)
    return img

def esc_problema(t):
    img = cubrir(foto(1), 1.05 + .08 * t).filter(ImageFilter.GaussianBlur(5))
    img = oscurecer(img, 200, 350, 1250)
    cajas(img, GUION["problema"], 640, tam=72, t=t)
    return img

def esc_solucion(t):
    img = oscurecer(cubrir(foto(2), 1.15 - .1 * t), 160, 1000, 1500)
    y = cajas(img, "LA SOLUCIÓN", 1060, tam=50, fondo=NAVY, color=YEL, t=t)
    cajas(img, GUION["solucion"], y + 10, tam=76, t=t - .08)
    return img

def esc_beneficio(n):
    def f(t):
        img = oscurecer(cubrir(foto(3 + n), 1.0 + .1 * t, (.5, .45)), 170, 1000, 1500)
        d = ImageDraw.Draw(img)
        d.ellipse([W / 2 - 46, 1010, W / 2 + 46, 1102], fill=YEL)
        num, fn = str(n + 1), F(BOLD, 60)
        d.text((W / 2 - d.textlength(num, font=fn) / 2, 1020), num, font=fn, fill=NAVY)
        cajas(img, GUION["beneficios"][n], 1130, tam=70, t=t)
        return img
    return f

def esc_precio(t):
    img = oscurecer(cubrir(foto(0), 1.08 - .06 * t), 220, 650, 1500)
    d = ImageDraw.Draw(img); y = 780
    if p.get("precio_antes") and p["precio_antes"] > p["precio"]:  # solo si el descuento es real
        fa = F(BOLD, 64); txt = clp(p["precio_antes"]); w = d.textlength(txt, font=fa)
        d.text(((W - w) / 2, y), txt, font=fa, fill=(200, 210, 225))
        d.line([(W - w) / 2, y + 40, (W + w) / 2, y + 40], fill=(255, 90, 90), width=6); y += 90
    fp = F(BOLD, max(20, int(150 * min(1.08, back(t * 3))))); txt = clp(p["precio"])
    d.text(((W - d.textlength(txt, font=fp)) / 2, y + (150 - fp.size) / 2), txt, font=fp, fill=YEL)
    y2 = cajas(img, f"o 6 cuotas de {clp(p['precio'] / 6)} sin interés", y + 200, tam=50, fondo=WHITE, color=GREEN, t=t - .15)
    cajas(img, "Envío a todo Chile", y2 + 10, tam=50, fondo=NAVY, color=WHITE, t=t - .25)
    return img

def esc_cta(t):
    img = Image.new("RGB", (W, H), NAVY)
    logo_blanco(img, 300, 300)
    y = cajas(img, GUION.get("cta", "Comenta QUIERO y te mando el link"), 640, tam=80, fondo=YEL, color=NAVY, t=t)
    y = cajas(img, "Síguenos @auselspa", y + 50, tam=64, fondo=WHITE, color=NAVY, t=t - .12)
    cajas(img, "www.myausel.com", y + 30, tam=54, fondo=BLUE, color=WHITE, t=t - .22)
    return img

ESCENAS = [(esc_gancho, 4), (esc_problema, 4), (esc_solucion, 4)] \
    + [(esc_beneficio(n), 3) for n in range(min(3, len(GUION["beneficios"])))] + [(esc_precio, 5), (esc_cta, 6)]
duraciones = [b * beat for _, b in ESCENAS]
total = sum(duraciones)

# ---------- audio ----------
if tema:
    largo = catalogo[tema]["segundos"]
    inicio = random.uniform(min(8, largo / 4), max(8, largo - total - 10))
    audio_in = ["-ss", f"{inicio:.1f}", "-i", os.path.join(MUSICA, tema)]
    audio_af = ["-af", f"afade=t=in:d=0.3,afade=t=out:st={total - 1.2:.2f}:d=1.2"]
else:
    wav = os.path.join(OUT, "musica.wav"); pista(total + .5, wav, semilla=int.from_bytes(os.urandom(2), "big"))
    audio_in, audio_af = ["-i", wav], []
open(os.path.join(OUT, "credito.txt"), "w", encoding="utf-8").write(credito)

# ---------- render ----------
ff = shutil.which("ffmpeg")
if not ff:
    import imageio_ffmpeg; ff = imageio_ffmpeg.get_ffmpeg_exe()
mp4 = os.path.join(OUT, "reel.mp4")
proc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    *audio_in, *audio_af, "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
    "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
transcurrido = 0.0
for k, ((escena, _), dur) in enumerate(zip(ESCENAS, duraciones)):
    n = max(2, round(dur * FPS))
    for j in range(n):
        img = escena(j / (n - 1))
        if j < 4 and k > 0:  # destello corto en cada corte
            img = Image.blend(img, Image.new("RGB", (W, H), WHITE), .4 * (1 - j / 4))
        ImageDraw.Draw(img).rectangle([0, 0, int(W * (transcurrido + j / FPS) / total), 10], fill=YEL)  # barra de progreso
        proc.stdin.write(img.tobytes())
    transcurrido += n / FPS
proc.stdin.close(); proc.wait()
esc_gancho(.8).save(os.path.join(OUT, "portada.jpg"), quality=92)
esc_precio(.9).save(os.path.join(OUT, "preview.jpg"), quality=85)
if wav: os.remove(wav)
print("ok", p["nombre"][:40], f"{total:.1f}s", credito or "música sintetizada", round(os.path.getsize(mp4) / 1e6, 1), "MB")
