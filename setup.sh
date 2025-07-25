#!/bin/bash

# Instala os navegadores e dependências via Playwright (sem apt-get)
npm install playwright
npx playwright install --with-deps
