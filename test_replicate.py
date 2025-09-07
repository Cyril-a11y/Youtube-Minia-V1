import os
import requests
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time

# --- Paramètres ---
PROMPT = "Une loutre sur un vélo dans un parc au coucher de soleil"
AUTHOR = "Cyril"
MODE_TEST = "black-forest-labs/flux-schnell"
MODE_FINAL = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

# --- Auth ---
token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

def generate_image(model, prompt, out_path, width=512, height=512):
    """ Génère une image avec Replicate (via API REST) """
    print(f"⏳ Génération avec Replicate ({model}) : {prompt}")

    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": model,
        "input": {
            "prompt": prompt,
            "width": width,
            "height": height
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

    r = requests.get(image_url, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Image générée : {out_path}")
    return out_path


def commit_and_push(msg):
    """ Force un commit + push """
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Résultat poussé dans le repo avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur lors du push : {e}")


# --- Étape 1 : Génération rapide (flux-schnell) ---
os.makedirs("data", exist_ok=True)
test_path = "data/generated_test.png"
generate_image(MODE_TEST, PROMPT, test_path, width=512, height=512)

# Push immédiat de l’image test
commit_and_push("🖼️ Version test rapide (flux-schnell)")

# --- Étape 2 : Génération finale (SDXL) ---
final_gen = "data/generated.png"
generate_image(MODE_FINAL, PROMPT, final_gen, width=1280, height=720)

# Montage avec miniature
miniature_path = "data/miniature.png"
if not os.path.exists(miniature_path):
    raise SystemExit(f"❌ {miniature_path} introuvable")

base = Image.open(miniature_path).convert("RGBA")
gen = Image.open(final_gen).convert("RGBA").resize((785, 502))

x, y = 458, 150
base.paste(gen, (x, y), gen)

# Texte sous l’image (max 70 chars)
draw = ImageDraw.Draw(base)
text_line = f"{AUTHOR} : {PROMPT}"
if len(text_line) > 70:
    text_line = text_line[:67] + "..."

try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
except Exception:
    font = ImageFont.load_default()

text_y = y + 502 + 10
bbox = draw.textbbox((0, 0), text_line, font=font)
text_w = bbox[2] - bbox[0]
text_x = x + 785 - text_w

draw.text((text_x, text_y), text_line, font=font, fill="white")

final_path = "data/final_thumbnail.png"
base.save(final_path)
print(f"✅ Miniature finale sauvegardée : {final_path}")

# Push final
commit_and_push("🖼️ Nouvelle miniature finale (SDXL)")
