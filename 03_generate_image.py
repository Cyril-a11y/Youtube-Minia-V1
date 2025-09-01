import os
import json
import requests
import time

# Clé API Replicate
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# Charger le commentaire choisi
with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

text = comment.get("text", "")
author = comment.get("author", "Anonyme")

# Construire le prompt
prompt = f"Une illustration artistique représentant : {text}"
print("🎨 Prompt envoyé à Replicate :", prompt)

# Appel à Replicate API (Stable Diffusion XL)
url = "https://api.replicate.com/v1/predictions"
headers = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "version": "stability-ai/sdxl",
    "input": {
        "prompt": prompt,
        "width": 1024,
        "height": 1024
    }
}

response = requests.post(url, headers=headers, json=payload)
if response.status_code not in [200, 201]:
    print("❌ Erreur API Replicate :", response.text)
    raise SystemExit(1)

prediction = response.json()
prediction_url = prediction["urls"]["get"]

# Attendre la fin du rendu
while prediction["status"] not in ["succeeded", "failed"]:
    time.sleep(3)
    prediction = requests.get(prediction_url, headers=headers).json()

if prediction["status"] != "succeeded":
    raise SystemExit("❌ La génération a échoué.")

image_url = prediction["output"][0]

# Télécharger l’image
img_data = requests.get(image_url).content
os.makedirs("data", exist_ok=True)
with open("data/thumbnail.png", "wb") as f:
    f.write(img_data)

print("✅ Image générée par Stable Diffusion XL et sauvegardée : data/thumbnail.png")
print("🌍 URL directe :", image_url)
