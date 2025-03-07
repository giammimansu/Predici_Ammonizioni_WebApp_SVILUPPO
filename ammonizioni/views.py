from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pandas as pd
import joblib
import os
import scipy.sparse
import sys

# Aggiungi FILES_PREDIZIONI alla variabile sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
files_predizioni_dir = os.path.join(parent_dir, 'ammonizioni', 'FILES_PREDIZIONI')

print(files_predizioni_dir)

# Aggiungi il percorso a sys.path per importare i file da FILES_PREDIZIONI
sys.path.append(files_predizioni_dir)

# Importa i file da FILES_PREDIZIONI
from input_data import crea_df_input
from main import aggiorno_dati_e_modello
from config import best_model, encoder, scaler


def index(request):
    casa = None
    trasferta = None
    error_message = None

    if request.method == 'POST':
        # Handle form submission and data processing here
        casa = request.POST.get('casa')
        trasferta = request.POST.get('trasferta')
        arbitro = request.POST.get('arbitro')
        giocatori_casa = request.POST.getlist('giocatori_casa')
        giocatori_trasferta = request.POST.getlist('giocatori_trasferta')

        # Debugging: Print selected teams
        print("Selected Casa:", casa)
        print("Selected Trasferta:", trasferta)

        if not casa or not trasferta:
            error_message = "Devi selezionare entrambe le squadre."
        elif not arbitro:
            error_message = "Devi selezionare un arbitro."
        elif not giocatori_casa and not giocatori_trasferta:
            error_message = "Devi selezionare almeno un giocatore."

        if not error_message:
            input_data = crea_df_input(parent_dir, casa, trasferta, arbitro, giocatori_casa + giocatori_trasferta)
            results = []

            for index, row in input_data.iterrows():
                df_input = pd.DataFrame([row])
                df_encoded = encoder.transform(df_input[['Casa', 'Trasferta', 'Giocatore', 'Arbitro', 'Ruolo']])
                numerical_features = df_input.drop(columns=['Casa', 'Trasferta', 'Giocatore', 'Arbitro', 'Ruolo']).columns
                df_scaled = scaler.transform(df_input[numerical_features])
                df_combined = scipy.sparse.hstack([df_encoded, df_scaled])
                probability = best_model.predict_proba(df_combined)[:, 1]
                results.append((row['Giocatore'], probability[0] * 100))

            results.sort(key=lambda x: x[1], reverse=True)
            return render(request, 'ammonizioni/index.html', {'results': results, 'error_message': error_message})

    # Load data for the form
    try:
        arbitro = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'processed', 'dataset.csv'), sep=';', header=0)
        squadre_df = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'silver', 'statistiche_squadre.csv'), sep=';')
        giocatori_df = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'silver', 'statistiche_giocatori.csv'), sep=';')
        
        # Debugging: Print columns of the DataFrames
        print("Columns in arbitro DataFrame:", arbitro.columns)
        print("Columns in squadre_df DataFrame:", squadre_df.columns)
        print("Columns in giocatori_df DataFrame:", giocatori_df.columns)
        
        ordine_ruoli = ['Por', 'Dif', 'Dif.Cen', 'Dif.Att', 'Cen.Dif', 'Cen', 'Cen.Att', 'Att.Dif', 'Att', 'Att.Cen']
        giocatori_df['Ruolo'] = pd.Categorical(giocatori_df['Ruolo'], categories=ordine_ruoli, ordered=True)
        giocatori_df = giocatori_df.sort_values(by='Ruolo')
        
        # Debugging: Print unique values in 'Squadra_giocatore' column
        print("Unique values in 'Squadra_giocatore' column:", giocatori_df['Squadra_giocatore'].unique())
    except FileNotFoundError as e:
        return HttpResponse(f"File not found: {e.filename}")
    except pd.errors.EmptyDataError as e:
        return HttpResponse(f"Empty or malformed file: {e}")
    except Exception as e:
        return HttpResponse(f"Error reading files: {e}")

    squadre = [s.strip() for s in squadre_df['Squadra'].unique()]
    arbitri = sorted([a.strip() for a in arbitro['Arbitro'].unique()], key=lambda x: x.split()[-1])

    giocatori_casa = []
    giocatori_trasferta = []

    if casa and trasferta:
        giocatori_casa = giocatori_df[giocatori_df['Squadra_giocatore'] == casa]['Giocatore'].tolist()
        giocatori_trasferta = giocatori_df[giocatori_df['Squadra_giocatore'] == trasferta]['Giocatore'].tolist()

    # Debugging: Print lists of players
    print("Giocatori Casa:", giocatori_casa)
    print("Giocatori Trasferta:", giocatori_trasferta)

    context = {
        'squadre': squadre,
        'arbitri': arbitri,
        'giocatori_casa': giocatori_casa,
        'giocatori_trasferta': giocatori_trasferta,
        'error_message': error_message
    }

    return render(request, 'ammonizioni/index.html', context)

def get_players(request):
    casa = request.GET.get('casa')
    trasferta = request.GET.get('trasferta')

    try:
        giocatori_df = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'silver', 'statistiche_giocatori.csv'), sep=';')
        ordine_ruoli = ['Por', 'Dif', 'Dif.Cen', 'Dif.Att', 'Cen.Dif', 'Cen', 'Cen.Att', 'Att.Dif', 'Att', 'Att.Cen']
        giocatori_df['Ruolo'] = pd.Categorical(giocatori_df['Ruolo'], categories=ordine_ruoli, ordered=True)
        giocatori_df = giocatori_df.sort_values(by='Ruolo')
    except FileNotFoundError as e:
        return JsonResponse({'error': f"File not found: {e.filename}"})
    except pd.errors.EmptyDataError as e:
        return JsonResponse({'error': f"Empty or malformed file: {e}"})
    except Exception as e:
        return JsonResponse({'error': f"Error reading files: {e}"})

    giocatori_casa = giocatori_df[giocatori_df['Squadra_giocatore'] == casa]['Giocatore'].tolist()
    giocatori_trasferta = giocatori_df[giocatori_df['Squadra_giocatore'] == trasferta]['Giocatore'].tolist()

    return JsonResponse({
        'giocatori_casa': giocatori_casa,
        'giocatori_trasferta': giocatori_trasferta
    })