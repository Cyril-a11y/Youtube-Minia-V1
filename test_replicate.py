import os
import requests
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time
import json

# --- Paramètres ---
PROMPT = "Une loutre sur un vélo dans un parc au coucher de soleil"
AUTHOR = "Cyril"
VERSION = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

# --- Auth ---
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# --- Génération image via API REST (version figée) ---
print(f"⏳ Génération avec Replicate (SDXL pinned) : {PROMPT}")

url = "https://api.replicate.com/v1/predictions"
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}
payload = {
    "version": VERSION,
    "input": {
        "prompt": PROMPT,
        "width": 1280,
        "height": 720
    }
}

response = requests.post(url, headers=headers, json=payload)
if response.status_code not in [200, 201]:
    raise SystemExit(f"❌ Erreur API Replicate : {response.text}")

prediction = response.json()
prediction_url = prediction["urls"]["get"]

while prediction["status"] not in ["succeeded", "failed"]:
    time.sleep(3)
    prediction = requests.get(prediction_url, headers=headers).json()

if prediction["status"] != "succeeded":
    raise SystemExit("❌ La génération a échoué")

image_url = prediction["output"][0]

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

# Texte sous l’image (limité à 70 caractères, aligné à droite)
draw = ImageDraw.Draw(base)
text_line = f"{AUTHOR} : {PROMPT}"

# Tronquer si trop long
if len(text_line) > 70:
    text_line = text_line[:67] + "..."

try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    print("✅ Police DejaVuSans-Bold chargée")
except Exception as e:
    font = ImageFont.load_default()
    print(f"⚠️ Fallback load_default() : {e}")

text_y = y + 502 + 10
bbox = draw.textbbox((0, 0), text_line, font=font)
text_w = bbox[2] - bbox[0]
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
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run([
        "git", "commit", "--allow-empty",
        "-m", "🖼️ Nouvelle miniature test avec SDXL (version figée, commit forcé)"
    ], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Résultat poussé dans le repo avec succès (commit forcé).")
except Exception as e:
    print(f"⚠️ Erreur lors du push : {e}")
