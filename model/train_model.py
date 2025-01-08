import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os

# Funkcja do wczytywania danych z pliku CSV i przypisania etykiety na podstawie nazwy pliku
def wczytaj_dane_z_csv(plik_csv, jezyk):
    df = pd.read_csv(plik_csv)
    df['język'] = jezyk
    return df

# Wczytanie danych
df_pol = wczytaj_dane_z_csv("data/polski.csv", "polski")
df_eng = wczytaj_dane_z_csv("data/angielski.csv", "angielski")
df_deu = wczytaj_dane_z_csv("data/niemiecki.csv", "niemiecki")

df = pd.concat([df_pol, df_eng, df_deu], ignore_index=True)

# Przygotowanie zmiennych
texts = df['tekst'].values
labels = df['język'].values

# Przetwarzanie danych
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = np.array(labels)

# Podział na zbiór treningowy i testowy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Trenowanie modelu
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Ewaluacja modelu
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Zapis modelu i wektoryzatora
os.makedirs("model", exist_ok=True)
joblib.dump(model, "models/language_model3.pkl")
joblib.dump(vectorizer, "models/tfidf_vectorizer3.pkl")
