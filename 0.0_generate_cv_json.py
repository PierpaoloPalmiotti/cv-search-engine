# generate_cv_json.py
"""
Generatore interattivo di JSON per CV.
Salva i profili nella cartella ./cv_json/ pronti per create_embeddings_weighted.py

Uso:
    python generate_cv_json.py              → Modalità interattiva (inserimento guidato)
    python generate_cv_json.py --list       → Elenca tutti i JSON esistenti
    python generate_cv_json.py --edit NOME  → Modifica un JSON esistente
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


# ── Configurazione ────────────────────────────────────────────
CV_JSON_FOLDER = Path("./cv_json")
CV_JSON_FOLDER.mkdir(exist_ok=True, parents=True)

TEMPLATE = {
    "name": "",
    "title": "",
    "Office": "",
    "Level": "",
    "summary": "",
    "skills": [],
    "technologies": [],
    "education": {
        "degree": "",
        "year": None,
        "program": ""
    },
    "certifications": [],
    "experience": []
}


# ── Utility ───────────────────────────────────────────────────

def clear_screen():
    print("\n" * 2)


def print_header(title):
    w = 70
    print(f"\n{'═' * w}")
    print(f"  {title}")
    print(f"{'═' * w}")


def print_section(title):
    print(f"\n{'─' * 50}")
    print(f"  📌 {title}")
    print(f"{'─' * 50}")


def input_required(prompt, allow_empty=False):
    """Input con validazione. Ripete finché non è valorizzato (se richiesto)."""
    while True:
        value = input(f"  {prompt}: ").strip()
        if value or allow_empty:
            return value
        print("  ⚠  Campo obbligatorio, riprova.")


def input_list(prompt, example=""):
    """Input per lista di valori separati da virgola."""
    hint = f" (es: {example})" if example else ""
    print(f"  {prompt}{hint}")
    print(f"  💡 Separa con virgola. Invio vuoto per terminare.\n")

    items = []
    while True:
        line = input(f"  → ").strip()
        if not line:
            break
        # Split su virgola, punto e virgola, pipe
        new_items = re.split(r'[,;|]', line)
        new_items = [i.strip() for i in new_items if i.strip()]
        items.extend(new_items)
        print(f"    ✓ Aggiunti: {', '.join(new_items)}")

    return list(dict.fromkeys(items))  # deduplica mantenendo ordine


def input_experience():
    """Input per una singola esperienza lavorativa."""
    print(f"\n  📋 Nuova esperienza:")
    company = input_required("  Azienda/Cliente", allow_empty=True)
    period = input_required("  Periodo (es: 2020-2023)", allow_empty=True)
    description = input_required("  Descrizione ruolo/attività", allow_empty=True)

    if not any([company, period, description]):
        return None

    return {
        "company": company,
        "period": period,
        "description": description
    }


def input_education():
    """Input per formazione."""
    print()
    degree = input_required("Titolo di studio (es: Laurea in Informatica)", allow_empty=True)
    program = input_required("Programma/Indirizzo", allow_empty=True)

    year_str = input_required("Anno conseguimento (es: 2018)", allow_empty=True)
    year = None
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            print(f"  ⚠  Anno non valido, impostato a null")
            year = None

    return {
        "degree": degree,
        "year": year,
        "program": program
    }


def name_to_filename(name):
    """Converte il nome in un filename sicuro."""
    clean = name.lower().strip()
    clean = re.sub(r'[^a-z0-9\s]', '', clean)
    clean = re.sub(r'\s+', '_', clean)
    return clean


def preview_json(data):
    """Mostra un'anteprima del JSON."""
    print_header("ANTEPRIMA JSON")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def save_json(data, filepath):
    """Salva il JSON su file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  ✅ Salvato: {filepath}")


# ── Raccolta dati completa ────────────────────────────────────

def collect_cv_data():
    """Raccoglie tutti i dati del CV in modo interattivo."""
    cv = json.loads(json.dumps(TEMPLATE))  # deep copy

    # ── ANAGRAFICA ──
    print_section("ANAGRAFICA")
    cv["name"] = input_required("Nome e Cognome")
    cv["title"] = input_required("Titolo/Ruolo professionale", allow_empty=True)
    cv["Office"] = input_required("Sede/Office (es: Milano, Roma)", allow_empty=True)
    cv["Level"] = input_required("Livello (es: Senior, Manager, Junior)", allow_empty=True)

    # ── SUMMARY ──
    print_section("PROFILO / SUMMARY")
    print("  Scrivi una breve descrizione del profilo professionale.")
    print("  💡 Puoi scrivere su più righe. Riga vuota per terminare.\n")

    summary_lines = []
    while True:
        line = input("  → ")
        if not line.strip():
            break
        summary_lines.append(line.strip())
    cv["summary"] = " ".join(summary_lines)

    # ── SKILLS ──
    print_section("SKILLS / COMPETENZE")
    cv["skills"] = input_list(
        "Inserisci le competenze:",
        example="Project Management, Data Analysis, Problem Solving"
    )

    # ── TECHNOLOGIES ──
    print_section("TECNOLOGIE")
    cv["technologies"] = input_list(
        "Inserisci le tecnologie:",
        example="Python, AWS, Docker, SQL, React"
    )

    # ── EDUCATION ──
    print_section("FORMAZIONE")
    cv["education"] = input_education()

    # ── CERTIFICATIONS ──
    print_section("CERTIFICAZIONI")
    cv["certifications"] = input_list(
        "Inserisci le certificazioni:",
        example="AWS Solutions Architect, PMP, ITIL"
    )

    # ── EXPERIENCE ──
    print_section("ESPERIENZE LAVORATIVE")
    print("  Inserisci le esperienze. Scrivi 'fine' o lascia vuoto per terminare.\n")

    experiences = []
    exp_num = 1
    while True:
        print(f"\n  ── Esperienza #{exp_num} ──")
        check = input("  Aggiungere un'esperienza? (s/n) [s]: ").strip().lower()
        if check in ('n', 'no', 'fine'):
            break

        exp = input_experience()
        if exp:
            experiences.append(exp)
            exp_num += 1
            print(f"    ✓ Esperienza aggiunta: {exp['company'] or 'N/A'}")
        else:
            print("    ⚠  Esperienza vuota, saltata.")
            break

    cv["experience"] = experiences

    return cv


# ── Modifica JSON esistente ───────────────────────────────────

def edit_cv(filepath):
    """Carica e modifica un JSON esistente."""
    with open(filepath, 'r', encoding='utf-8') as f:
        cv = json.load(f)

    print_header(f"MODIFICA: {cv.get('name', filepath.stem)}")
    preview_json(cv)

    FIELDS = {
        "1": ("name", "Nome e Cognome", "text"),
        "2": ("title", "Titolo/Ruolo", "text"),
        "3": ("Office", "Sede/Office", "text"),
        "4": ("Level", "Livello", "text"),
        "5": ("summary", "Summary/Profilo", "text"),
        "6": ("skills", "Skills", "list"),
        "7": ("technologies", "Tecnologie", "list"),
        "8": ("education", "Formazione", "education"),
        "9": ("certifications", "Certificazioni", "list"),
        "10": ("experience", "Esperienze", "experience"),
    }

    while True:
        print(f"\n{'─' * 50}")
        print("  Quale campo vuoi modificare?")
        print(f"{'─' * 50}")
        for key, (field, label, _) in FIELDS.items():
            current = cv.get(field, "")
            if isinstance(current, list):
                preview = f"[{len(current)} items]"
            elif isinstance(current, dict):
                preview = json.dumps(current, ensure_ascii=False)[:50]
            else:
                preview = str(current)[:50]
            print(f"  {key:>2}. {label:<20} → {preview}")

        print(f"   0. 💾 Salva e esci")
        print(f"   p. 👁  Anteprima")

        choice = input("\n  Scelta: ").strip()

        if choice == "0":
            break
        elif choice.lower() == "p":
            preview_json(cv)
            continue
        elif choice not in FIELDS:
            print("  ⚠  Scelta non valida.")
            continue

        field, label, field_type = FIELDS[choice]

        if field_type == "text":
            print(f"\n  Valore attuale: {cv.get(field, '')}")
            new_val = input(f"  Nuovo valore (invio per mantenere): ").strip()
            if new_val:
                cv[field] = new_val
                print(f"  ✓ Aggiornato.")

        elif field_type == "list":
            print(f"\n  Valori attuali: {cv.get(field, [])}")
            print("  a = aggiungi, r = riscrivi tutto, invio = mantieni")
            action = input("  Azione: ").strip().lower()

            if action == "a":
                new_items = input_list(f"Aggiungi a {label}:")
                cv[field] = list(dict.fromkeys(cv.get(field, []) + new_items))
                print(f"  ✓ Aggiunti {len(new_items)} items.")
            elif action == "r":
                cv[field] = input_list(f"Riscrivi {label}:")
                print(f"  ✓ Lista riscritta.")

        elif field_type == "education":
            print(f"\n  Valore attuale: {json.dumps(cv.get('education', {}), ensure_ascii=False)}")
            print("  Riscrivi la formazione:")
            cv["education"] = input_education()
            print(f"  ✓ Formazione aggiornata.")

        elif field_type == "experience":
            exps = cv.get("experience", [])
            print(f"\n  Esperienze attuali ({len(exps)}):")
            for i, exp in enumerate(exps, 1):
                print(f"    {i}. {exp.get('company', 'N/A')} ({exp.get('period', '')})")

            print("\n  a = aggiungi, d = elimina, r = riscrivi tutto, invio = mantieni")
            action = input("  Azione: ").strip().lower()

            if action == "a":
                exp = input_experience()
                if exp:
                    cv["experience"].append(exp)
                    print(f"  ✓ Esperienza aggiunta.")
            elif action == "d":
                idx_str = input(f"  Numero da eliminare (1-{len(exps)}): ").strip()
                try:
                    idx = int(idx_str) - 1
                    if 0 <= idx < len(exps):
                        removed = exps.pop(idx)
                        print(f"  ✓ Rimossa: {removed.get('company', 'N/A')}")
                except (ValueError, IndexError):
                    print("  ⚠  Indice non valido.")
            elif action == "r":
                cv["experience"] = []
                print("  Riscrivi le esperienze:")
                while True:
                    check = input("  Aggiungere? (s/n): ").strip().lower()
                    if check in ('n', 'no'):
                        break
                    exp = input_experience()
                    if exp:
                        cv["experience"].append(exp)

    save_json(cv, filepath)
    return cv


# ── Elenco JSON esistenti ─────────────────────────────────────

def list_existing():
    """Mostra tutti i JSON nella cartella."""
    files = sorted(CV_JSON_FOLDER.glob("*.json"))
    if not files:
        print("\n  📂 Nessun JSON trovato in", CV_JSON_FOLDER)
        return

    print_header(f"CV JSON ESISTENTI ({len(files)})")
    for i, f in enumerate(files, 1):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            name = data.get("name", "N/A")
            title = data.get("title", "")
            n_skills = len(data.get("skills", []))
            n_exp = len(data.get("experience", []))
            print(f"  {i:>3}. {f.name:<35} {name:<25} {title:<20} "
                  f"[{n_skills} skills, {n_exp} exp]")
        except Exception as e:
            print(f"  {i:>3}. {f.name:<35} ⚠ Errore: {e}")


# ── Menu principale ───────────────────────────────────────────

def main_menu():
    """Loop menu principale."""
    while True:
        print_header("GENERATE CV JSON - Menu Principale")
        print(f"  📂 Cartella: {CV_JSON_FOLDER.resolve()}\n")

        files = sorted(CV_JSON_FOLDER.glob("*.json"))
        print(f"  JSON esistenti: {len(files)}\n")

        print("  1. ➕ Crea nuovo profilo CV")
        print("  2. ✏️  Modifica profilo esistente")
        print("  3. 📋 Elenca tutti i profili")
        print("  4. 🔍 Cerca profilo per nome")
        print("  5. 📄 Duplica profilo (copia come base)")
        print("  0. 🚪 Esci")

        choice = input(f"\n  Scelta [1]: ").strip() or "1"

        if choice == "0":
            print("\n  👋 Arrivederci!\n")
            break

        elif choice == "1":
            # ── Crea nuovo ──
            print_header("NUOVO PROFILO CV")
            cv = collect_cv_data()

            # Anteprima
            preview_json(cv)

            # Conferma salvataggio
            confirm = input("\n  💾 Salvare? (s/n) [s]: ").strip().lower()
            if confirm in ('', 's', 'si', 'sì', 'y', 'yes'):
                filename = name_to_filename(cv["name"]) or "cv_senza_nome"
                filepath = CV_JSON_FOLDER / f"{filename}.json"

                # Verifica duplicato
                if filepath.exists():
                    overwrite = input(f"  ⚠  {filepath.name} esiste già. Sovrascrivere? (s/n): ").strip().lower()
                    if overwrite not in ('s', 'si', 'sì', 'y'):
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filepath = CV_JSON_FOLDER / f"{filename}_{ts}.json"
                        print(f"  → Salvato come: {filepath.name}")

                save_json(cv, filepath)
            else:
                print("  ❌ Salvataggio annullato.")

        elif choice == "2":
            # ── Modifica ──
            files = sorted(CV_JSON_FOLDER.glob("*.json"))
            if not files:
                print("\n  📂 Nessun profilo da modificare.")
                continue

            list_existing()
            idx_str = input(f"\n  Numero del profilo da modificare (1-{len(files)}): ").strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(files):
                    edit_cv(files[idx])
                else:
                    print("  ⚠  Indice fuori range.")
            except ValueError:
                print("  ⚠  Inserisci un numero valido.")

        elif choice == "3":
            list_existing()

        elif choice == "4":
            # ── Cerca ──
            search = input("\n  🔍 Nome da cercare: ").strip().lower()
            if not search:
                continue

            found = []
            for f in sorted(CV_JSON_FOLDER.glob("*.json")):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                    name = data.get("name", "").lower()
                    if search in name or search in f.stem.lower():
                        found.append((f, data))
                except Exception:
                    pass

            if found:
                print(f"\n  Trovati {len(found)} risultati:")
                for i, (f, data) in enumerate(found, 1):
                    print(f"  {i}. {data.get('name', 'N/A')} ({f.name})")

                action = input("\n  Modificare uno? (numero o invio per tornare): ").strip()
                try:
                    idx = int(action) - 1
                    if 0 <= idx < len(found):
                        edit_cv(found[idx][0])
                except (ValueError, IndexError):
                    pass
            else:
                print(f"  Nessun risultato per '{search}'.")

        elif choice == "5":
            # ── Duplica ──
            files = sorted(CV_JSON_FOLDER.glob("*.json"))
            if not files:
                print("\n  📂 Nessun profilo da duplicare.")
                continue

            list_existing()
            idx_str = input(f"\n  Numero del profilo da duplicare (1-{len(files)}): ").strip()
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(files):
                    with open(files[idx], 'r', encoding='utf-8') as fp:
                        cv = json.load(fp)

                    # Chiedi nuovo nome
                    new_name = input("  Nuovo nome per la copia: ").strip()
                    if new_name:
                        cv["name"] = new_name
                        filename = name_to_filename(new_name)
                    else:
                        filename = f"{files[idx].stem}_copia"

                    filepath = CV_JSON_FOLDER / f"{filename}.json"
                    save_json(cv, filepath)
                    print(f"  ✓ Duplicato come: {filepath.name}")
                    print(f"  💡 Usa 'Modifica' per aggiornare i dettagli.")
                else:
                    print("  ⚠  Indice fuori range.")
            except ValueError:
                print("  ⚠  Inserisci un numero valido.")

        else:
            print("  ⚠  Scelta non valida.")


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    # Gestione argomenti CLI
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == "--list":
            list_existing()
            sys.exit(0)

        elif arg == "--edit" and len(sys.argv) > 2:
            search_name = " ".join(sys.argv[2:]).lower()
            for f in sorted(CV_JSON_FOLDER.glob("*.json")):
                if search_name in f.stem.lower():
                    edit_cv(f)
                    sys.exit(0)
            print(f"  ⚠  Nessun profilo trovato per: {search_name}")
            sys.exit(1)

        elif arg == "--help":
            print(__doc__)
            sys.exit(0)

    # Modalità interattiva
    print_header("GENERATE CV JSON - Generatore Profili")
    print(f"  📂 Cartella output: {CV_JSON_FOLDER.resolve()}")
    print(f"  💡 Usa --help per opzioni CLI")
    main_menu()