# TODO: Creare una funzione che carica tutti i file CSV
# Input: nessuno (path fissi o da config)
# Output: dizionario con dataframe per ogni file
# File da caricare: progetti, risorse, timesheet, festività, ferie
# Validare che tutti i file esistano e abbiano le colonne richieste

def load_project_data():
    """
    Carica tutti i dati necessari per l'analisi progetti.
    Restituisce un dizionario con i dataframe.
    """
    