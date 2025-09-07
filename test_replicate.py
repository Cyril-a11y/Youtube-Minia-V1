import os
import replicate
import requests
from PIL import Image
import time

PROMPT = "un beau paysage"
MODEL = "google/gemini-2.5-flash-image"   # 👉 change ici le modèle que tu veux tester

# --- Auth ---
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# --- Étape 1 : Lister les modèles ---
print("📜 Listing des modèles Replicate accessibles...")
resp = requests.get(
    "https://api.replicate.com/v1/models",
    headers={"Authorization": f"Token {token}"}
)

if resp.status_code == 200:
    data = resp.json()
    for m in data.get("results", []):
        print(f" - {m['owner']}/{m['name']}")
else:
    print(f"⚠️ Impossible de lister les modèles ({resp.status_code}) : {resp.text}")

print("====================================")

# --- Étape 2 : Lister les versions du modèle choisi ---
print(f"🔎 Recherche des versions disponibles pour {MODEL}...")
resp_versions = requests.get(
    f"https://api.replicate.com/v1/models/{MODEL}/versions",
    headers={"Authorization": f"Token {token}"}
)

if resp_versions.status_code == 200:
    versions = resp_versions.json().get("results", [])
    if versions:
        print(f"✅ {len(versions)} version(s) trouvée(s) :")
        for v in versions:
            created = v.get("created_at", "?")
            vid = v.get("id", "?")
            print(f" - {vid} (créé le {created})")
        # ⚠️ Tu peux copier-coller un hash de version et l’ajouter à MODEL si nécessaire :
        # MODEL = f"{MODEL}:{vid}"
    else:
        print("⚠️ Aucune version trouvée pour ce modèle.")
else:
    print(f"⚠️ Impossible de lister les versions ({resp_versions.status_code}) : {resp_versions.text}")

print("====================================")

# --- Étape 3 : Génération image avec Replicate ---
print(f"⏳ Génération avec Replicate ({MODEL}) : {PROMPT}")
output = replicate.run(
    MODEL,
    input={"prompt": PROMPT, "width": 512, "height": 512}
)
image_url = output[0]

# --- Téléchargement ---
os.makedirs("data", exist_ok=True)
r = requests.get(image_url, stream=True)
r.raise_for_status()
with open("data/generated.png", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print("✅ Image générée : data/generated.png")

# --- Montage avec miniature.png ---
if not os.path.exists("miniature.png"):
    raise SystemExit("❌ miniature.png introuvable")

base = Image.open("miniature.png").convert("RGBA")
gen = Image.open("data/generated.png").convert("RGBA").resize((400, 400))

# Incrustation en bas à droite
base.paste(gen, (base.width - 420, base.height - 420), gen)

# Sauvegarde
final_path = "data/final_thumbnail.png"
os.makedirs("data/archives", exist_ok=True)
base.save(final_path)
print(f"✅ Miniature finale sauvegardée : {final_path}")

# Archive
archive_path = f"data/archives/test_{int(time.time())}.png"
base.save(archive_path)
print(f"💾 Archivé : {archive_path}")
