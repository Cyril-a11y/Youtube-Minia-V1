import os
import json
import requests
import time
import re

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

text = comment.get("text", "")
author = comment.get("author", "Anonyme")

author_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", author)

os.makedirs("data", exist_ok=True)

# --- Numéro par auteur ---
existing_author = [f for f in os.listdir("data") if f.startswith(author_safe) and f.endswith(".png")]
author_number = len(existing_author) + 1
author_filename = f"{author_safe}_{author_number}.png"

# --- Numéro global ---
all_pngs = [f for f in os.listdir("data") if f.endswith(".png") and not f == "thumbnail.png"]
global_number = len(all_pngs) + 1
global_filename = f"Image_{global_number}.png"

prompt = f"Une illustration artistique représentant : {text}"
print("🎨 Prompt envoyé à Replicate :", prompt)

url = "https://api.replicate.com/v1/predictions"
headers = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "version": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    "input": {
        "prompt": prompt,
        "width": 1280,
        "height": 720
    }
}

response = requests.post(url, headers=headers, json=payload)
if response.status_code not in [200, 201]:
    print("❌ Erreur API Replicate :", response.text)
    raise SystemExit(1)

prediction = response.json()
prediction_url = prediction["urls"]["get"]

while prediction["status"] not in ["succeeded", "failed"]:
    time.sleep(3)
    prediction = requests.get(prediction_url, headers=headers).json()

if prediction["status"] != "succeeded":
    raise SystemExit("❌ La génération a échoué.")

image_url = prediction["output"][0]
img_data = requests.get(image_url).content

# Sauvegardes multiples
with open(os.path.join("data", author_filename), "wb") as f:
    f.write(img_data)

with open(os.path.join("data", global_filename), "wb") as f:
    f.write(img_data)

with open("data/thumbnail.png", "wb") as f:
    f.write(img_data)

print(f"✅ Images sauvegardées : {author_filename}, {global_filename}, thumbnail.png")
print("🌍 URL directe :", image_url)
