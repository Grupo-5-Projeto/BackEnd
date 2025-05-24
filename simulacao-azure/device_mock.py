import json
import mysql.connector

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
        values = (payload['data_hora'], payload['valor'], payload['fk_upa'], payload['fk_paciente'], payload['fk_sensor'], payload['fk_unid_medida'])
        sql = "INSERT INTO HistoricoSensor (data_hora, valor, fk_upa, fk_paciente, fk_sensor, fk_unid_medida) VALUES (%s, %s, %s, %s, %s, %s);"
        self.cursor.execute(sql, values)
        self.db.commit()

    async def shutdown(self):
        self.db.close()
