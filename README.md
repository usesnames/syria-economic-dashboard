# 📊 Syria Economic Dashboard

Una dashboard interattiva per analizzare gli indicatori macroeconomici della Siria basata sui dati della Banca Mondiale.

## 🌐 Demo Live

🔗 **[Visualizza la Dashboard](https://[TUO-USERNAME].github.io/syria-economic-dashboard/)**

> ⚠️ Sostituisci `[TUO-USERNAME]` con il tuo username GitHub dopo il deployment

## 📋 Descrizione

Questo progetto presenta un'analisi completa della situazione macroeconomica della Siria attraverso:

- **PIL**: Andamento dal 1960 al 2023
- **Inflazione**: Indice CPI e tassi di inflazione annuali
- **Demografia**: PIL pro capite e crescita della popolazione
- **Settori Economici**: Composizione del PIL (Agricoltura, Industria, Servizi)
- **Indicatori Sociali**: Accesso all'elettricità, mortalità infantile, aspettativa di vita, alfabetizzazione, disoccupazione
- **Heatmap**: Evoluzione comparativa di indicatori economici chiave

## 🛠️ Tecnologie Utilizzate

- **Python 3.12**
- **Pandas**: Manipolazione e analisi dati
- **Plotly**: Visualizzazioni interattive
- **Jupyter Notebook**: Ambiente di sviluppo
- **GitHub Pages**: Hosting gratuito

## 📊 Fonte Dati

- **World Bank - World Development Indicators**
- Dataset: Syrian Arab Republic
- Periodo: 1960-2023
- Aggiornamento: 2024

## 🚀 Setup Locale

### Prerequisiti
```bash
python >= 3.12
conda (raccomandato)
```

### Installazione

1. Clona il repository:
```bash
git clone https://github.com/[TUO-USERNAME]/syria-economic-dashboard.git
cd syria-economic-dashboard
```

2. Crea l'ambiente conda:
```bash
conda create -n syria_dashboard python=3.12
conda activate syria_dashboard
```

3. Installa le dipendenze:
```bash
pip install pandas numpy plotly jupyter
```

4. Avvia Jupyter:
```bash
jupyter notebook test.ipynb
```

5. Esegui tutte le celle per generare `index.html`

## 📁 Struttura del Progetto

```
syria_in_numbers/
├── test.ipynb                          # Notebook principale
├── index.html                          # Dashboard HTML (generato)
├── DEPLOYMENT.md                       # Guida deployment
├── README.md                           # Questo file
├── .gitignore                          # File da escludere
└── P_Data_Extract_From_World_Development_Indicators/
    ├── f5f0999d-6264-40ae-9542-314fe97a5756_Data.csv
    └── f5f0999d-6264-40ae-9542-314fe97a5756_Series - Metadata.csv
```

## 📈 Caratteristiche

- ✅ **100% Interattivo**: Tutti i grafici sono interattivi (zoom, pan, hover)
- ✅ **Responsive**: Si adatta automaticamente a desktop, tablet e mobile
- ✅ **Veloce**: Utilizza CDN per Plotly, caricamento ottimizzato
- ✅ **Professionale**: Design moderno con gradient e card layout
- ✅ **Accessibile**: Hosting gratuito su GitHub Pages

## 🎨 Screenshots

_TODO: Aggiungi screenshots della dashboard_

## 📝 Come Contribuire

Contributi, issues e richieste di funzionalità sono benvenuti!

1. Fai un Fork del progetto
2. Crea un Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al Branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📜 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 👤 Autore

**[Il Tuo Nome]**

- GitHub: [@tuo-username](https://github.com/tuo-username)
- LinkedIn: [Il Tuo Profilo](https://linkedin.com/in/tuo-profilo)
- Email: tua.email@example.com

## 🙏 Ringraziamenti

- World Bank per i dati aperti
- Plotly team per l'eccellente libreria di visualizzazione
- GitHub per l'hosting gratuito

## 📊 Insights Chiave

Dal 2011, l'economia siriana ha subito trasformazioni drammatiche:

- 📉 **PIL**: Riduzione dell'82% rispetto al picco del 2010
- 💰 **Inflazione**: CPI oltre 600 (base 2010=100)
- 👥 **PIL pro capite**: Ritorno ai livelli degli anni '70
- 🌾 **Agricoltura**: Aumento del peso relativo nel PIL (>40%)
- 🏭 **Industria**: Forte contrazione del settore industriale

---

⭐ Se questo progetto ti è stato utile, lascia una stella!

🔗 **[Visualizza la Dashboard Live](https://[TUO-USERNAME].github.io/syria-economic-dashboard/)**
