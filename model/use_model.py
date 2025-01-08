import joblib

# Wczytanie modelu i wektoryzatora
model = joblib.load("models/language_model1.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer1.pkl")

# Funkcja do przewidywania języka
def przewiduj_jezyk(tekst):
    tekst_wektor = vectorizer.transform([tekst])
    przewidywanie = model.predict(tekst_wektor)
    return przewidywanie[0]  # Zwraca tylko najbardziej prawdopodobny język

# Przykładowe zdania
print(przewiduj_jezyk("siema oto przykladowe zdanko ale bez polskich znakow itd zobaczymy jak model sobie poradzi"))
print(przewiduj_jezyk("moje zdanie"))
print(przewiduj_jezyk("my sentence"))
print(przewiduj_jezyk("hello this is an example sntnc"))
print(przewiduj_jezyk("Hallo, main name ist John"))
