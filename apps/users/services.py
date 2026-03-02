import requests
from django.conf import settings

import core.settings as settings


def get_image_by_id(file_id: str) -> bytes:
    """
    Telegram file_id orqali rasmni yuklab beradi.
    """

    # 1️⃣ file info olish
    file_url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile"
    response = requests.get(file_url, params={"file_id": file_id})
    data = response.json()

    print("TELEGRAM FILE RESPONSE:", data)

    if not data.get("ok"):
        raise Exception(f"Telegram API error: {data}")

    file_path = data["result"]["file_path"]

    # 2️⃣ real file yuklab olish
    download_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"
    file_response = requests.get(download_url)

    if file_response.status_code != 200:
        raise Exception("Failed to download image")

    return file_response.content