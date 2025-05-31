import json
import mysql.connector
import os
from datetime import datetime

class DeviceLocal:
    def __init__(self):
        self.db = None
        self.cursor = None

    async def connect(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="urubu100",
            database="upa_connect"
        )
        self.cursor = self.db.cursor()

    async def send_message(self, payload):
        if os.getenv("SAVE") == "db":
            values = (payload['data_hora'], payload['valor'], payload['fk_upa'], payload['fk_paciente'], payload['fk_sensor'], payload['fk_unid_medida'])
            sql = "INSERT INTO HistoricoSensor (data_hora, valor, fk_upa, fk_paciente, fk_sensor, fk_unid_medida) VALUES (%s, %s, %s, %s, %s, %s);"
            self.cursor.execute(sql, values)
            self.db.commit()
        elif os.getenv("SAVE") == "archive":
            archive_name = f"dados_{payload['data_hora'].strftime("%Y_%m_%d")}"

            with open(f'arquivos/{archive_name}.json', 'a') as arquivo:
                values = {
                    "data_hora": str(payload['data_hora']), 
                    "valor": payload['valor'], 
                    "fk_upa": payload['fk_upa'], 
                    "fk_paciente": payload['fk_paciente'], 
                    "fk_sensor": payload['fk_sensor'], 
                    "fk_unid_medida": payload['fk_unid_medida']
                }
                arquivo.write(json.dumps(values) + ",\n")

    async def shutdown(self):
        if os.getenv("SAVE") == "db":
            self.db.close()
