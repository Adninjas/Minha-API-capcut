import os
import re
import asyncio
from flask import Flask, request, jsonify
from datetime import datetime
from playwright.async_api import async_playwright

app = Flask(__name__)

# Configurações
PAINEL_URL = "https://meuedu.email/dashboard"
USUARIO = "rogerfsferreira@gmail.com"
SENHA = "as395198"

URLS_CONTAS = {
    "cap2@universidadefederal.edu.pl": "https://meuedu.email/mailbox/f8b0de4a-3ab9-46ae-a91c-2aac322e8b02",
    "capcut@universidadefederal.edu.pl": "https://meuedu.email/mailbox/e016b008-52e2-4829-a64f-2bb21473ae3f"
}

# Função principal que usa Playwright para buscar o código
async def acessar_email_com_playwright(email_cliente):
    if email_cliente not in URLS_CONTAS:
        return None

    url_destino = URLS_CONTAS[email_cliente]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Login no painel
            await page.goto(PAINEL_URL)
            await page.fill('input#id_usuario', USUARIO)
            await page.fill('input#id_senha', SENHA)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(4000)

            # Acessar a página da conta de e-mail
            await page.goto(url_destino)
            await page.wait_for_timeout(4000)

            # Buscar o corpo do e-mail
            corpo = await page.inner_text("div.prose.max-w-none")
            codigo = extrair_codigo(corpo)
            await browser.close()
            return codigo

        except Exception as e:
            await browser.close()
            print("Erro Playwright:", e)
            return None

# Extrai o código do corpo do e-mail
def extrair_codigo(texto):
    match = re.search(r'(\d{6})', texto)
    if match:
        return match.group(1)
    return None

# Gera uma nova senha sequencial
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
    email = dados.get("email")

    if not email:
        return jsonify({"status": "erro", "mensagem": "E-mail não informado."}), 400

    # Chama o Playwright de forma assíncrona
    codigo = asyncio.run(acessar_email_com_playwright(email))

    if not codigo:
        return jsonify({"status": "erro", "mensagem": "Código de verificação não encontrado."}), 400

    nova_senha = gerar_senha()

    return jsonify({
        "codigo": codigo,
        "nova_senha": nova_senha
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
