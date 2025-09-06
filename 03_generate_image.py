import os
import json
import requests
import time
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

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
    if response.status_code not in (200, 201):
        print(f"❌ Erreur API ({label}):", response.text)
        return None

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    while prediction["status"] not in ["succeeded", "failed"]:
        time.sleep(3)
        prediction = requests.get(prediction_url, headers=headers).json()

    if prediction["status"] != "succeeded":
        print(f"❌ Génération {label} a échoué")
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
    "SDXL-Turbo": "jyoung105/sdxl-turbo",
    "PixArt-α": "lucataco/pixart-xl-2",
    "FLUX": "black-forest-labs/flux-dev"
}

generated_paths = []
for i, (label, model_slug) in enumerate(models.items()):
    path = generate_image(model_slug, label, i)
    if path:
        generated_paths.append(path)

# --- Composer une miniature avec la dernière image générée ---
final_path = None
if generated_paths:
    try:
        base_img = Image.open("data/miniature.png").convert("RGBA")
        gen_img = Image.open(generated_paths[-1]).convert("RGBA")  # dernière = FLUX
        gen_img = gen_img.resize((785, 502))
        base_img.paste(gen_img, (458, 150), gen_img)

        draw = ImageDraw.Draw(base_img)
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()

        text_color = (255, 255, 255, 255)
        draw.text((20, base_img.height - 90), f"Auteur: {author}", font=font, fill=text_color)
        wrapped = textwrap.fill(text, width=50)
        draw.text((20, base_img.height - 50), wrapped, font=font, fill=text_color)

        final_path = "data/final_thumbnail.png"
        base_img.save(final_path)
        print(f"✅ Miniature finale composée : {final_path}")
    except Exception as e:
        print("⚠️ Impossible de composer la miniature :", e)

# --- Sauvegarder dans selected_comments.json ---
selected_comments_path = "data/selected_comments.json"
if os.path.exists(selected_comments_path):
    try:
        with open(selected_comments_path, "r", encoding="utf-8") as f:
            all_selected = json.load(f)
        if not isinstance(all_selected, list):
            all_selected = []
    except Exception:
        all_selected = []
else:
    all_selected = []

entry = dict(comment)
entry["_generated_images"] = generated_paths
entry["_index"] = global_index
all_selected.append(entry)

with open(selected_comments_path, "w", encoding="utf-8") as f:
    json.dump(all_selected, f, ensure_ascii=False, indent=2)

print(f"✅ Commentaires agrégés : {selected_comments_path} (total: {len(all_selected)})")

# --- Mise à jour de l'horodatage ---
if final_path and os.path.exists(final_path):
    now_ts = int(time.time())
    last_update_path = "data/last_update.json"
    last_update = {"timestamp": now_ts}
    with open(last_update_path, "w", encoding="utf-8") as f:
        json.dump(last_update, f)
    print(f"🕒 Horodatage mis à jour : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now_ts))}")

print("🎉 Terminé. Images générées :", generated_paths)
