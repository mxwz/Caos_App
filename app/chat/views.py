from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import chat
from flask_socketio import emit
from app import socketio

@chat.route('/')
@login_required
def chat():
    return render_template('chat/index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    try:
        emit('user joined', current_user.username, broadcast=True)
    except AttributeError as f:
        print(f)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    try:
        emit('user left', current_user.username, broadcast=True)
    except AttributeError as f:
        print(f)

@socketio.on('chat message')
def handle_chat_message(data):
    message = data['message']
    quote = data.get('quote', None)
    emit('chat message', {
        'username': current_user.username,
        'message': message,
        'quote': quote
    }, broadcast=True)
