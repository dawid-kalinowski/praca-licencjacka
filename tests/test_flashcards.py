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
def test_add_word_success_bd(mock_update_one, client):
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

@patch('main.flashcard_sets_collection.update_one')
def test_add_word_success_message(mock_update_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())

    response = client.post('/add_word_to_set', data={
        'set_id': valid_id,
        'polish': 'kot',
        'english': 'cat',
    }, follow_redirects=True)
    assert 'Słowo dodane' in response.get_data(as_text=True)













def test_get_set_words_redirect_if_not_logged_in_code(client):
    response = client.get('/get_set_words/123')
    assert response.status_code == 302


def test_get_set_words_redirect_if_not_logged_in_location(client):
    response = client.get('/get_set_words/123')
    assert '/login' in response.headers['Location']

def test_get_set_words_invalid_id_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/get_set_words/invalid_id', follow_redirects=True)
    assert response.status_code == 200


def test_get_set_words_invalid_id_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/get_set_words/invalid_id', follow_redirects=True)
    assert 'Nieprawidłowy identyfikator zestawu' in response.get_data(as_text=True)


def test_get_set_words_set_not_found_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    response = client.get(f'/get_set_words/{valid_id}', follow_redirects=True)
    assert response.status_code == 200


def test_get_set_words_set_not_found_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    response = client.get(f'/get_set_words/{valid_id}', follow_redirects=True)
    assert 'Zestaw nie istnieje' in response.get_data(as_text=True)



@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_success_code(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }

    response = client.get(f'/get_set_words/{valid_id}', follow_redirects=False)

    assert response.status_code == 200



@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_success_set(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }

    response = client.get(f'/get_set_words/{valid_id}', follow_redirects=False)
    assert 'Testowy Zestaw' in response.get_data(as_text=True)


@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_success_polish(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }

    response = client.get(f'/get_set_words/{valid_id}', follow_redirects=False)
    assert 'kot' in response.get_data(as_text=True)


@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_success_english(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }

    response = client.get(f'/get_set_words/{valid_id}', follow_redirects=False)
    assert 'cat' in response.get_data(as_text=True)


def test_get_set_words_for_quiz_redirect_if_not_logged_in_code(client):
    response = client.get('/get_set_words_for_quiz/123')
    assert response.status_code == 302


def test_get_set_words_for_quiz_redirect_if_not_logged_in_location(client):
    response = client.get('/get_set_words_for_quiz/123')
    assert '/login' in response.headers['Location']

def test_get_set_words_for_quiz_invalid_id_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/get_set_words_for_quiz/invalid_id', follow_redirects=True)
    assert response.status_code == 200


def test_get_set_words_for_quiz_invalid_id_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/get_set_words_for_quiz/invalid_id', follow_redirects=True)
    assert 'Nieprawidłowy identyfikator zestawu' in response.get_data(as_text=True)


def test_get_set_words_for_quiz_set_not_found_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    response = client.get(f'/get_set_words_for_quiz/{valid_id}', follow_redirects=True)
    assert response.status_code == 200


def test_get_set_words_for_quiz_set_not_found_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    response = client.get(f'/get_set_words_for_quiz/{valid_id}', follow_redirects=True)
    assert 'Zestaw nie istnieje' in response.get_data(as_text=True)

@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_for_quiz_success_code(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }
    
    response = client.get(f'/get_set_words_for_quiz/{valid_id}', follow_redirects=False)
    assert response.status_code == 200

@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_for_quiz_success_setname(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }
    
    response = client.get(f'/get_set_words_for_quiz/{valid_id}', follow_redirects=False)
    response_json = response.get_json()
    assert response_json['set_name'] == 'Testowy Zestaw'

@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_for_quiz_success_nrwords(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }
    
    response = client.get(f'/get_set_words_for_quiz/{valid_id}', follow_redirects=False)
    response_json = response.get_json()
    assert len(response_json['words']) == 2

@patch('main.flashcard_sets_collection.find_one')
def test_get_set_words_for_quiz_success_words(mock_find_one, client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    valid_id = str(ObjectId())
    mock_find_one.return_value = {
        '_id': ObjectId(valid_id),
        'set_name': 'Testowy Zestaw',
        'words': [{'polish': 'kot', 'english': 'cat'}, {'polish': 'pies', 'english': 'dog'}]
    }
    
    response = client.get(f'/get_set_words_for_quiz/{valid_id}', follow_redirects=False)
    response_json = response.get_json()
    assert {'polish': 'kot', 'english': 'cat'} in response_json['words']

def test_delete_set_not_logged_in_code(client):
    response = client.post('/delete_set', data={})
    assert response.status_code == 401

def test_delete_set_not_logged_in_message(client):
    response = client.post('/delete_set', data={})
    data = response.get_json()
    assert data['error'] == 'Musisz być zalogowany'


def test_delete_set_invalid_set_id_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_set', data={
        'set_id': 'invalid_id!',
        'polish': 'dom',
        'english': 'house',
    }, follow_redirects=True)

    assert 'Nieprawidłowy identyfikator zestawu' in response.get_data(as_text=True)


def test_delete_set_invalid_set_id_location(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    
    response = client.post('/delete_set', data={
        'set_id': 'invalid_id!',
        'polish': 'dom',
        'english': 'house',
    }, follow_redirects=False)

    assert '/flashcards' in response.headers['Location']

def test_delete_set_success_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    test_set = {
        '_id': ObjectId(),
        'user': 'testuser',
        'title': 'Testowy zestaw',
        'cards': [{'polish': 'dom', 'english': 'house'}]
    }

    from main import flashcard_sets_collection
    flashcard_sets_collection.insert_one(test_set)
    response = client.post('/delete_set', data={
        'set_id': str(test_set['_id']),
    }, follow_redirects=False)

    assert response.status_code == 302


def test_delete_set_success_location(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    test_set = {
        '_id': ObjectId(),
        'user': 'testuser',
        'title': 'Testowy zestaw',
        'cards': [{'polish': 'dom', 'english': 'house'}]
    }

    from main import flashcard_sets_collection
    flashcard_sets_collection.insert_one(test_set)
    response = client.post('/delete_set', data={
        'set_id': str(test_set['_id']),
    }, follow_redirects=False)

    assert '/flashcards' in response.headers['Location']


def test_delete_set_success_none(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    test_set = {
        '_id': ObjectId(),
        'user': 'testuser',
        'title': 'Testowy zestaw',
        'cards': [{'polish': 'dom', 'english': 'house'}]
    }

    from main import flashcard_sets_collection
    flashcard_sets_collection.insert_one(test_set)
    response = client.post('/delete_set', data={
        'set_id': str(test_set['_id']),
    }, follow_redirects=False)

    assert flashcard_sets_collection.find_one({'_id': test_set['_id']}) is None

def test_delete_set_success_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    test_set = {
        '_id': ObjectId(),
        'user': 'testuser',
        'title': 'Testowy zestaw',
        'cards': [{'polish': 'dom', 'english': 'house'}]
    }

    from main import flashcard_sets_collection
    flashcard_sets_collection.insert_one(test_set)
    response = client.post('/delete_set', data={
        'set_id': str(test_set['_id']),
    }, follow_redirects=True)

    assert 'Zestaw usunięty' in response.get_data(as_text=True)

def test_delete_word_from_set_not_logged_in_code(client):
    response = client.post('/delete_word_from_set', data={})
    assert response.status_code == 401

def test_delete_word_from_set_not_logged_in_message(client):
    response = client.post('/delete_word_from_set', data={})
    data = response.get_json()
    assert data['error'] == 'Musisz być zalogowany'


def test_delete_word_from_set_missing_fields_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word_from_set', data={
        'set_id': '123', 
    }, follow_redirects=True)
    assert 'Wszystkie pola są wymagane' in response.get_data(as_text=True)



def test_delete_word_from_set_missing_fields_location(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word_from_set', data={
        'set_id': '123', 
    }, follow_redirects=False)
    assert '/get_set_words' in response.headers['Location']

def test_delete_word_from_set_invalid_set_id_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word_from_set', data={
        'set_id': 'invalid_id!',
        'polish': 'dom',
        'english': 'house',
    }, follow_redirects=True)
    assert 'Nieprawidłowy identyfikator zestawu' in response.get_data(as_text=True)

def test_delete_word_from_set_invalid_set_id_location(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/delete_word_from_set', data={
        'set_id': 'invalid_id!',
        'polish': 'dom',
        'english': 'house',
    }, follow_redirects=False)
    assert '/get_set_words' in response.headers['Location']


def test_delete_word_from_set_success_message(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    set_id = str(ObjectId())

    with patch('main.flashcard_sets_collection.update_one') as mock_update:
        mock_update.return_value = None
        response = client.post('/delete_word_from_set', data={
            'set_id': set_id,
            'polish': 'dom',
            'english': 'house'
        }, follow_redirects=True) 
        assert 'Słowo usunięte' in response.get_data(as_text=True)

def test_delete_word_from_set_success_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    set_id = str(ObjectId())

    with patch('main.flashcard_sets_collection.update_one') as mock_update:
        mock_update.return_value = None
        response = client.post('/delete_word_from_set', data={
            'set_id': set_id,
            'polish': 'dom',
            'english': 'house'
        }, follow_redirects=True) 
        assert response.status_code == 200


def test_delete_word_from_set_success_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})

    set_id = str(ObjectId())

    with patch('main.flashcard_sets_collection.update_one') as mock_update:
        mock_update.return_value = None
        response = client.post('/delete_word_from_set', data={
            'set_id': set_id,
            'polish': 'dom',
            'english': 'house'
        }, follow_redirects=False) 
        assert '/get_set_words' in response.headers['Location']
