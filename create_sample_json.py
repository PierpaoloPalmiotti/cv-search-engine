#!/usr/bin/env python3
"""
Genera 10 CV JSON di esempio per testare il sistema.
Eseguire una sola volta dalla root del progetto:
    python generate_sample_cvs.py
"""
import json
from pathlib import Path

OUTPUT_DIR = Path("input/cv_json")

SAMPLE_CVS = [
    {
        "name": "Marco Bianchi",
        "title": "Data Engineer Senior",
        "Office": "Milano",
        "Level": "Senior",
        "summary": "8 anni di esperienza nella progettazione e implementazione di pipeline dati su cloud. Specializzato in architetture big data e real-time streaming per il settore bancario e assicurativo.",
        "skills": ["Data Modeling", "ETL Design", "Data Governance", "Agile", "Problem Solving", "Team Leadership"],
        "technologies": ["Python", "Apache Spark", "AWS", "Terraform", "SQL", "Kafka", "Airflow", "Docker", "PostgreSQL", "Redshift"],
        "education": {
            "degree": "Laurea Magistrale in Ingegneria Informatica",
            "year": 2016,
            "program": "Politecnico di Milano"
        },
        "certifications": ["AWS Solutions Architect Associate", "Databricks Certified Data Engineer"],
        "experience": [
            {
                "company": "Accenture",
                "period": "2021-2025",
                "description": "Progettazione e sviluppo di data lake su AWS per primario gruppo bancario italiano. Gestione team di 5 persone, migrazione da on-premise a cloud."
            },
            {
                "company": "Deloitte",
                "period": "2018-2021",
                "description": "Sviluppo pipeline ETL con Apache Spark per clienti nel settore insurance. Implementazione di architetture lambda per processing real-time."
            },
            {
                "company": "Capgemini",
                "period": "2016-2018",
                "description": "Junior data engineer su progetti di Business Intelligence per il settore retail. Sviluppo report e dashboard con SQL e Python."
            }
        ]
    },
    {
        "name": "Laura Rossi",
        "title": "Cloud Architect",
        "Office": "Roma",
        "Level": "Senior",
        "summary": "10 anni di esperienza in architetture cloud ibride e multi-cloud. Forte background in sicurezza e compliance per la pubblica amministrazione e il settore energy.",
        "skills": ["Cloud Architecture", "Solution Design", "DevOps", "Security", "Cost Optimization", "Stakeholder Management", "ITIL"],
        "technologies": ["Microsoft Azure", "AWS", "Kubernetes", "Docker", "Terraform", "Ansible", "Python", "PowerShell", "Jenkins", "Git"],
        "education": {
            "degree": "Laurea Magistrale in Informatica",
            "year": 2014,
            "program": "Università La Sapienza, Roma"
        },
        "certifications": ["Azure Solutions Architect Expert", "AWS Solutions Architect Professional", "TOGAF 9 Certified"],
        "experience": [
            {
                "company": "Eni",
                "period": "2022-2025",
                "description": "Lead architect per la migrazione multi-cloud dell'infrastruttura globale. Coordinamento team internazionale di 12 persone tra Italia, Francia e UK."
            },
            {
                "company": "Accenture",
                "period": "2018-venv\Scripts\activate2022",
                "description": "Cloud architect per progetti di digital transformation nella pubblica amministrazione. Progettazione architetture conformi a requisiti AgID."
            },
            {
                "company": "IBM",
                "period": "2014-2018",
                "description": "System engineer su infrastrutture cloud private. Implementazione soluzioni di disaster recovery e high availability."
            }
        ]
    },
    {
        "name": "Alessandro Ferraro",
        "title": "Machine Learning Engineer",
        "Office": "Milano",
        "Level": "Middle",
        "summary": "5 anni di esperienza nello sviluppo di modelli ML/AI per applicazioni enterprise. Specializzato in NLP e computer vision per il settore finanziario.",
        "skills": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "MLOps", "Data Analysis", "Agile"],
        "technologies": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Google Cloud Platform", "BigQuery", "VertexAI", "Docker", "Kubernetes", "Git"],
        "education": {
            "degree": "Laurea Magistrale in Data Science",
            "year": 2019,
            "program": "Università degli Studi di Milano-Bicocca"
        },
        "certifications": ["Google Professional Machine Learning Engineer", "TensorFlow Developer Certificate"],
        "experience": [
            {
                "company": "Reply",
                "period": "2022-2025",
                "description": "Sviluppo modelli NLP per analisi automatica di documenti finanziari. Deploy su GCP con pipeline MLOps su Vertex AI."
            },
            {
                "company": "Jakala",
                "period": "2019-2022",
                "description": "Sviluppo modelli predittivi per customer churn e recommendation engine nel settore retail. Utilizzo di tecniche di deep learning su dati tabellari."
            }
        ]
    },
    {
        "name": "Giulia Conti",
        "title": "SAP Consultant",
        "Office": "Torino",
        "Level": "Senior",
        "summary": "9 anni di esperienza in consulenza SAP con focus su moduli FI/CO e S/4HANA. Gestione di progetti di migrazione e roll-out internazionali nel settore manufacturing.",
        "skills": ["SAP FI/CO", "SAP S/4HANA", "Business Process Reengineering", "Project Management", "Change Management", "Functional Analysis", "ABAP Basics"],
        "technologies": ["SAP ECC", "SAP S/4HANA", "SAP BW", "SAP Fiori", "SQL", "Excel Advanced", "Power BI", "JIRA", "ServiceNow"],
        "education": {
            "degree": "Laurea Magistrale in Economia e Management",
            "year": 2015,
            "program": "Università di Torino"
        },
        "certifications": ["SAP Certified Application Associate - S/4HANA Finance", "PMP - Project Management Professional", "ITIL v4 Foundation"],
        "experience": [
            {
                "company": "EY",
                "period": "2021-2025",
                "description": "Lead consultant per migrazione SAP S/4HANA di gruppo industriale multinazionale. Coordinamento workstream FI/CO su 8 country roll-out."
            },
            {
                "company": "Accenture",
                "period": "2017-2021",
                "description": "SAP FI/CO consultant per clienti nel settore automotive e manufacturing. Customizing, test e go-live su 3 progetti di implementazione."
            },
            {
                "company": "Altea UP",
                "period": "2015-2017",
                "description": "Junior SAP consultant. Supporto funzionale post go-live e formazione utenti su moduli FI/CO."
            }
        ]
    },
    {
        "name": "Davide Moretti",
        "title": "Full Stack Developer",
        "Office": "Napoli",
        "Level": "Middle",
        "summary": "4 anni di esperienza nello sviluppo di applicazioni web e mobile. Appassionato di architetture microservizi e DevOps. Esperienza nel settore e-commerce e fintech.",
        "skills": ["Full Stack Development", "REST API Design", "Microservices", "CI/CD", "Agile/Scrum", "Code Review"],
        "technologies": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "FastAPI", "PostgreSQL", "MongoDB", "Docker", "AWS", "Git", "GitHub Actions"],
        "education": {
            "degree": "Laurea Triennale in Informatica",
            "year": 2020,
            "program": "Università Federico II, Napoli"
        },
        "certifications": ["AWS Cloud Practitioner", "Meta Front-End Developer Certificate"],
        "experience": [
            {
                "company": "Fineco",
                "period": "2023-2025",
                "description": "Sviluppo di microservizi backend in Python/FastAPI e frontend React per piattaforma di trading. Implementazione CI/CD con GitHub Actions."
            },
            {
                "company": "Almaviva",
                "period": "2020-2023",
                "description": "Sviluppo applicazioni web per la pubblica amministrazione. Stack MERN (MongoDB, Express, React, Node.js). Integrazione con sistemi SPID e PagoPA."
            }
        ]
    },
    {
        "name": "Francesca De Luca",
        "title": "Business Intelligence Analyst",
        "Office": "Roma",
        "Level": "Middle",
        "summary": "5 anni di esperienza in analisi dati e reportistica avanzata. Specializzata in Power BI e Tableau per il settore pharma e healthcare.",
        "skills": ["Data Analysis", "Data Visualization", "KPI Design", "Storytelling", "SQL Advanced", "Stakeholder Management", "Agile"],
        "technologies": ["Power BI", "Tableau", "SQL Server", "Python", "Excel Advanced", "Azure Data Factory", "SSIS", "DAX", "Power Query"],
        "education": {
            "degree": "Laurea Magistrale in Statistica",
            "year": 2019,
            "program": "Università di Roma Tor Vergata"
        },
        "certifications": ["Microsoft Certified: Power BI Data Analyst Associate", "Tableau Desktop Specialist"],
        "experience": [
            {
                "company": "Pfizer",
                "period": "2022-2025",
                "description": "BI analyst per il dipartimento commercial excellence. Sviluppo dashboard Power BI per monitoraggio KPI di vendita su mercato italiano ed europeo."
            },
            {
                "company": "KPMG",
                "period": "2019-2022",
                "description": "Data analyst per clienti nel settore healthcare e insurance. Sviluppo reportistica con Tableau e SQL per analisi costi e performance."
            }
        ]
    },
    {
        "name": "Simone Greco",
        "title": "Cybersecurity Specialist",
        "Office": "Milano",
        "Level": "Senior",
        "summary": "7 anni di esperienza in sicurezza informatica con focus su penetration testing, incident response e security architecture. Background nel settore bancario e telco.",
        "skills": ["Penetration Testing", "Incident Response", "Security Architecture", "Risk Assessment", "Compliance", "Team Leadership", "Threat Intelligence"],
        "technologies": ["Splunk", "CrowdStrike", "Nessus", "Burp Suite", "Metasploit", "Python", "Bash", "Azure Sentinel", "Wireshark", "SIEM"],
        "education": {
            "degree": "Laurea Magistrale in Sicurezza Informatica",
            "year": 2017,
            "program": "Università degli Studi di Milano"
        },
        "certifications": ["OSCP - Offensive Security Certified Professional", "CISSP", "CEH - Certified Ethical Hacker", "Azure Security Engineer Associate"],
        "experience": [
            {
                "company": "Intesa Sanpaolo",
                "period": "2022-2025",
                "description": "Security architect per la divisione Digital Banking. Progettazione framework di sicurezza per applicazioni cloud-native e API gateway."
            },
            {
                "company": "PwC",
                "period": "2019-2022",
                "description": "Penetration tester e incident responder per clienti nei settori banking e telco. Conduzione di red team engagement e vulnerability assessment."
            },
            {
                "company": "Vodafone",
                "period": "2017-2019",
                "description": "Junior security analyst nel SOC. Monitoraggio SIEM, analisi log e gestione incidenti di sicurezza."
            }
        ]
    },
    {
        "name": "Elena Santoro",
        "title": "Salesforce Developer",
        "Office": "Roma",
        "Level": "Middle",
        "summary": "4 anni di esperienza nello sviluppo e customizzazione di piattaforme Salesforce. Focus su Sales Cloud, Service Cloud e integrazioni con sistemi esterni nel settore utility e retail.",
        "skills": ["Salesforce Development", "CRM Strategy", "Integration Design", "Agile/Scrum", "Requirements Gathering", "Technical Documentation"],
        "technologies": ["Salesforce", "Apex", "Lightning Web Components", "SOQL", "MuleSoft", "JavaScript", "REST API", "Git", "JIRA", "Copado"],
        "education": {
            "degree": "Laurea Triennale in Ingegneria Gestionale",
            "year": 2020,
            "program": "Politecnico di Bari"
        },
        "certifications": ["Salesforce Certified Platform Developer I", "Salesforce Certified Administrator", "MuleSoft Certified Developer"],
        "experience": [
            {
                "company": "A2A",
                "period": "2023-2025",
                "description": "Sviluppo Salesforce Service Cloud per gestione clienti B2C. Integrazione con SAP e sistemi di billing tramite MuleSoft."
            },
            {
                "company": "Engineering",
                "period": "2020-2023",
                "description": "Salesforce developer per progetti di CRM transformation nel settore retail. Sviluppo custom Lightning components e automazioni con Apex."
            }
        ]
    },
    {
        "name": "Roberto Marini",
        "title": "DevOps Engineer",
        "Office": "Bologna",
        "Level": "Senior",
        "summary": "6 anni di esperienza in automazione infrastrutturale, CI/CD e container orchestration. Forte background Linux e cloud-native. Settori: e-commerce, telco e fintech.",
        "skills": ["DevOps", "Infrastructure as Code", "CI/CD", "Container Orchestration", "Monitoring", "Site Reliability", "Agile"],
        "technologies": ["Kubernetes", "Docker", "Terraform", "Ansible", "AWS", "Jenkins", "GitLab CI", "Prometheus", "Grafana", "Python", "Bash", "Linux", "Helm"],
        "education": {
            "degree": "Laurea Magistrale in Ingegneria Informatica",
            "year": 2018,
            "program": "Università di Bologna"
        },
        "certifications": ["CKA - Certified Kubernetes Administrator", "AWS DevOps Engineer Professional", "HashiCorp Certified: Terraform Associate"],
        "experience": [
            {
                "company": "YOOX Net-A-Porter",
                "period": "2022-2025",
                "description": "Lead DevOps per piattaforma e-commerce. Gestione cluster Kubernetes (300+ pod), pipeline CI/CD con GitLab e monitoring con Prometheus/Grafana."
            },
            {
                "company": "TIM",
                "period": "2019-2022",
                "description": "DevOps engineer per piattaforme digitali B2C. Automazione infrastruttura AWS con Terraform, implementazione blue-green deployment."
            },
            {
                "company": "GFT",
                "period": "2018-2019",
                "description": "Junior system administrator. Gestione server Linux, scripting Bash e primi approcci all'automazione con Ansible."
            }
        ]
    },
    {
        "name": "Chiara Lombardi",
        "title": "Data Integration Specialist",
        "Office": "Milano",
        "Level": "Middle",
        "summary": "4 anni di esperienza in data integration e data quality con strumenti Talend e Informatica. Esperienza nei settori energy, retail e pubblica amministrazione.",
        "skills": ["Data Integration", "ETL Development", "Data Quality", "Data Mapping", "Process Design", "Agile", "SQL Advanced"],
        "technologies": ["Talend Data Integration", "Informatica Cloud", "Google Cloud Platform", "BigQuery", "Python", "SQL", "Shell Scripting", "PostgreSQL", "Oracle", "JIRA"],
        "education": {
            "degree": "Laurea Magistrale in Ingegneria Gestionale",
            "year": 2020,
            "program": "Politecnico di Milano"
        },
        "certifications": ["Talend Data Integration Certified", "Google Cloud Digital Leader", "Informatica Cloud Data Integration R41"],
        "experience": [
            {
                "company": "Enel",
                "period": "2023-2025",
                "description": "Sviluppo flussi ETL con Talend per migrazione dati da sistemi legacy a Google Cloud. Gestione data quality su dataset di 50M+ record."
            },
            {
                "company": "Accenture",
                "period": "2020-2023",
                "description": "Data integration developer per clienti nel settore retail e PA. Sviluppo job Talend e Informatica Cloud per integrazione sistemi ERP e CRM."
            }
        ]
    }
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("  GENERAZIONE CV DI ESEMPIO")
    print("=" * 60)
    
    for cv in SAMPLE_CVS:
        filename = cv["name"].lower().replace(" ", "_") + ".json"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cv, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ {filename:<30} → {cv['title']} ({cv['Office']}, {cv['Level']})")
    
    print()
    print(f"  📁 {len(SAMPLE_CVS)} file JSON creati in: {OUTPUT_DIR}/")
    print()
    print("  Prossimi passi:")
    print("    1. Genera gli embeddings:  python codes/embedding_generators/rag_bge-m3_v2.py")
    print("    2. Avvia la ricerca:       python codes/cv_search_app_v1.py")
    print("=" * 60)


if __name__ == "__main__":
    main()