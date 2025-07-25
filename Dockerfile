# Etapa 1: Usar uma imagem base do Python 3.11
FROM python:3.11-slim

# Etapa 2: Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    unzip \
    chromium \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libgbm-dev \
    && apt-get clean

# Etapa 3: Configurar o diretório de trabalho
WORKDIR /app

# Etapa 4: Copiar o arquivo requirements.txt
COPY requirements.txt /app/requirements.txt

# Etapa 5: Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 6: Copiar o código do aplicativo
COPY . /app

# Etapa 7: Definir variáveis de ambiente para o Selenium
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Etapa 8: Expor a porta que o Flask vai rodar
EXPOSE 5000

# Etapa 9: Rodar o aplicativo Flask com gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
