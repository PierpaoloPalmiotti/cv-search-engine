# CV Search Engine (RAG)

AI-powered CV search and matching system that uses semantic embeddings to find the best candidates for a given job query, with automatic CV generation in PowerPoint format.

## Features

- **Semantic Search**: BGE-M3 embeddings with weighted multi-section matching (Skills 40%, Experience 40%, Education 15%, Summary 5%)
- **Query Normalization**: Converts free-text queries into structured JSON, ensuring query and CV embeddings live in the same vector space
- **LLM Analysis**: Integrates with Ollama for local LLM-based candidate evaluation
- **CV Generation**: Automatically fills PowerPoint templates with candidate data
- **3D PCA Visualization**: Interactive scatter plot showing query position relative to CV cluster
- **CV JSON Generator**: GUI tool to create and manage candidate profiles

## Project Structure

```
RAG/
├── codes/
│   ├── create_json_cv/
│   │   └── generate_cv_json_v2.py      # CV profile editor (GUI)
│   ├── embedding_generators/
│   │   └── rag_bge-m3_v2.py            # Embedding generator (weighted)
│   └── cv_search_app_v1.py             # Main search & generation app (GUI)
│
├── input/
│   ├── cv_json/                        # CV profiles (JSON)
│   ├── embeddings/                     # Generated .npy embeddings
│   └── template/                       # PowerPoint templates (.pptx)
│
├── output/                             # Generated CVs (.pptx)
├── log_executions/                     # Execution logs
├── visualizations/                     # t-SNE and PCA plots
│
├── .gitignore
├── LICENSE
├── readme.md
└── requirements.txt
```

## Quick Start (from zero)

### 1. Clone and install

```bash
# Clone the repository
git clone https://github.com/PierpaoloPalmiotti/cv-search-engine.git
cd cv-search-engine

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate           # Windows
source venv/bin/activate        # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install and configure Ollama (for LLM analysis)

Ollama runs a local LLM to analyze and evaluate candidates. It is optional but recommended.

**Download and install:**
- Go to [https://ollama.ai/](https://ollama.ai/) and download the installer for your OS
- Run the installer

**Download the LLM model:**

Open a terminal and run:

```bash
# Start Ollama (if not already running)
ollama serve

# In another terminal, download the model
ollama pull llama3.2:1b

# Verify the model is installed
ollama list

# (Optional) Quick test
ollama run llama3.2:1b "Hello, are you working?"
```

> **Note:** `llama3.2:1b` requires ~1GB of RAM. For better results with 16GB+ RAM, you can also install `llama3.2:3b` (~2.5GB).

> **Important:** Ollama must be running in the background (`ollama serve`) whenever you use the search app with LLM analysis.

### 3. Create CV profiles

```bash
python codes/create_json_cv/generate_cv_json_v2.py
```

This opens a GUI where you can add candidate profiles. Fill in the fields (name, title, skills, technologies, experience, etc.) and click **Save**. Each profile is saved as a JSON file in `input/cv_json/`.

You need **at least 2-3 profiles** to generate meaningful embeddings.

### 4. Generate embeddings

```bash
python codes/embedding_generators/rag_bge-m3_v2.py
```

This processes all JSON profiles in `input/cv_json/` and creates weighted embeddings in `input/embeddings/`. The first run will download the BGE-M3 model (~1.5GB, one-time only).

At the end, you can optionally generate 2D/3D visualizations of the embedding space.

### 5. Prepare a PowerPoint template

Place a `.pptx` template in `input/template/`. The template must contain text placeholders that will be replaced with candidate data. See [Template Placeholders](#template-placeholders) below.

### 6. Search and generate CVs

```bash
python codes/cv_search_app_v1.py
```

This opens the main GUI. Enter a query using structured tags:

```
Skills: Python, AWS, Kubernetes
Industry: Banking
Level: Senior
Office: Milano
```

Click **"Avvia Ricerca e Genera CV"**. The system will:

1. Normalize the query into the same JSON structure as CVs
2. Generate weighted embeddings for the query
3. Find the most similar candidates via cosine similarity
4. Analyze candidates with local LLM (if Ollama is running)
5. Visualize results in a 3D PCA plot
6. Generate PowerPoint CVs from the selected template into `output/`

## Pipeline Overview

```
generate_cv_json_v2.py             → Create/edit CV profiles (GUI)
        ↓
  input/cv_json/*.json             → Structured CV data
        ↓
rag_bge-m3_v2.py                   → Generate weighted embeddings
        ↓
  input/embeddings/*.npy           → Vector representations
        ↓
cv_search_app_v1.py                → Search, match & generate CVs (GUI)
        ↓
  output/*.pptx                    → Final PowerPoint CVs
```

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | Required |
| Ollama | latest | Optional, for LLM analysis |
| RAM | 8GB minimum | 16GB recommended for larger models |

## Template Placeholders

PowerPoint templates support these placeholders:

| Placeholder | Description |
|---|---|
| `{{NOME}}` | Full name |
| `{{RUOLO}}` / `{{TITOLO}}` | Job title / Role |
| `{{BACKGROUND}}` | Professional summary |
| `{{SKILLS1}}` | First 5 skills |
| `{{SKILLS2}}` | Remaining skills (blank if ≤ 5) |
| `{{SKILLS}}` | All skills in single column (legacy) |
| `{{ESPERIENZE}}` | Work experience |
| `{{CERTIFICAZIONI}}` | Certifications |
| `{{LINGUE}}` | Languages |
| `{{FORMAZIONE}}` | Education |

## JSON Schema

Each CV profile follows this structure:

```json
{
  "name": "Mario Rossi",
  "title": "Cloud Architect",
  "Office": "Milano",
  "Level": "Senior",
  "summary": "10+ years in cloud infrastructure...",
  "skills": ["Project Management", "Agile", "Problem Solving"],
  "technologies": ["Python", "AWS", "Docker", "Kubernetes"],
  "education": {
    "degree": "Laurea in Informatica",
    "year": 2018,
    "program": "Ingegneria del Software"
  },
  "certifications": ["AWS Solutions Architect", "PMP"],
  "experience": [
    {
      "company": "Accenture",
      "period": "2020-2023",
      "description": "Led cloud migration projects for banking clients"
    }
  ]
}
```

## Embedding Weights

The system uses weighted multi-section embeddings for optimal matching:

| Section | Weight | Contents |
|---|---|---|
| Skills + Technologies | 40% | Technical competencies |
| Experience | 40% | Work history and context |
| Education + Certifications | 15% | Formal qualifications |
| Summary + Title | 5% | General overview |

## Query Tags

The search app recognizes these tags in the query box (Italian and English):

| Tag | Maps to |
|---|---|
| `Skills:` / `Competenze:` | Skills matching (40% weight) |
| `Technologies:` / `Tech:` | Technology matching (40% weight) |
| `Experience:` / `Esperienza:` | Experience matching (40% weight) |
| `Industry:` / `Settore:` | Added to summary context |
| `Level:` / `Livello:` / `Seniority:` | Seniority filter |
| `Office:` / `Sede:` | Location filter |
| `Role:` / `Ruolo:` | Role matching |
| `Certifications:` / `Certificazioni:` | Certification matching |
| `Education:` / `Formazione:` | Education matching |

## Troubleshooting

| Problem | Solution |
|---|---|
| `File mancanti: cv_embeddings.npy` | Run `rag_bge-m3_v2.py` first to generate embeddings |
| `Errore LLM: status 404` | Run `ollama pull llama3.2:1b` to download the model |
| `Ollama non disponibile` | Start Ollama with `ollama serve` in a separate terminal |
| `Nessun template trovato` | Place a `.pptx` template in `input/template/` |
| `PPTX non trovato` | Ensure the JSON file name matches the candidate name |
| App is slow to start | BGE-M3 model loads in background, wait for "Sistema pronto!" |

## License

MIT License