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
try:
    output = replicate.run(
        MODEL,
        input={"prompt": PROMPT, "width": 512, "height": 512}
    )
except Exception as e:
    raise SystemExit(f"❌ Erreur lors de la génération Replicate : {e}")

if not output or not isinstance(output, list):
    raise SystemExit("❌ Aucune image générée par Replicate")

image_url = output[0]

# --- Téléchargement ---
os.makedirs("data/archives", exist_ok=True)
gen_path = "data/generated.png"

try:
    r = requests.get(image_url, stream=True)
    r.raise_for_status()
    with open(gen_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
except Exception as e:
    raise SystemExit(f"❌ Erreur lors du téléchargement : {e}")

print(f"✅ Image générée : {gen_path}")

# --- Montage avec data/miniature.png ---
miniature_path = "data/miniature.png"
if not os.path.exists(miniature_path):
    raise SystemExit(f"❌ {miniature_path} introuvable")

try:
    base = Image.open(miniature_path).convert("RGBA")
    gen = Image.open(gen_path).convert("RGBA").resize((400, 400))

    # Incrustation en bas à droite
    base.paste(gen, (base.width - 420, base.height - 420), gen)

    # Sauvegarde finale
    final_path = "data/final_thumbnail.png"
    base.save(final_path)
    print(f"✅ Miniature finale sauvegardée : {final_path}")

    # Archive avec timestamp
    archive_path = f"data/archives/test_{int(time.time())}.png"
    base.save(archive_path)
    print(f"💾 Archivé : {archive_path}")
except Exception as e:
    raise SystemExit(f"❌ Erreur lors du montage : {e}")
