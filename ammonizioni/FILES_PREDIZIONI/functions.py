from bs4 import BeautifulSoup
from stem.control import Controller
from fake_useragent import UserAgent
import time
import requests
import pandas as pd
import re 
import random
import time 
from config import parent_dir , chrome_driver_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# Funzione per cambiare IP Tor
def change_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="rAminux97")  # Sostituisci con la password di Tor
        controller.signal('NEWNYM')  
# Funzione per creare una sessione che utilizza Tor come proxy
def _session_():
    session = requests.Session()

    # Usa Fake User-Agent per variare l'intestazione
    ua = UserAgent()
    session.headers.update({
        "User-Agent": ua.random  # Cambia l'User-Agent ad ogni richiesta
    })

    # Impostazione del proxy SOCKS5 per Tor
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }
    session.proxies.update(proxies)
    
    # Se vuoi, puoi anche disabilitare la gestione dei cookie
    session.cookies.clear()  # Assicurati che i cookie non siano salvati
    
    return session

def get_my_ip(url):
    session = _session_()
    
    # Fai una richiesta al sito
    response = session.get(url)

    # Aggiungi un ritardo casuale tra le richieste (da 3 a 8 secondi)
    time.sleep(random.uniform(3, 8))

    # Dopo un numero di richieste, cambia l'IP Tor (per esempio dopo ogni 5 richieste)
    if random.randint(1, 5) == 1:  # Modifica la probabilità se necessario
        print("Cambio IP...")
        change_ip()

    return response

def calendario(url):
    response = get_my_ip(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'sched_2024-2025_11_1'})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    data = []

    for row in rows:
        
        gameweek = row.find('th', {'data-stat': 'gameweek'}).text.strip()
        day_of_week = row.find('td', {'data-stat': 'dayofweek'}).text.strip()
        date = row.find('td', {'data-stat': 'date'}).text.strip()
        start_time = row.find('td', {'data-stat': 'start_time'}).text.strip()
        home_team = row.find('td', {'data-stat': 'home_team'}).text.strip()
        home_xg = row.find('td', {'data-stat': 'home_xg'}).text.strip()
        score = row.find('td', {'data-stat': 'score'}).text.strip()
        away_xg = row.find('td', {'data-stat': 'away_xg'}).text.strip()
        away_team = row.find('td', {'data-stat': 'away_team'}).text.strip()
        attendance = row.find('td', {'data-stat': 'attendance'}).text.strip()
        venue = row.find('td', {'data-stat': 'venue'}).text.strip()
        referee = row.find('td', {'data-stat': 'referee'}).text.strip()
        match_report_td = row.find('td', {'data-stat': 'match_report'})
        if match_report_td:
            link = match_report_td.find('a')
            if link:
                href = link.get('href')
                href = 'https://fbref.com' + href
        else:
            print("Nessuna cella 'match_report' trovata.")      

        data.append([gameweek, day_of_week, date, start_time, home_team, home_xg, score, away_xg, away_team, 
                            attendance, venue, referee,href])
    
    columns = ['Giornata', 'Giorno della Settimana', 'Data', 'Ora Inizio', 'Squadra di Casa', 'xG Casa', 'Risultato', 'xG Trasferta', 'Squadra Trasferta', 
               'Spettatori', 'Stadio', 'Arbitro','Link Report']
    df = pd.DataFrame(data, columns=columns)
    df.drop_duplicates(inplace=True)
    df = df[df['Risultato'] != '']
    df.to_csv(parent_dir+r"\FILES_PREDIZIONI\data\raw\calendario.csv", index=False, sep=';',header=True)
    print("Calendario salvato con successo!")

def get_table_id(url):
    response = get_my_ip(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div_element = soup.find_all("div", class_=lambda x: x and "table_container" in x)

    div_element_casa = div_element[0]
    # Trova la table dentro il div e ottieni l'id
    if div_element_casa:
        table_element_casa = div_element_casa.find("table")
        table_id_casa = table_element_casa.get("id") if table_element_casa else None
    else:
        print("Div non trovato")
        
    div_element_trasferta = div_element[7]

    # Trova la table dentro il div e ottieni l'id
    if div_element_trasferta:
        table_element_trasferta = div_element_trasferta.find("table")
        table_id_trasferta = table_element_trasferta.get("id") if table_element_trasferta else None
    else:
        print("Div non trovato")
        
    return table_id_casa,table_id_trasferta

def stats_match(url):
    response = get_my_ip(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table_id_casa,table_id_trasferta = get_table_id(url)
    table_casa = soup.find('table', {'id': table_id_casa})
    tbody_casa = table_casa.find('tbody')
    rows_casa = tbody_casa.find_all('tr')
    data_casa = []
    
    for row in rows_casa:
        try:
            player = row.find('th', {'data-stat': 'player'}).text.strip()
            minutes_played = row.find('td', {'data-stat': 'minutes'}).text.strip()
            goals = row.find('td', {'data-stat': 'goals'}).text.strip()
            assists = row.find('td', {'data-stat': 'assists'}).text.strip()
            shots = row.find('td', {'data-stat': 'shots'}).text.strip()
            shots_on_target = row.find('td', {'data-stat': 'shots_on_target'}).text.strip()
            cards_yellow = row.find('td', {'data-stat': 'cards_yellow'}).text.strip()
            cards_red = row.find('td', {'data-stat': 'cards_red'}).text.strip()
            touches = row.find('td', {'data-stat': 'touches'}).text.strip()
            blocks = row.find('td', {'data-stat': 'blocks'}).text.strip()
            xg_player = row.find('td', {'data-stat': 'xg'}).text.strip()

            data_casa.append([player, minutes_played, goals, assists, shots, shots_on_target, cards_yellow, cards_red, touches, blocks, xg_player])
        except Exception as e:
            print(f"Error: {e}")
            
    columns = ['Giocatore', 'Minuti Giocati', 'Goal', 'Assist', 'Tiri', 'Tiri in Porta', 'Cartellini Gialli', 'Cartellini Rossi', 'Tocchi', 'Blocchi', 'xG_giocatore']
    df_casa = pd.DataFrame(data_casa, columns=columns)
    df_casa.drop_duplicates(inplace=True)
    
    
    
    table_trasferta = soup.find('table', {'id': table_id_trasferta})
    tbody_trasferta = table_trasferta.find('tbody')
    rows_trasferta = tbody_trasferta.find_all('tr')
    data_trasferta = []
    for row in rows_trasferta:
        try:
            player = row.find('th', {'data-stat': 'player'}).text.strip()
            minutes_played = row.find('td', {'data-stat': 'minutes'}).text.strip()
            goals = row.find('td', {'data-stat': 'goals'}).text.strip()
            assists = row.find('td', {'data-stat': 'assists'}).text.strip()
            shots = row.find('td', {'data-stat': 'shots'}).text.strip()
            shots_on_target = row.find('td', {'data-stat': 'shots_on_target'}).text.strip()
            cards_yellow = row.find('td', {'data-stat': 'cards_yellow'}).text.strip()
            cards_red = row.find('td', {'data-stat': 'cards_red'}).text.strip()
            touches = row.find('td', {'data-stat': 'touches'}).text.strip()
            blocks = row.find('td', {'data-stat': 'blocks'}).text.strip()
            xg_player = row.find('td', {'data-stat': 'xg'}).text.strip()

            data_trasferta.append([player, minutes_played, goals, assists, shots, shots_on_target, cards_yellow, cards_red, touches, blocks, xg_player])
            
        except Exception as e:
            print(f"Error: {e}")
            
    columns = ['Giocatore', 'Minuti Giocati', 'Goal', 'Assist', 'Tiri', 'Tiri in Porta', 'Cartellini Gialli', 'Cartellini Rossi', 'Tocchi', 'Blocchi', 'xG_giocatore']
    df_trasferta = pd.DataFrame(data_trasferta, columns=columns)
    df_trasferta.drop_duplicates(inplace=True)

    df = pd.concat([df_casa, df_trasferta], axis=0)
    return df

def scarica_report_partita():
    dataset = pd.read_csv(parent_dir + r"\FILES_PREDIZIONI\data\processed\dataset_2.csv",sep=';',header=0)
    calendario = pd.read_csv(parent_dir + r"\FILES_PREDIZIONI\data\raw\calendario.csv",sep=';',header=0)
    dataset = dataset[["Casa","Trasferta"]].drop_duplicates()
    merged = calendario.merge(dataset, how='left', left_on=["Squadra di Casa", "Squadra Trasferta"], right_on=["Casa", "Trasferta"], indicator=True)
    new_matches = merged[merged['_merge'] == 'left_only'].drop(columns=['Casa', 'Trasferta', '_merge'])
    print(f"Nuove partite da scaricare: {len(new_matches)}")
    columns = ["Casa","Trasferta",'Giocatore','Minuti Giocati', 'Goal', 'Assist', 'Tiri', 'Tiri in Porta', 'Cartellini Gialli', 'Cartellini Rossi', 'Tocchi', 'Blocchi', 'xG_giocatore']    
    df_tot = pd.DataFrame(columns=columns)
    for i,row in new_matches.iterrows():
        now = time.time()
        casa = row['Squadra di Casa']
        trasferta = row['Squadra Trasferta']
        link = row['Link Report']
        df = stats_match(link)
        df['Casa'] = casa
        df['Trasferta'] = trasferta
        df_tot = pd.concat([df_tot,df],axis=0)
        tempo = time.time()-now
        print(f"Tempo impiegato per scaricare le statistiche della partita {casa} - {trasferta}: {tempo: .2f} secondi")
    df_tot.to_csv(parent_dir + r"\FILES_PREDIZIONI\data\silver\dataset_silver.csv", sep=';', index=False,header=True)
    print("Report partite scaricati con successo!")
    return new_matches

def converti_in_float(df):
    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
    return df

def scarico_stats_giocatori(url):
    # Configura il driver di Selenium
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    # Carica la pagina web
    driver.get(url)

    # Aumenta il tempo di attesa e verifica se l'elemento è presente
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "stats_misc"))
        )
        print("Elemento trovato")
    except TimeoutException:
        print("Timeout: elemento non trovato")
        html = driver.page_source
        print(html[:2000])  # Stampa i primi 2000 caratteri del contenuto HTML per debug
        driver.quit()
        exit()

    # Ottieni il contenuto HTML della pagina
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Trova la tabella con le statistiche dei giocatori
    table = soup.find('table', {'id': 'stats_misc'})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    data =[]
    for row in rows:
        if "thead" in row.get('class', []):
            continue

        player_name = row.find('td', {'data-stat': 'player'}).find('a').get_text(strip=True)
        position = row.find('td', {'data-stat': 'position'}).get_text(strip=True)
        team = row.find('td', {'data-stat': 'team'}).find('a').get_text(strip=True)
        age = row.find('td', {'data-stat': 'age'}).get_text(strip=True)[:2]
        minutes_played = row.find('td', {'data-stat': 'minutes_90s'}).get_text(strip=True)
        cards_yellow = row.find('td', {'data-stat': 'cards_yellow'}).get_text(strip=True)
        cards_red = row.find('td', {'data-stat': 'cards_red'}).get_text(strip=True)
        cards_yellow_red = row.find('td', {'data-stat': 'cards_yellow_red'}).get_text(strip=True)
        fouls = row.find('td', {'data-stat': 'fouls'}).get_text(strip=True)
        fouled = row.find('td', {'data-stat': 'fouled'}).get_text(strip=True)
        offsides = row.find('td', {'data-stat': 'offsides'}).get_text(strip=True)  
        crosses = row.find('td', {'data-stat': 'crosses'}).get_text(strip=True)
        interceptions = row.find('td', {'data-stat': 'interceptions'}).get_text(strip=True)
        tackles_won = row.find('td', {'data-stat': 'tackles_won'}).get_text(strip=True)
        pens_won = row.find('td', {'data-stat': 'pens_won'}).get_text(strip=True)
        pens_conceded = row.find('td', {'data-stat': 'pens_conceded'}).get_text(strip=True)
        own_goals = row.find('td', {'data-stat': 'own_goals'}).get_text(strip=True)
        ball_recoveries = row.find('td', {'data-stat': 'ball_recoveries'}).get_text(strip=True)
        aerials_won = row.find('td', {'data-stat': 'aerials_won'}).get_text(strip=True)
        aerials_lost = row.find('td', {'data-stat': 'aerials_lost'}).get_text(strip=True)
        aerials_won_pct = row.find('td', {'data-stat': 'aerials_won_pct'}).get_text(strip=True)
        link_giocatore = row.find('td', {'data-stat': 'player'}).find('a').get('href')
        link_giocatore = 'https://fbref.com' + link_giocatore
        data.append([player_name, position, team, age, minutes_played, cards_yellow, cards_red, cards_yellow_red, fouls, fouled, offsides, crosses, interceptions, tackles_won, pens_won, pens_conceded, own_goals, ball_recoveries, aerials_won, aerials_lost, aerials_won_pct,link_giocatore])

    driver.quit()
    columns = ['Giocatore', 'Ruolo', 'Squadra', 'Età', 'Minuti Giocati', 'Cartellini Gialli', 'Cartellini Rossi', 'Cartellini Gialli/Rossi', 'Falli', 'Fallo Subito', 'Fuorigioco', 'Cross', 'Intercettazioni', 'Tackle Vinti', 'Rigori Guadagnati', 'Rigori Concessi', 'Autoreti', 'Recupero Palla', 'Aerei Vinti', 'Aerei Persi', 'Percentuale Aerei Vinti',"Link Giocatore"]
    df = pd.DataFrame(data, columns=columns)
    df.drop_duplicates(inplace=True)
    df = converti_in_float(df)
    df.to_csv(parent_dir+r"\FILES_PREDIZIONI\data\raw\statistiche_varie_giocatori.csv", index=False, sep=';',header=True)   
    print("Statistiche giocatori aggiornate")   
    
def scarico_stats_difensive_squadre(url):
    response = get_my_ip(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'stats_squads_defense_for'})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    data = []
    for row in rows:
        team = row.find('th', {'data-stat': 'team'}).find('a').get_text(strip=True)
        matches_played = row.find('td', {'data-stat': 'minutes_90s'}).get_text(strip=True)
        tackles = row.find('td', {'data-stat': 'tackles'}).get_text(strip=True)
        tackles_won = row.find('td', {'data-stat': 'tackles_won'}).get_text(strip=True)
        tackles_def_3rd = row.find('td', {'data-stat': 'tackles_def_3rd'}).get_text(strip=True)
        tackles_mid_3rd = row.find('td', {'data-stat': 'tackles_mid_3rd'}).get_text(strip=True)
        tackles_att_3rd = row.find('td', {'data-stat': 'tackles_att_3rd'}).get_text(strip=True)
        challenge_tackles = row.find('td', {'data-stat': 'challenge_tackles'}).get_text(strip=True)
        challenges = row.find('td', {'data-stat': 'challenges'}).get_text(strip=True)
        challenges_lost = row.find('td', {'data-stat': 'challenges_lost'}).get_text(strip=True)
        blocks = row.find('td', {'data-stat': 'blocks'}).get_text(strip=True)
        interceptions = row.find('td', {'data-stat': 'interceptions'}).get_text(strip=True)
        clearances = row.find('td', {'data-stat': 'clearances'}).get_text(strip=True)
        errors = row.find('td', {'data-stat': 'errors'}).get_text(strip=True)

        data.append([team, matches_played, tackles, tackles_won, tackles_def_3rd, tackles_mid_3rd, tackles_att_3rd, challenge_tackles, challenges, challenges_lost, blocks, interceptions, clearances, errors])
    
    columns = ['Squadra', 'Partite Giocate', 'Tackle', 'Tackle Vinti', 'Tackle Difensivi Terzo', 'Tackle Centrocampo Terzo', 'Tackle Attacco Terzo', 'Tackle Sfida', 'Sfide', 'Sfide Perse', 'Blocchi', 'Intercettazioni', 'Disimpegni', 'Errori']
    df = pd.DataFrame(data, columns=columns)
    df.drop_duplicates(inplace=True)
    df = converti_in_float(df)
    df.to_csv(parent_dir+r"\FILES_PREDIZIONI\data\raw\statistiche_squadre_difensive.csv", index=False, sep=';',header=True)
    print("Statistiche difensive squadre aggiornate")

def scarico_ruoli():
    def scarica_ruolo(url):
        response = get_my_ip(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafi = soup.find_all('p')
        for p in paragrafi:
            if 'Posizione:' in p.text:
                # Estrai solo il ruolo ignorando altre informazioni
                ruolo = re.search(r'Posizione:\s*([^\n▪]*)', p.text)
                if ruolo:
                    return ruolo.group(1).strip()  # Ritorna solo il ruolo trovato

        return None

    giocatori = pd.read_csv(parent_dir+r"\FILES_PREDIZIONI\data\raw\statistiche_varie_giocatori.csv",sep=';',header=0)
    posizioni = pd.DataFrame(columns=["Giocatore", "Posizione"])
    for i, row in giocatori.iterrows():
        giocatore=row["Giocatore"]
        url = row["Link Giocatore"]
        pos = scarica_ruolo(url)
        giocatori.at[i, "Posizione"] = pos
        posizioni = pd.concat([posizioni, pd.DataFrame({"Giocatore": [giocatore], "Posizione": [pos]})])
        if i % 50 == 0:
            print(f"Scaricato {i} giocatori")
            posizioni.to_csv(parent_dir +"\data\raw\posizioni.csv",sep=';',index=False)
            print(f"{i}/{len(giocatori)} -- Salvato il file")


def associa_avversari():
    dataset = pd.read_csv(parent_dir + r"\FILES_PREDIZIONI\data\processed\dataset_2.csv",sep=';',header = 0 )
    giocatori = pd.read_csv(parent_dir + r"\FILES_PREDIZIONI\data\silver\statistiche_giocatori.csv",sep=';',header = 0 )
    dataset = pd.merge(dataset,giocatori[["Giocatore","Squadra_giocatore"]],how='left',left_on=['Giocatore'],right_on=['Giocatore'])

    # Mappatura dei ruoli
    role_mapping = {
    "Att": ["Dif"], 
    "Att.Cen": ["Dif", "Cen.Dif"], 
    "Att.Dif": ["Dif.Att","Dif.Cen","Dif"],
    "Cen": ["Cen.Att","Cen"], 
    "Cen.Att": ["Cen.Dif","Dif.Att","Cen"], 
    "Cen.Dif": ["Cen.Att","Cen"],
    "Dif": ["Att","Att.Cen"], 
    "Dif.Att": ["Att.Dif","Cen.Dif","Dif.Att","Att.Cen","Att"], 
    "Dif.Cen": ["Cen.Att","Att"],
    "Por": None  # Nessun avversario per il portiere
    }
    # Colonne da copiare per gli avversari
    stat_columns = ["Falli_per90", "Fallo Subito_per90", "Intercettazioni_per90", "Tackle Vinti_per90", "Recupero Palla_per90", "Aerei Vinti_per90", "Aerei Persi_per90"]

    def get_top_3_players(row):
        if pd.isna(row['Ruolo']) or row['Ruolo'] == "Por":
            return pd.Series([None] * (3 + len(stat_columns) * 3))

        # Determinare la squadra avversaria
        if row['Squadra_giocatore'] == row['Casa']:
            squadra_avversaria = row['Trasferta']
        else:
            squadra_avversaria = row['Casa']

        ruolo_avversario = role_mapping.get(row['Ruolo'])
        if not ruolo_avversario:
            return pd.Series([None] * (3 + len(stat_columns) * 3))

        # Filtrare i giocatori della squadra avversaria con il ruolo corrispondente
        giocatori_avversari = giocatori[(giocatori['Squadra_giocatore'] == squadra_avversaria) & (giocatori['Ruolo'].isin(ruolo_avversario))]

        # Controllare se ci sono abbastanza giocatori
        if giocatori_avversari.empty:
            return pd.Series([None] * (3 + len(stat_columns) * 3))

        # Ordinare per minuti giocati e selezionare i primi tre
        top_giocatori = giocatori_avversari.sort_values(by='Minuti Giocati', ascending=False).head(3)

        # Assicurarsi che ci siano sempre tre valori restituiti
        top_giocatori_list = top_giocatori['Giocatore'].tolist()
        while len(top_giocatori_list) < 3:
            top_giocatori_list.append(None)

        # Ottenere le statistiche associate
        stats_values = []
        for i in range(3):
            if i < len(top_giocatori):
                stats_values.extend(top_giocatori.iloc[i][stat_columns].values)
            else:
                stats_values.extend([None] * len(stat_columns))

        return pd.Series(top_giocatori_list + stats_values)

    # Applicare la funzione al dataset
    new_columns = ['Avversario_1', 'Avversario_2', 'Avversario_3']
    for i in range(1, 4):
        new_columns.extend([col + f"_avv{i}" for col in stat_columns])

    dataset[new_columns] = dataset.apply(get_top_3_players, axis=1)
    dataset.to_csv(parent_dir + r"\FILES_PREDIZIONI\data\processed\dataset_2.csv", sep=';', index=False)