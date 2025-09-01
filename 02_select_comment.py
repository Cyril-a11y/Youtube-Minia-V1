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

print(f"✅ Commentaire choisi : {selected['author']} → {selected['text']}")
