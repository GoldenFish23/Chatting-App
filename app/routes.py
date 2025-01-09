from app import app, socketio
from flask import Flask, render_template, redirect, session, url_for, request, logging
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import json, os

global Login
@app.route('/')
@app.route('/homepage')
def homepage():
    Login = session.get('login', False)
    if Login != False:
        return render_template('homepage.html', Login=Login)
    return render_template('base.html',Login=Login)

@app.route('/login', methods=['GET', 'POST'])
def login():
    Login = session.get('login', False)
    file_path = os.path.join('json', 'user.json')
    if Login == False:
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            login = request.form.get('login',False)

            if not username or not password:
                if not username:
                    return render_template('login.html', Login=Login, error='Username is required')
                if not password:
                    return render_template('login.html', Login=Login, error='Password is required')
            else:
                data = {'username': username, 'password': password}
                print('Recieved123: ' + data['username'] + ' ' + data['password'])
                try:
                    with open(file_path, 'r') as data_file:
                        content = json.load(data_file)
                        if data['username'] == content['valid_users']['username'] and data['password'] == content['valid_users']['password'] and login == False:
                            session['login'] = True
                            Login = session['login']
                            return render_template('homepage.html', username = username, Login = Login)
                except json.JSONDecodeError:
                    print("No user really exists.")
                    return render_template('login.html', Login=Login, error='No user found')
                except Exception as e:
                    print("Error: " + str(e))
        return render_template('login.html', Login=Login)
    try:
        with open(file_path, 'r') as data_file:
            content = json.load(data_file)
            if content['valid_users']['username'] and content['valid_users']['password']:
                username = content['valid_users']['username']
                session['login'] = True
                Login = session['login']
                return render_template('homepage.html', username = username, Login = Login)
    except json.JSONDecodeError:
        session['login'] = False
        Login = session['login']
        print("probably some mistake in logging in...") 
        return "probably some mistake in logging in..."
    return render_template('homepage.html', username=username, Login=Login)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    Login = session.get('login',False)
    file_path = os.path.join('json', 'user.json')
    if Login == False:
        if request.method == "POST":
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            if not username or not email or not password:
                if not username:
                    return render_template('signup.html', Login=Login, error='Username is required')
                if not email:
                    return render_template('signup.html', Login=Login, error='Email is required')
                if not password:
                    return render_template('signup.html', Login=Login, error='Password is required')
            else:
                data = {"valid_users":{'username': username, 'email': email, 'password': password}}
                print('Recieved: ' + data['valid_users']['username'] + ' ' + data['valid_users']['email'] + ' ' + data['valid_users']['password'])
                file_path = os.path.join('json', 'user.json')
                with open(file_path, 'w') as data_file:
                    json.dump(data, data_file)
                session['login'] = True
                Login = session['login']
                return render_template('homepage.html', username = username, Login = Login)
        return render_template('signup.html', Login=Login)
    try:
        with open(file_path, 'r') as data_file:
            content = json.load(data_file)
            if content['valid_users']['username'] and content['valid_users']['password']:
                username = content['valid_users']['username']
                session['login'] = True
                Login = session['login']
                return render_template('homepage.html', username = username, Login = Login)
    except json.JSONDecodeError:
        session['login'] = False
        Login = session['login']
        print("probably some mistake")
        return "probably some mistake"
    return render_template('homepage.html',username=username, Login=Login)

@app.route('/logout')
def logout():
    session['login'] = False
    Login = session.get('login', False)
    return render_template('base.html', Login=Login)

@app.route('/user/<username>', methods=['GET', 'POST'])
def user_host_room(username, selected=None):
    Login = session.get('login', False)
    if Login != False: #Bug here not secure
        if request.method == 'POST':
            
            if request.form.get('button_val') == 'hostroom':
                return render_template('homepage.html', Login=Login, selected = 'hostroom', username = username)
            elif request.form.get('button_val') == 'joinroom':
                return render_template('homepage.html', Login=Login, selected = 'joinroom', username = username)
            elif request.form.get('button_val') == 'settings':
                return render_template('homepage.html', Login=Login, selected = 'settings', username = username)
            elif request.form.get('button_val') == 'chats' or selected == None:
                return render_template('homepage.html', Login=Login, selected = 'chats', username = username)
            
        print('this not is a joinroom')
        return render_template('homepage.html', Login=Login, selected = 'joinroom', username = username)
    print('faced some error...')
    return render_template('base.html',Login=Login)

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_connect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message, broadcast=True)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', username + ' has left the room.', room=room)