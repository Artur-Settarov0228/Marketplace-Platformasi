import os

from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN = os.getenv("TOKEN")
Getfile_Url = f"https://api.telegram.org/bot{TOKEN}/getFile"
File_install_url = f"https://api.telegram.org/file/bot{TOKEN}"

def get_image_by_id(image_id:str):
        
        getfile = requests.get(
            Getfile_Url,
            params={"file_id":image_id}
            )
        
        getfile = getfile.json()

        filepath = getfile['result']['file_path']

        response = requests.get(
           f"{File_install_url}/{filepath}"
        )

        return response.content