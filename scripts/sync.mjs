// Trae las publicaciones activas del vendedor desde la API de Mercado Libre y escribe products.json.
// Necesita ML_CLIENT_ID, ML_CLIENT_SECRET y ML_REFRESH_TOKEN. ML entrega un refresh token nuevo
// en cada uso (el viejo deja de servir), así que lo guarda en .new_refresh_token para que el workflow lo actualice.
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";

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

// Un producto en catálogo tiene 2 publicaciones (la original y la de catálogo): nos quedamos con la de catálogo.
const items = [];
for (let i = 0; i < ids.length; i += 20) {
  const batch = await get(`/items?ids=${ids.slice(i, i + 20).join(",")}&attributes=id,title,price,original_price,permalink,pictures,catalog_product_id,catalog_listing`, tok.access_token);
  for (const { code, body: it } of batch) {
    if (code === 200) items.push(it);
  }
}
const enCatalogo = new Set(items.filter(it => it.catalog_listing).map(it => it.catalog_product_id));
const productos = items
  .filter(it => it.catalog_listing || !enCatalogo.has(it.catalog_product_id))
  .map(it => ({
    nombre: it.title,
    precio: it.price,
    precio_antes: it.original_price,
    img: it.pictures?.[0]?.secure_url || "",
    ml: it.permalink,
  }));

// Preguntas sin responder -> correo privado a ti (no se publican en ningún lado).
// .preguntas-avisadas guarda solo los números de las preguntas ya avisadas, para no repetir.
const { SMTP_USER, SMTP_PASS } = process.env;
// Si falla (p. ej. falta el permiso de preguntas en la app de ML), avisa en el log pero no frena la tienda.
if (SMTP_PASS) try {
  const F = ".preguntas-avisadas";
  const { questions } = await get(`/questions/search?seller_id=${userId}&status=UNANSWERED&api_version=4&limit=50`, tok.access_token);
  const avisadas = existsSync(F) ? readFileSync(F, "utf8").split("\n") : [];
  const nuevas = questions.filter(q => !avisadas.includes(String(q.id)));
  if (nuevas.length) {
    const cuerpo = nuevas.map(q => {
      const it = items.find(i => i.id === q.item_id);
      return `${it?.title || q.item_id}\n> ${q.text}\n${it?.permalink || ""}`;
    }).join("\n\n");
    const asunto = `=?UTF-8?B?${Buffer.from(`${nuevas.length} pregunta(s) nueva(s) en Mercado Libre`).toString("base64")}?=`;
    const correo = `From: Ausel bot <${SMTP_USER}>\r\nTo: ${SMTP_USER}\r\nSubject: ${asunto}\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n${cuerpo}\n\nResponde aquí: https://www.mercadolibre.cl/preguntas/vendedor\n`;
    execFileSync("curl", ["-sS", "--ssl-reqd", "--url", "smtps://smtp.gmail.com:465", "--user", `${SMTP_USER}:${SMTP_PASS}`,
      "--mail-from", SMTP_USER, "--mail-rcpt", SMTP_USER, "--upload-file", "-"], { input: correo });
  }
  writeFileSync(F, questions.map(q => q.id).join("\n") + "\n");
  console.log(`${questions.length} preguntas sin responder, ${nuevas.length} avisadas ahora`);
} catch (e) {
  console.log("::warning::Aviso de preguntas falló: " + e.message);
}

// ponytail: si la API devuelve 0 por un error raro, no vaciamos la tienda.
if (!productos.length) throw new Error("0 productos activos, no se actualiza products.json");
writeFileSync("products.json", JSON.stringify(productos, null, 1) + "\n");
console.log(`${productos.length} productos`);
