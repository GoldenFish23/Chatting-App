from app import app, socketio
from flask import Flask, render_template, redirect, session, url_for, request
from flask_socketio import SocketIO, send, emit
import json, os

global Login
@app.route('/')
@app.route('/homepage')
def homepage():
    Login = session.get('login', False)
    return render_template('base.html',Login=Login)

@app.route('/login', methods=['GET', 'POST'])
def login():
    Login = session.get('login', False)
    if Login == False:
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            login = request.form.get('login')
            if not username or not password:
                if not username:
                    return render_template('login.html', Login=Login, error='Username is required')
                if not password:
                    return render_template('login.html', Login=Login, error='Password is required')
            else:
                data = {'username': username, 'password': password}
                print('Recieved: ' + data['username'] + ' ' + data['password'])
                file_path = os.path.join('json', 'user.json')
                with open(file_path, 'w') as data_file:
                    json.dump(data, data_file)

        return render_template('login.html', Login=Login)
    return render_template('homepage.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    Login = session.get('login',False)
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
    return render_template('homepage.html')

@app.route('/logout')
def logout():
    session['login'] = False
    Login = session.get('login', False)
    return render_template('base.html', Login=Login)

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