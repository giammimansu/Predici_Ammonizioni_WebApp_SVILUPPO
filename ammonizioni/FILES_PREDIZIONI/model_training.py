import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))

def train_model():
    # Step 1: Load the Data
    data = pd.read_csv(parent_dir + r"\ammonizioni\FILES_PREDIZIONI\data\processed\dataset_2.csv", sep=';', header=0)
    
    # Step 2: Data Cleaning
    data.dropna(inplace=True)  # Handle missing values
    
    # Step 3: Feature Selection
    X = data.drop(columns=['Cartellini Gialli', 'Cartellini Rossi',"Squadra_giocatore",'Avversario_1', 'Avversario_2', 'Avversario_3'])
    y = data["Cartellini Gialli"]
    
    # Step 4: Encode Categorical Features
    features_to_encode = ['Casa', 'Trasferta', 'Giocatore', 'Arbitro', 'Ruolo']
    encoder = OneHotEncoder()
    X_encoded = encoder.fit_transform(X[features_to_encode])
    
    # Step 5: Normalize Numerical Features
    numerical_features = X.drop(columns=features_to_encode).columns
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X[numerical_features])
    
    # Combine encoded categorical features and scaled numerical features
    import scipy.sparse
    X_combined = scipy.sparse.hstack([X_encoded, X_scaled])
    
    # Step 6: Balance the Dataset
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_combined, y)
    
    # Step 7: Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
    
    # Step 8: Hyperparameter Tuning
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    grid_search = GridSearchCV(estimator=RandomForestClassifier(random_state=42), param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)
    
    # Step 9: Model Selection and Training
    best_model = grid_search.best_estimator_
    best_model.fit(X_train, y_train)
    
    # Step 10: Model Evaluation
    y_pred = best_model.predict(X_test)
    y_pred_proba = best_model.predict_proba(X_test)
    
    print(classification_report(y_test, y_pred))
    print("ROC AUC Score:", roc_auc_score(y_test, y_pred_proba, multi_class='ovr'))
    
    # Save the model, encoder, and scaler
    joblib.dump(best_model, parent_dir + r"\ammonizioni\FILES_PREDIZIONI\models\best_model.pkl")
    joblib.dump(encoder, parent_dir + r'\ammonizioni\FILES_PREDIZIONI\models\encoder.pkl')
    joblib.dump(scaler, parent_dir + r'\ammonizioni\FILES_PREDIZIONI\models\scaler.pkl')


