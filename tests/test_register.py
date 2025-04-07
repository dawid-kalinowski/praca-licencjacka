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

def test_register_success_message(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}qqqq"
    response = client.post('/register', data={
        'username': f'{username}',
        'password': 'testpass',
        'second_password': 'testpass'
    }, follow_redirects=True)
    assert 'Rejestracja zakończona sukcesem. Możesz się teraz zalogować.' in response.data.decode('utf-8')

def test_register_success_code(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}qqqq"
    response = client.post('/register', data={
        'username': f'{username}',
        'password': 'testpass',
        'second_password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_success_message(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert 'Zalogowano pomyślnie' in response.data.decode('utf-8')


def test_login_success_code(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_logout_success_message(client):
    response = client.get('/logout', follow_redirects=True)
    assert 'Wylogowano pomyślnie' in response.data.decode('utf-8')


def test_logout_success_code(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200