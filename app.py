import os
import re
import time
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # Usando WebDriver Manager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

# Configurações fixas
PAINEL_URL = "https://meuedu.email/dashboard"
USUARIO = "rogerfsferreira@gmail.com"
SENHA = "as395198"

# E-mails permitidos e suas URLs
URLS_CONTAS = {
    "capcut@universidadefederal.edu.pl": "https://meuedu.email/mailbox/e016b008-52e2-4829-a64f-2bb21473ae3f",
    "cap2@universidadefederal.edu.pl": "https://meuedu.email/mailbox/f8b0de4a-3ab9-46ae-a91c-2aac322e8b02"
}

# Rota para verificar se a API está funcionando
@app.route("/")
def home():
    return "API está funcionando corretamente!"

# Acessa a caixa de e-mail usando Selenium
def acessar_email_com_selenium(email_cliente):
    if email_cliente not in URLS_CONTAS:
        return None

    url_caixa = URLS_CONTAS[email_cliente]

    # Configuração do WebDriver com WebDriver Manager
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executar sem abrir a janela do navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Acessar painel e realizar login
        driver.get(PAINEL_URL)
        driver.find_element(By.ID, "id_usuario").send_keys(USUARIO)
        driver.find_element(By.ID, "id_senha").send_keys(SENHA)
        driver.find_element(By.ID, "id_senha").send_keys(Keys.RETURN)
        time.sleep(4)  # Aguardar login

        # Acessar o e-mail desejado
        driver.get(url_caixa)
        time.sleep(4)  # Aguardar carregamento

        # Extrair o corpo do e-mail
        corpo_email = driver.find_element(By.XPATH, "//div[@class='email-body']").text
        codigo = extrair_codigo(corpo_email)
        return codigo
    except Exception as e:
        print("Erro ao acessar o painel:", e)
        return None
    finally:
        driver.quit()  # Fechar o driver após o uso

# Extrai código de 6 dígitos do e-mail
def extrair_codigo(corpo_email):
    match = re.search(r'\b(\d{6})\b', corpo_email)
    if match:
        return match.group(1)
    return None

# Gera senha nova sequencial
def gerar_senha():
    caminho = "contador_senhas.txt"
    ultimo = 0
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            ultimo = int(f.read().strip())
    novo = ultimo + 1
    with open(caminho, "w") as f:
        f.write(str(novo))
    return f"capcut{novo}"

# Rota da API
@app.route("/recuperar-senha", methods=["POST"])
def recuperar_senha():
    dados = request.get_json()
    email = dados.get("email")

    if not email:
        return jsonify({"status": "erro", "mensagem": "E-mail não enviado."}), 400

    if email not in URLS_CONTAS:
        return jsonify({"status": "erro", "mensagem": "E-mail não reconhecido na configuração do servidor."}), 400

    codigo = acessar_email_com_selenium(email)
    if not codigo:
        return jsonify({"status": "erro", "mensagem": "Código de verificação não encontrado."}), 400

    nova_senha = gerar_senha()

    return jsonify({
        "codigo": codigo,
        "nova_senha": nova_senha
    }), 200

# Inicialização do servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
