import json
import mysql.connector
import os
from datetime import datetime

class DeviceLocal:
    async def send_message(self, payload):
        archive_name = f"{payload['data_hora'].strftime("%Y_%m_%d")}.csv"

        all_archives = os.listdir("./arquivos")
        if not archive_name in all_archives:
            with open(f'arquivos/{archive_name}', 'a') as archive:
                archive.write("data_hora,valor,fk_sensor,fk_unid_medida,fk_paciente,fk_upa\n")
        else:
            with open(f'arquivos/{archive_name}', 'a') as archive:
                values = {
                    "data_hora": payload['data_hora'].strftime("%Y-%m-%dT%H:%M:%S"), 
                    "valor": payload['valor'] if payload['valor'] != None else "", 
                    "fk_upa": payload['fk_upa'], 
                    "fk_paciente": payload['fk_paciente'] if payload['fk_paciente'] != None else "", 
                    "fk_sensor": payload['fk_sensor'], 
                    "fk_unid_medida": payload['fk_unid_medida'] if payload['fk_unid_medida'] != None else ""
                }
                archive.write(f"{values["data_hora"]},{values["valor"]},{values["fk_sensor"]},{values["fk_unid_medida"]},{values["fk_paciente"]},{values["fk_upa"]}\n")

