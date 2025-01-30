import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib


# Folder, w którym znajdują się pliki CSV z danymi językowymi
DATA_FOLDER = "data"

def wczytaj_dane_z_csv(plik_csv):
    """Wczytuje dane z pliku CSV i przypisuje język na podstawie nazwy pliku."""
    jezyk = os.path.splitext(os.path.basename(plik_csv))[0]  # Pobranie nazwy pliku bez rozszerzenia
    df = pd.read_csv(plik_csv)
    df['język'] = jezyk
    return df

# Pobranie listy wszystkich plików CSV w katalogu
pliki_csv = [os.path.join(DATA_FOLDER, f) for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

# Wczytanie danych z wszystkich plików CSV
df_list = [wczytaj_dane_z_csv(plik) for plik in pliki_csv]

# Połączenie wszystkich danych w jeden DataFrame
df = pd.concat(df_list, ignore_index=True)

# Przygotowanie danych do modelu
texts = df['tekst'].values
labels = df['język'].values

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = np.array(labels)

# Podział na zbiór treningowy i testowy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Trenowanie modelu
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Ocena modelu
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

def przewiduj_jezyk(tekst):
    """Przewiduje język podanego tekstu i zwraca prawdopodobieństwa dla każdej klasy."""
    tekst_wektor = vectorizer.transform([tekst])
    przewidywanie = model.predict_proba(tekst_wektor)
    klasy = model.classes_
    return {klasa: round(prob, 3) for klasa, prob in zip(klasy, przewidywanie[0])}

# Zapisz model do pliku
joblib.dump(model, 'language_model.pkl')

# Zapisz wektoryzator do pliku
joblib.dump(vectorizer, 'vectorizer.pkl')



# print(przewiduj_jezyk("Gestern habe ich einen langen Spaziergang im Wald gemacht und dabei viele interessante Vögel gesehen."))  # Niemiecki
# print(przewiduj_jezyk("Po całym dniu pracy uwielbiam usiąść na kanapie i oglądać ulubione filmy."))  # Polski
# print(przewiduj_jezyk("I have been studying programming for several months now, and I am really enjoying it, especially learning new languages."))  # Angielski
# print(przewiduj_jezyk("Wczoraj wieczorem spotkałem moich przyjaciół w kawiarni, gdzie rozmawialiśmy o naszych planach na przyszłość."))  # Polski
# print(przewiduj_jezyk("Ich möchte bald eine Reise nach Italien machen, um die Kultur und die wunderschöne Architektur zu erleben."))  # Niemiecki
# print(przewiduj_jezyk("I had a long day at work, but in the evening, I was able to relax and enjoy a great meal with my family."))  # Angielski
# print(przewiduj_jezyk("Die Aussicht vom Gipfel des Berges war atemberaubend, und wir haben viele Fotos gemacht, um uns an diesen Moment zu erinnern."))  # Niemiecki
# print(przewiduj_jezyk("W zeszłym tygodniu odwiedziłem swoje rodzinne miasto, gdzie spędziłem czas z bliskimi i wspomnieniami z dzieciństwa."))  # Polski
# print(przewiduj_jezyk("I have recently started reading a new book about history, and I find it fascinating how much we can learn from the past."))  # Angielski
# print(przewiduj_jezyk("Am Samstag haben wir einen Ausflug in die Berge gemacht und den ganzen Tag draußen verbracht, um die Natur zu genießen."))  # Niemiecki

print(przewiduj_jezyk("siema oto przykladowe zdanko ale bez polskich znakow itd zobaczymy jak model sobie poradzi"))
print(przewiduj_jezyk("moje zdanie"))
print(przewiduj_jezyk("my sentence"))
print(przewiduj_jezyk("hello this is an example sntnc"))