from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import nltk
import Levenshtein
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')

email = "connectupa@gmail.com"
senha = "UpaConnectTwitter"
username = "UpaConnect_"

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 5)

driver.get("https://twitter.com/login")

try:
    wait.until(EC.presence_of_element_located((By.NAME, "text")))
    input_email = driver.find_element(By.NAME, "text")
    input_email.send_keys(email)
    input_email.send_keys(Keys.RETURN)
    time.sleep(2)

    try:
        wait.until(EC.presence_of_element_located((By.NAME, "text")))
        username_input = driver.find_element(By.NAME, "text")
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        time.sleep(2)
    except:
        pass

    wait.until(EC.presence_of_element_located((By.NAME, "password")))
    input_senha = driver.find_element(By.NAME, "password")
    input_senha.send_keys(senha)
    input_senha.send_keys(Keys.RETURN)
    time.sleep(5)

except Exception as e:
    print("❌ Erro durante o login:", e)
    driver.quit()
    exit()

driver.get("https://twitter.com/search?q=UPA&src=typed_query")
try:
    wait.until(EC.presence_of_element_located((By.XPATH, '//article')))
    print("✅ Tweets carregados!")
except:
    print("❌ Nenhum tweet visível foi encontrado.")
    driver.quit()
    exit()

time.sleep(5)

last_height = driver.execute_script("return document.body.scrollHeight")
tweets_coletados = set()
scrolls = 0
max_scrolls = 30

while scrolls < max_scrolls:
    tweets = driver.find_elements(By.XPATH, '//div[@lang="pt"]')
    for t in tweets:
        txt = t.text.strip()
        if "upa" in txt.lower():
            tweets_coletados.add(txt)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    scrolls += 1

try:
    with open("dicionario_dados.json", "r", encoding="utf-8") as f:
        filtros = json.load(f)

    palavras_saude = [p.lower() for p in filtros.get("palavras_saude", [])]
    nomes_upa = [n.lower() for n in filtros.get("nomes_upa", [])]
    sentimentos_positivos = [s.lower() for s in filtros.get("sentimentos_positivos", [])]
    sentimentos_negativos = [s.lower() for s in filtros.get("sentimentos_negativos", [])]
    palavroes = [p.lower() for p in filtros.get("palavroes", [])]

except Exception as e:
    print("❌ Erro ao carregar filtros JSON:", e)
    driver.quit()
    exit()

stop_words = set(stopwords.words("portuguese"))

def analisar_lexico(texto):
    tokens = word_tokenize(texto.lower(), language="portuguese")
    return [t for t in tokens if t.isalpha() and t not in stop_words]

def extrair_palavras(texto, lista, threshold=0.8):
    texto_lower = texto.lower()
    tokens = word_tokenize(texto_lower, language="portuguese")
    encontrados = set()

    for palavra_lista in lista:
        for token in tokens:
            if token == palavra_lista:
                encontrados.add(palavra_lista)
            else:
                distancia = Levenshtein.distance(token, palavra_lista)
                similaridade = 1 - distancia / max(len(token), len(palavra_lista))
                if similaridade >= threshold:
                    encontrados.add(palavra_lista)
    return list(encontrados)

def destacar_palavras(texto, palavras):
    for palavra in palavras:
        texto = re.sub(rf"\b({re.escape(palavra)})\b", r">>>\1<<<", texto, flags=re.IGNORECASE)
    return texto

dados_resultado = {
    "tweets_filtrados": []
}

for tweet in tweets_coletados:
    tokens_lexicos = analisar_lexico(tweet)

    encontrados = []

    ps = extrair_palavras(tweet, palavras_saude)
    for p in ps:
        encontrados.append({"palavra": p, "tipo": "palavra_saude"})

    nu = extrair_palavras(tweet, nomes_upa)
    for n in nu:
        encontrados.append({"palavra": n, "tipo": "nome_upa"})

    sp = extrair_palavras(tweet, sentimentos_positivos)
    for s in sp:
        encontrados.append({"palavra": s, "tipo": "sentimento_positivo"})

    sn = extrair_palavras(tweet, sentimentos_negativos)
    for s in sn:
        encontrados.append({"palavra": s, "tipo": "sentimento_negativo"})

    pl = extrair_palavras(tweet, palavroes)
    for p in pl:
        encontrados.append({"palavra": p, "tipo": "palavrao"})

    palavras_para_destacar = list({e["palavra"] for e in encontrados})

    texto_destaque = destacar_palavras(tweet, palavras_para_destacar)

    dados_resultado["tweets_filtrados"].append({
        "tweet_original": tweet,
        "tweet_destaque": texto_destaque,
        "palavras_detectadas": encontrados,
        "tokens_lexicais": tokens_lexicos
    })

with open("tweets_filtrados.json", "w", encoding="utf-8") as f:
    json.dump(dados_resultado, f, ensure_ascii=False, indent=2)

print("\n✅ Tweets filtrados e tokens lexicais salvos em 'tweets_filtrados.json'")

driver.quit()

#Fazer as devidas correções no código
#Fazer o filtro de sentimentos com levenshtein
#Fazer Lexema dos tokens léxicos
#Gerar o json com os tweets filtrados
#Enviar(fazer requisição) o json para a AWS S3 RAW
