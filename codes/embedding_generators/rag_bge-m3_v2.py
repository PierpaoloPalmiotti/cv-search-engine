# create_embeddings_weighted.py
from FlagEmbedding import BGEM3FlagModel
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import plotly.graph_objects as go


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → RAG/

class EmbeddingLogger:
    """Gestisce il logging su file con timestamp"""
    def __init__(self, log_folder=BASE_DIR / "log_executions"):
        self.log_folder = Path(log_folder)
        self.log_folder.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_folder / f"{timestamp}_embeddings_creation.txt"
        
        self.log(f"{'='*80}")
        self.log(f"CREAZIONE EMBEDDINGS PESATI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*80}\n")
    
    def log(self, message, also_print=True):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
        if also_print:
            print(message)
    
    def log_section(self, title):
        separator = "="*80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(f"{separator}\n")
    
    def log_error(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ❌ ERRORE: {message}")
    
    def log_success(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ✓ {message}")
    
    def log_warning(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ⚠ WARNING: {message}")


def create_visualization_2d(embeddings, labels, output_folder=None, logger=None):
    output_path = Path(output_folder) if output_folder else BASE_DIR / "visualizations"
    """Crea visualizzazione 2D con matplotlib"""
    if logger:
        logger.log_section("CREAZIONE VISUALIZZAZIONE 2D")
    
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # t-SNE 2D
    if logger:
        logger.log("Applicando t-SNE 2D...")
    
    perplexity = min(30, len(embeddings) - 1)
    if perplexity < 5:
        perplexity = min(3, len(embeddings) - 1)
    
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    embeddings_2d = tsne.fit_transform(embeddings)
    
    # Plot
    plt.figure(figsize=(14, 10))
    
    # Scatter plot
    scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], 
                         s=200, alpha=0.7, c=range(len(labels)), 
                         cmap='viridis', edgecolors='black', linewidths=1.5)
    
    # Aggiungi etichette
    for i, label in enumerate(labels):
        plt.annotate(label, 
                    (embeddings_2d[i, 0], embeddings_2d[i, 1]),
                    xytext=(8, 8), 
                    textcoords='offset points',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                             edgecolor='black', alpha=0.8))
    
    plt.colorbar(scatter, label='CV Index')
    plt.title('Visualizzazione 2D Embeddings Pesati (t-SNE)\nWeights: Skills 40%, Experience 40%, Education 15%, Summary 5%', 
             fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Dimensione t-SNE 1', fontsize=12)
    plt.ylabel('Dimensione t-SNE 2', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Salva
    output_file = output_path / "cv_embeddings_weighted_2d_tsne.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    if logger:
        logger.log_success(f"Visualizzazione 2D salvata: {output_file}")
    
    plt.close()
    
    return embeddings_2d


def create_visualization_3d(embeddings, labels, cv_sections_list, output_folder="./visualizations", logger=None):
    """Crea visualizzazioni 3D interattive con Plotly"""
    if logger:
        logger.log_section("CREAZIONE VISUALIZZAZIONI 3D")
    
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Crea testi per hover
    hover_texts = []
    for i, (label, sections) in enumerate(zip(labels, cv_sections_list)):
        hover_text = f"<b>{label}</b><br><br>"
        hover_text += f"<b>Skills:</b> {sections['skills'][:150]}...<br>"
        hover_text += f"<b>Experience:</b> {sections['experience'][:150]}..."
        hover_texts.append(hover_text)
    
    # t-SNE 3D
    if logger:
        logger.log("Applicando t-SNE 3D...")
    
    perplexity = min(30, len(embeddings) - 1)
    if perplexity < 5:
        perplexity = min(3, len(embeddings) - 1)
    
    tsne_3d = TSNE(n_components=3, random_state=42, perplexity=perplexity)
    emb_3d_tsne = tsne_3d.fit_transform(embeddings)
    
    # Plot t-SNE 3D
    fig_tsne = go.Figure(data=[go.Scatter3d(
        x=emb_3d_tsne[:, 0],
        y=emb_3d_tsne[:, 1],
        z=emb_3d_tsne[:, 2],
        mode='markers+text',
        marker=dict(
            size=12,
            color=np.arange(len(labels)),
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="CV Index"),
            line=dict(color='black', width=1)
        ),
        text=labels,
        textposition="top center",
        textfont=dict(size=10, color='black'),
        hovertext=hover_texts,
        hoverinfo='text'
    )])
    
    fig_tsne.update_layout(
        title='Visualizzazione 3D Embeddings Pesati (t-SNE)<br><sub>Weights: Skills 40%, Experience 40%, Education 15%, Summary 5%</sub>',
        scene=dict(
            xaxis_title='t-SNE 1',
            yaxis_title='t-SNE 2',
            zaxis_title='t-SNE 3',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        width=1200,
        height=900
    )
    
    output_tsne = output_path / "cv_embeddings_weighted_3d_tsne.html"
    fig_tsne.write_html(str(output_tsne))
    if logger:
        logger.log_success(f"t-SNE 3D salvato: {output_tsne}")
    
    # PCA 3D
    if logger:
        logger.log("Applicando PCA 3D...")
    pca = PCA(n_components=3)
    emb_3d_pca = pca.fit_transform(embeddings)
    variance = pca.explained_variance_ratio_
    
    fig_pca = go.Figure(data=[go.Scatter3d(
        x=emb_3d_pca[:, 0],
        y=emb_3d_pca[:, 1],
        z=emb_3d_pca[:, 2],
        mode='markers+text',
        marker=dict(
            size=12,
            color=np.arange(len(labels)),
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="CV Index"),
            line=dict(color='black', width=1)
        ),
        text=labels,
        textposition="top center",
        textfont=dict(size=10, color='black'),
        hovertext=hover_texts,
        hoverinfo='text'
    )])
    
    fig_pca.update_layout(
        title=f'Visualizzazione 3D Embeddings Pesati (PCA)<br><sub>Varianza: {sum(variance):.1%} | Weights: Skills 40%, Experience 40%, Education 15%, Summary 5%</sub>',
        scene=dict(
            xaxis_title=f'PC1 ({variance[0]:.1%})',
            yaxis_title=f'PC2 ({variance[1]:.1%})',
            zaxis_title=f'PC3 ({variance[2]:.1%})',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        width=1200,
        height=900
    )
    
    output_pca = output_path / "cv_embeddings_weighted_3d_pca.html"
    fig_pca.write_html(str(output_pca))
    if logger:
        logger.log_success(f"PCA 3D salvato: {output_pca}")
    
    return emb_3d_tsne, emb_3d_pca


def json_to_sections(json_data):
    """
    Converte JSON in sezioni separate per embedding pesati.
    Ritorna un dizionario con le 4 sezioni principali.
    """
    sections = {}
    
    # SEZIONE 1: SKILLS + TECHNOLOGIES (40%)
    skills_parts = []
    
    skills = json_data.get("skills", [])
    if skills:
        skills_str = ", ".join(skills)
        skills_parts.append(f"Competenze tecniche: {skills_str}")
    
    technologies = json_data.get("technologies", [])
    if technologies:
        tech_str = ", ".join(technologies)
        skills_parts.append(f"Tecnologie: {tech_str}")
    
    sections['skills'] = ". ".join(skills_parts) if skills_parts else "Nessuna competenza specificata"
    
    # SEZIONE 2: EXPERIENCE (40%)
    experience_parts = []
    
    experiences = json_data.get("experience", [])
    for exp in experiences:
        company = exp.get("company", "")
        period = exp.get("period", "")
        description = exp.get("description", "")
        
        exp_text = f"Esperienza presso {company}"
        if period:
            exp_text += f" ({period})"
        if description:
            exp_text += f": {description}"
        
        experience_parts.append(exp_text)
    
    sections['experience'] = ". ".join(experience_parts) if experience_parts else "Nessuna esperienza specificata"
    
    # SEZIONE 3: EDUCATION + CERTIFICATIONS (15%)
    education_parts = []
    
    education = json_data.get("education", {})
    if education.get("degree"):
        edu_text = f"Formazione: {education['degree']}"
        if education.get("program"):
            edu_text += f" in {education['program']}"
        if education.get("year"):
            edu_text += f" ({education['year']})"
        education_parts.append(edu_text)
    
    certifications = json_data.get("certifications", [])
    if certifications:
        cert_str = ", ".join(certifications)
        education_parts.append(f"Certificazioni: {cert_str}")
    
    sections['education'] = ". ".join(education_parts) if education_parts else "Nessuna formazione specificata"
    
    # SEZIONE 4: SUMMARY + TITLE (5%)
    summary_parts = []
    
    name = json_data.get("name", "")
    if name:
        summary_parts.append(f"Nome: {name}")
    
    title = json_data.get("title", "")
    if title:
        summary_parts.append(f"Ruolo: {title}")
    
    summary = json_data.get("summary", "")
    if summary:
        # Limita il summary a 150 caratteri per non pesare troppo
        summary_parts.append(f"Profilo: {summary[:150]}")
    
    sections['summary'] = ". ".join(summary_parts) if summary_parts else "Nessun sommario"
    
    return sections


def load_json_files_with_sections(json_folder=None, logger=None):
    """Carica JSON e crea sezioni separate"""
    json_path = Path(json_folder) if json_folder else BASE_DIR / "input" / "cv_json"
    
    if not json_path.exists():
        error_msg = f"Cartella non trovata: {json_folder}"
        if logger:
            logger.log_error(error_msg)
        return None
    
    json_files = list(json_path.glob("*.json"))
    
    if not json_files:
        error_msg = f"Nessun file JSON trovato in: {json_folder}"
        if logger:
            logger.log_error(error_msg)
        return None
    
    if logger:
        logger.log_section("CARICAMENTO FILE JSON CON SEZIONI PESATE")
        logger.log(f"Cartella: {json_folder}")
        logger.log(f"File JSON trovati: {len(json_files)}\n")
    
    cv_sections_list = []
    cv_labels = []
    cv_json_names = []
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converti in sezioni
            sections = json_to_sections(data)
            cv_sections_list.append(sections)
            
            # Label
            label = data.get("name", json_file.stem)
            cv_labels.append(label)
            cv_json_names.append(json_file.stem)
            
            if logger:
                logger.log_success(f"Caricato: {json_file.name}")
                logger.log(f"    Nome: {label}")
                logger.log(f"    Skills preview: {sections['skills'][:80]}...")
                logger.log(f"    Experience preview: {sections['experience'][:80]}...")
                logger.log("")
            
        except Exception as e:
            if logger:
                logger.log_error(f"Errore caricando {json_file.name}: {e}")
    
    if logger:
        logger.log(f"Totale CV caricati: {len(cv_sections_list)}/{len(json_files)}")
    
    return cv_sections_list, cv_labels, cv_json_names


def create_weighted_embeddings(cv_sections_list, model, weights=None, logger=None):
    """
    Crea embeddings pesati per ogni CV.
    
    Args:
        cv_sections_list: Lista di dizionari con sezioni {skills, experience, education, summary}
        model: Modello BGE-M3
        weights: Dict con pesi per ogni sezione (default: raccomandazioni della guida)
        logger: Logger per output
    
    Returns:
        embeddings_final: Array numpy con embeddings pesati finali
        embeddings_by_section: Dict con embeddings per ogni sezione (per analisi)
    """
    if weights is None:
        # Pesi raccomandati dalla guida
        weights = {
            'skills': 0.40,      # 40% - Matching tecnico diretto
            'experience': 0.40,  # 40% - Contesto e competenze implicite
            'education': 0.15,   # 15% - Qualificazioni formali
            'summary': 0.05      # 5% - Overview generale
        }
    
    if logger:
        logger.log_section("CREAZIONE EMBEDDINGS PESATI PER SEZIONE")
        logger.log("Pesi applicati:")
        for section, weight in weights.items():
            logger.log(f"  - {section}: {weight*100:.0f}%")
        logger.log("")
    
    num_cvs = len(cv_sections_list)
    
    # Dizionario per salvare embeddings per sezione
    embeddings_by_section = {}
    
    # Processa ogni sezione
    for section in ['skills', 'experience', 'education', 'summary']:
        if logger:
            logger.log(f"Generando embeddings per sezione: {section.upper()}")
        
        # Estrai testi di questa sezione per tutti i CV
        section_texts = [cv[section] for cv in cv_sections_list]
        
        # Genera embeddings
        section_embeddings = model.encode(section_texts, batch_size=32)['dense_vecs']
        
        embeddings_by_section[section] = section_embeddings
        
        if logger:
            logger.log(f"  Shape: {section_embeddings.shape}")
    
    # Combina con pesi
    if logger:
        logger.log("\nCombinazione embeddings con pesi...")
    
    # Inizializza array finale
    embedding_dim = embeddings_by_section['skills'].shape[1]
    embeddings_final = np.zeros((num_cvs, embedding_dim))
    
    # Somma pesata
    for section, weight in weights.items():
        embeddings_final += embeddings_by_section[section] * weight
    
    if logger:
        logger.log_success(f"Embeddings finali creati: shape={embeddings_final.shape}")
    
    return embeddings_final, embeddings_by_section


def main():
    logger = EmbeddingLogger()
    
    logger.log("="*80)
    logger.log("CREAZIONE EMBEDDINGS PESATI MULTI-SEZIONE")
    logger.log("Implementazione basata su: 'CV Matching Best Practices Guide'")
    logger.log("="*80 + "\n")
    
    # Carica JSON con sezioni
    result = load_json_files_with_sections("./cv_json", logger=logger)
    if result is None:
        logger.log_error("Impossibile caricare i CV. Uscita.")
        return
    
    cv_sections_list, cv_labels, cv_json_names = result
    
    if not cv_sections_list:
        logger.log_error("Nessun CV da processare. Uscita.")
        return
    
    # Riepilogo
    logger.log_section(f"RIEPILOGO CV CARICATI: {len(cv_sections_list)}")
    for i, (label, json_name) in enumerate(zip(cv_labels, cv_json_names), 1):
        logger.log(f"  {i}. {label} (file: {json_name}.json)")
    
    # Carica modello
    logger.log_section("CARICAMENTO MODELLO BGE-M3")
    try:
        logger.log("Inizializzazione modello...")
        model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
        logger.log_success("Modello caricato con successo!")
    except Exception as e:
        logger.log_error(f"Impossibile caricare il modello: {e}")
        return
    
    # Crea embeddings pesati
    start_time = datetime.now()
    
    embeddings_final, embeddings_by_section = create_weighted_embeddings(
        cv_sections_list, 
        model, 
        logger=logger
    )
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    logger.log_success(f"Tempo totale calcolo embeddings: {elapsed:.2f} secondi")
    
    # Salva file
    logger.log_section("SALVATAGGIO FILE NPY")
    EMB_DIR = BASE_DIR / "input" / "embeddings"
    EMB_DIR.mkdir(exist_ok=True, parents=True)
    try:
        # Embeddings finali pesati
        np.save(str(EMB_DIR / 'cv_embeddings.npy'), embeddings_final)
        logger.log_success("cv_embeddings.npy salvato (weighted final)")
        
        # Salva anche embeddings per sezione (per analisi avanzate)
        for section, emb in embeddings_by_section.items():
            filename = f'cv_embeddings_{section}.npy'
            np.save(str(EMB_DIR / f'cv_embeddings_{section}.npy'), emb)
            logger.log_success(f"{filename} salvato")
        
        # Labels
        np.save(str(EMB_DIR / 'cv_labels.npy'), np.array(cv_labels))
        logger.log_success("cv_labels.npy salvato")
        
        # JSON names
        np.save(str(EMB_DIR / 'cv_json_names.npy'), np.array(cv_json_names))
        logger.log_success("cv_json_names.npy salvato")
        
        # Salva anche le sezioni testuali per riferimento
        cv_texts_full = []
        for sections in cv_sections_list:
            full_text = f"{sections['skills']} {sections['experience']} {sections['education']} {sections['summary']}"
            cv_texts_full.append(full_text)
        
        np.save(str(EMB_DIR / 'cv_texts.npy'), np.array(cv_texts_full))
        logger.log_success("cv_texts.npy salvato")
        
    except Exception as e:
        logger.log_error(f"Errore durante il salvataggio: {e}")
        return
    
    # Riepilogo finale
    logger.log_section("ESECUZIONE COMPLETATA CON SUCCESSO")
    logger.log(f"Numero di CV processati: {len(cv_sections_list)}")
    logger.log(f"Dimensione embedding: {embeddings_final.shape[1]}")
    logger.log(f"Tempo totale: {elapsed:.2f} secondi")
    logger.log(f"Metodo: Weighted Multi-Section Embeddings")
    logger.log(f"\nPesi applicati:")
    logger.log(f"  - Skills + Technologies: 40%")
    logger.log(f"  - Experience: 40%")
    logger.log(f"  - Education + Certifications: 15%")
    logger.log(f"  - Summary + Title: 5%")
    logger.log(f"\nFile NPY creati:")
    logger.log(f"  - cv_embeddings.npy (embeddings finali pesati)")
    logger.log(f"  - cv_embeddings_skills.npy (solo skills)")
    logger.log(f"  - cv_embeddings_experience.npy (solo experience)")
    logger.log(f"  - cv_embeddings_education.npy (solo education)")
    logger.log(f"  - cv_embeddings_summary.npy (solo summary)")
    logger.log(f"  - cv_labels.npy")
    logger.log(f"  - cv_json_names.npy")
    logger.log(f"  - cv_texts.npy")
    
    # Menu visualizzazioni
    logger.log_section("OPZIONI VISUALIZZAZIONE")
    print("\n" + "="*80)
    print("MENU VISUALIZZAZIONI")
    print("="*80)
    print("1. Solo creazione embeddings (nessuna visualizzazione)")
    print("2. Embeddings + visualizzazione 2D")
    print("3. Embeddings + visualizzazione 3D")
    print("4. Embeddings + visualizzazioni 2D e 3D")
    print("="*80)
    
    choice = input("\nScegli opzione (1-4) [default: 1]: ").strip() or "1"
    logger.log(f"Opzione selezionata: {choice}", also_print=False)
    
    if choice == "2":
        create_visualization_2d(embeddings_final, cv_labels, output_folder=None, logger=logger)
    elif choice == "3":
        create_visualization_3d(embeddings_final, cv_labels, cv_sections_list, output_folder=None, logger=logger)
    elif choice == "4":
        create_visualization_2d(embeddings_final, cv_labels, output_folder=None, logger=logger)
        create_visualization_3d(embeddings_final, cv_labels, cv_sections_list, output_folder=None, logger=logger)
    else:
        logger.log("Nessuna visualizzazione richiesta")
    
    # Riepilogo finale esteso
    logger.log(f"\nLista CV processati:")
    for i, (label, json_name) in enumerate(zip(cv_labels, cv_json_names), 1):
        logger.log(f"  {i}. {label} (da {json_name}.json)")
    
    if choice in ["2", "4"]:
        logger.log(f"\nVisualizzazioni 2D:")
        logger.log(f"  - visualizations/cv_embeddings_weighted_2d_tsne.png")
    
    if choice in ["3", "4"]:
        logger.log(f"\nVisualizzazioni 3D:")
        logger.log(f"  - visualizations/cv_embeddings_weighted_3d_tsne.html")
        logger.log(f"  - visualizations/cv_embeddings_weighted_3d_pca.html")
    
    logger.log("="*80)
    logger.log(f"\n✓ Log salvato in: {logger.log_file}")
    logger.log("="*80)
    
    # Info aggiuntiva
    logger.log("\n" + "="*80)
    logger.log("NOTA: UTILIZZO DEGLI EMBEDDINGS")
    logger.log("="*80)
    logger.log("L'applicazione CV Search caricherà automaticamente:")
    logger.log("  - cv_embeddings.npy → embeddings pesati finali per ricerca")
    logger.log("\nPer analisi avanzate, sono disponibili anche:")
    logger.log("  - cv_embeddings_skills.npy → per matching tecnico puro")
    logger.log("  - cv_embeddings_experience.npy → per matching basato su esperienza")
    logger.log("  - etc.")
    logger.log("="*80)


if __name__ == "__main__":
    main()