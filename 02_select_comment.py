import json
import random
import os
import re

with open("data/comments.json", "r", encoding="utf-8") as f:
    comments = json.load(f)

if not comments:
    raise SystemExit("❌ Aucun commentaire trouvé.")

selected = random.choice(comments)

# Nettoyer l’auteur pour nom de fichier
author = selected.get("author", "Anonyme")
author_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", author)

os.makedirs("data", exist_ok=True)

# --- Numéro par auteur ---
existing_author = [f for f in os.listdir("data") if f.startswith(author_safe) and f.endswith(".json")]
author_number = len(existing_author) + 1
author_filename = f"{author_safe}_{author_number}.json"

# --- Numéro global ---
all_jsons = [f for f in os.listdir("data") if f.endswith(".json") and not f == "selected_comment.json"]
global_number = len(all_jsons) + 1
global_filename = f"Comment_{global_number}.json"

# Sauvegarde fichiers
with open(os.path.join("data", author_filename), "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

with open(os.path.join("data", global_filename), "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

with open("data/selected_comment.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

print("====================================")
print("🎲 Nouveau commentaire choisi :")
print(f"👤 Auteur : {selected['author']}")
print(f"💬 Texte  : {selected['text']}")
print(f"💾 Sauvegardé dans : {author_filename} et {global_filename}")
print("====================================")
