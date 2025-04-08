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
from main import app, socketio

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_word_db'
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_chat_not_logged_location(client):
    response = client.get('/chat')
    assert '/login' in response.headers['Location']

def test_chat_not_logged_code(client):
    response = client.get('/chat')
    assert response.status_code == 401


def test_chat_route_logged_in_code(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/chat')
    assert response.status_code == 200
    
def test_chat_route_logged_in_page(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.get('/chat')
    assert b'<html' in response.data.lower()

@patch('main.chat_collection.find')
def test_get_messages_code(mock_find, client):
    mock_find.return_value = [
        {'username': 'User1', 'message': 'Hello'},
        {'username': 'User2', 'message': 'Hi'}
    ]
    response = client.get('/get_messages/testroom')
    assert response.status_code == 200


@patch('main.chat_collection.find')
def test_get_messages_content(mock_find, client):
    mock_find.return_value = [
        {'username': 'User1', 'message': 'Hello'},
        {'username': 'User2', 'message': 'Hi'}
    ]
    response = client.get('/get_messages/testroom')
    assert response.json == [
        {'username': 'User1', 'message': 'Hello'},
        {'username': 'User2', 'message': 'Hi'}
    ]


@pytest.fixture
def socketio_client(client):
    return socketio.test_client(flask_app, flask_test_client=client)


def test_join_event_correct_room(socketio_client):
    with patch('main.join_room') as mock_join, patch('main.send') as mock_send:
        socketio_client.emit('join', {'room': 'testroom'})
        mock_join.assert_called_with('testroom')


def test_join_event_correct_room_message(socketio_client):
    with patch('main.join_room') as mock_join, patch('main.send') as mock_send:
        socketio_client.emit('join', {'room': 'testroom'})
        mock_send.assert_called_with(
            {'username': 'System', 'message': 'Anonim dołączył do pokoju.'},
            room='testroom'
        )

def test_leave_event_room(socketio_client):
    with patch('main.leave_room') as mock_leave, patch('main.send') as mock_send:
        socketio_client.emit('leave', {'room': 'testroom'})
        mock_leave.assert_called_with('testroom')


def test_leave_event_message(socketio_client):
    with patch('main.leave_room') as mock_leave, patch('main.send') as mock_send:
        socketio_client.emit('leave', {'room': 'testroom'})
        mock_send.assert_called_with(
            {'username': 'System', 'message': 'Anonim opuścił pokój.'},
            room='testroom'
        )

@patch('main.chat_collection.insert_one')
def test_message_event_one_send(mock_insert, socketio_client):
    with patch('main.send') as mock_send:
        socketio_client.emit('message', {'room': 'testroom', 'message': 'Hello world!'})
        mock_insert.assert_called_once_with({
            'room': 'testroom',
            'username': 'Anonim',
            'message': 'Hello world!'
        })


@patch('main.chat_collection.insert_one')
def test_message_event_one_message(mock_insert, socketio_client):
    with patch('main.send') as mock_send:
        socketio_client.emit('message', {'room': 'testroom', 'message': 'Hello world!'})
        mock_send.assert_called_with(
            {'username': 'Anonim', 'message': 'Hello world!'},
            room='testroom'
        )