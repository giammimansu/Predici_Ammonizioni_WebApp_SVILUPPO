import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import ctypes
import joblib
from input_data import crea_df_input
from main import aggiorno_dati_e_modello
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import scipy.sparse

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PrediciAmmonizioni")

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))


best_model = joblib.load(os.path.join(parent_dir, 'ml-model-project', 'models', 'best_model.pkl'))
encoder = joblib.load(os.path.join(parent_dir, 'ml-model-project', 'models', 'encoder.pkl'))
scaler = joblib.load(os.path.join(parent_dir, 'ml-model-project', 'models', 'scaler.pkl'))


# Creazione della finestra principale
root = tk.Tk()
root.title("Predici Ammonizioni")



# Imposta l'icona della finestra principale
root.iconbitmap(os.path.join(parent_dir, r'ml-model-project\logo_pallone.ico'))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(6, weight=1)
root.grid_rowconfigure(8, weight=1)

def update_dati_progress():
    progress_bar.stop()
    progress_bar.grid_forget()
    messagebox.showinfo("Aggiornamento Dati", "I dati sono stati aggiornati con successo!")


# Funzione per aggiornare i dati
def aggiorna_dati():
    # Mostra la progress bar
    progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
    progress_bar.start()
    
    # Funzione per aggiornare i dati e il modello
    def update_data():
        try:
            aggiorno_dati_e_modello()
            root.after(2000, lambda: update_dati_progress())
        except Exception as e:
            progress_bar.stop()
            progress_bar.grid_forget()
            messagebox.showerror("Errore", f"Errore durante l'aggiornamento dei dati: {e}")

    # Simuliamo un processo lungo per l'aggiornamento dei dati
    root.after(100, update_data)

# Bottone rosso per aggiornare i dati

aggiorna_button = tk.Button(root, text="Aggiorna Dati", command=aggiorna_dati, bg="yellow", fg="black")
aggiorna_button.grid(row=0, column=0, padx=10, pady=10)

# Creazione della Progress Bar per l'aggiornamento dei dati
progress_bar = ttk.Progressbar(root, mode="indeterminate")


# Caricamento dati con gestione degli errori
try:
    arbitro = pd.read_csv(os.path.join(parent_dir, r'ml-model-project\data\processed\dataset.csv'), sep=';', header=0)
    squadre_df = pd.read_csv(os.path.join(parent_dir, r'ml-model-project\data\silver\statistiche_squadre.csv'), sep=';')
    giocatori_df = pd.read_csv(os.path.join(parent_dir, r'ml-model-project\data\silver\statistiche_giocatori.csv'), sep=';')
    ordine_ruoli = ['Por', 'Dif', 'Dif.Cen', 'Dif.Att', 'Cen.Dif', 'Cen', 'Cen.Att', 'Att.Dif', 'Att', 'Att.Cen']
    giocatori_df['Ruolo'] = pd.Categorical(giocatori_df['Ruolo'], categories=ordine_ruoli, ordered=True)
    giocatori_df = giocatori_df.sort_values(by='Ruolo')
except FileNotFoundError as e:
    messagebox.showerror("Errore", f"File non trovato: {e.filename}")
    root.destroy()
    exit()
except pd.errors.EmptyDataError as e:
    messagebox.showerror("Errore", f"File vuoto o malformato: {e}")
    root.destroy()
    exit()
except Exception as e:
    messagebox.showerror("Errore", f"Errore durante la lettura dei file: {e}")
    root.destroy()
    exit()

# Lista squadre uniche
squadre = [s.strip() for s in squadre_df['Squadra'].unique()]
# Lista arbitri unici ordinati per cognome
arbitri = sorted([a.strip() for a in arbitro['Arbitro'].unique()], key=lambda x: x.split()[-1])

# Liste per i giocatori selezionati
giocatori_selezionati_casa = []
giocatori_selezionati_trasferta = []

# Variabili per i contatori
contatore_casa = tk.StringVar(value="Casa (0)")
contatore_trasferta = tk.StringVar(value="Trasferta (0)")

# Variabili per le squadre selezionate
casa_var = tk.StringVar()
trasferta_var = tk.StringVar()
arbitro_var = tk.StringVar()

# Funzioni per aggiornare le listbox
def update_giocatori_casa(*args):
    casa = casa_var.get().strip().replace("'", "")
    giocatori_casa_listbox.delete(0, tk.END)
    giocatori_casa = giocatori_df[giocatori_df['Squadra_giocatore'].str.strip() == casa]
   
    for index, row in giocatori_casa.iterrows():
        giocatore = row['Giocatore']
        ruolo = row['Ruolo']
        giocatori_casa_listbox.insert(tk.END, f"{giocatore} ({ruolo})")

def update_giocatori_trasferta(*args):
    trasferta = trasferta_var.get().strip().replace("'", "")
    giocatori_trasferta_listbox.delete(0, tk.END)
    giocatori_trasferta = giocatori_df[giocatori_df['Squadra_giocatore'].str.strip() == trasferta]
   
    for index, row in giocatori_trasferta.iterrows():
        giocatore = row['Giocatore']
        ruolo = row['Ruolo']
        giocatori_trasferta_listbox.insert(tk.END, f"{giocatore} ({ruolo})")

def filtra_giocatori_casa(*args):
    search_term = search_casa_var.get().strip().lower()
   
    # Verifica se il termine di ricerca è uguale al placeholder
    if search_term == "cerca giocatori casa":
        search_term = ""  # Reset del termine di ricerca se è uguale al placeholder

    print(f"Filtrando giocatori per 'Casa' con il termine di ricerca: '{search_term}'")  # Debugging line
    giocatori_casa_listbox.delete(0, tk.END)  # Pulisce la lista
    casa = casa_var.get().strip().replace("'","")
    print(f"Squadra di Casa selezionata: {casa}")  # Debugging line
   
    # Verifica che la squadra di casa non sia vuota
    if not casa:
        print("Errore: nessuna squadra di casa selezionata!")
        return  # Non proseguire se la squadra di casa non è selezionata

    giocatori_casa = giocatori_df[giocatori_df['Squadra_giocatore'].str.strip() == casa]
    print(f"Giocatori trovati per casa: {giocatori_casa}")  # Debugging line
    if search_term:
        for index, row in giocatori_casa.iterrows():
            giocatore = row['Giocatore']
            ruolo = row['Ruolo']
            if search_term in giocatore.lower():
                print(f"Aggiungendo giocatore: {giocatore}")  # Debugging line
                giocatori_casa_listbox.insert(tk.END, f"{giocatore} ({ruolo})")
    else:
        for index, row in giocatori_casa.iterrows():
            giocatore = row['Giocatore']
            ruolo = row['Ruolo']
            print(f"Aggiungendo giocatore (nessuna ricerca): {giocatore}")  # Debugging line
            giocatori_casa_listbox.insert(tk.END, f"{giocatore} ({ruolo})")

def filtra_giocatori_trasferta(*args):
    search_term = search_trasferta_var.get().strip().lower()
   
    # Verifica se il termine di ricerca è uguale al placeholder
    if search_term == "cerca giocatori trasferta":
        search_term = ""  # Reset del termine di ricerca se è uguale al placeholder

    print(f"Filtrando giocatori per 'Trasferta' con il termine di ricerca: '{search_term}'")  # Debugging line
    giocatori_trasferta_listbox.delete(0, tk.END)  # Pulisce la lista
    trasferta = trasferta_var.get().strip().replace("'","")
   
    # Verifica che la squadra di trasferta non sia vuota
    if not trasferta:
        print("Errore: nessuna squadra di trasferta selezionata!")
        return  # Non proseguire se la squadra di trasferta non è selezionata

    giocatori_trasferta = giocatori_df[giocatori_df['Squadra_giocatore'].str.strip() == trasferta]
    print(f"Giocatori trovati per trasferta: {giocatori_trasferta}")  # Debugging line
    if search_term:
        for index, row in giocatori_trasferta.iterrows():
            giocatore = row['Giocatore']
            ruolo = row['Ruolo']
            if search_term in giocatore.lower():
                print(f"Aggiungendo giocatore: {giocatore}")  # Debugging line
                giocatori_trasferta_listbox.insert(tk.END, f"{giocatore} ({ruolo})")
    else:
        for index, row in giocatori_trasferta.iterrows():
            giocatore = row['Giocatore']
            ruolo = row['Ruolo']
            print(f"Aggiungendo giocatore (nessuna ricerca): {giocatore}")  # Debugging line
            giocatori_trasferta_listbox.insert(tk.END, f"{giocatore} ({ruolo})")

# Funzioni per gestire il placeholder
def on_entry_focus_in(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="black")  # Testo normale

def on_entry_focus_out(entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg="gray")  # Testo grigio per simulare placeholder

# ComboBox per la selezione delle squadre
tk.Label(root, text="Squadra di Casa").grid(row=1, column=0, padx=10, pady=5, sticky="w")
casa_combobox = ttk.Combobox(root, textvariable=casa_var, values=squadre)
casa_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
casa_combobox.bind("<<ComboboxSelected>>", lambda *args: [svuota_lista_giocatori_casa(), update_giocatori_casa()])

tk.Label(root, text="Squadra Trasferta").grid(row=2, column=0, padx=10, pady=5, sticky="w")
trasferta_combobox = ttk.Combobox(root, textvariable=trasferta_var, values=squadre)
trasferta_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
trasferta_combobox.bind("<<ComboboxSelected>>", lambda *args: [svuota_lista_giocatori_trasferta(), update_giocatori_trasferta()])

tk.Label(root, text="Arbitro").grid(row=3, column=0, padx=10, pady=5, sticky="w")
arbitro_combobox = ttk.Combobox(root, textvariable=arbitro_var, values=arbitri)
arbitro_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

# Listbox per i giocatori
tk.Label(root, text="Giocatori Casa").grid(row=4, column=0, padx=10, pady=5, sticky="w")
giocatori_casa_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=6)
giocatori_casa_listbox.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Giocatori Trasferta").grid(row=4, column=1, padx=10, pady=5, sticky="w")
giocatori_trasferta_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=6)
giocatori_trasferta_listbox.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

# Barre di ricerca per i giocatori
search_casa_var = tk.StringVar()
search_trasferta_var = tk.StringVar()

search_casa_entry = tk.Entry(root, textvariable=search_casa_var, fg="gray")
search_casa_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
search_casa_var.trace("w", filtra_giocatori_casa)

placeholder_text_casa = "Cerca Giocatori Casa"
search_casa_entry.insert(0, placeholder_text_casa)

# Associa gli eventi per gestire il placeholder
search_casa_entry.bind("<FocusIn>", lambda event: on_entry_focus_in(search_casa_entry, placeholder_text_casa))
search_casa_entry.bind("<FocusOut>", lambda event: on_entry_focus_out(search_casa_entry, placeholder_text_casa))

search_trasferta_entry = tk.Entry(root, textvariable=search_trasferta_var, fg="gray")
search_trasferta_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
search_trasferta_var.trace("w", filtra_giocatori_trasferta)

placeholder_text_trasferta = "Cerca Giocatori Trasferta"
search_trasferta_entry.insert(0, placeholder_text_trasferta)

# Associa gli eventi per gestire il placeholder
search_trasferta_entry.bind("<FocusIn>", lambda event: on_entry_focus_in(search_trasferta_entry, placeholder_text_trasferta))
search_trasferta_entry.bind("<FocusOut>", lambda event: on_entry_focus_out(search_trasferta_entry, placeholder_text_trasferta))

# Funzione per aggiungere giocatori alle liste
def aggiungi_giocatori_casa():
    selezionati = [giocatori_casa_listbox.get(i) for i in giocatori_casa_listbox.curselection()]
    for giocatore in selezionati:
        if giocatore not in giocatori_selezionati_casa:
            giocatori_selezionati_casa.append(giocatore)
    update_selected_table()

def aggiungi_giocatori_trasferta():
    selezionati = [giocatori_trasferta_listbox.get(i) for i in giocatori_trasferta_listbox.curselection()]
    for giocatore in selezionati:
        if giocatore not in giocatori_selezionati_trasferta:
            giocatori_selezionati_trasferta.append(giocatore)
    update_selected_table()

# Bottoni per aggiungere i giocatori selezionati
ttk.Button(root, text="Aggiungi Selezionati a Casa", command=aggiungi_giocatori_casa).grid(row=7, column=0, padx=10, pady=5)
ttk.Button(root, text="Aggiungi Selezionati a Trasferta", command=aggiungi_giocatori_trasferta).grid(row=7, column=1, padx=10, pady=5)

# Creazione della tabella per mostrare i giocatori selezionati
selected_table = ttk.Treeview(root, columns=("Casa", "Trasferta"), show="headings")
selected_table.heading("Casa", text="Casa")
selected_table.heading("Trasferta", text="Trasferta")
selected_table.grid(row=8, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

def update_selected_table():
    selected_table.delete(*selected_table.get_children())
    max_len = max(len(giocatori_selezionati_casa), len(giocatori_selezionati_trasferta))
    for i in range(max_len):
        casa_giocatore = giocatori_selezionati_casa[i] if i < len(giocatori_selezionati_casa) else ""
        trasferta_giocatore = giocatori_selezionati_trasferta[i] if i < len(giocatori_selezionati_trasferta) else ""
        selected_table.insert("", tk.END, values=(casa_giocatore, trasferta_giocatore))
    contatore_casa.set(f"Casa ({len(giocatori_selezionati_casa)})")
    contatore_trasferta.set(f"Trasferta ({len(giocatori_selezionati_trasferta)})")
    selected_table.heading("Casa", text=contatore_casa.get())
    selected_table.heading("Trasferta", text=contatore_trasferta.get())

# Funzione per svuotare le liste dei giocatori di casa
def svuota_lista_giocatori_casa():
    global giocatori_selezionati_casa
    giocatori_selezionati_casa = []
    update_selected_table()

# Funzione per svuotare le liste dei giocatori di trasferta
def svuota_lista_giocatori_trasferta():
    global giocatori_selezionati_trasferta
    giocatori_selezionati_trasferta = []
    update_selected_table()

# Funzione per svuotare tutte le liste
def svuota_lista_giocatori():
    svuota_lista_giocatori_casa()
    svuota_lista_giocatori_trasferta()

# Variabile per il testo del risultato
result_text = tk.StringVar()

# Funzione per fare la predizione (placeholder)
# ...existing code...

# Funzione per fare la predizione (placeholder)
# ...existing code...

# Funzione per fare la predizione (placeholder)
def predict():
    # Verifica che tutte le selezioni siano state fatte
    if not casa_var.get() or not trasferta_var.get() or not arbitro_var.get() or not (giocatori_selezionati_casa or giocatori_selezionati_trasferta):
        messagebox.showerror("Errore", "Seleziona le due squadre, l'arbitro e almeno un giocatore.")
        return

    # Creazione della finestra di riepilogo
    riepilogo = tk.Toplevel(root)
    riepilogo.title("Riepilogo")

    bold_font = ("TkDefaultFont", 10, "bold")

    # Mostra l'arbitro selezionato
    tk.Label(riepilogo, text="Arbitro:", font=bold_font).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Label(riepilogo, text=arbitro_var.get()).grid(row=0, column=1, padx=10, pady=5, sticky="w")

    # Mostra le squadre selezionate
    tk.Label(riepilogo, text="Squadra di Casa:", font=bold_font).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk.Label(riepilogo, text=casa_var.get()).grid(row=1, column=1, padx=10, pady=5, sticky="w")
    tk.Label(riepilogo, text="Squadra Trasferta:", font=bold_font).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    tk.Label(riepilogo, text=trasferta_var.get()).grid(row=2, column=1, padx=10, pady=5, sticky="w")

    # Mostra i giocatori selezionati per squadra
    tk.Label(riepilogo, text="Giocatori Casa:", font=bold_font).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    giocatori_casa_text = "\n".join(giocatori_selezionati_casa)
    tk.Label(riepilogo, text=giocatori_casa_text).grid(row=4, column=0, padx=10, pady=5, sticky="w")

    tk.Label(riepilogo, text="Giocatori Trasferta:", font=bold_font).grid(row=3, column=1, padx=10, pady=5, sticky="w")
    giocatori_trasferta_text = "\n".join(giocatori_selezionati_trasferta)
    tk.Label(riepilogo, text=giocatori_trasferta_text).grid(row=4, column=1, padx=10, pady=5, sticky="w")

    # Funzione per creare le interazioni tra i giocatori
    def crea_interazioni():
        interazioni = tk.Toplevel(riepilogo)
        interazioni.title("Crea Interazioni Giocatori")

        tk.Label(interazioni, text="Giocatori Casa", font=bold_font).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(interazioni, text="Giocatori Trasferta", font=bold_font).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        casa_listbox = tk.Listbox(interazioni, selectmode=tk.SINGLE, height=10)
        casa_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        for giocatore in giocatori_selezionati_casa:
            casa_listbox.insert(tk.END, giocatore)

        trasferta_listbox = tk.Listbox(interazioni, selectmode=tk.MULTIPLE, height=10)
        trasferta_listbox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        for giocatore in giocatori_selezionati_trasferta:
            trasferta_listbox.insert(tk.END, giocatore)

        avversari = {}

        def aggiungi_interazione():
            casa_giocatore = casa_listbox.get(tk.ACTIVE)
            trasferta_giocatori = [trasferta_listbox.get(i) for i in trasferta_listbox.curselection()]
            if len(trasferta_giocatori) != 3:
                messagebox.showerror("Errore", "Seleziona esattamente 3 giocatori della squadra trasferta.")
                return
            avversari[casa_giocatore] = trasferta_giocatori
            messagebox.showinfo("Successo", f"Interazione aggiunta per {casa_giocatore}")

        def conferma_interazioni():
            for giocatore in giocatori_selezionati_casa:
                if giocatore not in avversari:
                    avversari[giocatore] = ["", "", ""]
            interazioni.destroy()
            conferma(avversari)

        tk.Button(interazioni, text="Aggiungi Interazione", command=aggiungi_interazione).grid(row=2, column=0, padx=10, pady=5)
        tk.Button(interazioni, text="Conferma Interazioni", command=conferma_interazioni).grid(row=2, column=1, padx=10, pady=5)

    # Funzione per confermare la predizione
    def conferma(avversari):
        casa = casa_var.get()
        trasferta = trasferta_var.get()
        arbitro = arbitro_var.get()
        
        # Rimuovi il ruolo dal nome del giocatore
        giocatori = [giocatore.split(' (')[0] for giocatore in (giocatori_selezionati_casa + giocatori_selezionati_trasferta)]

        input_data = crea_df_input(parent_dir, casa, trasferta, arbitro, giocatori, avversari)
        
        print(input_data)

        results = []
        for index, row in input_data.iterrows():
            df_input = pd.DataFrame([row])
            df_encoded = encoder.transform(df_input[['Casa', 'Trasferta', 'Giocatore', 'Arbitro','Ruolo']])
            numerical_features = df_input.drop(columns=['Casa', 'Trasferta', 'Giocatore', 'Arbitro', 'Ruolo']).columns
            df_scaled = scaler.transform(df_input[numerical_features])
            df_combined = scipy.sparse.hstack([df_encoded, df_scaled])
            probability = best_model.predict_proba(df_combined)[:, 1]
            results.append((row['Giocatore'], probability[0] * 100))

        # Ordina i risultati in ordine decrescente di probabilità
        results.sort(key=lambda x: x[1], reverse=True)
        results_text = [f"Probability of {giocatore} receiving a yellow card: {prob:.2f}%" for giocatore, prob in results]

        # Assicurati che result_text sia accessibile
        global result_text
        result_text.set("\n".join(results_text))
        riepilogo.destroy()

    # Funzione per annullare la predizione
    def annulla():
        svuota_lista_giocatori()
        casa_var.set("")
        trasferta_var.set("")
        arbitro_var.set("")
        riepilogo.destroy()

    # Bottoni per creare interazioni o annullare
    ttk.Button(riepilogo, text="Crea Interazioni Giocatori", command=crea_interazioni).grid(row=5, column=0, padx=10, pady=5)
    ttk.Button(riepilogo, text="Annulla", command=annulla).grid(row=5, column=1, padx=10, pady=5)

# Pulsante per fare la predizione
tk.Button(root, text="Predict", command=predict, bg="green", fg="black").grid(row=9, column=1, padx=10, pady=5)

# Pulsante per svuotare la lista dei giocatori selezionati
ttk.Button(root, text="Svuota Liste", command=svuota_lista_giocatori).grid(row=9, column=0, padx=10, pady=5)

# Aggiungi un widget per mostrare il risultato
result_label = tk.Label(root, textvariable=result_text, wraplength=400)
result_label.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

# Avvio della finestra
root.mainloop()