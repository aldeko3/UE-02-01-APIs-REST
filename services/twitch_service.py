from typing import Optional
import requests


def get_twitch_token(client_id: str, client_secret: str) -> Optional[str]:
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
        return response.json().get("access_token")
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