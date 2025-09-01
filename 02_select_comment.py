import json
import random
import os
import re

with open("data/comments.json", "r", encoding="utf-8") as f:
    comments = json.load(f)

if not comments:
    raise SystemExit("❌ Aucun commentaire trouvé.")

# Sélection au hasard
selected = random.choice(comments)

# Nettoyer le nom d’auteur (pour nom de fichier sûr)
author = selected.get("author", "Anonyme")
author_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", author)

# Vérifier combien de fichiers existent déjà pour cet auteur
os.makedirs("data", exist_ok=True)
existing = [f for f in os.listdir("data") if f.startswith(author_safe) and f.endswith(".json")]
number = len(existing) + 1

# Nom unique
filename = f"{author_safe}_{number}.json"
filepath = os.path.join("data", filename)

# Sauvegarde sous fichier unique
with open(filepath, "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

# Sauvegarde aussi en alias (dernier choisi)
with open("data/selected_comment.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

# Log clair
print("====================================")
print("🎲 Nouveau commentaire choisi :")
print(f"👤 Auteur : {selected['author']}")
print(f"💬 Texte  : {selected['text']}")
print(f"💾 Sauvegardé dans : {filepath}")
print("====================================")
