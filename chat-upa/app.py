from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta, timezone
import mysql.connector
import json
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============ CONFIGURAÇÕES ============
API_KEY = "AIzaSyBlyuMSTVQT1IQzCQFU6gbC_Gys0KJoABI"

json_enderecos_upa = {}

conn = mysql.connector.connect(
    host='localhost',
    user='admin_upa_connect',
    password='urubu100',
    database='upa_connect'
)

# ============ APP FLASK ============
app = Flask(__name__)
CORS(app)


# ============ FUNÇÕES ============
def pegar_coordenadas(endereco, api_key):
    endereco_formatado = endereco.replace(" ", "+")
    geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_formatado}&key={api_key}"
    response = requests.get(geo_url)
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None


def gerar_link_maps(lat_origem, long_origem, lat_destino, long_destino, modo):
    return f"https://www.google.com/maps/dir/?api=1&origin={lat_origem},{long_origem}&destination={lat_destino},{long_destino}&travelmode={modo}"


def calcular_rotas(lat_origem, long_origem, destino, api_key):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    departure_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }

    modos_transporte = {
        "Carro": "DRIVE",
        "Moto": "TWO_WHEELER",
        "Transporte Público": "TRANSIT",
        "A Pé": "WALK"
    }

    resultados = {}

    for nome, modo in modos_transporte.items():
        data = {
            "origin": {"location": {"latLng": {"latitude": lat_origem, "longitude": long_origem}}},
            "destination": {"address": destino},
            "travelMode": modo,
            "departureTime": departure_time,
            "computeAlternativeRoutes": False
        }

        if modo in ["DRIVE", "TWO_WHEELER"]:
            data["routingPreference"] = "TRAFFIC_AWARE"

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            rota = response.json()
            if "routes" in rota:
                distancia_m = rota["routes"][0]["distanceMeters"]
                tempo_s = rota["routes"][0]["duration"]
                distancia_km = distancia_m / 1000
                tempo_min = int(tempo_s[:-1]) // 60

                resultados[nome] = {
                    "Distância": f"{distancia_km:.2f} km",
                    "Tempo Estimado": f"{tempo_min} min"
                }
            else:
                resultados[nome] = "Erro: Resposta sem rota."
        else:
            resultados[nome] = f"Erro: {response.status_code}"

    return resultados


def pegar_upas_proxima(api_key, lat_user, lon_user):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.nome, e.rua, e.numero, e.bairro, e.cidade, e.estado, e.cep, e.latitude, e.longitude
        FROM upa u
        JOIN endereco e ON u.fk_endereco = e.id_endereco
    """)
    upas = cursor.fetchall()
    cursor.close()

    for upa in upas:
        if upa["latitude"] is not None and upa["longitude"] is not None:
            upa["distancia_km"] = haversine(lat_user, lon_user, float(upa["latitude"]), float(upa["longitude"]))
        else:
            upa["distancia_km"] = float("inf")

    return sorted(upas, key=lambda x: x["distancia_km"])[:3]


def calcular_info_upa(upa, lat_origem, long_origem, api_key):
    destino_endereco = f"{upa['rua']}, {upa['numero']}, {upa['bairro']}, {upa['cidade']}, {upa['cep']}"
    rotas = calcular_rotas(lat_origem, long_origem, destino_endereco, api_key)    
    
    json_enderecos_upa = {
        "nome": upa["nome"],
        "endereco": destino_endereco,
        "latitude": upa['latitude'],
        "longitude": upa['longitude']
    }
    
    return {
        "nome": upa["nome"],
        #"endereco": destino_endereco,
        #"distancia": f"{upa['distancia_km']:.2f} km",
        "rotas": rotas,
        #"linkMaps": link_maps,
        #"linkImagem": "https://maps.gstatic.com/tactile/pane/default_geocode-2x.png"
    }


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ============ ROTA API ============
@app.route('/api/upa', methods=['POST'])
def recomendar_upa():
    data = request.get_json()
    endereco = data.get('endereco')  # Espera-se: string completa do endereço

    if not endereco:
        return jsonify({"erro": "Endereço não fornecido."}), 400

    lat_user, lon_user = pegar_coordenadas(endereco, API_KEY)
    if lat_user is None or lon_user is None:
        return jsonify({"erro": "Erro ao obter coordenadas do endereço informado."}), 500

    upas = pegar_upas_proxima(API_KEY, lat_user, lon_user)

    resultado_para_dijkstra = {"upas_proximas": []}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(calcular_info_upa, upa, lat_user, lon_user, API_KEY) for upa in upas]
        for future in as_completed(futures):
            resultado_para_dijkstra["upas_proximas"].append(future.result())


    json_dijkstra = resultado_para_dijkstra  # Isso é um dicionário, não um objeto Flask Response
    response_dijkstra = requests.post('http://localhost:8080/menor-caminho', json=json_dijkstra)

    
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    dados_dijkstra = response_dijkstra.json()
    nome_upa_retorno_api = dados_dijkstra['nome']
    destino_upa = json_enderecos_upa.get(nome_upa_retorno_api)
    print("DESTINO_UPA: ", destino_upa)
    
    origem = endereco
    dados = destino_upa.json()
    destino = dados['endereco']
    modo = dados_dijkstra["rotas"]["modo"]
    params = {
        "origin": origem,
        "destination": destino,
        "mode": modo,  # Pode ser walking, transit, bicycling
        "key": API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        polyline = data['routes'][0]['overview_polyline']['points']
        print("Encoded polyline:")
        print(polyline)
    else:
        print("Erro:", data['status'], data.get('error_message'))
    
    linkImagem = f"https://maps.googleapis.com/maps/api/staticmap?size=600x400&path=enc:{polyline}&key={API_KEY}"
    print(linkImagem)
    
    print("\n\n\n\n")
    
    link_maps = gerar_link_maps(lat_user, lon_user, destino_upa["latitude"], destino_upa["longitude"], response_dijkstra['modo'])
    print(link_maps)


    return response_dijkstra


# ============ EXECUTAR APP ============
if __name__ == "__main__":
    app.run(debug=True)
