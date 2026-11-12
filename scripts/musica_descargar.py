# Descarga temas alegres de Kevin MacLeod (incompetech.com, licencia CC BY 4.0) a una carpeta local.
# Uso: python3 scripts/musica_descargar.py /root/musica 30   -> deja al menos 30 temas (o agrega N nuevos con --nuevos N)
# Cada tema queda con su ficha en catalogo.json (título y duración) para elegir y dar crédito.
import json, os, random, sys, urllib.parse, urllib.request

BASE = "https://incompetech.com/music/royalty-free/"
SI = {"Bright", "Uplifting", "Bouncy", "Grooving"}
NO = {"Dark", "Eerie", "Unnerving", "Somber", "Mysterious", "Suspenseful", "Aggressive", "Epic", "Intense", "Mystical", "Ren Faire", "Medieval"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()

def segundos(largo):
    partes = [int(x) for x in (largo or "0:0").split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(partes)))

def main():
    carpeta = sys.argv[1]
    nuevos = "--nuevos" in sys.argv
    n = int(sys.argv[sys.argv.index("--nuevos") + 1]) if nuevos else int(sys.argv[2] if len(sys.argv) > 2 else 30)
    os.makedirs(carpeta, exist_ok=True)
    ruta_cat = os.path.join(carpeta, "catalogo.json")
    catalogo = json.load(open(ruta_cat, encoding="utf-8")) if os.path.exists(ruta_cat) else {}

    piezas = json.loads(get(BASE + "pieces.json"))
    candidatos = []
    for p in piezas:
        feel = {f.strip() for f in (p.get("feel") or "").split(",")}
        bpm = int(p.get("bpm") or 0)
        if feel & SI and not feel & NO and 95 <= bpm <= 140 and segundos(p.get("length")) >= 60 and p["filename"] not in catalogo:
            candidatos.append(p)
    random.shuffle(candidatos)
    faltan = n if nuevos else max(0, n - len(catalogo))
    for p in candidatos[:faltan]:
        archivo = p["filename"]
        try:
            datos = get(BASE + "mp3-royaltyfree/" + urllib.parse.quote(archivo))
        except Exception as e:
            print("salto", archivo, e); continue
        open(os.path.join(carpeta, archivo), "wb").write(datos)
        catalogo[archivo] = {"titulo": p["title"], "segundos": segundos(p.get("length")), "bpm": int(p.get("bpm") or 0)}
        print("ok", p["title"], round(len(datos) / 1e6, 1), "MB")
    json.dump(catalogo, open(ruta_cat, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(catalogo), "temas en", carpeta)

if __name__ == "__main__":
    main()
