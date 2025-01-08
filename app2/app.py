from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Dodaj import

import joblib
import os

app = Flask(__name__)
CORS(app)  # Dodaj tę linię, aby włączyć CORS dla wszystkich endpointów

# Ścieżki do modelu i wektoryzatora
MODEL_PATH = "model/models/language_model1.pkl"
VECTORIZER_PATH = "model/models/tfidf_vectorizer1.pkl"

# Ładowanie modelu i wektoryzatora
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Przekształcenie tekstu za pomocą wektoryzatora
        text_vectorized = vectorizer.transform([text])
        # Przewidywanie języka
        predicted_language = model.predict(text_vectorized)[0]
        return jsonify({"language": predicted_language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
