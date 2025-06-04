import time
import json
import re
import nltk
import Levenshtein
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# pacotes p tonkenização e stop words (a, o, os, as, e, para, com..)
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
    tokens = word_tokenize(texto.lower(), language="portuguese")
    return [re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) for t in tokens if re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) not in stop_words]

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
        texto = re.sub(rf"\\b({re.escape(palavra)})\\b", r">>>\1<<<", texto, flags=re.IGNORECASE)
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
        tokens_lexicos = analisar_lexico(tweet)
        encontrados, sentimentos, lex_nao_reconhecidos = [], [], []

        for tipo, lista in [
            ("palavra_saude", palavras_saude),
            ("nome_upa", nomes_upa),
            ("sentimento_positivo", sentimentos_positivos),
            ("sentimento_negativo", sentimentos_negativos),
            ("palavrao", palavroes)
        ]:
            palavras = extrair_palavras(tweet, lista)
            for p in palavras:
                encontrados.append({"palavra": p, "tipo": tipo})
                if "sentimento" in tipo:
                    sentimentos.append({"palavra": p, "tipo": tipo})

        detectadas_set = {e["palavra"] for e in encontrados}
        for token in tokens_lexicos:
            if token not in detectadas_set:
                lex_nao_reconhecidos.append(token)

        texto_destaque = destacar_palavras(tweet, detectadas_set)
        sentimento_geral = calcular_sentimento_geral(encontrados)

        dados_resultado["tweets_filtrados"].append({
            "tweet_original": tweet,
            "tweet_destaque": texto_destaque,
            "palavras_detectadas": encontrados,
            "tokens_lexicais": tokens_lexicos,
            "lexemas_nao_reconhecidos": lex_nao_reconhecidos,
            "sentimento_geral": sentimento_geral
        })

        dados_sentimentos["sentimentos_detectados"].append({
            "sentimentos_detectados": sentimentos
        })

    return dados_resultado, dados_sentimentos

# ===================== COLETA =====================
def coletar_tweets(driver, search_queries, max_scrolls=30):
    tweets_coletados = set()
    for query in search_queries:
        url = f"https://twitter.com/search?q={query}&src=typed_query&lang=pt"
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
            print(f"\n✅ Página carregada para busca: {query}")
        except:
            print(f"\n❌ Nenhum tweet visível encontrado para: {query}")
            continue

        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            tweets = driver.find_elements(By.XPATH, '//div[@lang="pt"]')
            for t in tweets:
                txt = t.text.strip()
                tweets_coletados.add(txt)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1
    print(f"\n✅ Total de tweets coletados: {len(tweets_coletados)}")
    return tweets_coletados
    
# ===================== LOGIN =====================
def login_twitter(driver, email, senha, username):
    wait = WebDriverWait(driver, 10)
    driver.get("https://twitter.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(email + Keys.RETURN)
        try:
            wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(username + Keys.RETURN)
        except:
            pass
        wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(senha + Keys.RETURN)
        wait.until(EC.presence_of_element_located((By.XPATH, '//a[@data-testid="AppTabBar_Home_Link"]')))
        print("\n✅ Login bem-sucedido!")
    except Exception as e:
        print(f"\n❌ Erro no login: {e}")
        driver.quit()
        exit()
    
# ===================== PRINCIPAL =====================
def main():
    email = "connectupa@gmail.com"
    senha = "UpaConnectTwitter"
    username = "UpaConnect_"
    search_query = ["UPA", "UPA Frio", "UPA Calor", "UPA Fila"]

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)

    login_twitter(driver, email, senha, username)
    tweets = coletar_tweets(driver, search_query)

    try:
        with open("dicionario_dados.json", "r", encoding="utf-8") as f:
            filtros = json.load(f)
    except Exception as e:
        print(f"\n❌ Erro carregando dicionário: {e}")
        driver.quit()
        return

    dados_resultado, dados_sentimentos = processar_tweets(tweets, filtros)

    # salvar resultados em um arquivo JSON
    output_filename = "tweets_filtrados.json"
    print(f"Salvando resultados em '{output_filename}'...")
    output_filename_sentimentos = "sentimentos_detectados.json"
    print(f"Salvando sentimentos detectados em '{output_filename_sentimentos}'...")

    json_conteudo = json.dumps(dados_resultado, ensure_ascii=False, indent=2)
    json_sentimentos = json.dumps(dados_sentimentos, ensure_ascii=False, indent=2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(json_conteudo)

    print(f"\n✅ Tweets filtrados e tokens lexicais salvos em '{output_filename}'")

    with open(output_filename_sentimentos, "w", encoding="utf-8") as f:
        f.write(json_sentimentos)

    print(f"✅ Sentimentos detectados salvos em '{output_filename_sentimentos}'")

    s3 = boto3.client('s3')
    try:
        s3.put_object(
            Bucket='bucket-raw-upa-connect',
            Key='sentimentos_encontrados.json',
            Body=json_sentimentos.encode('utf-8'),
            ContentType='application/json'
        )
        print("✅ Arquivo enviado para o S3 com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar para o S3: {e}")

    print("\n✅ Arquivos salvos com sucesso!")
    driver.quit()
    
if __name__ == "__main__":
    main()