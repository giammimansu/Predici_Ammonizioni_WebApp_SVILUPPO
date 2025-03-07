import pandas as pd
import os

def crea_df_input(parent_dir, casa, trasferta, arbitro, lista_giocatori):
    dataset_path = os.path.join(parent_dir, 'ammonizioni','FILES_PREDIZIONI', 'data', 'processed', 'dataset.csv')
    giocatori_path = os.path.join(parent_dir,'ammonizioni', 'FILES_PREDIZIONI', 'data', 'silver', 'statistiche_giocatori.csv')
    squadre_path = os.path.join(parent_dir,'ammonizioni', 'FILES_PREDIZIONI', 'data', 'silver', 'statistiche_squadre.csv')
    arbitri_path = os.path.join(parent_dir,'ammonizioni', 'FILES_PREDIZIONI', 'data', 'silver', 'arbitri.csv')

    dataset = pd.read_csv(dataset_path, sep=';', header=0)
    giocatori = pd.read_csv(giocatori_path, sep=';', header=0)
    squadre = pd.read_csv(squadre_path, sep=';', header=0)
    arbitri = pd.read_csv(arbitri_path, sep=';', header=0)

    squadra_casa = squadre[squadre["Squadra"] == casa]
    squadra_trasferta = squadre[squadre["Squadra"] == trasferta]

    if squadra_casa.empty:
        raise ValueError(f"La squadra di casa '{casa}' non è stata trovata nel dataset.")
    if squadra_trasferta.empty:
        raise ValueError(f"La squadra trasferta '{trasferta}' non è stata trovata nel dataset.")

    giocatori.dropna(inplace=True)
    X = dataset.drop(columns=['Cartellini Gialli', 'Cartellini Rossi'])
    df_tot = pd.DataFrame(columns=X.columns)

    for nome_giocatore in lista_giocatori:
        giocatore = giocatori[giocatori["Giocatore"] == nome_giocatore]

        if giocatore.empty:
            raise ValueError(f"Il giocatore '{nome_giocatore}' non è stato trovato nel dataset.")
        
        df_arbitro = arbitri[arbitri["Arbitro"] == arbitro]
        if df_arbitro.empty:
            raise ValueError(f"L'arbitro '{arbitro}' non è stato trovato nel dataset.")

        input = {
            "Casa": casa,
            "Trasferta": trasferta,
            "Arbitro": arbitro,
            "Ruolo" : giocatore["Ruolo"].values[0],
            "Giocatore": nome_giocatore,
            "Cartellini Gialli_per90": giocatore["Cartellini Gialli_per90"].values[0],
            "Cartellini Rossi_per90": giocatore["Cartellini Rossi_per90"].values[0],
            "Falli_per90": giocatore["Falli_per90"].values[0],
            "Fallo Subito_per90": giocatore["Fallo Subito_per90"].values[0],
            "Intercettazioni_per90": giocatore["Intercettazioni_per90"].values[0],
            "Tackle Vinti_per90": giocatore["Tackle Vinti_per90"].values[0],
            "Aerei Vinti_per90": giocatore["Aerei Vinti_per90"].values[0],
            "Aerei Persi_per90": giocatore["Aerei Persi_per90"].values[0],
            "Recupero Palla_per90": giocatore["Recupero Palla_per90"].values[0],
            "Tackle_per90_Casa": squadra_casa["Tackle_per90"].values[0],
            "Tackle Vinti_per90_Casa": squadra_casa["Tackle Vinti_per90"].values[0],
            "Tackle Difensivi Terzo_per90_Casa": squadra_casa["Tackle Difensivi Terzo_per90"].values[0],
            "Tackle Centrocampo Terzo_per90_Casa": squadra_casa["Tackle Centrocampo Terzo_per90"].values[0],
            "Tackle Attacco Terzo_per90_Casa": squadra_casa["Tackle Attacco Terzo_per90"].values[0],
            "Tackle Sfida_per90_Casa": squadra_casa["Tackle Sfida_per90"].values[0],
            "Sfide_per90_Casa": squadra_casa["Sfide_per90"].values[0],
            "Sfide Perse_per90_Casa": squadra_casa["Sfide Perse_per90"].values[0],
            "Blocchi_per90_Casa": squadra_casa["Blocchi_per90"].values[0],
            "Intercettazioni_per90_Casa": squadra_casa["Intercettazioni_per90"].values[0],
            "Disimpegni_per90_Casa": squadra_casa["Disimpegni_per90"].values[0],
            "Errori_per90_Casa": squadra_casa["Errori_per90"].values[0],
            "Tackle_per90_Trasferta": squadra_trasferta["Tackle_per90"].values[0],
            "Tackle Vinti_per90_Trasferta": squadra_trasferta["Tackle Vinti_per90"].values[0],
            "Tackle Difensivi Terzo_per90_Trasferta": squadra_trasferta["Tackle Difensivi Terzo_per90"].values[0],
            "Tackle Centrocampo Terzo_per90_Trasferta": squadra_trasferta["Tackle Centrocampo Terzo_per90"].values[0],
            "Tackle Attacco Terzo_per90_Trasferta": squadra_trasferta["Tackle Attacco Terzo_per90"].values[0],
            "Tackle Sfida_per90_Trasferta": squadra_trasferta["Tackle Sfida_per90"].values[0],
            "Sfide_per90_Trasferta": squadra_trasferta["Sfide_per90"].values[0],
            "Sfide Perse_per90_Trasferta": squadra_trasferta["Sfide Perse_per90"].values[0],
            "Blocchi_per90_Trasferta": squadra_trasferta["Blocchi_per90"].values[0],
            "Intercettazioni_per90_Trasferta": squadra_trasferta["Intercettazioni_per90"].values[0],
            "Disimpegni_per90_Trasferta": squadra_trasferta["Disimpegni_per90"].values[0],
            "Errori_per90_Trasferta": squadra_trasferta["Errori_per90"].values[0],
            "Media Cartellini a partita" : df_arbitro["Media Cartellini a partita"].values[0]
        }

        df_giocatore = pd.DataFrame([input])
        df_tot = pd.concat([df_tot, df_giocatore], ignore_index=True)
    return df_tot