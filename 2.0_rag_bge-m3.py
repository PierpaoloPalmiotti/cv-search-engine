# create_embeddings.py
from FlagEmbedding import BGEM3FlagModel
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class EmbeddingLogger:
    """Gestisce il logging su file con timestamp"""
    def __init__(self, log_folder="./log_executions"):
        self.log_folder = Path(log_folder)
        self.log_folder.mkdir(exist_ok=True, parents=True)
        
        # Crea nome file con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_folder / f"{timestamp}_embeddings_creation.txt"
        
        # Inizializza log
        self.log(f"{'='*80}")
        self.log(f"CREAZIONE EMBEDDINGS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*80}\n")
    
    def log(self, message, also_print=True):
        """Scrive su file e opzionalmente stampa"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
        if also_print:
            print(message)
    
    def log_section(self, title):
        """Log di una sezione con separatore"""
        separator = "="*80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(f"{separator}\n")
    
    def log_error(self, message):
        """Log di un errore"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ❌ ERRORE: {message}")
    
    def log_success(self, message):
        """Log di un successo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ✓ {message}")
    
    def log_warning(self, message):
        """Log di un warning"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ⚠ WARNING: {message}")

def json_to_text(json_data):
    """Converte un JSON in una stringa descrittiva per l'embedding"""
    parts = []
    
    # Nome (EID equivalente)
    if json_data.get("name"):
        parts.append(f"EID: {json_data['name']}")
    
    # Competenze
    skills = json_data.get("skills", [])
    if skills:
        skills_str = ", ".join(skills[:10])  # Limita a 10 per non essere troppo lungo
        parts.append(f"competenze: {skills_str}")
    
    # Tecnologie
    technologies = json_data.get("technologies", [])
    if technologies:
        tech_str = ", ".join(technologies[:10])
        parts.append(f"tecnologie: {tech_str}")
    
    # Formazione
    education = json_data.get("education", {})
    if education.get("degree"):
        parts.append(f"formazione: {education['degree']}")
    elif education.get("program"):
        parts.append(f"formazione: {education['program']}")
    else:
        parts.append("formazione: non specificata")
    
    # Certificazioni
    certifications = json_data.get("certifications", [])
    if certifications:
        cert_str = ", ".join(certifications[:5])
        parts.append(f"certificazioni: {cert_str}")
    else:
        parts.append("certificazioni: non specificate")
    
    # Esperienze (aziende)
    experiences = json_data.get("experience", [])
    if experiences:
        companies = [exp.get("company", "") for exp in experiences if exp.get("company")]
        if companies:
            industry_str = ", ".join(companies[:5])
            parts.append(f"industry: {industry_str}")
    
    # Titolo/Ruolo
    if json_data.get("title"):
        parts.append(f"ruolo: {json_data['title']}")
    
    # Summary (opzionale, solo primi 200 caratteri)
    if json_data.get("summary"):
        summary = json_data["summary"][:200]
        parts.append(f"profilo: {summary}")
    
    return ", ".join(parts)

def load_json_files(json_folder="./cv_json", logger=None):
    """Carica tutti i file JSON dalla cartella"""
    json_path = Path(json_folder)
    
    if not json_path.exists():
        error_msg = f"Cartella non trovata: {json_folder}"
        if logger:
            logger.log_error(error_msg)
        else:
            print(f"❌ {error_msg}")
        print("Creare la cartella e inserire i file JSON dei CV")
        return [], [], []
    
    json_files = list(json_path.glob("*.json"))
    
    if logger:
        logger.log_section("CARICAMENTO FILE JSON")
        logger.log(f"Cartella: {json_folder}")
        logger.log(f"File JSON trovati: {len(json_files)}\n")
    
    if not json_files:
        error_msg = f"Nessun file JSON trovato in: {json_folder}"
        if logger:
            logger.log_error(error_msg)
        else:
            print(f"❌ {error_msg}")
        return [], [], []
    
    cv_texts = []
    cv_labels = []
    cv_json_names = []
    
    # Lista tutti i file trovati
    if logger:
        logger.log("File JSON rilevati:")
        for i, json_file in enumerate(sorted(json_files), 1):
            logger.log(f"  {i}. {json_file.name}")
        logger.log("")
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Genera testo descrittivo
            text = json_to_text(data)
            cv_texts.append(text)
            
            # Usa il nome dal JSON o il nome del file
            label = data.get("name", json_file.stem)
            cv_labels.append(label)
            
            # Salva anche il nome del file JSON per riferimento
            cv_json_names.append(json_file.stem)
            
            if logger:
                logger.log_success(f"Caricato: {json_file.name}")
                logger.log(f"    Label: {label}")
                logger.log(f"    Preview: {text[:100]}...\n")
            else:
                print(f"✓ Caricato: {json_file.name}")
                print(f"  Label: {label}")
                print(f"  Preview: {text[:100]}...\n")
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON non valido in {json_file.name}: {e}"
            if logger:
                logger.log_error(error_msg)
            else:
                print(f"✗ {error_msg}\n")
        except Exception as e:
            error_msg = f"Errore caricando {json_file.name}: {e}"
            if logger:
                logger.log_error(error_msg)
            else:
                print(f"✗ {error_msg}\n")
    
    if logger:
        logger.log(f"\nTotale CV caricati con successo: {len(cv_texts)}/{len(json_files)}")
    
    return cv_texts, cv_labels, cv_json_names

def create_visualization_2d(embeddings, labels, output_folder="./visualizations", logger=None):
    """Crea visualizzazione 2D con matplotlib"""
    if logger:
        logger.log_section("CREAZIONE VISUALIZZAZIONE 2D")
    
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # t-SNE 2D
    if logger:
        logger.log("Applicando t-SNE 2D...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(3, len(embeddings)-1))
    embeddings_2d = tsne.fit_transform(embeddings)
    
    # Plot
    plt.figure(figsize=(12, 10))
    
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
    plt.title('Visualizzazione 2D degli Embeddings dei CV (t-SNE)', 
             fontsize=15, fontweight='bold', pad=20)
    plt.xlabel('Dimensione t-SNE 1', fontsize=12)
    plt.ylabel('Dimensione t-SNE 2', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Salva
    output_file = output_path / "cv_embeddings_2d_tsne.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    if logger:
        logger.log_success(f"Visualizzazione 2D salvata: {output_file}")
    
    plt.close()
    
    return embeddings_2d

def create_visualization_3d(embeddings, labels, texts, output_folder="./visualizations", logger=None):
    """Crea visualizzazioni 3D interattive con Plotly"""
    if logger:
        logger.log_section("CREAZIONE VISUALIZZAZIONI 3D")
    
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # t-SNE 3D
    if logger:
        logger.log("Applicando t-SNE 3D...")
    tsne_3d = TSNE(n_components=3, random_state=42, perplexity=min(3, len(embeddings)-1))
    emb_3d_tsne = tsne_3d.fit_transform(embeddings)
    
    # Hover text
    hover_texts = []
    for i, (label, text) in enumerate(zip(labels, texts)):
        hover_text = f"<b>{label}</b><br><br>{text[:200]}..."
        hover_texts.append(hover_text)
    
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
        title='Visualizzazione 3D degli Embeddings (t-SNE)',
        scene=dict(
            xaxis_title='t-SNE 1',
            yaxis_title='t-SNE 2',
            zaxis_title='t-SNE 3',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        width=1200,
        height=900
    )
    
    output_tsne = output_path / "cv_embeddings_3d_tsne.html"
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
        title=f'Visualizzazione 3D degli Embeddings (PCA)<br><sub>Varianza: {sum(variance):.1%}</sub>',
        scene=dict(
            xaxis_title=f'PC1 ({variance[0]:.1%})',
            yaxis_title=f'PC2 ({variance[1]:.1%})',
            zaxis_title=f'PC3 ({variance[2]:.1%})',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        width=1200,
        height=900
    )
    
    output_pca = output_path / "cv_embeddings_3d_pca.html"
    fig_pca.write_html(str(output_pca))
    if logger:
        logger.log_success(f"PCA 3D salvato: {output_pca}")
    
    return emb_3d_tsne, emb_3d_pca

def main():
    # Inizializza logger
    logger = EmbeddingLogger()
    
    logger.log("="*80)
    logger.log("CREAZIONE EMBEDDINGS DA FILE JSON")
    logger.log("="*80 + "\n")
    
    # Carica JSON dalla cartella
    cv_texts, cv_labels, cv_json_names = load_json_files("./cv_json", logger=logger)
    
    if not cv_texts:
        logger.log_error("Nessun CV da processare. Uscita.")
        logger.log("\n" + "="*80)
        logger.log("ESECUZIONE TERMINATA CON ERRORI")
        logger.log("="*80)
        return
    
    logger.log_section(f"RIEPILOGO CV CARICATI: {len(cv_texts)}")
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
    
    # Calcola embeddings
    logger.log_section("CALCOLO EMBEDDINGS")
    try:
        logger.log("Elaborazione in corso...")
        start_time = datetime.now()
        
        embeddings_cv = model.encode(cv_texts)['dense_vecs']
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        logger.log_success(f"Embeddings calcolati in {elapsed:.2f} secondi")
        logger.log(f"Shape: {embeddings_cv.shape}")
        logger.log(f"Dimensione: {embeddings_cv.shape[1]}")
        logger.log(f"Tipo: {embeddings_cv.dtype}")
    except Exception as e:
        logger.log_error(f"Errore durante il calcolo: {e}")
        return
    
    # Salva file
    logger.log_section("SALVATAGGIO FILE NPY")
    try:
        # Embeddings
        np.save('cv_embeddings.npy', embeddings_cv)
        logger.log_success("cv_embeddings.npy salvato")
        
        # Testi
        np.save('cv_texts.npy', np.array(cv_texts))
        logger.log_success("cv_texts.npy salvato")
        
        # Labels
        np.save('cv_labels.npy', np.array(cv_labels))
        logger.log_success("cv_labels.npy salvato")
        
        # JSON names
        np.save('cv_json_names.npy', np.array(cv_json_names))
        logger.log_success("cv_json_names.npy salvato")
        
    except Exception as e:
        logger.log_error(f"Errore durante il salvataggio: {e}")
        return
    
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
        create_visualization_2d(embeddings_cv, cv_labels, logger=logger)
    elif choice == "3":
        create_visualization_3d(embeddings_cv, cv_labels, cv_texts, logger=logger)
    elif choice == "4":
        create_visualization_2d(embeddings_cv, cv_labels, logger=logger)
        create_visualization_3d(embeddings_cv, cv_labels, cv_texts, logger=logger)
    else:
        logger.log("Nessuna visualizzazione richiesta")
    
    # Riepilogo finale
    logger.log_section("ESECUZIONE COMPLETATA CON SUCCESSO")
    logger.log(f"Numero di CV processati: {len(cv_texts)}")
    logger.log(f"Dimensione embedding: {embeddings_cv.shape[1]}")
    logger.log(f"Tempo calcolo embeddings: {elapsed:.2f} secondi")
    logger.log(f"\nFile NPY creati:")
    logger.log(f"  - cv_embeddings.npy")
    logger.log(f"  - cv_texts.npy")
    logger.log(f"  - cv_labels.npy")
    logger.log(f"  - cv_json_names.npy")
    
    if choice in ["2", "4"]:
        logger.log(f"\nVisualizzazioni 2D:")
        logger.log(f"  - visualizations/cv_embeddings_2d_tsne.png")
    
    if choice in ["3", "4"]:
        logger.log(f"\nVisualizzazioni 3D:")
        logger.log(f"  - visualizations/cv_embeddings_3d_tsne.html")
        logger.log(f"  - visualizations/cv_embeddings_3d_pca.html")
    
    logger.log(f"\nLista CV processati:")
    for i, (label, json_name) in enumerate(zip(cv_labels, cv_json_names), 1):
        logger.log(f"  {i}. {label} (da {json_name}.json)")
    logger.log("="*80)
    logger.log(f"\n✓ Log salvato in: {logger.log_file}")
    logger.log("="*80)

if __name__ == "__main__":
    main()
    """Gestisce il logging su file con timestamp"""
    def __init__(self, log_folder="./log_executions"):
        self.log_folder = Path(log_folder)
        self.log_folder.mkdir(exist_ok=True, parents=True)
        
        # Crea nome file con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_folder / f"{timestamp}_embeddings_creation.txt"
        
        # Inizializza log
        self.log(f"{'='*80}")
        self.log(f"CREAZIONE EMBEDDINGS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*80}\n")
    
    def log(self, message, also_print=True):
        """Scrive su file e opzionalmente stampa"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
        if also_print:
            print(message)
    
    def log_section(self, title):
        """Log di una sezione con separatore"""
        separator = "="*80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(f"{separator}\n")
    
    def log_error(self, message):
        """Log di un errore"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ❌ ERRORE: {message}")
    
    def log_success(self, message):
        """Log di un successo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ✓ {message}")
    
    def log_warning(self, message):
        """Log di un warning"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] ⚠ WARNING: {message}")

def json_to_text(json_data):
    """Converte un JSON in una stringa descrittiva per l'embedding"""
    parts = []
    
    # Nome (EID equivalente)
    if json_data.get("name"):
        parts.append(f"EID: {json_data['name']}")
    
    # Competenze
    skills = json_data.get("skills", [])
    if skills:
        skills_str = ", ".join(skills[:10])  # Limita a 10 per non essere troppo lungo
        parts.append(f"competenze: {skills_str}")
    
    # Tecnologie
    technologies = json_data.get("technologies", [])
    if technologies:
        tech_str = ", ".join(technologies[:10])
        parts.append(f"tecnologie: {tech_str}")
    
    # Formazione
    education = json_data.get("education", {})
    if education.get("degree"):
        parts.append(f"formazione: {education['degree']}")
    elif education.get("program"):
        parts.append(f"formazione: {education['program']}")
    else:
        parts.append("formazione: non specificata")
    
    # Certificazioni
    certifications = json_data.get("certifications", [])
    if certifications:
        cert_str = ", ".join(certifications[:5])
        parts.append(f"certificazioni: {cert_str}")
    else:
        parts.append("certificazioni: non specificate")
    
    # Esperienze (aziende)
    experiences = json_data.get("experience", [])
    if experiences:
        companies = [exp.get("company", "") for exp in experiences if exp.get("company")]
        if companies:
            industry_str = ", ".join(companies[:5])
            parts.append(f"industry: {industry_str}")
    
    # Titolo/Ruolo
    if json_data.get("title"):
        parts.append(f"ruolo: {json_data['title']}")
    
    # Summary (opzionale, solo primi 200 caratteri)
    if json_data.get("summary"):
        summary = json_data["summary"][:200]
        parts.append(f"profilo: {summary}")
    
    return ", ".join(parts)

def load_json_files(json_folder="./cv_json", logger=None):
    """Carica tutti i file JSON dalla cartella"""
    json_path = Path(json_folder)
    
    if not json_path.exists():
        error_msg = f"Cartella non trovata: {json_folder}"
        if logger:
            logger.log_error(error_msg)
        else:
            print(f"❌ {error_msg}")
        print("Creare la cartella e inserire i file JSON dei CV")
        return [], [], []
    
    json_files = list(json_path.glob("*.json"))
    
    if logger:
        logger.log_section("CARICAMENTO FILE JSON")
        logger.log(f"Cartella: {json_folder}")
        logger.log(f"File JSON trovati: {len(json_files)}\n")
    
    if not json_files:
        error_msg = f"Nessun file JSON trovato in: {json_folder}"
        if logger:
            logger.log_error(error_msg)
        else:
            print(f"❌ {error_msg}")
        return [], [], []
    
    cv_texts = []
    cv_labels = []
    cv_json_names = []
    
    # Lista tutti i file trovati
    if logger:
        logger.log("File JSON rilevati:")
        for i, json_file in enumerate(sorted(json_files), 1):
            logger.log(f"  {i}. {json_file.name}")
        logger.log("")
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Genera testo descrittivo
            text = json_to_text(data)
            cv_texts.append(text)
            
            # Usa il nome dal JSON o il nome del file
            label = data.get("name", json_file.stem)
            cv_labels.append(label)
            
            # Salva anche il nome del file JSON per riferimento
            cv_json_names.append(json_file.stem)
            
            if logger:
                logger.log_success(f"Caricato: {json_file.name}")
                logger.log(f"    Label: {label}")
                logger.log(f"    Preview: {text[:100]}...\n")
            else:
                print(f"✓ Caricato: {json_file.name}")
                print(f"  Label: {label}")
                print(f"  Preview: {text[:100]}...\n")
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON non valido in {json_file.name}: {e}"
            if logger:
                logger.log_error(error_msg)
            else:
                print(f"✗ {error_msg}\n")
        except Exception as e:
            error_msg = f"Errore caricando {json_file.name}: {e}"
            if logger:
                logger.log_error(error_msg)
            else:
                print(f"✗ {error_msg}\n")
    
    if logger:
        logger.log(f"\nTotale CV caricati con successo: {len(cv_texts)}/{len(json_files)}")
    
    return cv_texts, cv_labels, cv_json_names

def main():
    # Inizializza logger
    logger = EmbeddingLogger()
    
    logger.log("="*80)
    logger.log("CREAZIONE EMBEDDINGS DA FILE JSON")
    logger.log("="*80 + "\n")
    
    # Carica JSON dalla cartella
    cv_texts, cv_labels, cv_json_names = load_json_files("./cv_json", logger=logger)
    
    if not cv_texts:
        logger.log_error("Nessun CV da processare. Uscita.")
        logger.log("\n" + "="*80)
        logger.log("ESECUZIONE TERMINATA CON ERRORI")
        logger.log("="*80)
        return
    
    logger.log_section(f"RIEPILOGO CV CARICATI: {len(cv_texts)}")
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
    
    # Calcola embeddings
    logger.log_section("CALCOLO EMBEDDINGS")
    try:
        logger.log("Elaborazione in corso...")
        start_time = datetime.now()
        
        embeddings_cv = model.encode(cv_texts)['dense_vecs']
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        logger.log_success(f"Embeddings calcolati in {elapsed:.2f} secondi")
        logger.log(f"Shape: {embeddings_cv.shape}")
        logger.log(f"Dimensione: {embeddings_cv.shape[1]}")
        logger.log(f"Tipo: {embeddings_cv.dtype}")
    except Exception as e:
        logger.log_error(f"Errore durante il calcolo: {e}")
        return
    
    # Salva file
    logger.log_section("SALVATAGGIO FILE NPY")
    try:
        # Embeddings
        np.save('cv_embeddings.npy', embeddings_cv)
        logger.log_success("cv_embeddings.npy salvato")
        
        # Testi
        np.save('cv_texts.npy', np.array(cv_texts))
        logger.log_success("cv_texts.npy salvato")
        
        # Labels
        np.save('cv_labels.npy', np.array(cv_labels))
        logger.log_success("cv_labels.npy salvato")
        
        # JSON names
        np.save('cv_json_names.npy', np.array(cv_json_names))
        logger.log_success("cv_json_names.npy salvato")
        
    except Exception as e:
        logger.log_error(f"Errore durante il salvataggio: {e}")
        return
    
    # Riepilogo finale
    logger.log_section("ESECUZIONE COMPLETATA CON SUCCESSO")
    logger.log(f"Numero di CV processati: {len(cv_texts)}")
    logger.log(f"Dimensione embedding: {embeddings_cv.shape[1]}")
    logger.log(f"Tempo totale: {elapsed:.2f} secondi")
    logger.log(f"\nFile creati:")
    logger.log(f"  - cv_embeddings.npy (embeddings vettoriali)")
    logger.log(f"  - cv_texts.npy (testi descrittivi)")
    logger.log(f"  - cv_labels.npy (nomi candidati)")
    logger.log(f"  - cv_json_names.npy (nomi file JSON)")
    logger.log(f"\nLista CV processati:")
    for i, (label, json_name) in enumerate(zip(cv_labels, cv_json_names), 1):
        logger.log(f"  {i}. {label} (da {json_name}.json)")
    logger.log("="*80)
    logger.log(f"\n✓ Log salvato in: {logger.log_file}")
    logger.log("="*80)

if __name__ == "__main__":
    main()