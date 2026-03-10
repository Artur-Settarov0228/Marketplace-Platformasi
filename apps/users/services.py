import requests
import core.settings as settings


def get_image_by_id(file_id: str) -> bytes:
    """
    Telegram serveridan rasmni file_id orqali yuklab olish funksiyasi.

    Telegram bot API da rasm yoki fayl to'g'ridan-to'g'ri file_id orqali
    olinmaydi. Jarayon 2 bosqichdan iborat:

    1️⃣ getFile endpoint orqali fayl haqida ma'lumot olish
    2️⃣ qaytgan file_path orqali real faylni yuklab olish

    Parametrlar:
        file_id (str): Telegram yuborgan rasmning identifikatori

    Qaytaradi:
        bytes: rasmning binary (bytes) ko‘rinishidagi ma'lumotlari

    Xatoliklar:
        Exception:
            - Telegram API noto'g'ri javob qaytarsa
            - Fayl yuklab olinmasa
    """

    # 1️⃣ Telegram API orqali file ma'lumotini olish
    file_url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile"

    response = requests.get(
        file_url,
        params={"file_id": file_id}
    )

    data = response.json()

    # Debug uchun Telegram javobini chiqarish
    print("TELEGRAM FILE RESPONSE:", data)

    # Agar Telegram API xatolik qaytarsa
    if not data.get("ok"):
        raise Exception(f"Telegram API xatosi: {data}")

    # Telegram fayl joylashgan server path
    file_path = data["result"]["file_path"]

    # Telegram serveridan real faylni yuklab olish
    download_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"

    file_response = requests.get(download_url)

    # Agar fayl yuklab olinmasa
    if file_response.status_code != 200:
        raise Exception("Rasmni yuklab olishda xatolik yuz berdi")

    # Rasmning binary ma'lumotlarini qaytarish
    return file_response.content