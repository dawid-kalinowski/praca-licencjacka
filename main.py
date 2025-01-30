from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import random
import os
import joblib
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'secret'
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/word_db')
app.permanent_session_lifetime = timedelta(minutes=30)

# Inicjalizacja MongoDB
mongo = PyMongo(app)
users_collection = mongo.db.users
words_collection = mongo.db.words
history_collection = mongo.db.history
saved_words_collection = mongo.db.saved_words

MODEL_PATH = "model/language_model1.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer1.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html', username=session['user'])
    return render_template('index.html')

# ============= MODUŁ LOGOWANIA =============

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users_collection.find_one({'username': username}):
            flash('Nazwa użytkownika jest już zajęta.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        flash('Rejestracja zakończona sukcesem. Możesz się teraz zalogować.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session.permanent = True
            flash('Zalogowano pomyślnie!')
            return redirect(url_for('home'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Wylogowano pomyślnie!')
    return redirect(url_for('home'))

# ============= QUIZ =============

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

@app.route('/get_words', methods=['GET'])
def get_words():
    all_words = list(words_collection.find({}, {'_id': 0}))
    selected_words = random.sample(all_words, 10) if len(all_words) >= 10 else all_words
    return jsonify(selected_words)

@app.route('/check_word', methods=['POST'])
def check_word():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401
    
    user_answer = request.json.get('answer')
    correct_word = request.json.get('word')
    is_correct = user_answer.lower() == correct_word['english'].lower()
    result = {
        'polish': correct_word['polish'],
        'your_answer': user_answer,
        'correct_answer': correct_word['english'],
        'correct': is_correct
    }
    history_collection.insert_one({
        'username': session['user'],
        'word': correct_word['english'],
        'your_answer': user_answer,
        'correct': is_correct
    })
    return jsonify(result)

@app.route('/quiz/history', methods=['GET'])
def quiz_history():
    if 'user' not in session:
        return redirect(url_for('login'))
    history = list(history_collection.find({'username': session['user']}, {'_id': 0}))
    return render_template('history.html', history=history)

# ============= ZAPISYWANIE SŁÓW =============

@app.route('/words', methods=['GET'])
def words_page():
    all_words = list(words_collection.find({}, {'_id': 0}))
    return render_template('words.html', words=all_words)

@app.route('/save_word', methods=['POST'])
def save_word():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401
    
    word = request.json.get('word')
    if not word:
        return jsonify({'error': 'Brak słowa do zapisania'}), 400
    
    saved_words_collection.update_one(
        {'username': session['user']},
        {'$addToSet': {'words': word}},
        upsert=True
    )
    return jsonify({'message': 'Słowo zapisane'})

@app.route('/saved_words', methods=['GET'])
def saved_words_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    saved_words = saved_words_collection.find_one({'username': session['user']}, {'_id': 0, 'words': 1})
    words = saved_words.get('words', []) if saved_words else []
    return render_template('saved_words.html', words=words)

@app.route('/saved_words_quiz', methods=['GET'])
def saved_words_quiz():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401
    
    saved_words = saved_words_collection.find_one({'username': session['user']}, {'_id': 0, 'words': 1})
    words = saved_words.get('words', []) if saved_words else []
    selected_words = random.sample(words, min(10, len(words)))
    return jsonify(selected_words)


@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        text_vectorized = vectorizer.transform([text])
        predicted_language = model.predict(text_vectorized)[0]
        return jsonify({"language": predicted_language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/detect-language')
def detect_language_page():
    return render_template('detect_language.html')
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)