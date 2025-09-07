import os
import replicate
import requests
from PIL import Image
import time

PROMPT = "un beau paysage"
MODEL = "stability-ai/sdxl"   # modèle par défaut (tu peux changer)

# --- Étape 1 : Lister les modèles disponibles ---
print("📜 Listing des modèles Replicate accessibles...")
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

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

# --- Étape 2 : Génération image avec Replicate ---
print(f"⏳ Génération avec Replicate : {PROMPT}")
output = replicate.run(
    MODEL,
    input={"prompt": PROMPT, "width": 512, "height": 512}
)
image_url = output[0]

# --- Téléchargement ---
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
