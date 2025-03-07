import os 
import joblib
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
url_calendario = r"https://fbref.com/it/comp/11/calendario/Risultati-e-partite-di-Serie-A"
url_stats_giocatori  = r"https://fbref.com/it/comp/11/misc/Statistiche-di-Serie-A"
url_stats_difensive_squadre = r"https://fbref.com/it/comp/11/defense/Statistiche-di-Serie-A"
chrome_driver_path = parent_dir+"\chromedriver-win64\chromedriver.exe"  

# Carica i modelli e gli encoder
best_model = joblib.load(os.path.join(parent_dir, 'FILES_PREDIZIONI' , 'models', 'best_model.pkl'))
encoder = joblib.load(os.path.join(parent_dir, 'FILES_PREDIZIONI' , 'models', 'encoder.pkl'))
scaler = joblib.load(os.path.join(parent_dir, 'FILES_PREDIZIONI' , 'models', 'scaler.pkl'))