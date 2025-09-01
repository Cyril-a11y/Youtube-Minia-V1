import os
import json
import base64
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise SystemExit("❌ Manque le secret OPENAI_API_KEY")

# Charger le commentaire choisi
with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

author = comment.get("author", "Anonyme")
text = comment.get("text", "")

# Construire le prompt
prompt = f"Une illustration artistique représentant : {text}"

print("🎨 Prompt envoyé à l'IA :", prompt)

# Appel API OpenAI (DALL·E 3 ou 2 selon ton accès)
response = requests.post(
    "https://api.openai.com/v1/images/generations",
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-image-1",  # dalle-3 si activé sur ton compte
        "prompt": prompt,
        "size": "1024x1024"
    },
)

if response.status_code != 200:
    print("❌ Erreur API :", response.text)
    raise SystemExit(1)

data = response.json()
image_url = data["data"][0]["url"]

# Télécharger l’image
img_data = requests.get(image_url).content
os.makedirs("data", exist_ok=True)
with open("data/thumbnail.png", "wb") as f:
    f.write(img_data)

print("✅ Image générée par IA et sauvegardée : data/thumbnail.png")
