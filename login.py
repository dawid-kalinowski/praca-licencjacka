from flask import Flask, request, redirect, url_for, session, render_template, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'secret'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/word_db'
app.permanent_session_lifetime = timedelta(minutes=30)

# Inicjalizacja MongoDB
mongo = PyMongo(app)
users_collection = mongo.db.users

@app.route('/')
def home():
    if 'user' in session:
        return f"Witaj, {session['user']}! <a href='/logout'>Wyloguj</a>"
    return "<a href='/login'>Zaloguj</a> lub <a href='/register'>Zarejestruj</a>"

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

if __name__ == '__main__':
    app.run(debug=True)