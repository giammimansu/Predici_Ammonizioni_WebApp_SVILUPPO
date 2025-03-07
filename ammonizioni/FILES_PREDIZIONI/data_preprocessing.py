import pandas as pd
import os


def stats_giocatori_to_silver(parent_dir):
    giocatori_raw = pd.read_csv(parent_dir + r"\data\raw\statistiche_varie_giocatori.csv",sep=";",header=0)
    giocartori_silver = pd.read_csv(parent_dir + r"\data\silver\statistiche_giocatori.csv",sep=";",header=0)
    giocatori_raw["Squadra_giocatore"] = giocatori_raw["Squadra"]
    giocatori_raw["Cartellini Gialli_per90"] = giocatori_raw["Cartellini Gialli"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Cartellini Rossi_per90"] = giocatori_raw["Cartellini Rossi"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Falli_per90"] = giocatori_raw["Falli"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Fallo Subito_per90"] = giocatori_raw["Fallo Subito"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Intercettazioni_per90"] = giocatori_raw["Intercettazioni"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Tackle Vinti_per90"] = giocatori_raw["Tackle Vinti"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Recupero Palla_per90"] = giocatori_raw["Recupero Palla"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Aerei Vinti_per90"] = giocatori_raw["Aerei Vinti"] / giocatori_raw["Minuti Giocati"]
    giocatori_raw["Aerei Persi_per90"] = giocatori_raw["Aerei Persi"] / giocatori_raw["Minuti Giocati"]
    columns = list(giocartori_silver.columns)
    giocatori_raw = giocatori_raw[columns]

    # Rimuovo duplicati col min(Minuti Giocati)
    giocatori_raw = giocatori_raw.loc[giocatori_raw.groupby('Giocatore')['Minuti Giocati'].idxmax()]
    giocatori_raw.reset_index(drop=True, inplace=True)  
    giocatori_raw.to_csv(parent_dir+r"\data\silver\statistiche_giocatori.csv",sep=";",index=False)

def stats_squadre_to_silver(parent_dir):
    df_squadre = pd.read_csv(parent_dir + r"\data\raw\statistiche_squadre_difensive.csv",sep=";",header=0)
    df_squadre["Tackle_per90"]=df_squadre["Tackle"]/df_squadre["Partite Giocate"]
    df_squadre["Tackle Vinti_per90"]=df_squadre["Tackle Vinti"]/df_squadre["Partite Giocate"]
    df_squadre["Tackle Difensivi Terzo_per90"]=df_squadre["Tackle Difensivi Terzo"]/df_squadre["Partite Giocate"]
    df_squadre["Tackle Centrocampo Terzo_per90"]=df_squadre["Tackle Centrocampo Terzo"]/df_squadre["Partite Giocate"]
    df_squadre["Tackle Attacco Terzo_per90"]=df_squadre["Tackle Attacco Terzo"]/df_squadre["Partite Giocate"]
    df_squadre["Tackle Sfida_per90"]=df_squadre["Tackle Sfida"]/df_squadre["Partite Giocate"]
    df_squadre["Sfide_per90"]=df_squadre["Sfide"]/df_squadre["Partite Giocate"]
    df_squadre["Sfide Perse_per90"]=df_squadre["Sfide Perse"]/df_squadre["Partite Giocate"]
    df_squadre["Blocchi_per90"]=df_squadre["Blocchi"]/df_squadre["Partite Giocate"]
    df_squadre["Intercettazioni_per90"]=df_squadre["Intercettazioni"]/df_squadre["Partite Giocate"]
    df_squadre["Disimpegni_per90"]=df_squadre["Disimpegni"]/df_squadre["Partite Giocate"]
    df_squadre["Errori_per90"]=df_squadre["Errori"]/df_squadre["Partite Giocate"]

    df_squadre = df_squadre[["Squadra","Tackle_per90","Tackle Vinti_per90","Tackle Difensivi Terzo_per90","Tackle Centrocampo Terzo_per90","Tackle Attacco Terzo_per90","Tackle Sfida_per90","Sfide_per90","Sfide Perse_per90","Blocchi_per90","Intercettazioni_per90","Disimpegni_per90","Errori_per90"]]
    df_squadre.to_csv(parent_dir + r"\data\silver\statistiche_squadre.csv",sep=";",index=False)

def dataset_to_gold(parent_dir):
    dataset_silver = pd.read_csv(parent_dir + r"\data\silver\dataset_silver.csv",sep=";",header=0)
    giocatori_silver = pd.read_csv(parent_dir + r"\data\silver\statistiche_giocatori.csv",sep=";",header=0)
    squadre_silver = pd.read_csv(parent_dir + r"\data\silver\statistiche_squadre.csv",sep=";",header=0)
    calendario = pd.read_csv(parent_dir + r"\data\raw\calendario.csv",sep=";",header=0)

    dataset_silver = dataset_silver[["Casa","Trasferta","Giocatore","Cartellini Gialli","Cartellini Rossi"]]
    giocatori_silver = giocatori_silver[["Giocatore","Ruolo",'Cartellini Gialli_per90',
       'Cartellini Rossi_per90', 'Falli_per90', 'Fallo Subito_per90',
       'Intercettazioni_per90', 'Tackle Vinti_per90', 'Recupero Palla_per90',
       'Aerei Vinti_per90', 'Aerei Persi_per90']]
    dataset_silver = dataset_silver.merge(giocatori_silver, left_on="Giocatore", right_on="Giocatore", how="left")
    squadre_casa = squadre_silver.rename(columns=lambda x: x + "_Casa")
    squadre_trasferta = squadre_silver.rename(columns=lambda x: x + "_Trasferta")
    dataset_silver=dataset_silver.merge(squadre_casa, left_on="Casa", right_on="Squadra_Casa", how="left")
    dataset_silver=dataset_silver.merge(squadre_trasferta, left_on="Trasferta", right_on="Squadra_Trasferta", how="left")
    dataset_silver = dataset_silver.drop(columns=["Squadra_Casa","Squadra_Trasferta"])
    calendario=calendario[["Squadra di Casa","Squadra Trasferta","Arbitro"]]
    dataset_silver = dataset_silver.merge(calendario, left_on=["Casa","Trasferta"], right_on=["Squadra di Casa","Squadra Trasferta"], how="left")
    dataset_silver.drop(columns=["Squadra di Casa","Squadra Trasferta"],inplace=True)
    cols = list(dataset_silver.columns)
    cols.insert(2, cols.pop(cols.index('Arbitro')))
    dataset_silver = dataset_silver[cols]

    dataset_gold = pd.read_csv(parent_dir + r"\data\processed\dataset.csv",sep=";",header=0)
    dataset_gold = dataset_gold[['Casa', 'Trasferta', 'Arbitro', 'Giocatore', 'Cartellini Gialli',"Cartellini Rossi"]]
    dataset_gold = dataset_gold.merge(giocatori_silver, left_on="Giocatore", right_on="Giocatore", how="left")
    dataset_gold = dataset_gold.merge(squadre_casa, left_on="Casa", right_on="Squadra_Casa", how="left")
    dataset_gold = dataset_gold.merge(squadre_trasferta, left_on="Trasferta", right_on="Squadra_Trasferta", how="left")
    dataset_gold.drop(columns=["Squadra_Casa","Squadra_Trasferta"],inplace=True)
    dataset_combined = pd.concat([dataset_gold, dataset_silver], ignore_index=True)

    arbitri_part = dataset_combined[["Arbitro","Casa","Trasferta"]]
    arbitri_part["Partita"] = arbitri_part["Casa"] + " - " + arbitri_part["Trasferta"]
    arbitri_part.drop(columns=["Casa","Trasferta"],inplace=True)
    arbitri_part.drop_duplicates(inplace=True)
    arbitri_part = arbitri_part.groupby("Arbitro").count().reset_index()
    arbitri_cart = dataset_combined[["Arbitro","Cartellini Gialli","Cartellini Rossi"]]
    arbitri_cart["Cartellini"] = arbitri_cart["Cartellini Gialli"] + arbitri_cart["Cartellini Rossi"]
    arbitri_cart.drop(columns=["Cartellini Gialli","Cartellini Rossi"],inplace=True)
    arbitri_cart = arbitri_cart.groupby("Arbitro").sum().reset_index()
    arbitri_combined = arbitri_part.merge(arbitri_cart, left_on="Arbitro", right_on="Arbitro", how="left")
    arbitri_combined.fillna(0,inplace=True)
    arbitri_combined.rename(columns={"Partita":"Partite Arbitrate"},inplace=True)
    arbitri_combined["Media Cartellini a partita"] = arbitri_combined["Cartellini"] / arbitri_combined["Partite Arbitrate"]
    arbitri_combined.to_csv(parent_dir + r"\data\silver\arbitri.csv",sep=";",index=False)
    arbitri_combined.drop(columns=["Cartellini","Partite Arbitrate"],inplace=True)
    dataset_combined = dataset_combined.merge(arbitri_combined, left_on="Arbitro", right_on="Arbitro", how="left")

    dataset_combined.to_csv(parent_dir + r"\data\processed\dataset.csv",sep=";",index=False)
