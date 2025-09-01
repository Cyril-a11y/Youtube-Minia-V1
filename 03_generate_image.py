import json
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720

with open("data/selected_comment.json", "r", encoding="utf-8") as f:
    comment = json.load(f)

img = Image.new("RGB", (WIDTH, HEIGHT), color=(30, 30, 30))
draw = ImageDraw.Draw(img)

# Chargement police (fallback basique)
try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()

text = f"{comment['author']}:\n{comment['text']}"
draw.multiline_text((50, 300), text, font=font, fill=(255, 255, 255), spacing=10)

img.save("data/thumbnail.png")
print("✅ Image générée : data/thumbnail.png")
