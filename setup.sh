#!/bin/bash
set -e  # Faz o script parar se algum comando falhar
set -x  # Mostra no log todos os comandos sendo executados

# Instala os navegadores necessários do Playwright
npx playwright install

# (opcional) Verifique permissões ou outras dependências específicas aqui, se necessário
