import os
import replicate
import requests
from PIL import Image
import time

# --- Paramètres ---
PROMPT = "un beau paysage"   # 👉 change le prompt ici si tu veux tester autre chose
MODEL = "qwen/qwen-image"    # 👉 change le modèle ici (ex: "google/gemini-2.5-flash-image")

# --- Auth ---
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# --- Génération image avec Replicate ---
print(f"⏳ Génération avec Replicate ({MODEL}) : {PROMPT}")
output = replicate.run(
    MODEL,
    input={"prompt": PROMPT, "width": 512, "height": 512}
)
image_url = output[0]

# --- Téléchargement ---
os.makedirs("data/archives", exist_ok=True)
r = requests.get(image_url, stream=True)
r.raise_for_status()
with open("data/generated.png", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print("✅ Image générée : data/generated.png")

# --- Montage avec miniature.png ---
if not os.path.exists("miniature.png"):
    raise SystemExit("❌ miniature.png introuvable")

base = Image.open("data/miniature.png").convert("RGBA")
gen = Image.open("data/generated.png").convert("RGBA").resize((400, 400))

# Incrustation en bas à droite
base.paste(gen, (base.width - 420, base.height - 420), gen)

# Sauvegarde finale
final_path = "data/final_thumbnail.png"
base.save(final_path)
print(f"✅ Miniature finale sauvegardée : {final_path}")

# Archive
archive_path = f"data/archives/test_{int(time.time())}.png"
base.save(archive_path)
print(f"💾 Archivé : {archive_path}")
