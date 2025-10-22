#!/bin/bash

# Script per il deployment rapido su GitHub Pages
# Uso: ./deploy.sh "tuo-username-github"

set -e  # Exit on error

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Syria Economic Dashboard - Deployment Script${NC}\n"

# Verifica argomento username
if [ -z "$1" ]; then
    echo -e "${RED}❌ Errore: Specifica il tuo username GitHub${NC}"
    echo "Uso: ./deploy.sh tuo-username"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="syria-economic-dashboard"

echo -e "${GREEN}✓${NC} Username GitHub: $GITHUB_USERNAME"
echo -e "${GREEN}✓${NC} Nome repository: $REPO_NAME\n"

# Controlla se index.html esiste
if [ ! -f "index.html" ]; then
    echo -e "${RED}❌ Errore: index.html non trovato!${NC}"
    echo "Esegui prima tutte le celle del notebook per generare index.html"
    exit 1
fi

echo -e "${GREEN}✓${NC} File index.html trovato\n"

# Inizializza git se necessario
if [ ! -d ".git" ]; then
    echo -e "${BLUE}Inizializzo repository git...${NC}"
    git init
    echo -e "${GREEN}✓${NC} Repository inizializzato\n"
else
    echo -e "${GREEN}✓${NC} Repository git già esistente\n"
fi

# Aggiungi file
echo -e "${BLUE}Aggiunto file...${NC}"
git add index.html
git add test.ipynb
git add README.md
git add DEPLOYMENT.md
git add .gitignore
git add P_Data_Extract_From_World_Development_Indicators/

# Commit
echo -e "${BLUE}Creazione commit...${NC}"
git commit -m "Deploy: Syria economic dashboard" || echo "Nessuna modifica da committare"

# Rinomina branch in main
echo -e "${BLUE}Configurazione branch...${NC}"
git branch -M main

# Aggiungi remote (se non esiste)
if ! git remote | grep -q "origin"; then
    echo -e "${BLUE}Aggiunta remote origin...${NC}"
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo -e "${GREEN}✓${NC} Remote aggiunto\n"
else
    echo -e "${GREEN}✓${NC} Remote già configurato\n"
fi

# Push
echo -e "${BLUE}Push su GitHub...${NC}"
git push -u origin main

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment completato con successo!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "📋 Prossimi passi:"
echo -e "1. Vai su: ${BLUE}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "2. Clicca su ${BLUE}Settings${NC} > ${BLUE}Pages${NC}"
echo -e "3. Sotto 'Source', seleziona branch: ${BLUE}main${NC}, folder: ${BLUE}/ (root)${NC}"
echo -e "4. Clicca su ${BLUE}Save${NC}"
echo -e "\n🌐 La tua dashboard sarà disponibile su:"
echo -e "${GREEN}https://$GITHUB_USERNAME.github.io/$REPO_NAME/${NC}\n"

echo -e "⏱️  Attendi 1-3 minuti per il deployment automatico.\n"
