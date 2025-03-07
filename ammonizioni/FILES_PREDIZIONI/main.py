from config import url_calendario,url_stats_giocatori , url_stats_difensive_squadre , parent_dir
from functions import calendario,scarica_report_partita,scarico_stats_giocatori,scarico_stats_difensive_squadre
from data_preprocessing import stats_giocatori_to_silver , stats_squadre_to_silver , dataset_to_gold

def aggiorno_dati_e_modello():
    # Scarico i dati
    calendario(url_calendario)
    new_matches = scarica_report_partita()
    if len(new_matches) > 0:
        scarico_stats_giocatori(url_stats_giocatori)
        scarico_stats_difensive_squadre(url_stats_difensive_squadre)
        print("Dati scaricati con successo !")
        print("Ora inizio a trainare il nuovo modello...")
    else:
        print("Non ci sono nuove partite da scaricare !")
        
    #Pre processing Dati 
    print("Ora inizio a pre processare i dati...")
    stats_giocatori_to_silver(parent_dir)
    print("Statistiche giocatori pre processati con successo --> SILVER !")
    stats_squadre_to_silver(parent_dir)
    print("Statistiche squadre pre processati con successo --> SILVER !")

    #Creo il dataset per il modello
    dataset_to_gold(parent_dir)
    print("Dataset per il modello creato con successo --> SILVER !")

    