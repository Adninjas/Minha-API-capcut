import os
import re
import asyncio
from flask import Flask, request, jsonify
from datetime import datetime
from playwright.async_api import async_playwright

app = Flask(__name__)

# Configurações fixas
PAINEL_URL = "https://meuedu.email/dashboard"
USUARIO = "rogerfsferreira@gmail.com"
SENHA = "as395198"

# E-mails autorizados e suas URLs
URLS_CONTAS = {
    "capcut@universidadefederal.edu.pl": "https://meuedu.email/mailbox/e016b008-52e2-4829-a64f-2bb21473ae3f",
    "cap2@universidadefederal.edu.pl": "https://meuedu.email/mailbox/f8b0de4a-3ab9-46ae-a91c-2aac322e8b02"
}

# 🔧 Função para instalar os navegadores (caso não estejam no cache do Render)
async def instalar_browsers():
    from playwright.__main__ import main as playwright_main
    await asyncio.to_thread(playwright_main, "install")

# ⚙️ Executa uma vez ao iniciar o app
asyncio.run(instalar_browsers())

# 🔍 Função principal que usa o Playwright
async def acessar_email_com_playwright(email_cliente):
    if email_cliente not in URLS_CONTAS:
        return None

    url_da_caixa = URLS_CONTAS[email_cliente]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(PAINEL_URL)
        await asyncio.sleep(2)

        await page.fill('input[id="id_usuario"]', USUARIO)
        await page.fill('input[id="id_senha"]', SENHA)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(4000)

        await page.goto(url_da_caixa)
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

# 🧠 Extrai código do corpo do e-mail
def extrair_codigo(corpo_email):
    match = re.search(r'\b(\d{6})\b', corpo_email)
    if match:
        return match.group(1)
    return None

# 🔐 Gera nova senha sequencial
def gerar_senha():
    contador_path = "contador_senhas.txt"
    ultimo_num = 0
    if os.path.exists(contador_path):
        with open(contador_path, "r") as f:
            ultimo_num = int(f.read().strip())
    novo_num = ultimo_num + 1
    with open(contador_path, "w") as f:
        f.write(str(novo_num))
    return f"capcut{novo_num}"

# 🔁 Endpoint principal
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

# 🚀 Inicializa o servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
