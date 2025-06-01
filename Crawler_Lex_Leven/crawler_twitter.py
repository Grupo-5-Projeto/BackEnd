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

# --- NLTK Downloads ---
# Download necessary NLTK data. These are typically downloaded once.
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')

# --- Configuration ---
# Twitter account credentials and search query
email = "connectupa@gmail.com"
senha = "UpaConnectTwitter"
username = "UpaConnect_"
search_query = "UPA" # The term to search on Twitter

# --- Selenium Setup ---
# Configure Chrome options for the webdriver
options = Options()
options.add_argument("--start-maximized") # Start browser maximized
options.add_argument("--disable-notifications") # Disable browser notifications
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10) # Set a longer wait time for robustness

# --- Twitter Login Process ---
print("Attempting to log in to Twitter...")
driver.get("https://twitter.com/login")

try:
    # Wait for the email/username input field to be present
    email_input_locator = (By.NAME, "text")
    wait.until(EC.presence_of_element_located(email_input_locator))
    input_email = driver.find_element(*email_input_locator)
    input_email.send_keys(email)
    input_email.send_keys(Keys.RETURN)

    # After entering email, Twitter might ask for username or go directly to password.
    # We'll try to wait for either the username input or the password input.
    try:
        # Wait for the username input field (if it appears)
        username_input_locator = (By.NAME, "text")
        wait.until(EC.presence_of_element_located(username_input_locator))
        username_input = driver.find_element(*username_input_locator)
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        # After sending username, wait specifically for the password field
        password_input_locator = (By.NAME, "password")
        wait.until(EC.presence_of_element_located(password_input_locator))
    except Exception:
        # If username input doesn't appear, assume it went straight to password.
        # This block will execute if the previous wait for username input times out.
        password_input_locator = (By.NAME, "password")
        wait.until(EC.presence_of_element_located(password_input_locator))

    # Enter password
    input_senha = driver.find_element(*password_input_locator)
    input_senha.send_keys(senha)
    input_senha.send_keys(Keys.RETURN)

    # Wait for a common element on the logged-in homepage to confirm successful login.
    # This could be the 'Home' link or the search box input.
    wait.until(EC.presence_of_element_located((By.XPATH, '//a[@data-testid="AppTabBar_Home_Link"] | //input[@data-testid="SearchBox_Search_Input"]')))
    print("✅ Login bem-sucedido!")

except Exception as e:
    print(f"❌ Erro durante o login: {e}")
    driver.quit()
    exit()

# --- Navigate to Search Results ---
print(f"Navigating to Twitter search results for '{search_query}'...")
driver.get(f"https://twitter.com/search?q={search_query}&src=typed_query")

try:
    # Wait for the first tweet article to be visible
    wait.until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
    print("✅ Tweets carregados na página de busca!")
except Exception as e:
    print(f"❌ Nenhum tweet visível foi encontrado na página de busca: {e}")
    driver.quit()
    exit()

time.sleep(3) # Give a moment for content to settle after initial load

# --- Tweet Collection ---
print("Starting tweet collection by scrolling...")
last_height = driver.execute_script("return document.body.scrollHeight")
tweets_coletados = set() # Use a set to store unique tweet texts
scrolls = 0
max_scrolls = 30 # Limit the number of scrolls to prevent infinite looping

while scrolls < max_scrolls:
    # Find all tweet elements that have Portuguese language attribute
    tweets = driver.find_elements(By.XPATH, '//div[@lang="pt"]')
    for t in tweets:
        txt = t.text.strip()
        # Only add tweets that contain the search query (case-insensitive)
        if search_query.lower() in txt.lower():
            tweets_coletados.add(txt)

    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3) # Wait for new content to load

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        # If heights are the same, no new content loaded, so break the loop
        print("Reached end of scrollable content or no new tweets loaded.")
        break
    last_height = new_height
    scrolls += 1
    print(f"Scroll {scrolls}/{max_scrolls} completed. Collected {len(tweets_coletados)} unique tweets.")

print(f"Finished tweet collection. Total unique tweets collected: {len(tweets_coletados)}")

# --- Load Filter Dictionaries ---
print("Loading filter dictionaries from 'dicionario_dados.json'...")
try:
    with open("dicionario_dados.json", "r", encoding="utf-8") as f:
        filtros = json.load(f)

    # Convert all filter words to lowercase for case-insensitive matching
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

# Load Portuguese stop words for lexical analysis
stop_words = set(stopwords.words("portuguese"))

# --- Lexical Analysis Functions ---

def analisar_lexico(texto):
    """
    Tokenizes the input text, converts to lowercase, and removes non-alphabetic
    tokens and stop words.
    Returns a list of lexical tokens.

    >>> MODIFICAÇÃO: Aprimorado para limpar tokens (remover caracteres não alfabéticos)
    >>> antes de filtrar, tornando a detecção mais robusta para palavras com pontuação/símbolos.
    """
    tokens = word_tokenize(texto.lower(), language="portuguese")
    clean_tokens = []
    for t in tokens:
        # Remove qualquer caractere que não seja uma letra (incluindo acentuadas)
        cleaned_t = re.sub(r'[^a-záàãâéêíóôõúüç]', '', t) # Mantém apenas letras minúsculas (incluindo acentuadas)
        if cleaned_t and cleaned_t not in stop_words: # Garante que o token não está vazio após a limpeza e não é uma stop word
            clean_tokens.append(cleaned_t)
    return clean_tokens

def extrair_palavras(texto, lista, threshold=0.8):
    """
    Extracts words from the text that are present in the given list,
    using Levenshtein distance for fuzzy matching.
    Returns a list of matched words from the 'lista'.
    """
    texto_lower = texto.lower()
    tokens = word_tokenize(texto_lower, language="portuguese") # A tokenização bruta ainda é feita aqui
    encontrados = set() # Use a set to avoid duplicate matches

    # Importante: Aplique a mesma lógica de limpeza de tokens aqui para garantir consistência
    # com o que `analisar_lexico` produz.
    processed_tokens = []
    for t in tokens:
        cleaned_t = re.sub(r'[^a-záàãâéêíóôõúüç]', '', t)
        if cleaned_t: # Adiciona apenas se não estiver vazio após a limpeza
            processed_tokens.append(cleaned_t)

    for palavra_lista in lista:
        for token in processed_tokens: # Use os tokens processados aqui
            # Exact match first
            if token == palavra_lista:
                encontrados.add(palavra_lista)
            else:
                # Calculate Levenshtein similarity for fuzzy matching
                distancia = Levenshtein.distance(token, palavra_lista)
                # Similarity is 1 - (distance / max_length)
                similaridade = 1 - (distancia / max(len(token), len(palavra_lista), 1)) # Avoid division by zero
                if similaridade >= threshold:
                    encontrados.add(palavra_lista)
    return list(encontrados)

def destacar_palavras(texto, palavras):
    """
    Highlights detected words in the original text by wrapping them with '>>>word<<<'.
    Uses regular expressions for case-insensitive whole-word matching.
    """
    for palavra in palavras:
        # Use word boundaries (\b) to match whole words and re.escape to handle special chars
        texto = re.sub(rf"\b({re.escape(palavra)})\b", r">>>\1<<<", texto, flags=re.IGNORECASE)
    return texto

def calcular_sentimento_geral(palavras_detectadas):
    """
    Calculates the overall sentiment of a tweet based on detected positive and negative words.
    Returns "Positivo", "Negativo", or "Neutro".
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
        return "Neutro" # Including cases where both are zero or equal

# --- Process Collected Tweets ---
print("Processing collected tweets for lexical analysis...")
dados_resultado = {
    "tweets_filtrados": []
}

for tweet in tweets_coletados:
    # Importante: A `analisar_lexico` agora já retorna tokens limpos.
    tokens_lexicos = analisar_lexico(tweet) # Estes são os tokens limpos do tweet.

    encontrados = [] # Stores detected words with their types
    unrecognized_lexemes = [] # Stores tokens not found in any filter list

    # Extract words from each category using fuzzy matching
    # A função extrair_palavras foi modificada para também limpar os tokens que recebe
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

    # Check for unrecognized lexemes (tokens that are not in any of our defined lists)
    # Convert 'encontrados' to a set of lowercase words for efficient lookup
    palavras_detectadas_set = {e["palavra"].lower() for e in encontrados}
    for token in tokens_lexicos: # Usando os tokens limpos para esta verificação
        if token not in palavras_detectadas_set:
            unrecognized_lexemes.append(token)

    # Prepare words for highlighting in the original tweet
    palavras_para_destacar = list({e["palavra"] for e in encontrados})
    texto_destaque = destacar_palavras(tweet, palavras_para_destacar)

    # Calculate overall sentiment for the tweet
    sentimento_geral = calcular_sentimento_geral(encontrados)

    # Append the processed tweet data to the results
    dados_resultado["tweets_filtrados"].append({
        "tweet_original": tweet,
        "tweet_destaque": texto_destaque,
        "palavras_detectadas": encontrados, # This list serves as the lexeme identification
        "tokens_lexicais": tokens_lexicos, # Estes são os tokens limpos que foram analisados
        "lexemas_nao_reconhecidos": unrecognized_lexemes, # New field for unrecognized tokens
        "sentimento_geral": sentimento_geral # New field for overall sentiment
    })

# --- Save Results to JSON ---
output_filename = "tweets_filtrados.json"
print(f"Saving filtered tweets and lexical analysis results to '{output_filename}'...")
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(dados_resultado, f, ensure_ascii=False, indent=2)

print(f"\n✅ Tweets filtrados e tokens lexicais salvos em '{output_filename}'")

# --- Cleanup ---
driver.quit()
print("Browser closed.")
