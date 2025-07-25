import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# Definir as credenciais para login no painel
PAINEL_URL = "https://meuedu.email/dashboard"
USUARIO = "rogerfsferreira@gmail.com"
SENHA = "as395198"

# URLs específicas para cada conta
URLS_CONTAS = {
    "cap2@universidadefederal.edu.pl": "https://meuedu.email/mailbox/f8b0de4a-3ab9-46ae-a91c-2aac322e8b02",
    "capcut@universidadefederal.edu.pl": "https://meuedu.email/mailbox/e016b008-52e2-4829-a64f-2bb21473ae3f"
}

# Inicializa o Selenium com Chrome Headless
def inicializar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver_path = "/usr/local/bin/chromedriver"  # Caminho corrigido no Render
    return webdriver.Chrome(service=Service(driver_path), options=chrome_options)

# Extrai o código de verificação do corpo do e-mail
def extrair_codigo(corpo_email):
    match = re.search(r'\b\d{6}\b', corpo_email)
    if match:
        return match.group(0)
    return None

# Faz login no painel e busca o código na caixa de e-mail
def acessar_email_capcut(email_cliente):
    if email_cliente not in URLS_CONTAS:
        return None

    url_conta = URLS_CONTAS[email_cliente]
    driver = inicializar_driver()

    try:
        driver.get(PAINEL_URL)
        time.sleep(3)

        driver.find_element(By.ID, "id_usuario").send_keys(USUARIO)
        senha_input = driver.find_element(By.ID, "id_senha")
        senha_input.send_keys(SENHA)
        senha_input.send_keys(Keys.RETURN)
        time.sleep(5)

        driver.get(url_conta)
        time.sleep(5)

        corpo_email = driver.find_element(By.XPATH, "//div[@class='email-body']").text

        print(driver.page_source)  # DEBUG: imprime o HTML da página
        driver.quit()

        return extrair_codigo(corpo_email)
    except Exception as e:
        print(f"Erro: {e}")
        driver.quit()
        return None

# Gera senha nova com base em contador local
def gerar_senha():
    contador_path = "contador_senhas.txt"
    ultimo = 0
    if os.path.exists(contador_path):
        with open(contador_path, "r") as f:
            ultimo = int(f.read().strip())
    novo = ultimo + 1
    with open(contador_path, "w") as f:
        f.write(str(novo))
    return f"capcut{novo}"

@app.route('/recuperar-senha', methods=['POST'])
def recuperar_senha():
    dados = request.get_json()
    email_cliente = dados.get('email')

    if not email_cliente:
        return jsonify({"status": "erro", "mensagem": "E-mail não informado."}), 400

    codigo = acessar_email_capcut(email_cliente)

    if not codigo:
        return jsonify({"status": "erro", "mensagem": "Código de verificação não encontrado."}), 400

    nova_senha = gerar_senha()
    return jsonify({
        "codigo": codigo,
        "nova_senha": nova_senha
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
