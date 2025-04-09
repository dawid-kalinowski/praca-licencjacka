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


def test_detect_language_no_text_code(client):
    response = client.post('/detect-language', json={})
    assert response.status_code == 400


def test_detect_language_no_text_message(client):
    response = client.post('/detect-language', json={})
    assert response.get_json() == {"error": "No text provided"}

def test_detect_language_success_status(client, mocker):
    mock_vectorizer = mocker.patch('main.vectorizer')
    mock_model = mocker.patch('main.model')
    mock_vectorizer.transform.return_value = 'mock_vector'
    mock_model.predict.return_value = ['English']
    response = client.post('/detect-language', json={"text": "Hello, how are you?"})
    assert response.status_code == 200


def test_detect_language_success_language(client, mocker):
    mock_vectorizer = mocker.patch('main.vectorizer')
    mock_model = mocker.patch('main.model')
    mock_vectorizer.transform.return_value = 'mock_vector'
    mock_model.predict.return_value = ['English']
    response = client.post('/detect-language', json={"text": "Hello, how are you?"})
    assert response.get_json() == {"language": "English"}


def test_detect_language_success_status_once_checked(client, mocker):
    mock_vectorizer = mocker.patch('main.vectorizer')
    mock_model = mocker.patch('main.model')
    mock_vectorizer.transform.return_value = 'mock_vector'
    mock_model.predict.return_value = ['English']
    response = client.post('/detect-language', json={"text": "Hello, how are you?"})
    mock_vectorizer.transform.assert_called_once_with(["Hello, how are you?"])

def test_detect_language_exception_code(client, mocker):
    mock_vectorizer = mocker.patch('main.vectorizer')
    mock_vectorizer.transform.side_effect = Exception("Vectorizer failed")
    response = client.post('/detect-language', json={"text": "Hola, cómo estás?"})
    assert response.status_code == 500


def test_detect_language_exception_message(client, mocker):
    mock_vectorizer = mocker.patch('main.vectorizer')
    mock_vectorizer.transform.side_effect = Exception("Vectorizer failed")
    response = client.post('/detect-language', json={"text": "Hola, cómo estás?"})
    assert "Vectorizer failed" in response.get_json()["error"]


