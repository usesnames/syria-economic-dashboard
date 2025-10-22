# 🎯 QUICK START - Deploy in 5 Minuti

## ⚡ Procedura Veloce

### 1️⃣ Esegui il Notebook
```bash
# Attiva l'ambiente
conda activate s_i_n

# Installa dipendenze (se non già fatto)
pip install pandas plotly jupyter

# Apri il notebook
jupyter notebook test.ipynb
```

**Esegui TUTTE le celle** (Cell > Run All) per generare `index.html`

### 2️⃣ Crea Repository GitHub

1. Vai su https://github.com/new
2. Nome: `syria-economic-dashboard`
3. Public ✅
4. **NON** aggiungere README/License
5. Click "Create repository"

### 3️⃣ Deploy con Script Automatico

```bash
# Torna nel terminale
cd /Users/ema/Documents/personal_projects/syria_in_numbers

# Esegui lo script (sostituisci con il TUO username)
./deploy.sh tuo-username-github
```

### 4️⃣ Attiva GitHub Pages

1. Vai su: `https://github.com/tuo-username/syria-economic-dashboard`
2. Click **Settings** ⚙️
3. Click **Pages** (menu laterale)
4. Source: 
   - Branch: `main` 
   - Folder: `/ (root)`
5. Click **Save** 💾

### 5️⃣ Visualizza la Dashboard! 🎉

Dopo 1-3 minuti, vai su:
```
https://tuo-username.github.io/syria-economic-dashboard/
```

---

## 🔧 Alternative: Deployment Manuale

Se lo script non funziona, usa questi comandi:

```bash
# Nella cartella del progetto
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tuo-username/syria-economic-dashboard.git
git push -u origin main
```

---

## ❓ Problemi Comuni

### Script non eseguibile?
```bash
chmod +x deploy.sh
```

### File index.html mancante?
Esegui tutte le celle del notebook prima!

### Repository già esiste?
```bash
git remote set-url origin https://github.com/tuo-username/syria-economic-dashboard.git
git push -f origin main
```

---

## 📞 Aiuto

Leggi la guida completa: `DEPLOYMENT.md`

O apri una issue su GitHub! 🐛
