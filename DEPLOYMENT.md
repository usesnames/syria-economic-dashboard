# 🚀 Guida al Deployment su GitHub Pages

## Prerequisiti
- Account GitHub
- Git installato sul tuo computer

## Passaggi per il Deployment

### 1. Esegui il Notebook
Prima di tutto, esegui tutte le celle del notebook `test.ipynb` fino all'ultima cella che genera il file `index.html`.

### 2. Crea un Nuovo Repository su GitHub

1. Vai su [GitHub](https://github.com)
2. Clicca su "New repository" (il pulsante verde)
3. Nome suggerito: `syria-economic-dashboard`
4. Descrizione: "Interactive dashboard analyzing Syria's macroeconomic indicators using World Bank data"
5. Seleziona "Public" (richiesto per GitHub Pages gratuito)
6. **NON** aggiungere README, .gitignore o license (li creeremo dopo)
7. Clicca su "Create repository"

### 3. Inizializza Git Localmente

Apri il terminale nella cartella del progetto ed esegui:

```bash
cd /Users/ema/Documents/personal_projects/syria_in_numbers

# Inizializza repository git
git init

# Aggiungi i file
git add index.html
git add test.ipynb
git add P_Data_Extract_From_World_Development_Indicators/

# Crea il primo commit
git commit -m "Initial commit: Syria economic dashboard"

# Collega al repository remoto (sostituisci con il TUO username)
git remote add origin https://github.com/TUO-USERNAME/syria-economic-dashboard.git

# Rinomina branch in main (se necessario)
git branch -M main

# Fai push
git push -u origin main
```

### 4. Attiva GitHub Pages

1. Vai sul repository GitHub appena creato
2. Clicca su **Settings** (ingranaggio in alto)
3. Nel menu laterale, clicca su **Pages**
4. Sotto "Source":
   - Seleziona "Deploy from a branch"
   - Branch: `main`
   - Folder: `/ (root)`
5. Clicca su **Save**

### 5. Attendi il Deployment

- GitHub impiegherà 1-3 minuti per il deployment
- Vedrai un messaggio verde con l'URL: `https://TUO-USERNAME.github.io/syria-economic-dashboard/`
- Clicca sull'URL per visualizzare la dashboard!

## 🎨 Personalizzazione

### Modificare i Colori
Modifica la sezione `<style>` nel file `index.html`:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Prova altri gradienti su [uiGradients](https://uigradients.com/)

### Aggiungere il Tuo Nome
Modifica la sezione footer nel file `index.html`:

```html
<p>© 2025 - Dashboard realizzata da [TUO NOME]</p>
```

### Cambiare il Titolo della Pagina
Modifica il tag `<title>` nell'HTML:

```html
<title>Il Tuo Titolo Personalizzato</title>
```

## 📱 Condivisione

Una volta pubblicata, puoi condividere la dashboard con:
- Link diretto: `https://TUO-USERNAME.github.io/syria-economic-dashboard/`
- QR code (genera su [qr-code-generator.com](https://www.qr-code-generator.com/))
- Social media

## 🔄 Aggiornare la Dashboard

Quando modifichi i dati o i grafici:

```bash
# Rigenera index.html eseguendo l'ultima cella del notebook

# Poi fai commit e push
git add index.html
git commit -m "Update dashboard with new data"
git push
```

GitHub Pages si aggiornerà automaticamente in 1-3 minuti.

## ⚡ Ottimizzazioni Avanzate

### Dominio Personalizzato
Puoi usare un tuo dominio (es: `syria-data.com`):
1. Vai su Settings > Pages
2. Sotto "Custom domain", inserisci il tuo dominio
3. Configura il DNS presso il tuo provider

### Analytics
Aggiungi Google Analytics per tracciare le visite:
1. Crea un account su [analytics.google.com](https://analytics.google.com)
2. Ottieni il codice di tracking
3. Inseriscilo nel `<head>` dell'HTML

### Velocizzare il Caricamento
- I grafici Plotly sono già ottimizzati
- Usa la CDN per Plotly (già implementato)
- Considera di minimizzare l'HTML per deployment di produzione

## 🆘 Troubleshooting

### La pagina non si carica
- Controlla che il file si chiami esattamente `index.html`
- Verifica che il repository sia "Public"
- Attendi 5 minuti dopo il primo deployment

### I grafici non appaiono
- Controlla la console del browser (F12)
- Verifica che la CDN Plotly sia raggiungibile
- Ricarica la pagina con Ctrl+F5 (cache refresh)

### Errore 404
- Verifica l'URL: deve essere `https://username.github.io/repo-name/`
- Controlla che GitHub Pages sia attivato nelle Settings

## 📚 Risorse Utili

- [Documentazione GitHub Pages](https://docs.github.com/en/pages)
- [Plotly Documentation](https://plotly.com/python/)
- [HTML/CSS Reference](https://www.w3schools.com/)

---

**Buon deployment! 🚀**

Se hai domande, apri una Issue sul repository.
