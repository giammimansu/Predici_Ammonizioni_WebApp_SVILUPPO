from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import pandas as pd
import os
import sys
import scipy.sparse
from .FILES_PREDIZIONI.input_data import crea_df_input
from .FILES_PREDIZIONI.config import best_model, encoder, scaler

# Set up paths for loading data
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
files_predizioni_dir = os.path.join(parent_dir, 'ammonizioni', 'FILES_PREDIZIONI')

sys.path.append(files_predizioni_dir)

# Importa i file da FILES_PREDIZIONI
def index(request):
    casa = None
    trasferta = None
    error_message = None

    if request.method == 'POST':
        casa = request.POST.get('casa')
        trasferta = request.POST.get('trasferta')
        arbitro = request.POST.get('arbitro')
        giocatori_casa = request.POST.getlist('giocatori_casa')
        giocatori_trasferta = request.POST.getlist('giocatori_trasferta')

        if not casa or not trasferta:
            error_message = "Devi selezionare entrambe le squadre."
        elif not arbitro:
            error_message = "Devi selezionare un arbitro."
        elif not giocatori_casa and not giocatori_trasferta:
            error_message = "Devi selezionare almeno un giocatore."
        else:
            # Redirect to the second page with the selected data
            request.session['casa'] = casa
            request.session['trasferta'] = trasferta
            request.session['arbitro'] = arbitro
            request.session['giocatori_casa'] = giocatori_casa
            request.session['giocatori_trasferta'] = giocatori_trasferta
            return redirect('interazioni')

    # Load data for the form
    try:
        arbitro = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'processed', 'dataset_2.csv'), sep=';', header=0)
        squadre_df = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'silver', 'statistiche_squadre.csv'), sep=';')
        giocatori_df = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'silver', 'statistiche_giocatori.csv'), sep=';')

        # Set up player roles and sorting
        ordine_ruoli = ['Por', 'Dif', 'Dif.Cen', 'Dif.Att', 'Cen.Dif', 'Cen', 'Cen.Att', 'Att.Dif', 'Att', 'Att.Cen']
        giocatori_df['Ruolo'] = pd.Categorical(giocatori_df['Ruolo'], categories=ordine_ruoli, ordered=True)
        giocatori_df = giocatori_df.sort_values(by='Ruolo')

    except Exception as e:
        return JsonResponse({'error': f"Error: {e}"})

    squadre = [s.strip() for s in squadre_df['Squadra'].unique()]
    arbitri = sorted([a.strip() for a in arbitro['Arbitro'].unique()], key=lambda x: x.split()[-1])

    giocatori_casa = []
    giocatori_trasferta = []

    if casa and trasferta:
        giocatori_casa = giocatori_df[giocatori_df['Squadra_giocatore'] == casa]['Giocatore'].tolist()
        giocatori_trasferta = giocatori_df[giocatori_df['Squadra_giocatore'] == trasferta]['Giocatore'].tolist()

    context = {
        'squadre': squadre,
        'arbitri': arbitri,
        'giocatori_casa': giocatori_casa,
        'giocatori_trasferta': giocatori_trasferta,
        'error_message': error_message
    }

    return render(request, 'ammonizioni/index.html', context)



def interazioni(request):
    casa = request.session.get('casa')
    trasferta = request.session.get('trasferta')
    arbitro = request.session.get('arbitro')
    giocatori_casa = request.session.get('giocatori_casa')
    giocatori_trasferta = request.session.get('giocatori_trasferta')

    error_message = None  # Definisci error_message all'inizio

    if request.method == 'POST':
        interazioni = request.POST.getlist('interazioni')
        avversari = request.POST.getlist('avversari')

        # Creare la lista di liste di avversari di dimensione 3
        avversari_liste = [avversari[i:i+3] for i in range(0, len(avversari), 3)]

        # Validazione delle interazioni
        for avversari_giocatore in avversari_liste:
            if len(avversari_giocatore) != 3:
                error_message = "Ogni giocatore deve avere esattamente 3 avversari selezionati."
                context = {
                    'casa': casa,
                    'trasferta': trasferta,
                    'arbitro': arbitro,
                    'giocatori_casa': giocatori_casa,
                    'giocatori_trasferta': giocatori_trasferta,
                    'error_message': error_message
                }
                return render(request, 'ammonizioni/interazioni.html', context)

        # Unire le liste di giocatori di casa e trasferta
        lista_giocatori = giocatori_casa + giocatori_trasferta

        # Processa le interazioni e fai le previsioni
        try:
            input_data = crea_df_input(parent_dir, casa, trasferta, arbitro, lista_giocatori, avversari_liste)
            try:
                input_data = input_data.drop(columns=['Squadra_giocatore', 'Avversario_1', 'Avversario_2', 'Avversario_3'])
            except Exception as e:
                print(f"Error: {e}")
            print(input_data.columns)  # Aggiungi un log per verificare il dataframe
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
            #arrotondo results al secondo decimale
            results = [(giocatore, round(prob, 2)) for giocatore, prob in results]
            context = {
                'casa': casa,
                'trasferta': trasferta,
                'arbitro': arbitro,
                'giocatori_casa': giocatori_casa,
                'giocatori_trasferta': giocatori_trasferta,
                'results': results  # Aggiungi results al contesto
            }
            return render(request, 'ammonizioni/interazioni.html', context)
        except ValueError as e:
            error_message = str(e)
            context = {
                'casa': casa,
                'trasferta': trasferta,
                'arbitro': arbitro,
                'giocatori_casa': giocatori_casa,
                'giocatori_trasferta': giocatori_trasferta,
                'error_message': error_message
            }
            return render(request, 'ammonizioni/interazioni.html', context)

    context = {
        'casa': casa,
        'trasferta': trasferta,
        'arbitro': arbitro,
        'giocatori_casa': giocatori_casa,
        'giocatori_trasferta': giocatori_trasferta,
        'error_message': error_message  # Aggiungi error_message al contesto
    }

    return render(request, 'ammonizioni/interazioni.html', context)


from django.http import JsonResponse
import pandas as pd
import os

# Set up paths for loading data
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
files_predizioni_dir = os.path.join(parent_dir, 'ammonizioni', 'FILES_PREDIZIONI')

def get_players(request):
    casa = request.GET.get('casa')
    trasferta = request.GET.get('trasferta')

    try:
        giocatori_df = pd.read_csv(os.path.join(files_predizioni_dir, 'data', 'silver', 'statistiche_giocatori.csv'), sep=';')

        giocatori_casa = giocatori_df[giocatori_df['Squadra_giocatore'] == casa]['Giocatore'].tolist() if casa else []
        giocatori_trasferta = giocatori_df[giocatori_df['Squadra_giocatore'] == trasferta]['Giocatore'].tolist() if trasferta else []

        return JsonResponse({
            'giocatori_casa': giocatori_casa,
            'giocatori_trasferta': giocatori_trasferta
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})