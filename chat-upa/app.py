from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isso libera o CORS para todas as rotas

@app.route('/api/upa', methods=['POST'])
def recomendar_upa():
    # Simulando a obtenção de dados do usuário
    data = request.get_json()
    # Capturando dados recebidos
    # cep = data.get('cep')
    # numero = data.get('numero')

    # Aqui você pode processar os dados recebidos e fazer a lógica de recomendação
    #
    cep = "03277-000"  # Exemplo de CEP
    numero = "1234" # Exemplo de número

    # Simulando uma resposta
    resposta = {
        "nome": "UPA Central",
        "endereco": f"Rua das UPAs, nº {numero} - CEP {cep}",
        "distancia": "2.5 km",
        "transporte": "Carro",
        "tempo": "8 min",
        "linkImagem": "https://maps.gstatic.com/tactile/pane/default_geocode-2x.png",
        "linkMaps": "https://www.google.com/maps"
    }

    return jsonify(resposta)

if __name__ == "__main__":
    app.run(debug=True)


# Instruções para executar o código:
# 1. Instale as dependências necessárias:
# pip install flask
# pip install flask-cors
# 2. Rode o seguinte codigo dentro da pasta chat-upa no terminal.
# python app.py