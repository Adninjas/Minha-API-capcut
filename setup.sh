#!/bin/bash

# Instalar o Chrome e o ChromeDriver
apt-get update
apt-get install -y wget unzip curl gnupg

# Instala o Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || apt --fix-broken install -y

# Baixa o ChromeDriver compatível com o Chrome instalado
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9.]+' | head -1 | cut -d. -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Instala dependências Python
pip install -r requirements.txt
