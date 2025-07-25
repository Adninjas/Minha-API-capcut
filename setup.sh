#!/bin/bash
# Instalar as dependências necessárias para o Playwright
apt-get update -y
apt-get install -y libx11-dev libxcomposite-dev libxrandr-dev libgtk-3-dev libgbm-dev
apt-get install -y libasound2 libnspr4 libnss3 libxss1 libxtst6
apt-get install -y fonts-liberation
apt-get install -y wget unzip

# Baixar os binários do Playwright
python3 -m playwright install
