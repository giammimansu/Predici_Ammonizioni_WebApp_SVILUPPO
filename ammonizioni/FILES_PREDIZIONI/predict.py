import pandas as pd
import joblib
from input_data import crea_df_input

# Load the model and encoder
best_model = joblib.load(r'C:\Users\gianm\OneDrive\Desktop\Football Stats\ML_Model\ml-model-project_SVILUPPO\models\best_model.pkl')
encoder = joblib.load(r'C:\Users\gianm\OneDrive\Desktop\Football Stats\ML_Model\ml-model-project_SVILUPPO\models\encoder.pkl')

# Predict the probability of a new player receiving a yellow card
input_data = pd.read_csv(r"C:\Users\gianm\OneDrive\Desktop\Football Stats\ML_Model\input_data.csv", sep=';', header=0)

for index, row in input_data.iterrows():
    # Crea un nuovo dataframe con una singola riga
    df_input = pd.DataFrame([row])
    df_encoded = encoder.transform(df_input[['Casa', 'Trasferta', 'Giocatore',"Arbitro"]])
    probability = best_model.predict_proba(df_encoded)[:, 1]
    print("Probability of {} receiving a yellow card: {:.2f}%".format(row["Giocatore"], probability[0] * 100))