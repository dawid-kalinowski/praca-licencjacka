from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import random
import os
import joblib
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Włączamy CORS dla wszystkich endpointów

# Konfiguracja MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'word_db')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Ładowanie modelu i wektoryzatora dla rozpoznawania języka
MODEL_PATH = "model/language_model1.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer1.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

@app.route('/detect-language')
def detect_language_page():
    return render_template('detect_language.html')

# Endpointy dla quizu
@app.route('/get_words', methods=['GET'])
def get_words():
    words_collection = db.words
    all_words = list(words_collection.find({}, {'_id': 0}))  # Pobierz wszystkie słowa, bez pola _id
    selected_words = random.sample(all_words, 10) if len(all_words) >= 10 else all_words
    return jsonify(selected_words)

@app.route('/check_word', methods=['POST'])
def check_word():
    user_answer = request.json.get('answer')
    correct_word = request.json.get('word')

    is_correct = user_answer.lower() == correct_word['english'].lower()
    result = {
        'polish': correct_word['polish'],
        'your_answer': user_answer,
        'correct_answer': correct_word['english'],
        'correct': is_correct
    }

    return jsonify(result)

# Endpointy dla rozpoznawania języka
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
    app.run(debug=True, port=5000)