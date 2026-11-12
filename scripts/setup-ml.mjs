// Se corre UNA vez en tu computador: conecta tu cuenta de Mercado Libre y guarda las llaves
// como secretos del repo en GitHub (nunca quedan en el código).
import { createInterface } from "node:readline/promises";
import { execFileSync } from "node:child_process";

const REDIRECT = "https://www.myausel.com/";
const rl = createInterface({ input: process.stdin, output: process.stdout });

const clientId = (await rl.question("App ID (client_id) de tu app de Mercado Libre: ")).trim();
const clientSecret = (await rl.question("Clave secreta (client_secret): ")).trim();

const authUrl = `https://auth.mercadolibre.cl/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(REDIRECT)}`;
console.log("\nAbre este link, acepta, y copia la direccion completa a la que te manda (myausel.com/?code=...):\n\n" + authUrl + "\n");
const back = (await rl.question("Pega aqui esa direccion: ")).trim();
rl.close();

const code = new URL(back).searchParams.get("code");
const tok = await fetch("https://api.mercadolibre.com/oauth/token", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded", accept: "application/json" },
  body: new URLSearchParams({ grant_type: "authorization_code", client_id: clientId, client_secret: clientSecret, code, redirect_uri: REDIRECT }),
}).then(r => r.json());
if (!tok.refresh_token) throw new Error("Mercado Libre no entrego refresh token: " + JSON.stringify(tok));

const secrets = { ML_CLIENT_ID: clientId, ML_CLIENT_SECRET: clientSecret, ML_REFRESH_TOKEN: tok.refresh_token };
for (const [name, value] of Object.entries(secrets)) {
  execFileSync("gh", ["secret", "set", name], { input: value, stdio: ["pipe", "inherit", "inherit"] });
}
console.log("\nListo. Mercado Libre quedo conectado.");
