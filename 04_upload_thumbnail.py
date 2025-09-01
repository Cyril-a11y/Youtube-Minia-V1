import os
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# ⚠️ Besoin d'un token OAuth2 généré en local et stocké comme secret
CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

def main():
    # Auth via OAuth2 (refresh token en secret GitHub)
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES
    )
    creds = flow.run_console()

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    request = youtube.thumbnails().set(
        videoId=VIDEO_ID,
        media_body="data/thumbnail.png"
    )
    response = request.execute()
    print("✅ Miniature mise à jour :", response)

if __name__ == "__main__":
    main()
