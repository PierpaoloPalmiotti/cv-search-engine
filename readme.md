# 🔍 CV Search Engine — RAG Pipeline
Tempo di lettura: 10-15 min

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
│  │  LLM          │    │  Grafico 3D  │    │  CV PowerPoint   │  │
│  │  Analisi      │    │  PCA/t-SNE/  │    │  (output)        │  │
│  │  (opzionale)  │    │  UMAP        │    │                  │  │
│  └──────────────┘    │  (opzionale)  │    └──────────────────┘  │
│                      └──────────────┘                           │
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
├── codes/
│   ├── cv_search_app_v1.py      ← Applicazione principale
│   └── embedding_generators/rag_bge-m3_v2.py ← Script generazione embeddings
│
└── README.md
```

---

## ⚙️ Setup Iniziale (una tantum)

> **Il setup va eseguito una sola volta.** Successivamente, gli embeddings andranno ricreati solo quando vengono aggiunti nuovi CV.

### 1. Requisiti Software

**Python 3.10+** e le seguenti dipendenze:

```bash
pip install customtkinter numpy scikit-learn matplotlib FlagEmbedding python-pptx requests umap-learn
```

Oppure tramite requirements.txt:

```bash
pip install -r requirements.txt
```

**Ollama** (LLM locale):

```bash
# Installa Ollama da https://ollama.com
# Poi scarica il modello:
ollama pull llama3.2:3b
# oppure
ollama pull llama3.2:1b
```

### 2. Preparazione dei CV

#### Raccolta di massa

Il processo consigliato per raccogliere i dati/CV in formato json è:

1. Inviare una comunicazione a tutti gli interessati
2. Ogni persona compila il proprio CV in formato JSON tramite il tool online:  
   **👉 [https://pierpaolopalmiotti.github.io/cv-json-generator/](https://pierpaolopalmiotti.github.io/cv-json-generator/)**
3. il JSON viene copiato, incollato e salvato in una **cartella condivisa** (es. SharePoint, Google Drive, cartella di rete)
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
cd codes
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

## ⏱️ Tempistiche

### Tempo totale per essere operativi (da zero a prima ricerca)

| Fase | PC Base (8GB RAM, no GPU) | PC Medio (16GB RAM, no GPU) | PC con GPU |
|---|---|---|---|
| 1. Lettura README e comprensione progetto | ~10 min | ~10 min | ~10 min |
| 2. Installazione Python + dipendenze (`pip install`) | 5-10 min | 5-10 min | 5-10 min |
| 3. Download modello BGE-M3 (~2GB) | 5-15 min | 5-15 min | 5-15 min |
| 4. Installazione Ollama + download llama3.2 (~2GB) | 5-15 min | 5-15 min | 5-15 min |
| 5. Preparazione CV JSON (se non già pronti) | variabile | variabile | variabile |
| 6. Generazione embeddings (10 CV) | 3-5 min | 1-3 min | 30-60 sec |
| 7. Primo avvio app + prima ricerca | 2-3 min | 1-2 min | 30-60 sec |
| **TOTALE (escluso punto 5)** | **~40-60 min** | **~30-50 min** | **~25-45 min** |

> La maggior parte del tempo è download. Una volta completato il setup, le esecuzioni successive partono in pochi secondi.

> Il collo di bottiglia è l'analisi LLM candidato per candidato. Se non serve una valutazione qualitativa, disabilitarla riduce i tempi dell'80-90%.

### Tempistiche di generazione embeddings

| Numero CV | PC Base (8GB) | PC Medio (16GB) | PC con GPU |
|---|---|---|---|
| 10 CV | 3-5 min | 1-3 min | 30-60 sec |
| 50 CV | 15 min | 7-15 min | 2-3 min |
| 100 CV | 20 min | 10-20 min | 3-5 min |
| 500 CV | 2 ore | 1-2 ore | 15-25 min |

> **Nota:** Il primo avvio di Ollama con un nuovo modello è più lento perché deve caricare i pesi in memoria. Le esecuzioni successive sono significativamente più veloci perché il modello resta in cache.

---

## 💻 Consigli per Configurazione Hardware

### Scelta del modello LLM (Ollama)

| Hardware | Modello consigliato | Note |
|---|---|---|
| 8GB RAM, no GPU | `llama3.2:1b` | Parsing meno preciso ma stabile. Evita di tenere aperte altre applicazioni pesanti durante l'uso. |
| 16GB RAM, no GPU | `llama3.2:3b` | Buon compromesso qualità/velocità. Consigliato per la maggior parte degli utenti. |
| 16GB+ RAM, con GPU | `llama3.2:3b` | Risposte rapide (3-8 sec). Si può valutare anche `llama3.1:8b` se si vuole più qualità nell'analisi candidati. |

> **Perché non modelli più grandi?** Modelli come `llama3.1:8b` o superiori richiedono 8-16GB solo per i pesi. Con BGE-M3 già in memoria (~2GB), su macchine con 16GB RAM si rischia di andare in swap e rallentare tutto. Valutare solo se si ha GPU dedicata con almeno 8GB VRAM.

### Scelta del modello di embedding

Il sistema usa **BGE-M3** (BAAI/bge-m3) come modello di embedding. È la scelta consigliata perché supporta nativamente il multilingua (italiano incluso) e produce embeddings densi a 1024 dimensioni con un buon rapporto qualità/dimensione.

| Hardware | Configurazione | Note |
|---|---|---|
| 8GB RAM | BGE-M3 con `use_fp16=True` | Configurazione attuale. Occupa ~2GB in RAM. Funziona ma lascia poco margine per l'LLM. |
| 16GB RAM | BGE-M3 con `use_fp16=True` | Configurazione ideale. Spazio sufficiente per BGE-M3 + LLM 3b in parallelo. |
| GPU con 4GB+ VRAM | BGE-M3 con `use_fp16=True` | L'encoding viene accelerato sulla GPU, utile soprattutto per la generazione embeddings di molti CV. |

### Quanti CV senza database vettoriale?

Il sistema attuale carica tutti gli embeddings in memoria come array NumPy (file `.npy`) e calcola la cosine similarity con un'operazione matriciale. Questo approccio è semplice ed efficace, ma ha dei limiti legati alla RAM disponibile.

| Numero CV | RAM occupata dagli embeddings | Funziona su 8GB? | Funziona su 16GB? | Tempo di ricerca |
|---|---|---|---|---|
| 10-50 | ~0.2-1 MB | ✅ Sì | ✅ Sì | istantaneo |
| 100-500 | ~1-5 MB | ✅ Sì | ✅ Sì | istantaneo |
| 500-2.000 | ~5-20 MB | ✅ Sì | ✅ Sì | < 1 sec |
| 2.000-5.000 | ~20-50 MB | ✅ Sì | ✅ Sì | 1-2 sec |
| 5.000-10.000 | ~50-100 MB | ⚠️ Possibile | ✅ Sì | 2-5 sec |
| 10.000+ | 100+ MB | ❌ Rischio swap | ⚠️ Possibile | 5+ sec |

> **Il vero collo di bottiglia non è la ricerca, ma la generazione degli embeddings.** Con 1.000 CV, la generazione iniziale può richiedere diverse ore su CPU. La ricerca in sé resta sotto i 2 secondi anche con migliaia di CV.

**Regola pratica:**
- **Fino a ~2.000 CV** → L'approccio attuale (NumPy in memoria) funziona senza problemi su qualsiasi macchina
- **2.000-10.000 CV** → Funziona ancora, ma valutare i tempi di rigenerazione embeddings e la RAM disponibile considerando che BGE-M3 + LLM sono già in memoria
- **Oltre 10.000 CV** → Conviene migrare a un database vettoriale (FAISS, ChromaDB, Qdrant, Milvus) per gestire l'indicizzazione, gli aggiornamenti incrementali e la ricerca approssimata (ANN)

### Configurazioni consigliate per scenario

| Scenario | Hardware minimo | Modello LLM | Note |
|---|---|---|---|
| POC / Demo (10-20 CV) | 8GB RAM, no GPU | `llama3.2:1b` | Funziona ma con tempi lunghi. Disabilitare analisi LLM per velocizzare. |
| Team piccolo (50-200 CV) | 16GB RAM, no GPU | `llama3.2:3b` | Configurazione ideale. Setup in ~1 ora, ricerche in ~15 sec. |
| Business unit (200-1.000 CV) | 16GB RAM, GPU consigliata | `llama3.2:3b` | GPU utile per la generazione embeddings. Ricerca comunque istantanea. |
| Azienda (1.000-5.000 CV) | 32GB RAM, GPU | `llama3.2:3b` o `llama3.1:8b` | Valutare database vettoriale per aggiornamenti incrementali. |
---

## 🚀 Avvio

```bash
# Assicurati che Ollama sia in esecuzione
ollama serve

# Avvia l'applicazione
cd cv-search-engine\\codes
python cv_search_app_v1.py
```

---

## 💡 Utilizzo

### Ricerca e Generazione CV

1. Scrivi la query nella casella di testo (linguaggio naturale o formato strutturato)
2. Seleziona il template PowerPoint
3. Seleziona il modello LLM (consigliato: `llama3.2:3b`)
4. **(Opzionale)** Spunta **"Abilita analisi LLM dei candidati"** per ottenere una valutazione dettagliata di ogni candidato (punti di forza, gap, idoneità). Questa opzione aumenta significativamente i tempi di elaborazione.
5. **(Opzionale)** Spunta **"Mostra grafico 3D"** e seleziona il metodo di riduzione dimensionale (PCA, t-SNE o UMAP) per visualizzare la posizione della query rispetto ai CV nello spazio degli embeddings. Si Congliglia in ordine: UMAP, t-SNE, PCA. 
6. Imposta il numero di candidati da estrarre
7. Clicca **"Avvia Ricerca e Genera CV"**

Al termine, il riquadro risultati mostra il riepilogo completo con il **tempo totale di elaborazione**.

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

Se conosci già il candidato, inserisci nome e cognome nel campo dedicato e clicca **"Genera CV Diretto"** per generare il draft ppt CV senza ricerca.

### Opzioni di Visualizzazione 3D

Il grafico 3D proietta gli embeddings ad alta dimensionalità (1024D) in uno spazio tridimensionale per visualizzare la vicinanza tra query e candidati. Sono disponibili tre metodi:

| Metodo | Caratteristiche | Quando usarlo |
|---|---|---|
| **PCA** | Deterministico, veloce, preserva varianza globale | Debug rapido, analisi della varianza |
| **t-SNE** | Preserva distanze locali, non deterministico | Esplorare cluster e vicinanze |
| **UMAP** | Preserva struttura locale e globale, veloce | **Consigliato** — miglior compromesso per visualizzare la similarità tra CV e query |

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
- **Analisi LLM** (opzionale) con valutazione, punti di forza e gap per ogni candidato
- **Grafico 3D** (opzionale) con PCA, t-SNE o UMAP che mostra la posizione della query rispetto a tutti i CV
- **CV generati** in formato PowerPoint come draft nel template predisposto
- **Tempo totale di elaborazione** della pipeline

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
| Errore import umap | Installa con `pip install umap-learn` (non `umap`) |

---

## 📄 Licenza

Progetto interno — tutti i diritti riservati.
