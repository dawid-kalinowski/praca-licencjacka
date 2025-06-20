import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, accuracy_score



DATA_FOLDER = "data"

def wczytaj_dane_z_csv(plik_csv):
    jezyk = os.path.splitext(os.path.basename(plik_csv))[0]
    df = pd.read_csv(plik_csv)
    df['język'] = jezyk
    return df

pliki_csv = [os.path.join(DATA_FOLDER, f) for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

df_list = [wczytaj_dane_z_csv(plik) for plik in pliki_csv]

df = pd.concat(df_list, ignore_index=True)

texts = df['tekst'].values
labels = df['język'].values

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

def przewiduj_jezyk(tekst):
    tekst_wektor = vectorizer.transform([tekst])
    przewidywanie = model.predict_proba(tekst_wektor)
    klasy = model.classes_
    return {klasa: round(prob, 3) for klasa, prob in zip(klasy, przewidywanie[0])}

joblib.dump(model, 'language_model.pkl')

joblib.dump(vectorizer, 'vectorizer.pkl')

# Macierz błędów
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
accuracy = accuracy_score(y_test, y_pred)


disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
fig, ax = plt.subplots(figsize=(10, 10))
disp.plot(ax=ax, cmap='Purples', xticks_rotation=45, colorbar=False)

plt.title(f"Macierz błędów\nDokładność: {accuracy:.2%}")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()