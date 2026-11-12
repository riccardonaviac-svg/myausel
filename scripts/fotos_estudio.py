# Crea fotos "de estudio" de cada producto a partir de sus fotos reales de Mercado Libre:
# recorta el producto del fondo blanco y lo pone sobre fondos de marca con sombra, luz y acercamientos.
# Uso: python3 scripts/fotos_estudio.py [carpeta_salida]   (por defecto img/estudio)
# Escribe <carpeta>/estudio.json: {nombre_producto: [rutas relativas]} para que reels y carruseles las usen.
import io, json, os, re, sys, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageOps

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SITE, "img", "estudio")
W, H = 1080, 1350
FONDOS = [  # (arriba, abajo) degradados de la marca
    ((18, 52, 104), (6, 21, 43)),       # azul noche
    ((239, 251, 252), (198, 226, 240)),  # celeste claro
    ((255, 244, 179), (255, 214, 102)),  # amarillo cálido
    ((0, 63, 130), (10, 30, 70)),        # azul marca
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")

def recorte(foto):
    """Devuelve el producto con transparencia si la foto tiene fondo blanco; si no, None."""
    w, h = foto.size
    esquinas = [foto.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    if not all(min(c) > 232 for c in esquinas):
        return None
    marca = foto.copy()
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(marca, p, (255, 0, 255), thresh=28)
    fondo = Image.new("L", (w, h), 0)
    px, mk = marca.load(), fondo.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] != (255, 0, 255):
                mk[x, y] = 255
    alfa = fondo.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    bbox = alfa.getbbox()
    if not bbox or (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) < 0.05 * w * h:
        return None
    prod = foto.convert("RGBA"); prod.putalpha(alfa)
    return prod.crop(bbox)

def degradado(arriba, abajo):
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        g.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(arriba, abajo)))
    img = g.resize((W, H))
    # foco de luz suave detrás del producto
    luz = Image.new("L", (W, H), 0)
    ImageDraw.Draw(luz).ellipse([W * .1, H * .12, W * .9, H * .78], fill=90)
    luz = luz.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img, luz)

def estudio(prod, fondo, escala=0.62, giro=0, alto_piso=0.8):
    img = degradado(*fondo)
    p = prod.rotate(giro, resample=Image.BICUBIC, expand=True) if giro else prod
    k = min(W * escala / p.width, H * escala / p.height)
    p = p.resize((int(p.width * k), int(p.height * k)), Image.LANCZOS)
    x, y = (W - p.width) // 2, int(H * alto_piso) - p.height
    # sombra de contacto
    sombra = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sombra).ellipse([x + p.width * .1, y + p.height - 18, x + p.width * .9, y + p.height + 26], fill=150)
    sombra = sombra.filter(ImageFilter.GaussianBlur(22))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, sombra.point(lambda v: v * .55))
    # reflejo tenue en el piso
    refl = ImageOps.flip(p); a = refl.getchannel("A").point(lambda v: v * .18)
    grad = Image.linear_gradient("L").resize(refl.size).point(lambda v: 255 - v)
    refl.putalpha(Image.composite(a, Image.new("L", refl.size, 0), grad))
    img.paste(refl, (x, y + p.height), refl)
    img.paste(p, (x, y), p)
    return img

def acercamiento(foto):
    # crop 1.7x hacia el centro del producto, para mostrar detalle
    w, h = foto.size; cw, ch = int(w / 1.7), int(h / 1.7)
    c = foto.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2))
    return ImageOps.fit(c, (W, H), Image.LANCZOS)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower())[:22].strip("-")

def main():
    productos = json.load(open(os.path.join(SITE, "products.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    indice = {}
    for p in productos:
        carpeta = os.path.join(OUT, slug(p["nombre"])); os.makedirs(carpeta, exist_ok=True)
        rutas, n = [], 0
        for i, url in enumerate((p.get("fotos") or [p["img"]])[:6]):
            foto = fetch(url)
            prod = recorte(foto)
            if prod is not None:  # foto de producto sobre blanco: 2 de estudio + detalle
                variantes = [estudio(prod, FONDOS[i % 4]), estudio(prod, FONDOS[(i + 1) % 4], escala=.5, giro=-8), acercamiento(foto)]
            else:  # foto ambientada: se usa completa (el producto puede no estar al centro)
                variantes = [ImageOps.fit(foto, (W, H), Image.LANCZOS)]
            for v in variantes:
                n += 1
                ruta = os.path.join(carpeta, f"{n}.jpg")
                v.save(ruta, quality=90)
                rutas.append(os.path.relpath(ruta, SITE).replace(os.sep, "/"))
        indice[p["nombre"]] = rutas
        print(len(rutas), "fotos", p["nombre"][:40])
    json.dump(indice, open(os.path.join(OUT, "estudio.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
