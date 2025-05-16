from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta, timezone
import mysql.connector
import math
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============ CONFIGURAÇÕES ============
API_KEY = "AIzaSyA7ikFFKe-48bj_4LTwn-27FWQjSgqhdnE"

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

    # print("=====================================================")
    # print(json.dumps(upas, indent=4))
    # print("=====================================================")

    return sorted(upas, key=lambda x: x["distancia_km"])[:3]


def calcular_info_upa(upa, lat_origem, long_origem, api_key):
    global json_enderecos_upa

    destino_endereco = f"{upa['rua']}, {upa['numero']}, {upa['bairro']}, {upa['cidade']}, {upa['cep']}"
    rotas = calcular_rotas(lat_origem, long_origem, destino_endereco, api_key)

    json_enderecos_upa[upa["nome"]] = {
        "endereco": destino_endereco,
        "latitude": upa['latitude'],
        "longitude": upa['longitude']
    }

    return {
        "nome": upa["nome"],
        "rotas": rotas
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


def obter_endereco_completo(cep, numero, api_key):
    endereco_busca = f"{cep}, {numero}, Brasil"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_busca}&key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            resultado = data['results'][0]
            endereco_formatado = resultado['formatted_address']
            return endereco_formatado
        else:
            print("Nenhum resultado encontrado.")
    else:
        print("Erro na requisição:", response.status_code)

    return None

# ============ ROTA API ============
@app.route('/api/upa', methods=['POST'])
def recomendar_upa():
    global json_enderecos_upa
    json_enderecos_upa = {}

    data = request.get_json()
    cep = data.get('cep')
    numero = data.get('numero')

    endereco = obter_endereco_completo(cep, numero, API_KEY)
    
    lat_user, lon_user = pegar_coordenadas(endereco, API_KEY)
    if lat_user is None or lon_user is None:
        return jsonify({"erro": "Erro ao obter coordenadas do endereço informado."}), 500

    upas = pegar_upas_proxima(API_KEY, lat_user, lon_user)

    resultado_para_dijkstra = {"upas_proximas": []}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(calcular_info_upa, upa, lat_user, lon_user, API_KEY) for upa in upas]
        for future in as_completed(futures):
            resultado_para_dijkstra["upas_proximas"].append(future.result())

    print("=====================================================")
    print(json.dumps(resultado_para_dijkstra, indent=4))
    print("=====================================================")

    response_dijkstra = requests.get('http://localhost:8081/grafos/melhor-caminho', json=resultado_para_dijkstra)
    dados_dijkstra = response_dijkstra.json()

    print("=====================================================")
    print(json.dumps(dados_dijkstra, indent=4))
    print("=====================================================")

    nome_upa_retorno_api = dados_dijkstra['nome']
    destino_upa = json_enderecos_upa.get(nome_upa_retorno_api)

    if not destino_upa:
        return jsonify({"erro": f"UPA '{nome_upa_retorno_api}' não encontrada nos endereços."}), 500

    origem = endereco
    destino = destino_upa['endereco']
    modo = dados_dijkstra["rotas"]["modo"]

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origem,
        "destination": destino,
        "mode": modo,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        polyline = data['routes'][0]['overview_polyline']['points']
        linkImagem = f"https://maps.googleapis.com/maps/api/staticmap?size=600x400&path=enc:{polyline}&key={API_KEY}"
    else:
        linkImagem = None

    link_maps = gerar_link_maps(lat_user, lon_user, destino_upa["latitude"], destino_upa["longitude"], modo)

    # ===== PEGAR DISTÂNCIA ASSOCIADA =====
    distancia_upa = None
    for upa in resultado_para_dijkstra["upas_proximas"]:
        if upa["nome"] == nome_upa_retorno_api:
            rotas = upa.get("rotas", {})
            info_modo = rotas.get(modo)
            if info_modo:
                distancia_upa = info_modo.get("Distância")
            break

    return jsonify({
        "upa_recomendada": dados_dijkstra,
        "destino": destino,
        "linkImagem": linkImagem,
        "linkMaps": link_maps,
        "distancia": distancia_upa
    })


# ============ EXECUTAR APP ============
if __name__ == "__main__":
    app.run(debug=True)
