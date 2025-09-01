import os
import json
from googleapiclient.discovery import build

API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

if not API_KEY or not VIDEO_ID:
    raise SystemExit("❌ Secrets YOUTUBE_API_KEY et YOUTUBE_VIDEO_ID requis.")

youtube = build("youtube", "v3", developerKey=API_KEY)

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
    comments.append({
        "author": snippet["authorDisplayName"],
        "text": snippet["textDisplay"],
        "likes": snippet["likeCount"]
    })

os.makedirs("data", exist_ok=True)
with open("data/comments.json", "w", encoding="utf-8") as f:
    json.dump(comments, f, ensure_ascii=False, indent=2)

print(f"✅ {len(comments)} commentaires récupérés et sauvegardés dans data/comments.json")
