import time
import json
import re
import nltk
import Levenshtein
import boto3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Pacotes para tokenização e stop words (a, o, os, as, e, para, com..)
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')
    
stop_words = set(stopwords.words("portuguese"))

# ===================== ANÁLISE =====================
def analisar_lexico(texto):
    """
    Analisa o texto para extrair tokens lexicais, removendo pontuações,
    convertendo para minúsculas e filtrando stop words.
    """
    tokens = word_tokenize(texto.lower(), language="portuguese")
    # Remove caracteres não alfabéticos e filtra stop words
    return [re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) for t in tokens if re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) not in stop_words]

def extrair_palavras(texto, lista, threshold=0.8):
    """
    Extrai palavras do texto que correspondem ou são similares às palavras em uma lista,
    utilizando a distância de Levenshtein para similaridade.
    """
    tokens = analisar_lexico(texto)
    encontrados = set()
    for palavra_lista in lista:
        for token in tokens:
            if token == palavra_lista:
                encontrados.add(palavra_lista)
            else:
                # Calcula a distância de Levenshtein e a similaridade
                distancia = Levenshtein.distance(token, palavra_lista)
                similaridade = 1 - (distancia / max(len(token), len(palavra_lista), 1))
                if similaridade >= threshold:
                    encontrados.add(palavra_lista)
    return list(encontrados)

def destacar_palavras(texto, palavras):
    """
    Destaca palavras no texto original adicionando '>>>' e '<<<' ao redor delas.
    """
    for palavra in palavras:
        # Usa regex para substituir as palavras no texto, ignorando maiúsculas/minúsculas
        texto = re.sub(rf"\b({re.escape(palavra)})\b", r">>>\1<<<", texto, flags=re.IGNORECASE)
    return texto

def calcular_sentimento_geral(palavras_detectadas):
    """
    Calcula o sentimento geral (Positivo, Negativo ou Neutro) com base
    nas palavras de sentimento detectadas.
    """
    positivo = sum(1 for p in palavras_detectadas if p['tipo'] == 'sentimento_positivo')
    negativo = sum(1 for p in palavras_detectadas if p['tipo'] == 'sentimento_negativo')
    if positivo > negativo:
        return "Positivo"
    elif negativo > positivo:
        return "Negativo"
    return "Neutro"

# ===================== PROCESSAMENTO =====================
def processar_tweets(tweets, filtros):
    """
    Processa uma lista de tweets, aplicando filtros e detectando sentimentos.
    Retorna dois dicionários: um com os tweets filtrados e outro com os sentimentos detectados.
    """
    dados_resultado = {"tweets_filtrados": []}
    dados_sentimentos = {"sentimentos_detectados": []} # Lista principal para sentimentos detectados

    # Carrega as listas de palavras dos filtros
    palavras_saude = [p.lower() for p in filtros.get("palavras_saude", [])]
    nomes_upa = [n.lower() for n in filtros.get("nomes_upa", [])]
    sentimentos_positivos = [s.lower() for s in filtros.get("sentimentos_positivos", [])]
    sentimentos_negativos = [s.lower() for s in filtros.get("sentimentos_negativos", [])]
    palavroes = [p.lower() for p in filtros.get("palavroes", [])]

    for tweet in tweets:
        tokens_lexicos = analisar_lexico(tweet)
        encontrados_no_tweet, sentimentos_no_tweet, lex_nao_reconhecidos = [], [], []

        # Itera sobre os tipos de palavras e suas listas correspondentes
        for tipo, lista in [
            ("palavra_saude", palavras_saude),
            ("nome_upa", nomes_upa),
            ("sentimento_positivo", sentimentos_positivos),
            ("sentimento_negativo", sentimentos_negativos),
            ("palavrao", palavroes)
        ]:
            palavras = extrair_palavras(tweet, lista)
            for p in palavras:
                # Adiciona palavra detectada à lista geral de encontrados no tweet
                encontrados_no_tweet.append({"palavra": p, "tipo": tipo})
                # Se for uma palavra de sentimento, adiciona à lista de sentimentos para este tweet
                if "sentimento" in tipo:
                    sentimentos_no_tweet.append({"palavra": p, "tipo": tipo})

        # Identifica lexemas não reconhecidos
        detectadas_set = {e["palavra"] for e in encontrados_no_tweet}
        for token in tokens_lexicos:
            if token not in detectadas_set:
                lex_nao_reconhecidos.append(token)

        # Destaca palavras no tweet original e calcula o sentimento geral
        texto_destaque = destacar_palavras(tweet, detectadas_set)
        sentimento_geral = calcular_sentimento_geral(encontrados_no_tweet)

        # Adiciona os dados processados deste tweet aos resultados
        dados_resultado["tweets_filtrados"].append({
            "tweet_original": tweet,
            "tweet_destaque": texto_destaque,
            "palavras_detectadas": encontrados_no_tweet,
            "tokens_lexicais": tokens_lexicos,
            "lexemas_nao_reconhecidos": lex_nao_reconhecidos,
            "sentimento_geral": sentimento_geral
        })
        
        # Adiciona os sentimentos detectados neste tweet à lista principal de sentimentos
        dados_sentimentos["sentimentos_detectados"].extend(sentimentos_no_tweet)

    return dados_resultado, dados_sentimentos

# ===================== COLETA =====================
def coletar_tweets(driver, search_queries, max_scrolls=30):
    """
    Coleta tweets do Twitter usando Selenium.
    Navega para cada consulta de busca e rola a página para coletar mais tweets.
    """
    tweets_coletados = set()
    for query in search_queries:
        url = f"https://twitter.com/search?q={query}&src=typed_query&lang=pt"
        driver.get(url)
        try:
            # Espera até que os elementos de tweet sejam visíveis
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
            print(f"\n✅ Página carregada para busca: {query}")
        except:
            print(f"\n❌ Nenhum tweet visível encontrado para: {query}")
            continue

        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            # Encontra todos os elementos de tweet com linguagem portuguesa
            tweets = driver.find_elements(By.XPATH, '//div[@lang="pt"]')
            for t in tweets:
                txt = t.text.strip()
                tweets_coletados.add(txt)
            # Rola a página para baixo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Espera o conteúdo carregar
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: # Se não houver mais conteúdo para carregar
                break
            last_height = new_height
            scrolls += 1
    print(f"\n✅ Total de tweets coletados: {len(tweets_coletados)}")
    return tweets_coletados
    
# ===================== LOGIN =====================
def login_twitter(driver, email, senha, username):
    """
    Realiza o login no Twitter usando as credenciais fornecidas.
    """
    wait = WebDriverWait(driver, 10)
    driver.get("https://twitter.com/login")
    try:
        # Preenche o email e avança
        wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(email + Keys.RETURN)
        try:
            # Tenta preencher o username, caso seja solicitado
            wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(username + Keys.RETURN)
        except:
            pass # Continua se o username não for solicitado
        # Preenche a senha e submete
        wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(senha + Keys.RETURN)
        # Espera até que o link da página inicial apareça, indicando login bem-sucedido
        wait.until(EC.presence_of_element_located((By.XPATH, '//a[@data-testid="AppTabBar_Home_Link"]')))
        print("\n✅ Login bem-sucedido!")
    except Exception as e:
        print(f"\n❌ Erro no login: {e}")
        driver.quit()
        exit()
        
# ===================== PRINCIPAL =====================
def main():
    """
    Função principal que orquestra a coleta, processamento e salvamento dos tweets.
    """
    # Credenciais do Twitter e consultas de busca
    email = "connectupa@gmail.com"
    senha = "UpaConnectTwitter"
    username = "UpaConnect_"
    search_query = ["UPA", "UPA Frio", "UPA Calor", "UPA Fila", "UPA Demora", "UPA Remédio"]

    # Configurações do Chrome WebDriver
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)

    # Realiza o login no Twitter
    login_twitter(driver, email, senha, username)
    # Coleta os tweets
    tweets = coletar_tweets(driver, search_query)

    # Carrega o dicionário de filtros
    try:
        with open("dicionario_dados.json", "r", encoding="utf-8") as f:
            filtros = json.load(f)
    except Exception as e:
        print(f"\n❌ Erro carregando dicionário: {e}")
        driver.quit()
        return

    # Processa os tweets coletados
    dados_resultado, dados_sentimentos = processar_tweets(list(tweets), filtros)

    # Salva os resultados dos tweets filtrados em um arquivo JSON
    output_filename = "tweets_filtrados.json"
    print(f"Salvando resultados em '{output_filename}'...")
    json_conteudo = json.dumps(dados_resultado, ensure_ascii=False, indent=2)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(json_conteudo)
    print(f"\n✅ Tweets filtrados e tokens lexicais salvos em '{output_filename}'")

    # Salva os sentimentos detectados em um arquivo JSON
    output_filename_sentimentos = "sentimentos_detectados.json"
    print(f"Salvando sentimentos detectados em '{output_filename_sentimentos}'...")
    json_sentimentos = json.dumps(dados_sentimentos, ensure_ascii=False, indent=2)
    with open(output_filename_sentimentos, "w", encoding="utf-8") as f:
        f.write(json_sentimentos)
    print(f"✅ Sentimentos detectados salvos em '{output_filename_sentimentos}'")
    
    # Converte os sentimentos detectados para um DataFrame e salva como CSV
    try:
        # Acessa a lista de sentimentos diretamente para criar o DataFrame
        data_list = json.loads(json_sentimentos)["sentimentos_detectados"] 
        # Garante que data_list é uma lista de dicionários
        if not isinstance(data_list, list):
            print("❌ Erro: 'sentimentos_detectados' não é uma lista no JSON.")
            data_list = []
    except json.JSONDecodeError as e:
        print(f"❌ Erro decodificando JSON: {e}")
        data_list = [] # Garante que data_list seja uma lista vazia em caso de erro
            
    df_sentimentos = pd.DataFrame(data_list)
    df_sentimentos.to_csv('sentimentos_encontrados.csv', index=False, encoding='utf-8')
    print("CSV saved successfully!")

    # Envia o arquivo CSV para o S3
    s3 = boto3.client('s3')
    try:
        with open('sentimentos_encontrados.csv', 'rb') as f: # 'rb' para ler em modo binário
            csv_content = f.read()
        
        s3.put_object(
            Bucket='bucket-raw-upa-connect',
            Key='sentimentos_encontrados.csv', # Nome da chave no S3 para o CSV
            Body=csv_content, # O conteúdo do arquivo CSV
            ContentType='text/csv' # Tipo de conteúdo para arquivos CSV
        )
        print("✅ Arquivo enviado para o S3 com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar para o S3: {e}")

    print("\n✅ Arquivos salvos com sucesso!")
    driver.quit()
    
if __name__ == "__main__":
    main()
