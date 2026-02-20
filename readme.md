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
│   │   ├── generate_cv_json_v1.py      # CV profile editor (terminal)
│   │   └── generate_cv_json_v2.py      # CV profile editor (GUI)
│   ├── embedding_generators/
│   │   ├── rag_bge-m3_v1.py            # Embedding generator v1
│   │   └── rag_bge-m3_v2.py            # Embedding generator v2 (weighted)
│   ├── ppt_to_json/
│   │   └── ppt_to_json_v1.py           # PPTX to JSON extractor
│   ├── cv_search_app_v0.py             # Search app v0
│   └── cv_search_app_v1.py             # Search app v1 (latest)
│
├── input/
│   ├── cv_json/                        # CV profiles (JSON)
│   ├── embeddings/                     # Generated .npy embeddings
│   └── template/                       # PowerPoint templates (.pptx)
│
├── cv_ppt/                             # Source CVs in PPTX (optional)
├── output/                             # Generated CVs (.pptx)
├── log_executions/                     # Execution logs
├── visualizations/                     # t-SNE and PCA plots
│
├── .gitignore
├── LICENSE
├── readme.md
└── requirements.txt
```

## Pipeline

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

- Python 3.10+
- [Ollama](https://ollama.ai/) (optional, for LLM analysis)

## Installation

```bash
# Clone the repository
git clone https://github.com/PierpaoloPalmiotti/cv-search-engine.git
cd cv-search-engine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Ollama Setup (Optional)

```bash
# Install Ollama from https://ollama.ai/
ollama pull llama3.2:1b
```

## Usage

### Step 1: Create CV Profiles

```bash
python codes/create_json_cv/generate_cv_json_v2.py
```

Use the GUI to add candidate profiles. Each profile is saved in `input/cv_json/`.

### Step 2: Generate Embeddings

```bash
python codes/embedding_generators/rag_bge-m3_v2.py
```

Processes all JSON profiles and creates weighted embeddings in `input/embeddings/`.

### Step 3: Search & Generate CVs

```bash
python codes/cv_search_app_v1.py
```

Enter a query using structured tags:

```
Skills: Python, AWS, Kubernetes
Industry: Banking
Level: Senior
Office: Milano
```

The system will:
1. Normalize the query into the same JSON structure as CVs
2. Generate weighted embeddings for the query
3. Find the most similar candidates via cosine similarity
4. (Optional) Analyze candidates with local LLM
5. Visualize results in a 3D PCA plot
6. Generate PowerPoint CVs from the selected template

## Template Placeholders

PowerPoint templates support these placeholders:

| Placeholder | Description |
|---|---|
| `{{NOME}}` | Full name |
| `{{RUOLO}}` / `{{TITOLO}}` | Job title / Role |
| `{{BACKGROUND}}` | Professional summary |
| `{{SKILLS1}}` | First 5 skills |
| `{{SKILLS2}}` | Remaining skills |
| `{{SKILLS}}` | All skills (single column) |
| `{{ESPERIENZE}}` | Work experience |
| `{{CERTIFICAZIONI}}` | Certifications |
| `{{LINGUE}}` | Languages |
| `{{FORMAZIONE}}` | Education |

## JSON Schema

```json
{
  "name": "Mario Rossi",
  "title": "Cloud Architect",
  "Office": "Milano",
  "Level": "Senior",
  "summary": "Professional summary...",
  "skills": ["Project Management", "Agile"],
  "technologies": ["Python", "AWS", "Docker"],
  "education": {
    "degree": "Laurea in Informatica",
    "year": 2018,
    "program": "Ingegneria del Software"
  },
  "certifications": ["AWS Solutions Architect"],
  "experience": [
    {
      "company": "Accenture",
      "period": "2020-2023",
      "description": "Cloud migration projects"
    }
  ]
}
```

## Embedding Weights

| Section | Weight | Contents |
|---|---|---|
| Skills + Technologies | 40% | Technical competencies |
| Experience | 40% | Work history and context |
| Education + Certifications | 15% | Formal qualifications |
| Summary + Title | 5% | General overview |

## License

MIT License