# cv_creator_app.py
"""
CV Creator - Interfaccia per creare JSON strutturati da testo libero
Usa LLM locale (Ollama) per estrarre informazioni e generare JSON
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import requests
from pathlib import Path
from datetime import datetime
import re

# Configura tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Logger:
    """Logger semplice per debug"""
    def __init__(self, log_file="cv_creator_log.txt"):
        self.log_file = log_file
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{log_msg}\n")


class CVCreatorApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CV Creator - Da Testo a JSON")
        self.root.geometry("1400x900")
        
        self.logger = Logger()
        self.selected_llm = "llama3.2:3b"  # Default
        self.output_folder = Path("./cv_json")
        self.output_folder.mkdir(exist_ok=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=("gray90", "gray13"), height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 CV Creator - Genera JSON da Testo Libero",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=15)
        
        # ===== MAIN CONTENT =====
        content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Layout a 2 colonne
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # ===== COLONNA SINISTRA: INPUT =====
        left_column = ctk.CTkFrame(content_frame, corner_radius=10)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Header input
        input_header = ctk.CTkFrame(left_column, fg_color=("gray85", "gray17"), corner_radius=8)
        input_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            input_header,
            text="✏️ Inserisci Informazioni CV (testo libero)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=8)
        
        # Info box con esempio
        info_frame = ctk.CTkFrame(left_column, fg_color=("gray90", "gray20"), corner_radius=8)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        info_text = """💡 Scrivi liberamente! Esempi:

"Mi chiamo Mario Rossi, sono un senior developer con 8 anni di esperienza. 
Conosco Python, Java, AWS, Docker. Ho lavorato in Accenture dal 2018 al 2023 
come backend developer su progetti banking. Laurea in Informatica nel 2015. 
Certificato AWS Solutions Architect."

Oppure in formato CV tradizionale, bullet points, ecc."""

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=9),
            justify="left",
            anchor="w"
        ).pack(padx=10, pady=8, fill="x")
        
        # Text input area
        self.input_text = ctk.CTkTextbox(
            left_column,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            wrap="word"
        )
        self.input_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # ===== CONTROLLI =====
        controls_frame = ctk.CTkFrame(left_column, fg_color=("gray90", "gray20"), corner_radius=8)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Selezione LLM
        ctk.CTkLabel(
            controls_frame,
            text="🤖 Modello LLM:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 2))
        
        self.llm_var = ctk.StringVar(value="llama3.2:3b (Raccomandato)")
        self.llm_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.llm_var,
            values=[
                "llama3.2:1b (Veloce, meno accurato)",
                "llama3.2:3b (Raccomandato)",
                "mistral:7b (Più accurato, più lento)",
                "phi3:mini (Alternativa efficiente)"
            ],
            command=self.on_llm_selected,
            font=ctk.CTkFont(size=10),
            height=32
        )
        self.llm_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Bottone genera
        self.generate_button = ctk.CTkButton(
            controls_frame,
            text="🚀 Genera JSON",
            command=self.generate_json,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=8,
            fg_color=("#2E7D32", "#1B5E20"),
            hover_color=("#1B5E20", "#0D3F10")
        )
        self.generate_button.pack(fill="x", padx=10, pady=(0, 10))
        
        # ===== COLONNA DESTRA: OUTPUT =====
        right_column = ctk.CTkFrame(content_frame, corner_radius=10)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Header output
        output_header = ctk.CTkFrame(right_column, fg_color=("gray85", "gray17"), corner_radius=8)
        output_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            output_header,
            text="📄 JSON Generato",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=8)
        
        # Output textbox
        self.output_text = ctk.CTkTextbox(
            right_column,
            font=ctk.CTkFont(family="Courier", size=10),
            corner_radius=8,
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.output_text.configure(state="disabled")
        
        # Bottoni azioni
        actions_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        self.save_button = ctk.CTkButton(
            actions_frame,
            text="💾 Salva JSON",
            command=self.save_json,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            state="disabled"
        )
        self.save_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.copy_button = ctk.CTkButton(
            actions_frame,
            text="📋 Copia JSON",
            command=self.copy_json,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            state="disabled"
        )
        self.copy_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # ===== STATUS BAR =====
        status_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=("gray90", "gray13"), height=40)
        status_frame.pack(fill="x", padx=0, pady=0)
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="✅ Pronto. Scrivi le informazioni CV e premi 'Genera JSON'",
            font=ctk.CTkFont(size=11),
            text_color="#2CC985"
        )
        self.status_label.pack(pady=10)
    
    def on_llm_selected(self, choice):
        """Callback selezione LLM"""
        model_map = {
            "llama3.2:1b (Veloce, meno accurato)": "llama3.2:1b",
            "llama3.2:3b (Raccomandato)": "llama3.2:3b",
            "mistral:7b (Più accurato, più lento)": "mistral:7b",
            "phi3:mini (Alternativa efficiente)": "phi3:mini"
        }
        self.selected_llm = model_map.get(choice, "llama3.2:3b")
        self.logger.log(f"Modello LLM selezionato: {self.selected_llm}")
    
    def extract_json_from_llm(self, text):
        """Estrae informazioni strutturate usando LLM locale"""
        
        prompt = f"""Sei un assistente che estrae informazioni da CV in formato JSON.

TESTO CV:
{text}

Estrai le seguenti informazioni e restituisci SOLO un JSON valido (senza markdown, senza spiegazioni):

{{
  "name": "Nome Cognome completo",
  "title": "Ruolo/Job Title principale",
  "summary": "Breve summary professionale (2-3 frasi)",
  "skills": ["skill1", "skill2", ...],
  "technologies": ["tech1", "tech2", ...],
  "experience": [
    {{
      "company": "Nome azienda",
      "period": "YYYY-YYYY o YYYY-present",
      "description": "Descrizione ruolo/progetto",
      "location": "Città (se presente)",
      "responsibilities": "Responsabilità principali",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "education": {{
    "degree": "Titolo di studio",
    "program": "Corso di laurea",
    "institution": "Università",
    "year": 2020
  }},
  "certifications": ["Cert1", "Cert2", ...],
  "languages": ["Italiano (madrelingua)", "Inglese (fluente)"]
}}

REGOLE IMPORTANTI:
1. Estrai SOLO informazioni presenti nel testo
2. Se un campo non è presente, usa stringa vuota "" o array vuoto []
3. Per skills: separa competenze soft (comunicazione, leadership) da tecnologie
4. Per technologies: solo tecnologie/tool specifici (Python, AWS, Docker, ecc.)
5. Per experience: se mancano date usa "N/A", descrizione dettagliata
6. Restituisci SOLO il JSON, niente altro

JSON:"""

        try:
            self.status_label.configure(
                text="⏳ Elaborazione con LLM in corso...",
                text_color="orange"
            )
            self.root.update()
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": self.selected_llm,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Bassa per output consistente
                        "num_predict": 2000,  # Più lungo per CV completi
                        "num_ctx": 4096
                    }
                },
                timeout=180
            )
            
            if response.status_code == 200:
                llm_output = response.json()['response'].strip()
                
                # Pulisci output (rimuovi markdown, testo extra)
                llm_output = llm_output.replace("```json", "").replace("```", "")
                
                # Trova JSON
                json_start = llm_output.find('{')
                json_end = llm_output.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = llm_output[json_start:json_end]
                    
                    # Valida JSON
                    cv_data = json.loads(json_str)
                    
                    # Validazione campi obbligatori
                    if not cv_data.get("name"):
                        cv_data["name"] = "Nome Non Specificato"
                    
                    self.logger.log(f"JSON estratto con successo: {cv_data.get('name', 'N/A')}")
                    return cv_data, None
                else:
                    return None, "LLM non ha restituito JSON valido"
            else:
                return None, f"Errore API LLM: status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return None, "Ollama non disponibile. Verifica che sia in esecuzione."
        except requests.exceptions.Timeout:
            return None, "Timeout: il modello sta impiegando troppo tempo."
        except json.JSONDecodeError as e:
            return None, f"Errore parsing JSON: {e}\n\nOutput LLM:\n{llm_output[:500]}"
        except Exception as e:
            return None, f"Errore: {str(e)}"
    
    def generate_json(self):
        """Genera JSON da testo input"""
        input_text = self.input_text.get("1.0", "end").strip()
        
        if not input_text or len(input_text) < 50:
            messagebox.showwarning(
                "Attenzione",
                "Inserisci almeno 50 caratteri di informazioni CV!"
            )
            return
        
        # Disabilita bottone
        self.generate_button.configure(state="disabled", text="⏳ Elaborazione...")
        self.root.update()
        
        self.logger.log(f"=== INIZIO GENERAZIONE JSON ===")
        self.logger.log(f"Lunghezza input: {len(input_text)} caratteri")
        self.logger.log(f"Modello: {self.selected_llm}")
        
        # Estrai JSON con LLM
        cv_data, error = self.extract_json_from_llm(input_text)
        
        if error:
            messagebox.showerror("Errore", error)
            self.status_label.configure(
                text=f"❌ Errore: {error[:50]}...",
                text_color="red"
            )
            self.generate_button.configure(state="normal", text="🚀 Genera JSON")
            self.logger.log(f"Errore: {error}", )
            return
        
        # Formatta JSON per output
        json_output = json.dumps(cv_data, indent=2, ensure_ascii=False)
        
        # Mostra output
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", json_output)
        self.output_text.configure(state="disabled")
        
        # Abilita bottoni
        self.save_button.configure(state="normal")
        self.copy_button.configure(state="normal")
        self.generate_button.configure(state="normal", text="🚀 Genera JSON")
        
        # Salva temporaneamente per il salvataggio
        self.current_json = cv_data
        
        self.status_label.configure(
            text=f"✅ JSON generato! Candidato: {cv_data.get('name', 'N/A')}",
            text_color="#2CC985"
        )
        
        self.logger.log(f"=== JSON GENERATO CON SUCCESSO ===")
        self.logger.log(f"Nome: {cv_data.get('name', 'N/A')}")
        self.logger.log(f"Skills: {len(cv_data.get('skills', []))} items")
        self.logger.log(f"Esperienze: {len(cv_data.get('experience', []))} items")
    
    def save_json(self):
        """Salva JSON su file"""
        if not hasattr(self, 'current_json'):
            messagebox.showwarning("Attenzione", "Nessun JSON da salvare!")
            return
        
        # Genera nome file da nome candidato
        name = self.current_json.get('name', 'CV_Unknown')
        # Normalizza nome file
        filename = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
        filename = f"CV_{filename}.json"
        
        # Chiedi conferma/modifica nome
        filepath = filedialog.asksaveasfilename(
            initialdir=self.output_folder,
            initialfile=filename,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return  # Utente ha annullato
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_json, f, indent=2, ensure_ascii=False)
            
            self.logger.log(f"JSON salvato: {filepath}")
            self.status_label.configure(
                text=f"✅ JSON salvato: {Path(filepath).name}",
                text_color="#2CC985"
            )
            
            messagebox.showinfo(
                "Successo!",
                f"JSON salvato con successo:\n\n{Path(filepath).name}\n\nCartella: {Path(filepath).parent}"
            )
            
        except Exception as e:
            error_msg = f"Errore salvataggio: {e}"
            self.logger.log(error_msg)
            messagebox.showerror("Errore", error_msg)
    
    def copy_json(self):
        """Copia JSON negli appunti"""
        json_text = self.output_text.get("1.0", "end").strip()
        
        if not json_text:
            messagebox.showwarning("Attenzione", "Nessun JSON da copiare!")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(json_text)
            self.status_label.configure(
                text="✅ JSON copiato negli appunti!",
                text_color="#2CC985"
            )
            self.logger.log("JSON copiato negli appunti")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile copiare: {e}")
    
    def run(self):
        """Avvia applicazione"""
        self.root.mainloop()


def main():
    app = CVCreatorApp()
    app.run()


if __name__ == "__main__":
    main()

#```

#---

# ## 🎯 Funzionalità

# ### **1. Input Testo Libero**
# ```
# "Mi chiamo Mario Rossi, sono un senior Python developer con 8 anni 
# di esperienza. Ho lavorato in Accenture dal 2018 al 2023 su progetti 
# banking. Conosco Python, AWS, Docker, Kubernetes. Laurea in Informatica 
# nel 2015. Certificato AWS Solutions Architect."