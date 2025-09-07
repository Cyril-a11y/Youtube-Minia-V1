import os
import replicate
from PIL import Image

# --- Paramètres ---
PROMPT = "un beau paysage"
MODEL = "stability-ai/sdxl:8cfed36c"  # modèle par défaut (tu peux changer)

os.makedirs("data/archives", exist_ok=True)

# --- Génération image avec Replicate ---
print(f"⏳ Génération avec Replicate : {PROMPT}")
output = replicate.run(
    MODEL,
    input={"prompt": PROMPT, "width": 512, "height": 512}
)
image_url = output[0]

# Téléchargement
import requests
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
base.save(final_path)
print(f"✅ Miniature finale sauvegardée : {final_path}")

# Archive (avec un numéro unique)
import time
archive_path = f"data/archives/test_{int(time.time())}.png"
base.save(archive_path)
print(f"💾 Archivé : {archive_path}")
