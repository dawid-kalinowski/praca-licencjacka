import joblib

# Wczytanie modelu i wektoryzatora
model = joblib.load("models/language_model1.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer1.pkl")

# Funkcja do przewidywania
def przewiduj_jezyk(tekst):
    tekst_wektor = vectorizer.transform([tekst])
    przewidywanie = model.predict_proba(tekst_wektor)
    klasy = model.classes_
    return {klasa: round(prob, 3) for klasa, prob in zip(klasy, przewidywanie[0])}

# Przykładowe zdania
print(przewiduj_jezyk("siema oto przykladowe zdanko ale bez polskich znakow itd zobaczymy jak model sobie poradzi"))
print(przewiduj_jezyk("moje zdanie"))
print(przewiduj_jezyk("my sentence"))
print(przewiduj_jezyk("hello this is an example sntnc"))
print(przewiduj_jezyk("Hallo maine name ist John und ich bin gut"))
print(przewiduj_jezyk("Hallo maine name ist John"))