#!/bin/bash

# Instala dependências necessárias para Playwright
apt-get update
apt-get install -y wget gnupg libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm-dev libxshmfence1 libxrandr2 libxdamage1 libxcomposite1 libxcursor1 libxi6 libxtst6

# Instala Playwright e os browsers necessários
npm install playwright
npx playwright install
