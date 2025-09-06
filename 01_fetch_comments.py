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
last_update_ts = 0
if os.path.exists(last_update_path):
    try:
        with open(last_update_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_update_ts = data.get("timestamp", 0)
    except Exception:
        last_update_ts = 0

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

    # Filtrer selon le temps de mise à jour
    published = snippet["publishedAt"]  # ex: "2025-09-06T09:50:43Z"
    ts = int(time.mktime(time.strptime(published, "%Y-%m-%dT%H:%M:%SZ")))
    if ts <= last_update_ts:
        continue

    comments.append({
        "author": snippet["authorDisplayName"],
        "text": text,
        "likes": snippet["likeCount"],
        "publishedAt": published
    })

os.makedirs("data", exist_ok=True)
with open("data/comments.json", "w", encoding="utf-8") as f:
    json.dump(comments, f, ensure_ascii=False, indent=2)

print(f"✅ {len(comments)} commentaires filtrés et sauvegardés dans data/comments.json")
