# 🔍 CV Search Engine — RAG Pipeline per Selezione Candidati

Sistema di ricerca e generazione CV basato su **Retrieval-Augmented Generation (RAG)**.  
Analizza query in linguaggio naturale, trova i candidati più adatti tramite similarità semantica e genera CV formattati in PowerPoint.

---

## 📐 Architettura del Sistema

### Pipeline Completa

```
┌─────────────────────────────────────────────────────────────────┐
│                    CV SEARCH ENGINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  CV JSON      │    │  BGE-M3      │    │  Embeddings      │  │
│  │  (input)      │───▶│  Encoder     │───▶│  .npy files      │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                   │             │
│        SETUP (una tantum)                         │             │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─  │
│        RUNTIME (ogni ricerca)                     │             │
│                                                   ▼             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Query        │    │  Ollama LLM  │    │  JSON            │  │
│  │  (testo       │───▶│  Parsing     │───▶│  strutturato     │  │
│  │   libero)     │    │  (3b)        │    │  della query     │  │
│  └──────────────┘    └──────────────┘    └────────┬─────────┘  │
│                                                   │             │
│                                                   ▼             │
│                                          ┌──────────────────┐  │
│                                          │  4 Sezioni        │  │
│                                          │  Pesate           │  │
│                                          │  Skills    (40%)  │  │
│                                          │  Experience(40%)  │  │
│                                          │  Education (15%)  │  │
│                                          │  Summary   ( 5%)  │  │
│                                          └────────┬─────────┘  │
│                                                   │             │
│                                                   ▼             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Top N        │◀──│  Cosine      │◀──│  Query           │  │
│  │  Candidati    │    │  Similarity  │    │  Embedding       │  │
│  └──────┬───────┘    └──────────────┘    └──────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  LLM          │    │  Grafico     │    │  CV PowerPoint   │  │
│  │  Analisi      │    │  PCA 3D      │    │  (output)        │  │
│  │  Candidati    │    │              │    │                  │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Parsing della Query (LLM + Fallback)

```
                    Testo Libero
                         │
                         ▼
              ┌─────────────────────┐
              │ Ollama LLM (1b o 3b)│
              │  format: "json"     │
              └──────────┬──────────┘
                         │
                    JSON valido?
                   /           \
                 SÌ             NO
                 │               │
                 ▼               ▼
          ┌────────────┐  ┌────────────────┐
          │ JSON        │  │ Parser Regex   │
          │ strutturato │  │ (fallback      │
          │ da LLM      │  │  deterministico│
          └──────┬─────┘  └───────┬────────┘
                 │                │
                 └──────┬─────────┘
                        ▼
              ┌───────────────────┐
              │  query_json_to_   │
              │  sections()       │
              │  (4 sezioni)      │
              └───────────────────┘
```

### Struttura Cartelle

```
cv-search-engine/
│
├── input/
│   ├── cv_json/              ← JSON dei candidati (da qui si parte)
│   ├── embeddings/           ← File .npy generati (setup)
│   │   ├── cv_embeddings.npy
│   │   ├── cv_texts.npy
│   │   ├── cv_labels.npy
│   │   └── cv_json_names.npy
│   └── template/             ← Template PowerPoint (.pptx)
│
├── output/                   ← CV generati dalla pipeline
│
├── cv_ppt/                   ← CV originali in PowerPoint (opzionale)
│
├── log_executions/           ← File di log
│   └── cv_search_log.txt
│
├── src/
│   ├── cv_search_app_modern.py      ← Applicazione principale
│   └── create_embeddings_weighted.py ← Script generazione embeddings
│
└── README.md
```

---

## ⚙️ Setup Iniziale (una tantum)

> **Il setup va eseguito una sola volta.** Successivamente, gli embeddings andranno ricreati solo quando vengono aggiunti nuovi CV.

### 1. Requisiti Software

**Python 3.10+** e le seguenti dipendenze:

```bash
pip install customtkinter numpy scikit-learn matplotlib FlagEmbedding python-pptx requests
```

**Ollama** (LLM locale):

```bash
# Installa Ollama da https://ollama.com
# Poi scarica il modello:
ollama pull llama3.2:3b
```

### 2. Preparazione dei CV

#### Raccolta di massa

Il processo consigliato per raccogliere i CV in azienda è:

1. Inviare una comunicazione a tutti i dipendenti/consulenti
2. Ogni persona compila il proprio CV in formato JSON tramite il tool online:  
   **👉 [https://pierpaolopalmiotti.github.io/cv-json-generator/](https://pierpaolopalmiotti.github.io/cv-json-generator/)**
3. I file JSON generati vengono salvati in una **cartella condivisa** (es. SharePoint, Google Drive, cartella di rete)
4. L'admin raccoglie tutti i JSON e li copia nella cartella `input/cv_json/` del progetto

#### Struttura JSON attesa

Ogni file JSON deve avere questa struttura:

```json
{
  "name": "Mario Rossi",
  "title": "Senior Developer",
  "summary": "10 anni di esperienza nello sviluppo software...",
  "skills": ["Python", "Java", "SQL"],
  "technologies": ["AWS", "Docker", "Kubernetes"],
  "certifications": ["AWS Solutions Architect"],
  "education": {
    "degree": "Laurea in Informatica",
    "year": 2015,
    "program": "Università di Roma"
  },
  "experience": [
    {
      "company": "Accenture",
      "period": "2018 - 2023",
      "description": "Sviluppo piattaforme cloud per il settore banking"
    }
  ]
}
```

### 3. Generazione Embeddings

```bash
cd src
python rag_bge-m3_v2.py
```

Questo script:
- Legge tutti i JSON dalla cartella `input/cv_json/`
- Divide ogni CV in 4 sezioni (skills 40%, experience 40%, education 15%, summary 5%)
- Genera embeddings con BGE-M3 (1024 dimensioni)
- Salva i file `.npy` in `input/embeddings/`

> **⚠️ Gli embeddings vanno ricreati ogni volta che si aggiungono nuovi CV di nuovi candidati o se ci sono variazioni in quelli già esistenti. Valutare quindi una creazione automatica degli embedding ogni N mesi**

### 4. Template PowerPoint

Posiziona almeno un template `.pptx` nella cartella `input/template/`.  
Tale template verrà utilizzato come base per la creazione del draft finale con le informazioni dei candidati estratti. 
Le informazioni 
I placeholder, o TAG, supportati sono:

| Placeholder | Contenuto |
|---|---|
| `{{NOME}}` | Nome e cognome |
| `{{TITOLO}}` / `{{RUOLO}}` | Ruolo professionale |
| `{{BACKGROUND}}` | Sommario / profilo |
| `{{SKILLS}}` | Lista competenze (singola) |
| `{{SKILLS1}}` / `{{SKILLS2}}` | Competenze su due colonne |
| `{{ESPERIENZE}}` | Esperienze lavorative |
| `{{CERTIFICAZIONI}}` | Certificazioni |
| `{{FORMAZIONE}}` | Titolo di studio |
| `{{LINGUE}}` | Lingue parlate |

---

## ⏱️ Tempistiche di Setup

Le tempistiche variano in base all'hardware. Ecco una stima indicativa:

| Operazione | PC Base (8GB RAM, no GPU) | PC Medio (16GB RAM, no GPU) | PC con GPU |
|---|---|---|---|
| Download modello BGE-M3 (~2GB) | 5-15 min | 5-15 min | 5-15 min |
| Download Ollama llama3.2:3b (~2GB) | 5-10 min | 5-10 min | 5-10 min |
| Generazione embeddings (10 CV) | 3-5 min | 1-3 min | 30-60 sec |
| Generazione embeddings (100 CV) | 20-40 min | 10-20 min | 3-5 min |
| Avvio applicazione (caricamento BGE-M3) | 30-60 sec | 15-30 sec | 5-10 sec |
| Parsing query con LLM (per query) | 20-40 sec | 10-25 sec | 3-8 sec |
| Analisi candidato con LLM (per candidato) | 30-60 sec | 15-30 sec | 5-10 sec |

> **Nota:** Il primo avvio di Ollama con un nuovo modello è più lento perché deve caricare i pesi in memoria.  
> Le esecuzioni successive sono significativamente più veloci perché il modello resta in cache.

> **Nota per PC con 8GB RAM:** L'uso simultaneo di BGE-M3 e llama3.2:3b può saturare la RAM.  
> Se si verificano rallentamenti, considerare l'uso di `llama3.2:1b` (meno preciso nel parsing ma più leggero).

---

## 🚀 Avvio

```bash
# Assicurati che Ollama sia in esecuzione
ollama serve

# Avvia l'applicazione
cd src
python cv_search_app_v1.py
```

---

## 💡 Utilizzo

### Ricerca e Generazione CV

1. Scrivi la query nella casella di testo (linguaggio naturale o formato strutturato)
2. Seleziona il template PowerPoint
3. Seleziona il modello LLM (consigliato: `llama3.2:3b`)
4. Imposta il numero di candidati da estrarre
5. Clicca **"Avvia Ricerca e Genera CV"**

**Esempi di query supportate:**

```
# Linguaggio naturale (richiede LLM attivo)
Cerco senior developer Python AWS con esperienza banking

# Formato strutturato (funziona anche senza LLM)
Skills: Python, AWS, Docker
Industry: Banking
Level: Senior
```

### Generazione Diretta CV

Se conosci già il candidato, inserisci nome e cognome nel campo dedicato e clicca **"Genera CV Diretto"** per generare il CV senza ricerca.

---

## 🧠 Come Funziona il Matching

### Parsing della Query

Quando inserisci una query in linguaggio naturale, il sistema:

1. **Invia il testo a Ollama** (llama3.2:3b) che estrae skills, ruolo, settore, ecc. in formato JSON
2. Se l'LLM non è disponibile o fallisce, usa un **parser regex** come fallback
3. Il JSON estratto viene convertito in **4 sezioni pesate**

### Pesi delle Sezioni

| Sezione | Peso | Contenuto |
|---|---|---|
| Skills | 40% | Competenze tecniche e tecnologie |
| Experience | 40% | Esperienze lavorative e settori |
| Education | 15% | Formazione e certificazioni |
| Summary | 5% | Nome, ruolo, profilo generale |

Le stesse 4 sezioni e gli stessi pesi vengono usati sia per i CV che per la query di ricerca, garantendo che il confronto avvenga nello stesso spazio semantico.

### Output della Pipeline

Per ogni ricerca, il sistema produce:
- **Classifica candidati** con score di similarità
- **Analisi LLM** con valutazione, punti di forza e gap per ogni candidato
- **Grafico PCA 3D e t-SNE 2D** che mostra la posizione della query rispetto a tutti i CV
- **CV generati** in formato PowerPoint come draft nel template predisposto

---

## 🔧 Troubleshooting

| Problema | Soluzione |
|---|---|
| "LLM non disponibile" | Verifica che Ollama sia attivo: `ollama serve` |
| "bind: Only one usage..." | Ollama è già in esecuzione, tutto ok |
| Skills vuote nel parsing | Usa `llama3.2:3b`, non 1b |
| Timeout LLM | Aumenta timeout o aspetta il primo caricamento del modello |
| Embeddings mancanti | Esegui `python create_embeddings_weighted.py` |
| RAM insufficiente | Usa `llama3.2:1b` o chiudi applicazioni in background |

---

## 📄 Licenza

Progetto interno — tutti i diritti riservati.