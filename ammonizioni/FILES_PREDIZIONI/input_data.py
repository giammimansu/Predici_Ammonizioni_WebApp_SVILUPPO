import pandas as pd
import sys

def crea_df_input(parent_dir, casa, trasferta, arbitro, lista_giocatori, avversari):
    dataset = pd.read_csv(parent_dir + r"\ammonizioni\FILES_PREDIZIONI\data\processed\dataset_2.csv", sep=';', header=0)
    giocatori = pd.read_csv(parent_dir + r"\ammonizioni\FILES_PREDIZIONI\data\silver\statistiche_giocatori.csv", sep=';', header=0)
    squadre = pd.read_csv(parent_dir + r"\ammonizioni\FILES_PREDIZIONI\data\silver\statistiche_squadre.csv", sep=';', header=0)
    arbitri = pd.read_csv(parent_dir + r"\ammonizioni\FILES_PREDIZIONI\data\silver\arbitri.csv", sep=';', header=0)

    squadra_casa = squadre[squadre["Squadra"] == casa]
    squadra_trasferta = squadre[squadre["Squadra"] == trasferta]

    if squadra_casa.empty:
        raise ValueError(f"La squadra di casa '{casa}' non è stata trovata nel dataset.")
    if squadra_trasferta.empty:
        raise ValueError(f"La squadra trasferta '{trasferta}' non è stata trovata nel dataset.")

    giocatori.dropna(inplace=True)
    X = dataset.drop(columns=['Cartellini Gialli', 'Cartellini Rossi'])
    df_tot = pd.DataFrame(columns=X.columns)

    for nome_giocatore, avversari_giocatore in zip(lista_giocatori, avversari):
        if len(avversari_giocatore) != 3:
            raise ValueError(f"La lista degli avversari per '{nome_giocatore}' deve contenere esattamente 3 elementi.")

        giocatore = giocatori[giocatori["Giocatore"] == nome_giocatore]
        avv1, avv2, avv3 = (giocatori[giocatori["Giocatore"] == avv] for avv in avversari_giocatore)

        if giocatore.empty:
            raise ValueError(f"Il giocatore '{nome_giocatore}' non è stato trovato nel dataset.")
        if avv1.empty or avv2.empty or avv3.empty:
            raise ValueError(f"Uno o più avversari di '{nome_giocatore}' non sono stati trovati nel dataset.")

        df_arbitro = arbitri[arbitri["Arbitro"] == arbitro]
        if df_arbitro.empty:
            raise ValueError(f"L'arbitro '{arbitro}' non è stato trovato nel dataset.")

        input_data = {
            "Casa": casa,
            "Trasferta": trasferta,
            "Arbitro": arbitro,
            "Ruolo": giocatore["Ruolo"].values[0],
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
            "Media Cartellini a partita": df_arbitro["Media Cartellini a partita"].values[0]
        }

        # Aggiungere le statistiche della squadra di casa
        for col in squadra_casa.columns:
            if col != "Squadra":
                input_data[f"{col}_Casa"] = squadra_casa[col].values[0]

        # Aggiungere le statistiche della squadra in trasferta
        for col in squadra_trasferta.columns:
            if col != "Squadra":
                input_data[f"{col}_Trasferta"] = squadra_trasferta[col].values[0]

        # Aggiungere statistiche degli avversari
        for i, avv in enumerate([avv1, avv2, avv3], start=1):
            input_data.update({
                f'Falli_per90_avv{i}': avv['Falli_per90'].values[0],
                f'Fallo Subito_per90_avv{i}': avv['Fallo Subito_per90'].values[0],
                f'Intercettazioni_per90_avv{i}': avv['Intercettazioni_per90'].values[0],
                f'Tackle Vinti_per90_avv{i}': avv['Tackle Vinti_per90'].values[0],
                f'Recupero Palla_per90_avv{i}': avv['Recupero Palla_per90'].values[0],
                f'Aerei Vinti_per90_avv{i}': avv['Aerei Vinti_per90'].values[0],
                f'Aerei Persi_per90_avv{i}': avv['Aerei Persi_per90'].values[0]
            })

        df_giocatore = pd.DataFrame([input_data])
        df_tot = pd.concat([df_tot, df_giocatore], ignore_index=True)

        #df_tot.drop(columns=['Squadra_giocatore', 'Avversario_1', 'Avversario_2', 'Avversario_3'], inplace=True)

    return df_tot
