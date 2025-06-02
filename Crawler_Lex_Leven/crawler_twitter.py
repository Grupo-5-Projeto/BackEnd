import time
import json
import re
import nltk
import Levenshtein
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

# configs de acesso e busca - Twitter
email = "connectupa@gmail.com"
senha = "UpaConnectTwitter"
username = "UpaConnect_"
search_query = "UPA" # The term to search on Twitter

# inicializa o chrome com essas opções
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10) # tmp de espera p elementos carregarem

# --- login Twitter ---
print("Entrando na página de login do Twitter")
driver.get("https://twitter.com/login")

try:
    # email
    email_input_locator = (By.NAME, "text")
    wait.until(EC.presence_of_element_located(email_input_locator))
    input_email = driver.find_element(*email_input_locator)
    input_email.send_keys(email)
    input_email.send_keys(Keys.RETURN)

    try:
        # username 
        username_input_locator = (By.NAME, "text")
        wait.until(EC.presence_of_element_located(username_input_locator))
        username_input = driver.find_element(*username_input_locator)
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        # senha
        password_input_locator = (By.NAME, "password")
        wait.until(EC.presence_of_element_located(password_input_locator))
    except Exception:
        password_input_locator = (By.NAME, "password")
        wait.until(EC.presence_of_element_located(password_input_locator))

    # enter na senha
    input_senha = driver.find_element(*password_input_locator)
    input_senha.send_keys(senha)
    input_senha.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.XPATH, '//a[@data-testid="AppTabBar_Home_Link"] | //input[@data-testid="SearchBox_Search_Input"]')))
    print("✅ Login bem-sucedido!")

except Exception as e:
    print(f"❌ Erro durante o login: {e}")
    driver.quit()
    exit()

# navegar para a página de busca
print(f"Navegando para a página de busca para '{search_query}'...")
driver.get(f"https://twitter.com/search?q={search_query}&src=typed_query")

try:
    # esperar o primeiro tweet estar visível na página
    wait.until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
    print("✅ Tweets carregados na página de busca!")
except Exception as e:
    print(f"❌ Nenhum tweet visível foi encontrado na página de busca: {e}")
    driver.quit()
    exit()

time.sleep(3)

# coleta tweets de 30 scrolls
print("Começando a coleta de tweets...")
last_height = driver.execute_script("return document.body.scrollHeight")
tweets_coletados = set()
scrolls = 0
max_scrolls = 30 

while scrolls < max_scrolls:
    # achar tweets que estão em português
    tweets = driver.find_elements(By.XPATH, '//div[@lang="pt"]')
    for t in tweets:
        txt = t.text.strip()
        if search_query.lower() in txt.lower():
            tweets_coletados.add(txt)

    # scroll
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3) 

    # cálculo do tamanho do novo scroll
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        print("Final do scroll.")
        break
    last_height = new_height
    scrolls += 1
    print(f"Scroll {scrolls}/{max_scrolls} completo. Foram coletados {len(tweets_coletados)} tweets.")

print(f"Término da coleta. Total de tweets coletados: {len(tweets_coletados)}")

# carregar dicionario de dados
print("Carregando dicionário de dados...")
try:
    with open("dicionario_dados.json", "r", encoding="utf-8") as f:
        filtros = json.load(f)

    # convertendo todas palavras do dicionario para lowercase 
    palavras_saude = [p.lower() for p in filtros.get("palavras_saude", [])]
    nomes_upa = [n.lower() for n in filtros.get("nomes_upa", [])]
    sentimentos_positivos = [s.lower() for s in filtros.get("sentimentos_positivos", [])]
    sentimentos_negativos = [s.lower() for s in filtros.get("sentimentos_negativos", [])]
    palavroes = [p.lower() for p in filtros.get("palavroes", [])]

except FileNotFoundError:
    print("❌ Erro: 'dicionario_dados.json' não encontrado. Certifique-se de que o arquivo existe.")
    driver.quit()
    exit()
except json.JSONDecodeError:
    print("❌ Erro: 'dicionario_dados.json' está mal formatado. Verifique a sintaxe JSON.")
    driver.quit()
    exit()
except Exception as e:
    print(f"❌ Erro ao carregar filtros JSON: {e}")
    driver.quit()
    exit()

stop_words = set(stopwords.words("portuguese"))


# ANALISADOR LÉXICO
def analisar_lexico(texto):
    """
    Divide o texto em tokens
    e remove stop words e caracteres não alfabéticos.

    Retornando uma lista de tokens limpos
    """
    tokens = word_tokenize(texto.lower(), language="portuguese")
    clean_tokens = []
    for t in tokens:
        cleaned_t = re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) 
        if cleaned_t and cleaned_t not in stop_words: 
            clean_tokens.append(cleaned_t)
    return clean_tokens

def extrair_palavras(texto, lista, threshold=0.8):
    """
    Extrai palavras do texto que correspondem a uma lista de palavras
    Utiliza Levenshtein para encontrar palavras semelhantes
    Retorna uma lista de palavras encontradas.
    """
    texto_lower = texto.lower()
    tokens = word_tokenize(texto_lower, language="portuguese")
    encontrados = set() # evitar duplicatas

    processed_tokens = []
    for t in tokens:
        cleaned_t = re.sub(r'[^a-záàãâéêíóôõúüç]', '', t)
        if cleaned_t:
            processed_tokens.append(cleaned_t)

    for palavra_lista in lista:
        for token in processed_tokens:
            if token == palavra_lista:
                encontrados.add(palavra_lista)
            else:
                distancia = Levenshtein.distance(token, palavra_lista)
                similaridade = 1 - (distancia / max(len(token), len(palavra_lista), 1)) # evitando divisão por zero
                if similaridade >= threshold:
                    encontrados.add(palavra_lista)
    return list(encontrados)

def destacar_palavras(texto, palavras):
    """
    Destaca palavras no texto, colocando '>>>' e '<<<'.
    """
    for palavra in palavras:
        texto = re.sub(rf"\b({re.escape(palavra)})\b", r">>>\1<<<", texto, flags=re.IGNORECASE)
    return texto

def calcular_sentimento_geral(palavras_detectadas):
    """
    Calcula o sentimento geral de um tweet com base nas palavras positivas e negativas detectadas.
    Conta o número de palavras positivas e negativas
    e retorna "Positivo", "Negativo" ou "Neutro".
    """
    contagem_positivo = 0
    contagem_negativo = 0

    for palavra_info in palavras_detectadas:
        if palavra_info["tipo"] == "sentimento_positivo":
            contagem_positivo += 1
        elif palavra_info["tipo"] == "sentimento_negativo":
            contagem_negativo += 1

    if contagem_positivo > contagem_negativo:
        return "Positivo"
    elif contagem_negativo > contagem_positivo:
        return "Negativo"
    else:
        return "Neutro"
    

# processamento dos tweets coletados
print("Processando tweets coletados...")
dados_resultado = {
    "tweets_filtrados": []
}

for tweet in tweets_coletados:
    tokens_lexicos = analisar_lexico(tweet) 

    encontrados = []
    unrecognized_lexemes = [] 

    # extração de palavras para cada categoria
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

    # lexemas não reconhecidos
    palavras_detectadas_set = {e["palavra"].lower() for e in encontrados}
    for token in tokens_lexicos: # Usando os tokens limpos para esta verificação
        if token not in palavras_detectadas_set:
            unrecognized_lexemes.append(token)

    # destacar palavras encontradas no tweet
    palavras_para_destacar = list({e["palavra"] for e in encontrados})
    texto_destaque = destacar_palavras(tweet, palavras_para_destacar)

    # calcular o sentimento geral do tweet
    sentimento_geral = calcular_sentimento_geral(encontrados)

    # armazenar os resultados
    dados_resultado["tweets_filtrados"].append({
        "tweet_original": tweet,
        "tweet_destaque": texto_destaque,
        "palavras_detectadas": encontrados, 
        "tokens_lexicais": tokens_lexicos,
        "lexemas_nao_reconhecidos": unrecognized_lexemes, 
        "sentimento_geral": sentimento_geral 
    })

# salvar resultados em um arquivo JSON
output_filename = "tweets_filtrados.json"
print(f"Salvando resultados em '{output_filename}'...")
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(dados_resultado, f, ensure_ascii=False, indent=2)

print(f"\n✅ Tweets filtrados e tokens lexicais salvos em '{output_filename}'")


driver.quit()
print("Browser fechado.")
