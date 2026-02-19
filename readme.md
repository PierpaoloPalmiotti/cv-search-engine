# CV Search Engine

AI-powered CV search and matching system that uses semantic embeddings to find the best candidates for a given job query, with automatic CV generation in PowerPoint format.

## Features

- **Semantic Search**: Uses BGE-M3 embeddings with weighted multi-section matching (Skills 40%, Experience 40%, Education 15%, Summary 5%)
- **Query Normalization**: Converts free-text queries into structured JSON, ensuring query and CV embeddings live in the same vector space
- **LLM Analysis**: Integrates with Ollama for local LLM-based candidate evaluation
- **CV Generation**: Automatically fills PowerPoint templates with candidate data
- **3D PCA Visualization**: Interactive scatter plot showing query position relative to CV cluster
- **CV JSON Generator**: GUI tool to create and manage candidate profiles

## Architecture

```
generate_cv_json.py          → Create/edit CV profiles (GUI)
        ↓
    cv_json/*.json           → Structured CV data
        ↓
create_embeddings_weighted.py → Generate weighted embeddings
        ↓
    cv_embeddings.npy        → Vector representations
        ↓
cv_search_app_modern.py      → Search, match & generate CVs (GUI)
        ↓
    cv_generati/*.pptx       → Final PowerPoint CVs
```

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) (optional, for LLM analysis)

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/cv-search-engine.git
cd cv-search-engine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Ollama Setup (Optional)

For local LLM candidate analysis:

```bash
# Install Ollama from https://ollama.ai/
ollama pull llama3.2:1b
```

## Project Structure

```
cv-search-engine/
├── cv_search_app_modern.py       # Main search & generation app (GUI)
├── create_embeddings_weighted.py # Embedding creation pipeline
├── generate_cv_json.py           # CV profile editor (GUI)
├── requirements.txt
├── README.md
├── .gitignore
├── template/                     # PowerPoint templates (.pptx)
├── cv_json/                      # CV profiles (JSON) — auto-created
├── cv_ppt/                       # Source CVs (PPTX) — optional
├── cv_generati/                  # Generated CVs — auto-created
└── log_executions/               # Execution logs — auto-created
```

## Usage

### 1. Create CV Profiles

```bash
python generate_cv_json.py
```

Use the GUI to add candidate profiles. Each profile is saved as a JSON file in `./cv_json/`.

### 2. Generate Embeddings

```bash
python create_embeddings_weighted.py
```

This processes all JSON profiles and creates weighted embeddings (`cv_embeddings.npy`).

### 3. Search & Generate CVs

```bash
python cv_search_app_modern.py
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
6. Generate PowerPoint CVs from templates

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

Each CV profile follows this structure:

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

The system uses weighted multi-section embeddings for optimal matching:

| Section | Weight | Contents |
|---|---|---|
| Skills + Technologies | 40% | Technical competencies |
| Experience | 40% | Work history and context |
| Education + Certifications | 15% | Formal qualifications |
| Summary + Title | 5% | General overview |

## License

MIT License