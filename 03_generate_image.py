import os
import json
import requests
import time
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont  # ✅ pour texte

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# Charger le commentaire sélectionné
with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

text = comment.get("text", "")
author = comment.get("author", "Anonyme")

author_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", author)
snippet = text[:14] if text else "no_text"
snippet_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", snippet)

os.makedirs("data", exist_ok=True)
os.makedirs("data/archives", exist_ok=True)

# --- Numéro global basé sur le nombre d'archives existantes ---
existing_archives = [f for f in os.listdir("data/archives") if f.lower().endswith(".png")]
global_index = len(existing_archives) + 1

# --- Prompt commun ---
prompt = (
    f"{text}. "
    "High quality, realistic, detailed, coherent with the description, 8k, sharp focus"
)
negative_prompt = (
    "low quality, blurry, deformed, distorted, text, watermark, bad anatomy, extra limbs, cropped, "
    "lowres, jpeg artifacts, worst quality, ugly, cartoonish, disfigured"
)

headers = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}
url = "https://api.replicate.com/v1/predictions"

# --- Fonction générique ---
def generate_image(model_version, label, index_offset=0):
    payload = {
        "version": model_version,
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": 1280,
            "height": 720,
            "guidance_scale": 9,
            "num_inference_steps": 50
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in [200, 201]:
        print(f"❌ Erreur API ({label}):", response.text)
        return None

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    while prediction["status"] not in ["succeeded", "failed"]:
        time.sleep(3)
        prediction = requests.get(prediction_url, headers=headers).json()

    if prediction["status"] != "succeeded":
        print(f"❌ La génération {label} a échoué")
        return None

    image_url = prediction["output"][0]
    img_data = requests.get(image_url).content

    archive_filename = f"{global_index+index_offset:04d}_{author_safe}_{snippet_safe}_{label}.png"
    archive_path = os.path.join("data/archives", archive_filename)

    with open(archive_path, "wb") as f:
        f.write(img_data)

    print(f"✅ Image {label} sauvegardée :", archive_path)
    return archive_path

# --- Générer avec 3 modèles ---
models = {
    "SDXL-Turbo": "stability-ai/sdxl-turbo:latest",
    "PixArt-α": "tencentarc/pixart-alpha:latest",
    "FLUX": "black-forest-labs/flux:latest"
}

generated_paths = []
for i, (label, model) in enumerate(models.items()):
    path = generate_image(model, label, i)
    if path:
        generated_paths.append(path)

# --- Composer une miniature avec la dernière image générée (optionnel) ---
if generated_paths:
    try:
        base_img = Image.open("data/miniature.png").convert("RGBA")
        gen_img = Image.open(generated_paths[-1]).convert("RGBA")
        gen_img = gen_img.resize((785, 502))
        x, y = 458, 150
        base_img.paste(gen_img, (x, y), gen_img)

        draw = ImageDraw.Draw(base_img)
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()

        text_color = (255, 255, 255, 255)
        author_text = f"Auteur: {author}"
        draw.text((20, base_img.height - 90), author_text, font=font, fill=text_color)

        wrapped = textwrap.fill(text, width=50)
        draw.text((20, base_img.height - 50), wrapped, font=font, fill=text_color)

        final_path = "data/final_thumbnail.png"
        base_img.save(final_path)
        print(f"✅ Miniature finale composée : {final_path}")
    except Exception as e:
        print("⚠️ Impossible de composer la miniature :", e)

print("🎉 Terminé. Images générées :", generated_paths)
