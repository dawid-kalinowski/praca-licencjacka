from flask import Flask, render_template, request, jsonify
import mysql.connector
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'word_db')
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_words', methods=['GET'])
def get_words():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM words")
    all_words = cursor.fetchall()
    connection.close()
    selected_words = random.sample(all_words, 10)
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
