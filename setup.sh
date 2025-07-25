#!/bin/bash

# Atualiza pacotes
apt-get update

# Instala dependências de bibliotecas gráficas que o Chromium precisa no Linux
apt-get install -y wget gnupg libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm-dev libxshmfence1 libxrandr2 libxdamage1 libxcomposite1 libxcursor1 libxi6 libxtst6

# Instala o Playwright e os navegadores com todas as dependências
npm install playwright
npx playwright install --with-deps
