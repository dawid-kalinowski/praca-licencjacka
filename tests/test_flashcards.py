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
from unittest.mock import patch

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_word_db'
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()


def test_flashcards_home_redirect_if_not_logged_in_code(client):
    response = client.get('/flashcards')
    assert response.status_code == 302


def test_flashcards_home_redirect_if_not_logged_in_location(client):
    response = client.get('/flashcards')
    assert '/login' in response.headers['Location']


def test_flashcards_home_logged_in_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/flashcards')
    assert response.status_code == 200



def test_create_set_redirect_if_not_logged_in_code(client):
    response = client.get('/create_set')
    assert response.status_code == 302


def test_create_set_redirect_if_not_logged_in_location(client):
    response = client.get('/create_set')
    assert '/login' in response.headers['Location']

def test_post_create_set_redirect_if_not_logged_in_code(client):
    response = client.post('/create_set')
    assert response.status_code == 302


def test_post_create_set_redirect_if_not_logged_in_location(client):
    response = client.post('/create_set')
    assert '/login' in response.headers['Location']

def test_create_set_no_name_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/create_set', data={'set_name': ''}, follow_redirects=True)
    assert b'Nazwa zestawu jest wymagana' in response.data

def test_create_set_no_name_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/create_set', data={'set_name': ''}, follow_redirects=True)
    assert response.status_code == 200 




def test_create_set_success_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/create_set', data={'set_name': 'Mój zestaw'}, follow_redirects=True)
    assert b'Zestaw utworzony' in response.data


def test_create_set_success_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/create_set', data={'set_name': 'Mój zestaw'}, follow_redirects=True)
    assert response.status_code == 200

def test_add_word_to_set_not_logged_in_code(client):
    response = client.post('/add_word_to_set', data={})
    assert response.status_code == 401

def test_add_word_to_set_not_logged_in_message(client):
    response = client.post('/add_word_to_set', data={})
    data = response.get_json()
    assert data['error'] == 'Musisz być zalogowany'

def test_add_word_missing_fields(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/add_word_to_set', data={
        'set_id': '123', 
    }, follow_redirects=True)

    assert 'Wszystkie pola są wymagane' in response.get_data(as_text=True)

def test_add_word_invalid_set_id(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/add_word_to_set', data={
        'set_id': 'invalid_id!',
        'polish': 'dom',
        'english': 'house',
    }, follow_redirects=True)

    assert 'Nieprawidłowy identyfikator zestawu' in response.get_data(as_text=True)

@patch('main.flashcard_sets_collection.update_one')
def test_add_word_success(mock_update_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())

    response = client.post('/add_word_to_set', data={
        'set_id': valid_id,
        'polish': 'kot',
        'english': 'cat',
    }, follow_redirects=True)

    mock_update_one.assert_called_once_with(
        {'_id': ObjectId(valid_id)},
        {'$push': {'words': {'polish': 'kot', 'english': 'cat'}}}
    )
    assert 'Słowo dodane' in response.get_data(as_text=True)