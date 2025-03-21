from config import url_calendario,url_stats_giocatori , url_stats_difensive_squadre , parent_dir
from functions import calendario,scarica_report_partita,scarico_stats_giocatori,scarico_stats_difensive_squadre, associa_avversari
from data_preprocessing import stats_giocatori_to_silver , stats_squadre_to_silver , dataset_to_gold
from model_training import train_model

def aggiorno_dati_e_modello():
    # Scarico i dati
    print("Inizio a scaricare i dati...")
    calendario(url_calendario)
    new_matches = scarica_report_partita()
    if len(new_matches) > 0:
        scarico_stats_giocatori(url_stats_giocatori)
        scarico_stats_difensive_squadre(url_stats_difensive_squadre)
        print("Dati scaricati con successo !")
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
    print("Dataset per il modello creato con successo --> GOLD !")

    associa_avversari()
    print("Avversari associati con successo !")

    if len(new_matches) > 0:
        print("Ora inizio ad aggiornare il modello...")
        train_model()
        print("Modello aggiornato con successo !")

aggiorno_dati_e_modello()
    