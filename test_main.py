import pytest
from main import app as flask_app
from flask_pymongo import PyMongo
import json
from bson import ObjectId
import uuid

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_word_db'
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_login_logout(client):
    # Rejestracja
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    response = client.post('/register', data={
        'username': f'{username}',
        'password': 'testpass',
        'second_password': 'testpass'
    }, follow_redirects=True)
    assert 'Rejestracja zakończona sukcesem' in response.data.decode('utf-8')

    # Logowanie
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert 'Zalogowano pomyślnie' in response.data.decode('utf-8')

    # Wylogowanie
    response = client.get('/logout', follow_redirects=True)
    assert 'Wylogowano pomyślnie' in response.data.decode('utf-8')

def test_get_words(client):
    response = client.get('/get_words')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_check_word_not_logged_in(client):
    response = client.post('/check_word', json={'answer': 'test', 'word': {'english': 'apple', 'polish': 'jabłko'}})
    assert response.status_code == 401

def test_save_and_get_word(client):
    # Logowanie
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    # Dodaj testowe słowo do bazy
    from main import words_collection
    word_id = words_collection.insert_one({'english': 'apple', 'polish': 'jabłko'}).inserted_id

    # Zapisz słowo
    response = client.post('/save_word', json={'word_id': str(word_id)})
    assert response.status_code == 200
    assert response.json['message'] == 'Słowo zapisane'

    # Pobierz zapisane słowa
    response = client.get('/get_saved_words')
    assert response.status_code == 200
    assert any(w['english'] == 'apple' for w in response.json)

def test_delete_word(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    from main import saved_words_collection, words_collection
    word_id = words_collection.insert_one({'english': 'banana', 'polish': 'banan'}).inserted_id
    saved_words_collection.update_one({'username': 'testuser'}, {'$addToSet': {'words': word_id}}, upsert=True)

    response = client.post('/delete_word', json={'word_id': str(word_id)})
    assert response.status_code == 200
    assert response.json['message'] == 'Słowo usunięte'

def test_flashcard_set_flow(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    # Utwórz zestaw
    response = client.post('/create_set', data={'set_name': 'Zestaw 1'}, follow_redirects=True)
    assert 'Zestaw utworzony' in response.data.decode('utf-8')

    from main import flashcard_sets_collection
    flashcard_set = flashcard_sets_collection.find_one({'username': 'testuser', 'set_name': 'Zestaw 1'})
    assert flashcard_set

    # Dodaj słowo
    response = client.post('/add_word_to_set', data={
        'set_id': str(flashcard_set['_id']),
        'polish': 'pies',
        'english': 'dog'
    }, follow_redirects=True)
    assert 'Słowo dodane' in response.data.decode('utf-8')

    # Usuń słowo
    response = client.post('/delete_word_from_set', data={
        'set_id': str(flashcard_set['_id']),
        'polish': 'pies',
        'english': 'dog'
    }, follow_redirects=True)
    assert 'Słowo usunięte' in response.data.decode('utf-8')

    # Usuń zestaw
    response = client.post('/delete_set', data={'set_id': str(flashcard_set['_id'])}, follow_redirects=True)
    assert 'Zestaw usunięty' in response.data.decode('utf-8')

def test_detect_language(client):
    response = client.post('/detect-language', json={'text': 'Hello, how are you?'})
    assert response.status_code == 200
    assert 'language' in response.json or 'error' in response.json
