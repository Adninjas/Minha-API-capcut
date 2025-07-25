import os
import re
import json
import asyncio
import subprocess
from flask import Flask, request, jsonify
from datetime import datetime
from playwright.async_api import async_playwright

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

# 🔧 Instala navegadores no runtime usando subprocess
async def instalar_browsers():
    process = await asyncio.create_subprocess_exec(
        "npx", "playwright", "install",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print("Erro ao instalar navegadores:", stderr.decode())
    else:
        print("Navegadores instalados com sucesso:", stdout.decode())

# Roda instalação assim que o app carregar
asyncio.run(instalar_browsers())

# 🔍 Acessa a caixa de e-mail usando Playwright
async def acessar_email_com_playwright(email_cliente):
    if email_cliente not in URLS_CONTAS:
        return None

    url_caixa = URLS_CONTAS[email_cliente]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login
        await page.goto(PAINEL_URL)
        await page.fill('input[id="id_usuario"]', USUARIO)
        await page.fill('input[id="id_senha"]', SENHA)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(4000)

        # Vai direto para a caixa do e-mail informado
        await page.goto(url_caixa)
        await page.wait_for_timeout(4000)

        try:
            corpo = await page.inner_text("//div[@class='email-body']")
            codigo = extrair_codigo(corpo)
            await browser.close()
            return codigo
        except Exception as e:
            await browser.close()
            print("Erro ao extrair código:", e)
            return None

# 🧠 Extrai código de 6 dígitos do e-mail
def extrair_codigo(corpo_email):
    match = re.search(r'\b(\d{6})\b', corpo_email)
    if match:
        return match.group(1)
    return None

# 🔐 Gera senha nova sequencial
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

# 🔁 Rota da API
@app.route("/recuperar-senha", methods=["POST"])
def recuperar_senha():
    dados = request.get_json()
    email = dados.get("email")

    if not email:
        return jsonify({"status": "erro", "mensagem": "E-mail não enviado."}), 400

    if email not in URLS_CONTAS:
        return jsonify({"status": "erro", "mensagem": "E-mail não reconhecido na configuração do servidor."}), 400

    codigo = asyncio.run(acessar_email_com_playwright(email))
    if not codigo:
        return jsonify({"status": "erro", "mensagem": "Código de verificação não encontrado."}), 400

    nova_senha = gerar_senha()

    return jsonify({
        "codigo": codigo,
        "nova_senha": nova_senha
    }), 200

# 🚀 Inicialização do servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
