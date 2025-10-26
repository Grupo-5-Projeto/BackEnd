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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ===================== TOKENIZAÇÃO / STOPWORDS =====================
try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except Exception:
    nltk.download('stopwords')

stop_words = set(stopwords.words("portuguese"))

# ===================== ANÁLISE LÉXICA =====================
def analisar_lexico(texto):
    tokens = word_tokenize(texto.lower(), language="portuguese")
    return [
        re.sub(r'[^a-záàãâéêíóôõúüç]', '', t)
        for t in tokens
        if re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) not in stop_words and re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) != ''
    ]

def extrair_palavras(texto, lista, threshold=0.8):
    tokens = analisar_lexico(texto)
    encontrados = set()
    for palavra_lista in lista:
        for token in tokens:
            if token == palavra_lista:
                encontrados.add(palavra_lista)
            else:
                distancia = Levenshtein.distance(token, palavra_lista)
                similaridade = 1 - (distancia / max(len(token), len(palavra_lista), 1))
                if similaridade >= threshold:
                    encontrados.add(palavra_lista)
    return list(encontrados)

def destacar_palavras(texto, palavras):
    for palavra in palavras:
        texto = re.sub(rf"\b({re.escape(palavra)})\b", r">>>\1<<<", texto, flags=re.IGNORECASE)
    return texto

def calcular_sentimento_geral(palavras_detectadas):
    positivo = sum(1 for p in palavras_detectadas if p['tipo'] == 'sentimento_positivo')
    negativo = sum(1 for p in palavras_detectadas if p['tipo'] == 'sentimento_negativo')
    if positivo > negativo:
        return "Positivo"
    elif negativo > positivo:
        return "Negativo"
    return "Neutro"

# ===================== PROCESSAMENTO =====================
def processar_tweets(tweets, filtros):
    dados_resultado = {"tweets_filtrados": []}
    dados_sentimentos = {"sentimentos_detectados": []}

    palavras_saude = [p.lower() for p in filtros.get("palavras_saude", [])]
    nomes_upa = [n.lower() for n in filtros.get("nomes_upa", [])]
    sentimentos_positivos = [s.lower() for s in filtros.get("sentimentos_positivos", [])]
    sentimentos_negativos = [s.lower() for s in filtros.get("sentimentos_negativos", [])]
    palavroes = [p.lower() for p in filtros.get("palavroes", [])]

    for tweet in tweets:
        texto = tweet["texto"]
        data_pub = tweet["data"]
        tokens_lexicos = analisar_lexico(texto)
        encontrados_no_tweet, sentimentos_no_tweet, lex_nao_reconhecidos = [], [], []

        for tipo, lista in [
            ("palavra_saude", palavras_saude),
            ("nome_upa", nomes_upa),
            ("sentimento_positivo", sentimentos_positivos),
            ("sentimento_negativo", sentimentos_negativos),
            ("palavrao", palavroes)
        ]:
            palavras = extrair_palavras(texto, lista)
            for p in palavras:
                encontrados_no_tweet.append({"palavra": p, "tipo": tipo})
                if "sentimento" in tipo:
                    sentimentos_no_tweet.append({"palavra": p, "tipo": tipo, "dataPublicacao": data_pub})

        detectadas_set = {e["palavra"] for e in encontrados_no_tweet}
        for token in tokens_lexicos:
            if token not in detectadas_set:
                lex_nao_reconhecidos.append(token)

        texto_destaque = destacar_palavras(texto, detectadas_set)
        sentimento_geral = calcular_sentimento_geral(encontrados_no_tweet)

        dados_resultado["tweets_filtrados"].append({
            "tweet_original": texto,
            "tweet_destaque": texto_destaque,
            "palavras_detectadas": encontrados_no_tweet,
            "tokens_lexicais": tokens_lexicos,
            "lexemas_nao_reconhecidos": lex_nao_reconhecidos,
            "sentimento_geral": sentimento_geral,
            "dataPublicacao": data_pub
        })
        dados_sentimentos["sentimentos_detectados"].extend(sentimentos_no_tweet)

    return dados_resultado, dados_sentimentos

# ===================== COLETA =====================
def coletar_tweets(driver, search_queries, max_scrolls=30):
    tweets_coletados = set()
    tweets_detalhados = []

    for query in search_queries:
        url = f"https://twitter.com/search?q={query}&src=typed_query&f=live&lang=pt-br"
        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
            print(f"\n✅ Página carregada para busca: {query}")
        except Exception:
            print(f"\n❌ Nenhum tweet visível encontrado para: {query}")
            continue

        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            for t in tweets:
                try:
                    texto = t.find_element(By.XPATH, './/div[@lang]').text.strip()
                    data_element = t.find_element(By.XPATH, './/time')
                    data_publicacao = data_element.get_attribute("datetime")
                    if texto and texto not in tweets_coletados:
                        tweets_coletados.add(texto)
                        tweets_detalhados.append({"texto": texto, "data": data_publicacao})
                except Exception:
                    pass
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1
    print(f"\n✅ Total de tweets coletados: {len(tweets_detalhados)}")
    return tweets_detalhados

# ===================== LOGIN VIA COOKIES =====================
def carregar_cookies(driver, path="cookies_twitter.json"):
    driver.get("https://twitter.com")
    try:
        with open(path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        for cookie in cookies:
            cookie_to_add = {k: v for k, v in cookie.items() if k not in ("hostOnly", "storeId", "id", "session")}
            if 'sameSite' in cookie_to_add:
                s = cookie_to_add['sameSite']
                if s is None:
                    cookie_to_add['sameSite'] = 'Lax'
                elif s.lower() in ("no_restriction", "unspecified"):
                    cookie_to_add['sameSite'] = 'Lax'
            try:
                driver.add_cookie(cookie_to_add)
            except Exception:
                pass
        driver.refresh()
        print("✅ Cookies carregados — sessão reutilizada.")
    except Exception as e:
        print(f"❌ Erro ao carregar cookies: {e}")

# ===================== FUNÇÃO PRINCIPAL =====================
def main():
    search_query = ["UPA", "UPA Frio", "UPA Calor", "UPA Fila", "UPA Demora", "UPA Remédio"]

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("✅ ChromeDriver iniciado.")
    carregar_cookies(driver)
    time.sleep(3)

    tweets = coletar_tweets(driver, search_query)

    try:
        with open("dicionario_dados.json", "r", encoding="utf-8") as f:
            filtros = json.load(f)
    except Exception as e:
        print(f"\n❌ Erro carregando dicionário: {e}")
        filtros = {}

    dados_resultado, dados_sentimentos = processar_tweets(tweets, filtros)

    try:
        df_sentimentos = pd.DataFrame(dados_sentimentos.get("sentimentos_detectados", []))
        df_sentimentos.to_csv('sentimentos_encontrados.csv', index=False, encoding='utf-8')
        print("✅ CSV gerado com data da publicação: 'sentimentos_encontrados.csv'")
    except Exception as e:
        print(f"❌ Erro gerando CSV: {e}")

    s3 = boto3.client('s3')
    try:
        with open('sentimentos_encontrados.csv', 'rb') as f:
            s3.put_object(
                Bucket='bucket-raw-upa-connect-mateus',
                Key='sentimentos_encontrados.csv',
                Body=f.read(),
                ContentType='text/csv'
            )
        print("✅ Arquivo enviado ao S3 com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar para o S3: {e}")

    driver.quit()
    print("\n✅ Execução concluída com sucesso.")

if __name__ == "__main__":
    main()
