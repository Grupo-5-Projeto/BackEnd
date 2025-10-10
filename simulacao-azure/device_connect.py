import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class Device:
    async def send_message(self, payload):
        url = os.environ["URL_API"]
        response = requests.post(url, data=json.dumps(payload))
        print(response)
        if response.status_code != 200:
            print("erro ao fazer requisicao para api")