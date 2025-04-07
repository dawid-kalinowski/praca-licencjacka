import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../model')))

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

def test_get_words_code(client):
    response = client.get('/get_words')
    assert response.status_code == 200

def test_get_words_type(client):
    response = client.get('/get_words')
    assert isinstance(response.json, list)

def test_check_word_not_logged_in_code(client):
    response = client.post('/check_word', json={'answer': 'test', 'word': {'english': 'apple', 'polish': 'jabłko'}})
    assert response.status_code == 401

def test_check_word_not_logged_in_message(client):
    response = client.post('/check_word', json={'answer': 'test', 'word': {'english': 'apple', 'polish': 'jabłko'}})
    data = response.get_json()
    assert data['error'] == 'Musisz być zalogowany'

def test_save_word_word_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    from main import words_collection
    word_id = words_collection.insert_one({'english': 'apple', 'polish': 'jabłko'}).inserted_id
    response = client.post('/save_word', json={'word_id': str(word_id)})
    assert response.status_code == 200


def test_save_word_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    from main import words_collection
    word_id = words_collection.insert_one({'english': 'apple', 'polish': 'jabłko'}).inserted_id
    response = client.post('/save_word', json={'word_id': str(word_id)})
    assert response.json['message'] == 'Słowo zapisane'

def test_save_word_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    from main import words_collection
    word_id = words_collection.insert_one({'english': 'apple', 'polish': 'jabłko'}).inserted_id
    client.post('/save_word', json={'word_id': str(word_id)})
    response = client.get('/get_saved_words')
    assert response.status_code == 200


def test_save_word_type(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    from main import words_collection
    word_id = words_collection.insert_one({'english': 'apple', 'polish': 'jabłko'}).inserted_id
    client.post('/save_word', json={'word_id': str(word_id)})
    response = client.get('/get_saved_words')
    assert isinstance(response.json, list)

def test_save_word_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    from main import words_collection
    word_id = words_collection.insert_one({'english': 'apple', 'polish': 'jabłko'}).inserted_id
    client.post('/save_word', json={'word_id': str(word_id)})
    response = client.get('/get_saved_words')
    assert any(w['english'] == 'apple' for w in response.json)


def test_delete_word_not_logged_in_code(client):
    response = client.post('/delete_word', json={'answer': 'test', 'word': {'english': 'apple', 'polish': 'jabłko'}})
    assert response.status_code == 401

def test_delete_word_not_logged_in_message(client):
    response = client.post('/delete_word', json={'answer': 'test', 'word': {'english': 'apple', 'polish': 'jabłko'}})
    data = response.get_json()
    assert data['error'] == 'Musisz być zalogowany'

    
def test_delete_word_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    from main import saved_words_collection, words_collection
    word_id = words_collection.insert_one({'english': 'banana', 'polish': 'banan'}).inserted_id
    saved_words_collection.update_one({'username': 'testuser'}, {'$addToSet': {'words': word_id}}, upsert=True)

    response = client.post('/delete_word', json={'word_id': str(word_id)})
    assert response.status_code == 200


def test_delete_word_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    from main import saved_words_collection, words_collection
    word_id = words_collection.insert_one({'english': 'banana', 'polish': 'banan'}).inserted_id
    saved_words_collection.update_one({'username': 'testuser'}, {'$addToSet': {'words': word_id}}, upsert=True)

    response = client.post('/delete_word', json={'word_id': str(word_id)})
    assert response.json['message'] == 'Słowo usunięte'



def test_delete_word_missing_word_id_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word', json={})
    assert response.status_code == 400

def test_delete_word_missing_word_id_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word', json={})
    assert response.get_json()['error'] == 'Brak słowa do usunięcia'

def test_delete_word_invalid_word_id_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word', json={'word_id': 'invalid_id'})
    assert response.status_code == 400


def test_delete_word_invalid_word_id_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word', json={'word_id': 'invalid_id'})
    assert response.get_json()['error'] == 'Nieprawidłowy identyfikator'

def test_delete_word_not_found_code(client, mocker):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    mock_result = mocker.MagicMock()
    mock_result.modified_count = 0
    mocker.patch('main.saved_words_collection.update_one', return_value=mock_result)

    fake_id = str(ObjectId())
    response = client.post('/delete_word', json={'word_id': fake_id})
    assert response.status_code == 400


def test_delete_word_not_found_message(client, mocker):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    mock_result = mocker.MagicMock()
    mock_result.modified_count = 0
    mocker.patch('main.saved_words_collection.update_one', return_value=mock_result)

    fake_id = str(ObjectId())
    response = client.post('/delete_word', json={'word_id': fake_id})
    assert response.get_json()['error'] == 'Nie znaleziono słowa do usunięcia'