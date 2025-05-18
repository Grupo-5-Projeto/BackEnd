import asyncio
import json

class Device:
    def __init__(self):
        print("[MOCK] Device iniciado (simulado)")

    async def connect(self, connect_string):
        print(f"[MOCK] Conectado com a string: {connect_string}")

    async def send_message(self, payload):
        print(f"[MOCK] Payload que seria enviado: {json.dumps(payload)}")
        # pass

    async def shutdown(self):
        print("[MOCK] Shutdown chamado")
