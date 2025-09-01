import json
import random

with open("data/comments.json", "r", encoding="utf-8") as f:
    comments = json.load(f)

if not comments:
    raise SystemExit("❌ Aucun commentaire trouvé.")

# Sélection au hasard
selected = random.choice(comments)

with open("data/selected_comment.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

# Log dans la console GitHub Actions
print("====================================")
print(f"🎲 Commentaire choisi :")
print(f"👤 Auteur : {selected['author']}")
print(f"💬 Texte  : {selected['text']}")
print("====================================")
