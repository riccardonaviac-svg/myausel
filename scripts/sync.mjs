// Trae las publicaciones activas del vendedor desde la API de Mercado Libre y escribe products.json.
// Necesita ML_CLIENT_ID, ML_CLIENT_SECRET y ML_REFRESH_TOKEN. ML entrega un refresh token nuevo
// en cada uso (el viejo deja de servir), así que lo guarda en .new_refresh_token para que el workflow lo actualice.
import { writeFileSync } from "node:fs";

const API = "https://api.mercadolibre.com";
const { ML_CLIENT_ID, ML_CLIENT_SECRET, ML_REFRESH_TOKEN } = process.env;

async function get(path, token) {
  const r = await fetch(API + path, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new Error(`${path}: ${r.status} ${await r.text()}`);
  return r.json();
}

const tok = await fetch(API + "/oauth/token", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded", accept: "application/json" },
  body: new URLSearchParams({ grant_type: "refresh_token", client_id: ML_CLIENT_ID, client_secret: ML_CLIENT_SECRET, refresh_token: ML_REFRESH_TOKEN }),
}).then(r => r.json());
if (!tok.access_token) throw new Error("No se pudo renovar el token: " + (tok.message || tok.error));
writeFileSync(".new_refresh_token", tok.refresh_token);

const { id: userId } = await get("/users/me", tok.access_token);
const ids = [];
for (let offset = 0; ; offset += 50) {
  const page = await get(`/users/${userId}/items/search?status=active&limit=50&offset=${offset}`, tok.access_token);
  ids.push(...page.results);
  if (offset + 50 >= page.paging.total) break;
}

const productos = [];
for (let i = 0; i < ids.length; i += 20) {
  const batch = await get(`/items?ids=${ids.slice(i, i + 20).join(",")}&attributes=title,price,original_price,permalink,pictures`, tok.access_token);
  for (const { code, body: it } of batch) {
    if (code !== 200) continue;
    productos.push({
      nombre: it.title,
      precio: it.price,
      precio_antes: it.original_price,
      img: it.pictures?.[0]?.secure_url || "",
      ml: it.permalink,
    });
  }
}

// ponytail: si la API devuelve 0 por un error raro, no vaciamos la tienda.
if (!productos.length) throw new Error("0 productos activos, no se actualiza products.json");
writeFileSync("products.json", JSON.stringify(productos, null, 1) + "\n");
console.log(`${productos.length} productos`);
