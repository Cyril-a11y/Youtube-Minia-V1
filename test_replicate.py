import os
import replicate
import requests
from PIL import Image, ImageDraw, ImageFont
import subprocess

# --- Paramètres ---
PROMPT = "Une loutre sur un vélo dans un parc au coucher de soleil"
AUTHOR = "Cyril"
MODEL = "qwen/qwen-image"

# --- Auth ---
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# --- Génération image ---
print(f"⏳ Génération avec Replicate ({MODEL}) : {PROMPT}")
try:
    output = replicate.run(
        MODEL,
        input={"prompt": PROMPT, "width": 1280, "height": 720}
    )
except Exception as e:
    raise SystemExit(f"❌ Erreur lors de la génération Replicate : {e}")

if not output or not isinstance(output, list):
    raise SystemExit("❌ Aucune image générée")

image_url = output[0]

# --- Téléchargement ---
os.makedirs("data", exist_ok=True)
gen_path = "data/generated.png"

r = requests.get(image_url, stream=True)
r.raise_for_status()
with open(gen_path, "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"✅ Image générée : {gen_path}")

# --- Montage ---
miniature_path = "data/miniature.png"
if not os.path.exists(miniature_path):
    raise SystemExit(f"❌ {miniature_path} introuvable")

base = Image.open(miniature_path).convert("RGBA")
gen = Image.open(gen_path).convert("RGBA").resize((785, 502))

# Cadrage issu du code principal
x, y = 458, 150
base.paste(gen, (x, y), gen)

# Texte sous l’image (limité à 50 caractères, aligné à droite)
draw = ImageDraw.Draw(base)
text_line = f"{AUTHOR} : {PROMPT}"

# Tronquer si trop long
if len(text_line) > 70:
    text_line = text_line[:67] + "..."

try:
    # ✅ DejaVuSans est dispo sur Ubuntu / GitHub Actions
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    print("✅ Police DejaVuSans-Bold chargée")
except Exception as e:
    font = ImageFont.load_default()
    print(f"⚠️ Impossible de charger DejaVuSans-Bold, fallback load_default() ({e})")

text_y = y + 502 + 10
bbox = draw.textbbox((0, 0), text_line, font=font)
text_w = bbox[2] - bbox[0]

# Aligné à droite sous le cadre
text_x = x + 785 - text_w
draw.text((text_x, text_y), text_line, font=font, fill="white")

# Sauvegarde finale
final_path = "data/final_thumbnail.png"
base.save(final_path)
print(f"✅ Miniature finale sauvegardée : {final_path}")

# --- Commit & push ---
print("📤 Commit & push des résultats (forcé)...")
try:
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "-A"], check=True)  # inclut les nouveaux fichiers
    subprocess.run([
        "git", "commit", "--allow-empty",
        "-m", "🖼️ Nouvelle miniature test avec texte ajustable (commit forcé)"
    ], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Résultat poussé dans le repo avec succès (commit forcé).")
except Exception as e:
    print(f"⚠️ Erreur lors du push : {e}")
