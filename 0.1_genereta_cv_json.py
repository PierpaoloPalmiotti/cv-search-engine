# generate_cv_json.py
"""
Generatore GUI di JSON per CV con CustomTkinter.
Salva i profili nella cartella ./cv_json/ pronti per create_embeddings_weighted.py

Uso:
    python generate_cv_json.py
"""

import customtkinter as ctk
import json
import re
from pathlib import Path
from datetime import datetime
from tkinter import messagebox, filedialog

# ── Configurazione ────────────────────────────────────────────
CV_JSON_FOLDER = Path("./cv_json")
CV_JSON_FOLDER.mkdir(exist_ok=True, parents=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TEMPLATE = {
    "name": "", "title": "", "Office": "", "Level": "",
    "summary": "", "skills": [], "technologies": [],
    "education": {"degree": "", "year": None, "program": ""},
    "certifications": [],
    "experience": []
}


def name_to_filename(name):
    clean = name.lower().strip()
    clean = re.sub(r'[^a-z0-9\s]', '', clean)
    clean = re.sub(r'\s+', '_', clean)
    return clean or "cv_senza_nome"


# ══════════════════════════════════════════════════════════════
#  WIDGET: Lista editabile (per skills, technologies, certs)
# ══════════════════════════════════════════════════════════════

class EditableListWidget(ctk.CTkFrame):
    """Widget riutilizzabile per gestire una lista di stringhe."""

    def __init__(self, master, label, placeholder="Aggiungi elemento...", **kwargs):
        super().__init__(master, **kwargs)
        self.items = []

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header, text=label,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        self.count_label = ctk.CTkLabel(header, text="(0)", font=ctk.CTkFont(size=11),
                                        text_color="gray")
        self.count_label.pack(side="left", padx=5)

        # Riga input + bottone
        input_row = ctk.CTkFrame(self, fg_color="transparent")
        input_row.pack(fill="x", pady=(0, 5))

        self.entry = ctk.CTkEntry(input_row, placeholder_text=placeholder,
                                  font=ctk.CTkFont(size=11), height=32)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda e: self._add())

        ctk.CTkButton(input_row, text="＋", width=40, height=32,
                      command=self._add,
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="right")

        # Textbox per mostrare la lista
        self.listbox = ctk.CTkTextbox(self, height=80, font=ctk.CTkFont(size=10),
                                      corner_radius=6, state="disabled")
        self.listbox.pack(fill="x")

        # Bottoni sotto la lista
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(3, 0))

        ctk.CTkButton(btn_row, text="🗑 Rimuovi ultimo", width=130, height=28,
                      font=ctk.CTkFont(size=10),
                      fg_color=("#D32F2F", "#B71C1C"),
                      hover_color=("#B71C1C", "#7F0000"),
                      command=self._remove_last).pack(side="left")

        ctk.CTkButton(btn_row, text="🧹 Svuota", width=90, height=28,
                      font=ctk.CTkFont(size=10),
                      fg_color=("gray60", "gray30"),
                      hover_color=("gray50", "gray20"),
                      command=self._clear).pack(side="left", padx=5)

    def _add(self):
        text = self.entry.get().strip()
        if not text:
            return
        # Split su virgola per inserimenti multipli
        new_items = [i.strip() for i in re.split(r'[,;|]', text) if i.strip()]
        for item in new_items:
            if item not in self.items:
                self.items.append(item)
        self.entry.delete(0, "end")
        self._refresh()

    def _remove_last(self):
        if self.items:
            self.items.pop()
            self._refresh()

    def _clear(self):
        self.items.clear()
        self._refresh()

    def _refresh(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for i, item in enumerate(self.items, 1):
            self.listbox.insert("end", f"  {i}. {item}\n")
        self.listbox.configure(state="disabled")
        self.count_label.configure(text=f"({len(self.items)})")

    def get_items(self):
        return list(self.items)

    def set_items(self, items):
        self.items = list(items) if items else []
        self._refresh()


# ══════════════════════════════════════════════════════════════
#  WIDGET: Lista esperienze lavorative
# ══════════════════════════════════════════════════════════════

class ExperienceListWidget(ctk.CTkFrame):
    """Widget per gestire le esperienze lavorative."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.experiences = []

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header, text="💼 Esperienze Lavorative",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        self.count_label = ctk.CTkLabel(header, text="(0)",
                                        font=ctk.CTkFont(size=11), text_color="gray")
        self.count_label.pack(side="left", padx=5)

        # Form input
        form = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=8)
        form.pack(fill="x", pady=(0, 5))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(8, 3))

        ctk.CTkLabel(row1, text="Azienda:", font=ctk.CTkFont(size=10),
                     width=65).pack(side="left")
        self.company_entry = ctk.CTkEntry(row1, placeholder_text="Es: Accenture",
                                          font=ctk.CTkFont(size=11), height=30)
        self.company_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(row1, text="Periodo:", font=ctk.CTkFont(size=10),
                     width=55).pack(side="left")
        self.period_entry = ctk.CTkEntry(row1, placeholder_text="Es: 2020-2023",
                                         font=ctk.CTkFont(size=11), height=30, width=130)
        self.period_entry.pack(side="left")

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(0, 5))

        ctk.CTkLabel(row2, text="Descrizione:", font=ctk.CTkFont(size=10),
                     width=65).pack(side="left")
        self.desc_entry = ctk.CTkEntry(row2, placeholder_text="Ruolo e attività svolte",
                                       font=ctk.CTkFont(size=11), height=30)
        self.desc_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(row2, text="＋ Aggiungi", width=100, height=30,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self._add).pack(side="right")

        # Lista esperienze
        self.listbox = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(size=10),
                                      corner_radius=6, state="disabled")
        self.listbox.pack(fill="x")

        # Bottoni
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(3, 0))

        ctk.CTkButton(btn_row, text="🗑 Rimuovi ultima", width=130, height=28,
                      font=ctk.CTkFont(size=10),
                      fg_color=("#D32F2F", "#B71C1C"),
                      hover_color=("#B71C1C", "#7F0000"),
                      command=self._remove_last).pack(side="left")

        ctk.CTkButton(btn_row, text="🧹 Svuota", width=90, height=28,
                      font=ctk.CTkFont(size=10),
                      fg_color=("gray60", "gray30"),
                      hover_color=("gray50", "gray20"),
                      command=self._clear).pack(side="left", padx=5)

    def _add(self):
        company = self.company_entry.get().strip()
        period = self.period_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not any([company, period, desc]):
            return

        self.experiences.append({
            "company": company, "period": period, "description": desc
        })

        self.company_entry.delete(0, "end")
        self.period_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self._refresh()

    def _remove_last(self):
        if self.experiences:
            self.experiences.pop()
            self._refresh()

    def _clear(self):
        self.experiences.clear()
        self._refresh()

    def _refresh(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for i, exp in enumerate(self.experiences, 1):
            line = f"  {i}. {exp['company'] or 'N/A'}"
            if exp['period']:
                line += f" ({exp['period']})"
            if exp['description']:
                line += f" — {exp['description'][:60]}"
            self.listbox.insert("end", line + "\n")
        self.listbox.configure(state="disabled")
        self.count_label.configure(text=f"({len(self.experiences)})")

    def get_experiences(self):
        return list(self.experiences)

    def set_experiences(self, exps):
        self.experiences = list(exps) if exps else []
        self._refresh()


# ══════════════════════════════════════════════════════════════
#  APP PRINCIPALE
# ══════════════════════════════════════════════════════════════

class GenerateCVJsonApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CV JSON Generator")
        self.root.geometry("1100x850")

        self.current_file = None  # File JSON attualmente caricato

        self._build_ui()

    # ── Layout ────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top_bar = ctk.CTkFrame(self.root, corner_radius=0,
                               fg_color=("gray90", "gray13"), height=40)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="📝 CV JSON Generator",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15)

        self.status_label = ctk.CTkLabel(top_bar, text="Nuovo profilo",
                                         font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack(side="right", padx=15)

        # Toolbar bottoni
        toolbar = ctk.CTkFrame(self.root, fg_color="transparent", height=45)
        toolbar.pack(fill="x", padx=15, pady=(8, 0))

        ctk.CTkButton(toolbar, text="📂 Apri JSON", width=120, height=34,
                      font=ctk.CTkFont(size=11),
                      command=self._load_json).pack(side="left", padx=(0, 5))

        ctk.CTkButton(toolbar, text="📄 Nuovo", width=90, height=34,
                      font=ctk.CTkFont(size=11),
                      fg_color=("gray60", "gray35"),
                      hover_color=("gray50", "gray25"),
                      command=self._new_profile).pack(side="left", padx=(0, 5))

        ctk.CTkButton(toolbar, text="💾 Salva", width=90, height=34,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color=("#2E7D32", "#1B5E20"),
                      hover_color=("#1B5E20", "#0D3F10"),
                      command=self._save_json).pack(side="left", padx=(0, 5))

        ctk.CTkButton(toolbar, text="💾 Salva come...", width=120, height=34,
                      font=ctk.CTkFont(size=11),
                      fg_color=("#1565C0", "#0D47A1"),
                      hover_color=("#0D47A1", "#0A3A80"),
                      command=self._save_as_json).pack(side="left", padx=(0, 15))

        ctk.CTkButton(toolbar, text="👁 Anteprima", width=110, height=34,
                      font=ctk.CTkFont(size=11),
                      fg_color=("#6A1B9A", "#4A148C"),
                      hover_color=("#4A148C", "#38006B"),
                      command=self._show_preview).pack(side="left")

        # ── Profili esistenti (sidebar destra) ──
        self.profiles_list_var = ctk.StringVar(value="")
        existing = self._get_existing_profiles()

        profiles_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        profiles_frame.pack(side="right")

        ctk.CTkLabel(profiles_frame, text="Profili:",
                     font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 5))

        self.profiles_combo = ctk.CTkComboBox(
            profiles_frame,
            values=existing if existing else ["(nessuno)"],
            width=200, height=34,
            font=ctk.CTkFont(size=10),
            command=self._on_profile_selected
        )
        self.profiles_combo.pack(side="left")

        # ── Area scrollabile principale ──
        main_scroll = ctk.CTkScrollableFrame(self.root, corner_radius=10)
        main_scroll.pack(fill="both", expand=True, padx=15, pady=10)

        # Layout a 2 colonne
        main_scroll.grid_columnconfigure(0, weight=1, uniform="col")
        main_scroll.grid_columnconfigure(1, weight=1, uniform="col")

        # ════════ COLONNA SINISTRA ════════
        left = ctk.CTkFrame(main_scroll, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # -- Anagrafica --
        ana_frame = ctk.CTkFrame(left, corner_radius=8)
        ana_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(ana_frame, text="👤 Anagrafica",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", padx=10, pady=(10, 5))

        fields_data = [
            ("name", "Nome e Cognome *", "Es: Mario Rossi"),
            ("title", "Titolo / Ruolo", "Es: Cloud Architect"),
            ("office", "Sede / Office", "Es: Milano"),
            ("level", "Livello / Seniority", "Es: Senior, Manager"),
        ]

        self.fields = {}
        for key, label, ph in fields_data:
            ctk.CTkLabel(ana_frame, text=label,
                         font=ctk.CTkFont(size=10, weight="bold")).pack(
                anchor="w", padx=12, pady=(5, 0))
            entry = ctk.CTkEntry(ana_frame, placeholder_text=ph,
                                 font=ctk.CTkFont(size=11), height=32)
            entry.pack(fill="x", padx=12, pady=(0, 3))
            self.fields[key] = entry

        # -- Summary --
        ctk.CTkLabel(ana_frame, text="Profilo / Summary",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(
            anchor="w", padx=12, pady=(8, 0))
        self.summary_text = ctk.CTkTextbox(ana_frame, height=80,
                                           font=ctk.CTkFont(size=11),
                                           corner_radius=6)
        self.summary_text.pack(fill="x", padx=12, pady=(0, 10))

        # -- Formazione --
        edu_frame = ctk.CTkFrame(left, corner_radius=8)
        edu_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(edu_frame, text="🎓 Formazione",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", padx=10, pady=(10, 5))

        edu_fields_data = [
            ("edu_degree", "Titolo di studio", "Es: Laurea in Informatica"),
            ("edu_program", "Programma / Indirizzo", "Es: Ingegneria del Software"),
            ("edu_year", "Anno conseguimento", "Es: 2018"),
        ]

        self.edu_fields = {}
        for key, label, ph in edu_fields_data:
            ctk.CTkLabel(edu_frame, text=label,
                         font=ctk.CTkFont(size=10, weight="bold")).pack(
                anchor="w", padx=12, pady=(3, 0))
            entry = ctk.CTkEntry(edu_frame, placeholder_text=ph,
                                 font=ctk.CTkFont(size=11), height=30)
            entry.pack(fill="x", padx=12, pady=(0, 3))
            self.edu_fields[key] = entry

        # padding bottom
        ctk.CTkLabel(edu_frame, text="").pack(pady=2)

        # -- Esperienze --
        self.experience_widget = ExperienceListWidget(left)
        self.experience_widget.pack(fill="x", pady=(0, 10))

        # ════════ COLONNA DESTRA ════════
        right = ctk.CTkFrame(main_scroll, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # -- Skills --
        self.skills_widget = EditableListWidget(
            right, label="🛠 Skills / Competenze",
            placeholder="Es: Project Management, Agile, Leadership")
        self.skills_widget.pack(fill="x", pady=(0, 10))

        # -- Technologies --
        self.tech_widget = EditableListWidget(
            right, label="💻 Tecnologie",
            placeholder="Es: Python, AWS, Docker, Kubernetes")
        self.tech_widget.pack(fill="x", pady=(0, 10))

        # -- Certifications --
        self.cert_widget = EditableListWidget(
            right, label="📜 Certificazioni",
            placeholder="Es: AWS Solutions Architect, PMP")
        self.cert_widget.pack(fill="x", pady=(0, 10))

    # ── Helpers ───────────────────────────────────────────────

    def _get_existing_profiles(self):
        """Restituisce lista nomi dei JSON esistenti."""
        profiles = []
        for f in sorted(CV_JSON_FOLDER.glob("*.json")):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                name = data.get("name", f.stem)
                profiles.append(f"{name} ({f.name})")
            except Exception:
                profiles.append(f.name)
        return profiles

    def _refresh_profiles_combo(self):
        """Aggiorna la combo dei profili esistenti."""
        profiles = self._get_existing_profiles()
        self.profiles_combo.configure(values=profiles if profiles else ["(nessuno)"])

    def _on_profile_selected(self, choice):
        """Carica il profilo selezionato dalla combo."""
        # Estrai nome file dalla stringa "Nome (filename.json)"
        match = re.search(r'\((.+\.json)\)', choice)
        if match:
            filepath = CV_JSON_FOLDER / match.group(1)
            if filepath.exists():
                self._load_from_file(filepath)

    # ── Collect / Populate ────────────────────────────────────

    def _collect_data(self):
        """Raccoglie tutti i dati dalla GUI e ritorna il dizionario."""
        year_str = self.edu_fields["edu_year"].get().strip()
        year = None
        if year_str:
            try:
                year = int(year_str)
            except ValueError:
                pass

        return {
            "name": self.fields["name"].get().strip(),
            "title": self.fields["title"].get().strip(),
            "Office": self.fields["office"].get().strip(),
            "Level": self.fields["level"].get().strip(),
            "summary": self.summary_text.get("1.0", "end").strip(),
            "skills": self.skills_widget.get_items(),
            "technologies": self.tech_widget.get_items(),
            "education": {
                "degree": self.edu_fields["edu_degree"].get().strip(),
                "year": year,
                "program": self.edu_fields["edu_program"].get().strip(),
            },
            "certifications": self.cert_widget.get_items(),
            "experience": self.experience_widget.get_experiences(),
        }

    def _populate_form(self, data):
        """Popola tutti i campi della GUI dal dizionario JSON."""
        # Anagrafica
        field_map = {
            "name": data.get("name", ""),
            "title": data.get("title", ""),
            "office": data.get("Office", "") or data.get("office", ""),
            "level": data.get("Level", "") or data.get("level", ""),
        }
        for key, value in field_map.items():
            self.fields[key].delete(0, "end")
            self.fields[key].insert(0, value)

        # Summary
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", data.get("summary", ""))

        # Education
        edu = data.get("education", {})
        self.edu_fields["edu_degree"].delete(0, "end")
        self.edu_fields["edu_degree"].insert(0, edu.get("degree", ""))
        self.edu_fields["edu_program"].delete(0, "end")
        self.edu_fields["edu_program"].insert(0, edu.get("program", ""))
        self.edu_fields["edu_year"].delete(0, "end")
        if edu.get("year"):
            self.edu_fields["edu_year"].insert(0, str(edu["year"]))

        # Liste
        self.skills_widget.set_items(data.get("skills", []))
        self.tech_widget.set_items(data.get("technologies", []))
        self.cert_widget.set_items(data.get("certifications", []))

        # Esperienze
        self.experience_widget.set_experiences(data.get("experience", []))

    def _clear_form(self):
        """Svuota tutti i campi."""
        for entry in self.fields.values():
            entry.delete(0, "end")
        self.summary_text.delete("1.0", "end")
        for entry in self.edu_fields.values():
            entry.delete(0, "end")
        self.skills_widget.set_items([])
        self.tech_widget.set_items([])
        self.cert_widget.set_items([])
        self.experience_widget.set_experiences([])

    # ── Azioni ────────────────────────────────────────────────

    def _new_profile(self):
        """Reset completo per nuovo profilo."""
        if messagebox.askyesno("Nuovo profilo",
                               "Svuotare tutti i campi per un nuovo profilo?"):
            self._clear_form()
            self.current_file = None
            self.status_label.configure(text="Nuovo profilo", text_color="gray")

    def _save_json(self):
        """Salva il JSON (sovrascrive se già aperto, altrimenti crea nuovo)."""
        data = self._collect_data()

        if not data["name"]:
            messagebox.showwarning("Attenzione", "Il campo 'Nome e Cognome' è obbligatorio!")
            return

        if self.current_file and self.current_file.exists():
            filepath = self.current_file
        else:
            filename = name_to_filename(data["name"])
            filepath = CV_JSON_FOLDER / f"{filename}.json"

            if filepath.exists():
                if not messagebox.askyesno("File esistente",
                                           f"{filepath.name} esiste già.\nSovrascrivere?"):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = CV_JSON_FOLDER / f"{filename}_{ts}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.current_file = filepath
        self.status_label.configure(text=f"✅ Salvato: {filepath.name}",
                                    text_color="#2CC985")
        self._refresh_profiles_combo()
        messagebox.showinfo("Salvato", f"Profilo salvato in:\n{filepath}")

    def _save_as_json(self):
        """Salva con nome personalizzato."""
        data = self._collect_data()

        if not data["name"]:
            messagebox.showwarning("Attenzione", "Il campo 'Nome e Cognome' è obbligatorio!")
            return

        filepath = filedialog.asksaveasfilename(
            initialdir=str(CV_JSON_FOLDER),
            initialfile=f"{name_to_filename(data['name'])}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if not filepath:
            return

        filepath = Path(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.current_file = filepath
        self.status_label.configure(text=f"✅ Salvato: {filepath.name}",
                                    text_color="#2CC985")
        self._refresh_profiles_combo()
        messagebox.showinfo("Salvato", f"Profilo salvato in:\n{filepath}")

    def _load_json(self):
        """Apri un file JSON esistente."""
        filepath = filedialog.askopenfilename(
            initialdir=str(CV_JSON_FOLDER),
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            self._load_from_file(Path(filepath))

    def _load_from_file(self, filepath):
        """Carica un JSON e popola il form."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._populate_form(data)
            self.current_file = filepath
            self.status_label.configure(
                text=f"📂 {filepath.name}",
                text_color="#64B5F6")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare:\n{e}")

    def _show_preview(self):
        """Mostra anteprima JSON in finestra separata."""
        data = self._collect_data()

        preview_win = ctk.CTkToplevel(self.root)
        preview_win.title("Anteprima JSON")
        preview_win.geometry("600x700")
        preview_win.transient(self.root)
        preview_win.grab_set()

        ctk.CTkLabel(preview_win, text="👁 Anteprima JSON",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        textbox = ctk.CTkTextbox(preview_win, font=ctk.CTkFont(family="Courier", size=11),
                                 corner_radius=8)
        textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        textbox.insert("1.0", json.dumps(data, ensure_ascii=False, indent=2))
        textbox.configure(state="disabled")

        ctk.CTkButton(preview_win, text="Chiudi", width=100,
                      command=preview_win.destroy).pack(pady=(0, 15))

    # ── Run ───────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    app = GenerateCVJsonApp()
    app.run()