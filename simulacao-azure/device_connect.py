from  azure.identity import DefaultAzureCredential
from azure.iot.device.aio import IoTHubDeviceClient
import asyncio
import json

class Device:
    def __init__(self):
        self.__client = None
        DefaultAzureCredential()

    async def connect(self, connect_string):
       self.__client = IoTHubDeviceClient.create_from_connection_string(connect_string)
       await self.__client.connect()
    
    async def send_message(self, payload):
        print(f"[INFO] Enviando payload: {payload}")
        await self.__client.send_message(json.dumps(payload))

    async def disconnect(self):
        await self.__client.shutdown()
