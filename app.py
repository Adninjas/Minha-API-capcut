import os
import time
import re
from datetime import datetime

from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Definir as credenciais para login no painel
PAINEL_URL = "https://meuedu.email/dashboard"
USUARIO = "rogerfsferreira@gmail.com"  # E-mail de login
SENHA = "as395198"  # Senha de login

# URLs específicas para cada conta
URLS_CONTAS = {
    "cap2@universidadefederal.edu.pl": "https://meuedu.email/mailbox/f8b0de4a-3ab9-46ae-a91c-2aac322e8b02",
    "capcut@universidadefederal.edu.pl": "https://meuedu.email/mailbox/e016b008-52e2-4829-a64f-2bb21473ae3f"
}

# Função para inicializar o Selenium WebDriver
def inicializar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem abrir a janela do navegador
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Caminho do ChromeDriver – ajuste aqui ou use a env var CHROMEDRIVER_PATH
    driver_path = os.getenv("CHROMEDRIVER_PATH", "/caminho/para/o/chromedriver")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Função para fazer login e acessar o e-mail
def acessar_email_capcut(email_cliente):
    # Verificar se a URL da conta foi definida
    if email_cliente not in URLS_CONTAS:
        return None  # Caso o e-mail não seja reconhecido

    # A URL é associada ao e-mail fornecido no gatilho
    url_conta = URLS_CONTAS[email_cliente]

    driver = inicializar_driver()

    try:
        # Abrir o painel de login
        driver.get(PAINEL_URL)
        time.sleep(3)  # Espera o carregamento da página

        # Preencher o formulário de login
        usuario_input = driver.find_element(By.ID, "id_usuario")  # ID do campo de usuário
        senha_input = driver.find_element(By.ID, "id_senha")      # ID do campo de senha
        usuario_input.send_keys(USUARIO)
        senha_input.send_keys(SENHA)
        senha_input.send_keys(Keys.RETURN)
        time.sleep(5)  # Espera o login ser processado

        # Acessa diretamente a URL da conta de e-mail fornecida
        driver.get(url_conta)
        time.sleep(5)  # Espera a página carregar

        # *** Ajuste aqui o seletor conforme o HTML real da página ***
        # Você pode trocar por um seletor mais específico quando souber a classe correta.
        # Exemplo alternativo: By.XPATH, que procura um <p> que contenha apenas números de 6 dígitos.
        try:
            # Primeiro tenta pegar todo o texto da página de e-mail
            corpo_email = driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            # fallback para caso precise de outro seletor
            corpo_email = driver.page_source  # Pode te ajudar a debugar

        codigo = extrair_codigo(corpo_email)
        return codigo
    except Exception as e:
        print(f"Erro ao extrair código: {e}")
        return None
    finally:
        driver.quit()

def extrair_codigo(corpo_email: str):
    """
    Procura qualquer sequência de 6 dígitos no corpo do e-mail.
    Isso cobre casos como:
      "Verification Code ... 328688"
      "To verify your account ...\n\n328688\n\n..."
    """
    if not corpo_email:
        return None

    match = re.search(r'\b\d{6}\b', corpo_email)
    if match:
        return match.group(0)

    # Fallback (caso o código venha com outro tamanho entre 4 e 8 dígitos)
    match = re.search(r'(?:c[oó]digo de verifica[cç][aã]o|verification code)[^\d]*(\d{4,8})', corpo_email, re.I)
    if match:
        return match.group(1)

    return None

# Função para gerar senhas únicas e sequenciais
def gerar_senha():
    # Verificar o número da última senha gerada
    ultimo_numero = 0
    if os.path.exists("contador_senhas.txt"):
        with open("contador_senhas.txt", "r") as f:
            try:
                ultimo_numero = int(f.read().strip())
            except ValueError:
                ultimo_numero = 0

    novo_numero = ultimo_numero + 1  # Incrementa o número

    # Salvar o novo número para a próxima senha
    with open("contador_senhas.txt", "w") as f:
        f.write(str(novo_numero))

    return f"capcut{novo_numero}"

@app.route('/recuperar-senha', methods=['POST'])
def recuperar_senha():
    dados = request.get_json(silent=True) or {}
    email_cliente = dados.get('email')

    if not email_cliente:
        return jsonify({"status": "erro", "mensagem": "Campo 'email' é obrigatório no JSON."}), 400

    if email_cliente not in URLS_CONTAS:
        return jsonify({"status": "erro", "mensagem": "E-mail não reconhecido na configuração do servidor."}), 400

    # Chama a função para acessar o e-mail e pegar o código de verificação
    codigo = acessar_email_capcut(email_cliente)
    if not codigo:
        return jsonify({"status": "erro", "mensagem": "Código de verificação não encontrado."}), 400

    # Gerar a nova senha com base em um contador sequencial
    nova_senha = gerar_senha()

    # Retorna o código de verificação e a nova senha
    return jsonify({
        "codigo": codigo,
        "nova_senha": nova_senha
    }), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
