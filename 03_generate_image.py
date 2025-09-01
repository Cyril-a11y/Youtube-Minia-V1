import os
import json
import requests
import time
import re

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise SystemExit("❌ Manque le secret REPLICATE_API_TOKEN")

# Charger le commentaire choisi
with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

text = comment.get("text", "")
author = comment.get("author", "Anonyme")

# Nettoyer le nom d’auteur (pas d’espaces ni caractères spéciaux)
author_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", author)

# Vérifier combien d’images existent déjà pour incrémenter
os.makedirs("data", exist_ok=True)
existing = [f for f in os.listdir("data") if f.startswith(author_safe) and f.endswith(".png")]
number = len(existing) + 1

filename = f"{author_safe}_{number}.png"
filepath = os.path.join("data", filename)

# Construire le prompt
prompt = f"Une illustration artistique représentant : {text}"
print("🎨 Prompt envoyé à Replicate :", prompt)

# Appel à Replicate (SDXL, exemple avec version fixe)
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

# Attendre la fin
while prediction["status"] not in ["succeeded", "failed"]:
    time.sleep(3)
    prediction = requests.get(prediction_url, headers=headers).json()

if prediction["status"] != "succeeded":
    raise SystemExit("❌ La génération a échoué.")

image_url = prediction["output"][0]
img_data = requests.get(image_url).content

# Sauvegarder sous nouveau nom
with open(filepath, "wb") as f:
    f.write(img_data)

# Copier aussi en "thumbnail.png" (alias pour la dernière image)
with open("data/thumbnail.png", "wb") as f:
    f.write(img_data)

print(f"✅ Nouvelle image sauvegardée : {filepath}")
print("🌍 URL directe :", image_url)
