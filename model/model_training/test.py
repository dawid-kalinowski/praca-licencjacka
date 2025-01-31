import joblib

model = joblib.load('../language_model.pkl')
vectorizer = joblib.load('../vectorizer.pkl')

def przewiduj_jezyk(tekst):
    """Przewiduje język podanego tekstu i zwraca 3 najbardziej prawdopodobne języki."""
    tekst_wektor = vectorizer.transform([tekst])
    przewidywanie = model.predict_proba(tekst_wektor)
    klasy = model.classes_

    prawdopodobienstwa = {klasa: prob for klasa, prob in zip(klasy, przewidywanie[0])}

    posortowane_prawdopodobienstwa = sorted(prawdopodobienstwa.items(), key=lambda x: x[1], reverse=True)


    return [(klasa, round(prob, 3)) for klasa, prob in posortowane_prawdopodobienstwa[:3]]

# testy = {
#     "Angielski": "The sun sets over the mountains, casting a golden glow on the landscape.",
#     "Czeski": "Včera večer jsem si užil skvělý koncert v centru města.",
#     "Francuski": "Les fleurs dans le jardin sont magnifiques cette saison.",
#     "Hiszpański": "La vida es un viaje lleno de sorpresas y nuevas oportunidades.",
#     "Niemiecki": "Der Regen prasselt gegen die Fenster, während wir drinnen sitzen und ein Buch lesen.",
#     "Polski": "Zima przyszła szybciej, niż się spodziewaliśmy, a śnieg pokrył całą okolicę.",
#     "Portugalski": "O café da manhã estava delicioso, com pão quente e suco de laranja.",
#     "Słowacki": "V horách je krásne ticho a vzduch je osviežujúci.",
#     "Szwedzki": "Solen går ner bakom bergen och målar himlen i röda och orangea färger.",
#     "Turecki": "Kuşlar sabah erkenden uçarak güneşin doğuşunu selamlar.",
#     "Włoski": "Le strade di Roma sono piene di storia e cultura, ogni angolo racconta una storia."
# }

testy = {
    "Angielski": [
        "The sky is blue.",
        "I like apples.",
        "She runs fast.",
        "He is my friend."
    ],
    "Czeski": [
        "Mám rád jablka.",
        "Dnes je hezky.",
        "Půjdu domů.",
        "On je můj přítel."
    ],
    "Francuski": [
        "Le ciel est bleu.",
        "J'aime les pommes.",
        "Elle court vite.",
        "Il est mon ami."
    ],
    "Hiszpański": [
        "El cielo es azul.",
        "Me gustan las manzanas.",
        "Ella corre rápido.",
        "Él es mi amigo."
    ],
    "Niemiecki": [
        "Der Himmel ist blau.",
        "Ich mag Äpfel.",
        "Sie läuft schnell.",
        "Er ist mein Freund."
    ],
    "Polski": [
        "Niebo jest niebieskie.",
        "Lubię jabłka.",
        "Ona biega szybko.",
        "On jest moim przyjacielem."
    ],
    "Portugalski": [
        "O céu é azul.",
        "Eu gosto de maçãs.",
        "Ela corre rápido.",
        "Ele é meu amigo."
    ],
    "Słowacki": [
        "Nebesá je modrá.",
        "Mám rád jablká.",
        "Beží rýchlo.",
        "On je môj priateľ."
    ],
    "Szwedzki": [
        "Himlen är blå.",
        "Jag gillar äpplen.",
        "Hon springer snabbt.",
        "Han är min vän."
    ],
    "Turecki": [
        "Gökyüzü mavi.",
        "Elmalarını seviyorum.",
        "O hızlı koşar.",
        "O benim arkadaşım."
    ],
    "Włoski": [
        "Il cielo è blu.",
        "Mi piacciono le mele.",
        "Lei corre veloce.",
        "Lui è mio amico."
    ]
}

for jezyk, zdania in testy.items():
    for zdanie in zdania:
        wynik = przewiduj_jezyk(zdanie)
        print(f"{jezyk}: {wynik}")
