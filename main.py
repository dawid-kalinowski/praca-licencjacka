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
from bson import ObjectId
from flask_socketio import SocketIO, join_room, leave_room, send

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

app.secret_key = 'secret'
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/word_db')
app.permanent_session_lifetime = timedelta(minutes=30)

mongo = PyMongo(app)
users_collection = mongo.db.users
words_collection = mongo.db.words
history_collection = mongo.db.history
saved_words_collection = mongo.db.saved_words
flashcard_sets_collection = mongo.db.flashcard_sets
chat_collection = mongo.db.chats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'language_model.pkl')
VECTORIZER_PATH= os.path.join(BASE_DIR, 'model', 'vectorizer.pkl')

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
        second_password = request.form['second_password']
        
        if users_collection.find_one({'username': username}):
            flash('Nazwa użytkownika jest już zajęta.')
            return redirect(url_for('register'))
        
        if password != second_password:
            flash('Hasła nie są takie same!')
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
    all_words = list(words_collection.find({}, {'_id': 1, 'polish': 1, 'english': 1}))
    return render_template('words.html', words=all_words)

@app.route('/save_word', methods=['POST'])
def save_word():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401

    data = request.get_json()
    word_id = data.get('word_id')

    if not word_id:
        return jsonify({'error': 'Brak słowa do zapisania'}), 400

    try:
        word_object_id = ObjectId(word_id) 
    except Exception as e:
        return jsonify({'error': 'Nieprawidłowy identyfikator'}), 400

    word = words_collection.find_one({'_id': word_object_id})
    if not word:
        return jsonify({'error': 'Słowo nie istnieje'}), 400

    saved_words_collection.update_one(
        {'username': session['user']},
        {'$addToSet': {'words': word_object_id}}, 
        upsert=True
    )

    return jsonify({'message': 'Słowo zapisane'})

@app.route('/saved_words', methods=['GET'])
def saved_words_page():
    if 'user' not in session:
        return redirect(url_for('login'))

    saved_words = saved_words_collection.find_one({'username': session['user']}, {'_id': 0, 'words': 1})
    
    words = []
    if saved_words and 'words' in saved_words:
        word_ids = saved_words['words']
        words = list(words_collection.find({'_id': {'$in': word_ids}}, {'_id': 1, 'polish': 1, 'english': 1}))
    
    return render_template('saved_words.html', words=words)

@app.route('/get_saved_words', methods=['GET'])
def get_saved_words():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    saved_words = saved_words_collection.find_one({'username': session['user']}, {'_id': 0, 'words': 1})
    
    words = []
    if saved_words and 'words' in saved_words:
        word_ids = saved_words['words']
        words = list(words_collection.find({'_id': {'$in': word_ids}}, {'_id': 0, 'polish': 1, 'english': 1}))
    return jsonify(words)

@app.route('/delete_word', methods=['POST'])
def delete_word():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401

    data = request.get_json()
    word_id = data.get('word_id')

    if not word_id:
        return jsonify({'error': 'Brak słowa do usunięcia'}), 400

    try:
        word_object_id = ObjectId(word_id)
    except Exception:
        return jsonify({'error': 'Nieprawidłowy identyfikator'}), 400

    result = saved_words_collection.update_one(
        {'username': session['user']},
        {'$pull': {'words': word_object_id}}
    )

    if result.modified_count == 0:
        return jsonify({'error': 'Nie znaleziono słowa do usunięcia'}), 400

    return jsonify({'message': 'Słowo usunięte'})


# Strona główna dla fiszek
@app.route('/flashcards')
def flashcards_home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_sets = list(flashcard_sets_collection.find({'username': session['user']}))
    return render_template('flashcards.html', sets=user_sets)

@app.route('/create_set', methods=['GET', 'POST'])
def create_set():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        set_name = request.form.get('set_name')
        
        if not set_name:
            flash('Nazwa zestawu jest wymagana')
            return redirect(url_for('create_set'))
        
        flashcard_sets_collection.insert_one({'username': session['user'], 'set_name': set_name, 'words': []})
        flash('Zestaw utworzony')
        return redirect(url_for('flashcards_home'))
    
    return render_template('create_set.html')

@app.route('/add_word_to_set', methods=['POST'])
def add_word_to_set():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401
    
    set_id = request.form.get('set_id')
    polish = request.form.get('polish')
    english = request.form.get('english')
    
    if not set_id or not polish or not english:
        flash('Wszystkie pola są wymagane')
        return redirect(url_for('get_set_words', set_id=set_id))
    
    try:
        set_object_id = ObjectId(set_id)
    except:
        flash('Nieprawidłowy identyfikator zestawu')
        return redirect(url_for('get_set_words', set_id=set_id))
    
    flashcard_sets_collection.update_one(
        {'_id': set_object_id},
        {'$push': {'words': {'polish': polish, 'english': english}}}
    )
    flash('Słowo dodane')
    return redirect(url_for('get_set_words', set_id=set_id))

@app.route('/get_set_words/<set_id>', methods=['GET'])
def get_set_words(set_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        set_object_id = ObjectId(set_id)
    except:
        flash('Nieprawidłowy identyfikator zestawu')
        return redirect(url_for('flashcards_home'))
    
    flashcard_set = flashcard_sets_collection.find_one({'_id': set_object_id})
    if not flashcard_set:
        flash('Zestaw nie istnieje')
        return redirect(url_for('flashcards_home'))
    
    return render_template('flashcard_set.html', set_id=set_id, set_name=flashcard_set['set_name'], words=flashcard_set['words'])


@app.route('/get_set_words_for_quiz/<set_id>', methods=['GET'])
def get_set_words_for_quiz(set_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        set_object_id = ObjectId(set_id)
    except:
        flash('Nieprawidłowy identyfikator zestawu')
        return redirect(url_for('flashcards_home'))
    
    flashcard_set = flashcard_sets_collection.find_one({'_id': set_object_id})
    if not flashcard_set:
        flash('Zestaw nie istnieje')
        return redirect(url_for('flashcards_home'))
    flashcard_set.pop('_id', None)

    return jsonify(flashcard_set)


@app.route('/delete_set', methods=['POST'])
def delete_set():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401
    
    set_id = request.form.get('set_id')
    
    try:
        set_object_id = ObjectId(set_id)
    except:
        flash('Nieprawidłowy identyfikator zestawu')
        return redirect(url_for('flashcards_home'))

    
    flashcard_sets_collection.delete_one({'_id': set_object_id})
    flash('Zestaw usunięty')
    return redirect(url_for('flashcards_home'))

@app.route('/delete_word_from_set', methods=['POST'])
def delete_word_from_set():
    if 'user' not in session:
        return jsonify({'error': 'Musisz być zalogowany'}), 401
    
    set_id = request.form.get('set_id')
    polish = request.form.get('polish')
    english = request.form.get('english')
    
    if not set_id or not polish or not english:
        flash('Wszystkie pola są wymagane')
        return redirect(url_for('get_set_words', set_id=set_id))
    
    try:
        set_object_id = ObjectId(set_id)
    except:
        flash('Nieprawidłowy identyfikator zestawu')
        return redirect(url_for('get_set_words', set_id=set_id))
    
    flashcard_sets_collection.update_one(
        {'_id': set_object_id},
        {'$pull': {'words': {'polish': polish, 'english': english}}}
    )
    flash('Słowo usunięte')
    return redirect(url_for('get_set_words', set_id=set_id))



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

# ------------------- CHAT -------------------
@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('login'), code = 401)
    return render_template('chat.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = session.get('user', 'Anonim')
    join_room(room)
    send({'username': 'System', 'message': f'{username} dołączył do pokoju.'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = session.get('user', 'Anonim')
    leave_room(room)
    send({'username': 'System', 'message': f'{username} opuścił pokój.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = session.get('user', 'Anonim')
    message = data['message']

    chat_collection.insert_one({'room': room, 'username': username, 'message': message})

    send({'username': username, 'message': message}, room=room)

@app.route('/get_messages/<room>')
def get_messages(room):
    messages = list(chat_collection.find({'room': room}, {'_id': 0, 'username': 1, 'message': 1}))
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True, port=5000)