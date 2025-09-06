import os
import json
import time
from googleapiclient.discovery import build

API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

if not API_KEY or not VIDEO_ID:
    raise SystemExit("❌ Secrets YOUTUBE_API_KEY et YOUTUBE_VIDEO_ID requis.")

youtube = build("youtube", "v3", developerKey=API_KEY)

# Charger la date du dernier update si dispo
last_update_path = "data/last_update.json"
use_time_filter = False
last_update_ts = 0

if os.path.exists(last_update_path):
    try:
        with open(last_update_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_update_ts = data.get("timestamp", 0)
            if last_update_ts > 0:
                use_time_filter = True
    except Exception:
        last_update_ts = 0
        use_time_filter = False

# Récupère les 50 derniers commentaires (triés par date)
request = youtube.commentThreads().list(
    part="snippet",
    videoId=VIDEO_ID,
    maxResults=50,
    order="time"
)
response = request.execute()

comments = []
for item in response.get("items", []):
    snippet = item["snippet"]["topLevelComment"]["snippet"]
    text = snippet["textDisplay"].strip()

    # Garder seulement si ça commence par #
    if not text.startswith("#"):
        continue

    if use_time_filter:
        # Filtrer selon le temps de mise à jour
        published = snippet["publishedAt"]  # ex: "2025-09-06T09:50:43Z"
        ts = int(time.mktime(time.strptime(published, "%Y-%m-%dT%H:%M:%SZ")))
        if ts <= last_update_ts:
            continue

    comments.append({
        "author": snippet["authorDisplayName"],
        "text": text,
        "likes": snippet["likeCount"],
        "publishedAt": snippet["publishedAt"]
    })

# Si pas de filtre temps : garder max 30 derniers
if not use_time_filter:
    comments = comments[:30]

# Sauvegarde et gestion des cas vides
os.makedirs("data", exist_ok=True)

if not comments:
    print("ℹ️ Aucun nouveau commentaire valide trouvé.")
    with open("no_comments.flag", "w") as f:
        f.write("no comments")
else:
    with open("data/comments.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    if use_time_filter:
        print(f"✅ {len(comments)} nouveaux commentaires après {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_update_ts))}")
    else:
        print(f"✅ {len(comments)} derniers commentaires sélectionnés (aucun horodatage trouvé)")
