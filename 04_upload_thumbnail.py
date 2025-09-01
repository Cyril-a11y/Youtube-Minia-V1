import os
import google.auth.transport.requests
import google.oauth2.credentials
import googleapiclient.discovery

# Récupération des secrets (variables d’environnement injectées par GitHub)
CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, VIDEO_ID]):
    raise SystemExit("❌ Manque un secret GitHub (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, VIDEO_ID)")

# Scopes nécessaires pour gérer les vidéos & miniatures
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    # Création des credentials à partir du refresh token
    creds = google.oauth2.credentials.Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES
    )

    # Rafraîchir le token si nécessaire
    request = google.auth.transport.requests.Request()
    creds.refresh(request)

    # Client YouTube API
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # Upload miniature
    request = youtube.thumbnails().set(
        videoId=VIDEO_ID,
        media_body="data/thumbnail.png"
    )
    response = request.execute()

    print("✅ Miniature mise à jour :", response)

if __name__ == "__main__":
    main()
