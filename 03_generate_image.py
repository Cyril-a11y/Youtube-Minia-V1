import json
from PIL import Image, ImageDraw, ImageFont
import textwrap

WIDTH, HEIGHT = 1280, 720
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

# Charger le commentaire choisi
with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

author = comment.get("author", "Anonyme")
text = comment.get("text", "")

# Créer une image
img = Image.new("RGB", (WIDTH, HEIGHT), color=BACKGROUND_COLOR)
draw = ImageDraw.Draw(img)

# Charger une police
try:
    font_author = ImageFont.truetype("arial.ttf", 50)
    font_text = ImageFont.truetype("arial.ttf", 40)
except:
    font_author = ImageFont.load_default()
    font_text = ImageFont.load_default()

# Auteur
draw.text((50, 100), f"{author} a écrit :", font=font_author, fill=(200, 200, 255))

# Texte du commentaire (retour à la ligne auto)
wrapped_text = textwrap.fill(text, width=40)
draw.multiline_text((50, 200), wrapped_text, font=font_text, fill=TEXT_COLOR, spacing=10)

# Sauvegarder
img.save("data/thumbnail.png")
print("✅ Image générée : data/thumbnail.png")
