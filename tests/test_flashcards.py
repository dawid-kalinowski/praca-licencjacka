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