import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random
import re
from flask import Flask, request, jsonify
from datetime import datetime

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
    driver_path = "/caminho/para/o/chromedriver"  # Caminho para o seu ChromeDriver
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    return driver

# Função para fazer login e acessar o e-mail
def acessar_email_capcut(email_cliente):
    # Verificar se a URL da conta foi definida
    if email_cliente not in URLS_CONTAS:
        return None  # Caso o e-mail não seja reconhecido

    # A URL é associada ao e-mail fornecido no gatilho
    url_conta = URLS_CONTAS[email_cliente]
    
    driver = inicializar_driver()

    # Abrir o painel de login
    driver.get(PAINEL_URL)
    time.sleep(3)  # Espera o carregamento da página
    
    # Preencher o formulário de login
    usuario_input = driver.find_element(By.ID, "id_usuario")  # ID do campo de usuário
    senha_input = driver.find_element(By.ID, "id_senha")  # ID do campo de senha
    usuario_input.send_keys(USUARIO)
    senha_input.send_keys(SENHA)
    senha_input.send_keys(Keys.RETURN)
    time.sleep(5)  # Espera o login ser processado

    # Acessa diretamente a URL da conta de e-mail fornecida
    driver.get(url_conta)
    time.sleep(5)  # Espera a página carregar

    # Buscar o código de verificação no corpo do e-mail
    try:
        # Pega o corpo do e-mail
        corpo_email = driver.find_element(By.XPATH, "//div[@class='email-body']").text
        codigo = extrair_codigo(corpo_email)
        driver.quit()
        return codigo
    except Exception as e:
        driver.quit()
        print(f"Erro ao extrair código: {e}")
        return None

def extrair_codigo(corpo_email):
    # Usando expressão regular para encontrar o código de verificação no corpo do e-mail
    match = re.search(r'Código de verificação:\s*(\d+)', corpo_email)
    if match:
        return match.group(1)
    return None

# Função para gerar senhas únicas e sequenciais
def gerar_senha():
    # Verificar o número da última senha gerada
    ultimo_numero = 0
    if os.path.exists("contador_senhas.txt"):
        with open("contador_senhas.txt", "r") as f:
            ultimo_numero = int(f.read().strip())  # Leitura do último número usado
    novo_numero = ultimo_numero + 1  # Incrementa o número
    # Salvar o novo número para a próxima senha
    with open("contador_senhas.txt", "w") as f:
        f.write(str(novo_numero))
    return f"capcut{novo_numero}"

@app.route('/recuperar-senha', methods=['POST'])
def recuperar_senha():
    dados = request.get_json()
    email_cliente = dados['email']  # E-mail informado pelo administrador
    
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

