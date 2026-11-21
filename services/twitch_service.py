import time
from typing import Optional
import requests

_token_cache = {
    "access_token": None,
    "expires_at": 0.0,
}

# Se guarde en caché
def get_twitch_token(client_id: str, client_secret: str) -> Optional[str]:
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)

        _token_cache["access_token"] = access_token
        _token_cache["expires_at"] = now + expires_in - 60

        return access_token
    except requests.exceptions.RequestException:
        return None


def get_streamer_data(login: str, client_id: str, client_secret: str) -> dict:
    token = get_twitch_token(client_id, client_secret)
    if not token:
        return {"error": "Could not authenticate with Twitch API"}

    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"login": login.lower()}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return {"error": "Error querying Twitch API"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    data = response.json().get("data", [])
    if not data:
        return {"error": "Streamer not found"}

    streamer = data[0]
    result = {
        "twitch_streamer_id": streamer["id"],
        "login": streamer["login"],
        "display_name": streamer["display_name"],
        "description": streamer["description"],
        "broadcaster_type": streamer["broadcaster_type"],
        "profile_image_url": streamer["profile_image_url"],
    }
    return result

def get_streamer_videos(login: str, client_id: str, client_secret: str) -> dict:

    # No hace falta hacer get_twitch_token primero ya que en get_streamer_data se obtiene
    streamer = get_streamer_data(login, client_id, client_secret)
    if "error" in streamer:
        return streamer

    token = get_twitch_token(client_id, client_secret)
    if not token:
        return {"error": "Could not authenticate with Twitch API"}

    url = "https://api.twitch.tv/helix/videos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {
        "user_id": streamer["twitch_streamer_id"],
        "first": 10,  # Devuelve los últimos 10 vídeos/directos
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return {"error": "Error querying Twitch API"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    data = response.json().get("data", [])

    result = {
        "streamer": streamer["login"],
        "videos": [
            {
                "twitch_video_id": video["id"],
                "title": video["title"],
                "streamer_login": video["user_login"],
                "url": video["url"],
                "duration": video["duration"],
                "view_count": video["view_count"],
                "created_at": video["created_at"],
            }
            for video in data
        ],
    }

    return result

def get_video_by_id(video_id: str, client_id: str, client_secret: str) -> dict:
    token = get_twitch_token(client_id, client_secret)
    if not token:
        return {"error": "Could not authenticate with Twitch API"}

    url = "https://api.twitch.tv/helix/videos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"id": video_id}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return {"error": "Video not found on Twitch"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    data = response.json().get("data", [])
    if not data:
        return {"error": "Video not found on Twitch"}

    video = data[0]

    result = {
        "twitch_video_id": video["id"],
        "title": video["title"],
        "streamer_login": video["user_login"],
        "url": video["url"],
        "duration": video["duration"],
    }

    return result