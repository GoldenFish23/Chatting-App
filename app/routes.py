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
                        user_exists = False
                        for user in content['valid_users']:
                            if data['username'] == user['username'] and data['password'] == user['password'] and login == False:
                                user_exists = True
                                break
                        if user_exists:
                            session['login'] = True
                            Login = session['login']
                            return redirect(url_for('user_host_room', username = username, selected = 'chats'))
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
                data = {"valid_users":[{'username': username, 'email': email, 'password': password}]}
                print('Recieved: ' + data['valid_users'][0]['username'] + ' ' + data['valid_users'][0]['email'] + ' ' + data['valid_users'][0]['password'])    
                with open(file_path, 'r+') as data_file:
                    try:
                        file_data = json.load(data_file)
                        user_exists = False
                        print(file_data)
                        for users in file_data['valid_users']:
                            if users['username'] == data['valid_users'][0]['username']:
                                user_exists = True
                                break
                        if not user_exists:
                            file_data['valid_users'].append({'username': username, 'email': email, 'password': password})
                            print('Changing somme data')
                            print(file_data)
                            data_file.seek(0)
                            json.dump(file_data, data_file, indent=4)
                    except json.JSONDecodeError:
                        json.dump(data, data_file)
                        print('dumped some')
                    session['login'] = True
                    Login = session['login']
                return redirect(url_for('user_host_room', username = username, selected = 'chats'))
        return render_template('signup.html', Login=Login)
    try:
        with open(file_path, 'r+') as data_file:
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
def user_host_room(username): #roomcode is a problem
    Login = session.get('login', False)
    selected = 'chats'
    rooms_file_path = os.path.join('json', 'rooms.json')
    roomcode = ""
    if Login:
        if request.method == 'POST':
            selected = request.form.get('button_val', selected)
            if selected == "hostroom":
                roomcode = request.form.get('roomcode', "").strip()
                if request.form.get('but_room') == 'hostroomy' and roomcode != "":
                    room_data = {"rooms":[{"host": username, "roomcode": roomcode, "client":[]}]}
                    with open(rooms_file_path, 'r+') as room_file:
                        try:
                            rooms_file_content = json.load(room_file)
                            room_exists = False
                            for room in rooms_file_content['rooms']:
                                if room['roomcode'] == room_data['rooms'][0]['roomcode']:
                                    room_exists = True
                                    break
                            if not room_exists:
                                rooms_file_content["rooms"].append(room_data["rooms"])
                                print(rooms_file_content)
                                room_file.seek(0)
                                json.dump(rooms_file_content, room_file, indent=4)
                            else:
                                print('Room already exists')
                        except json.JSONDecodeError:
                            json.dump(room_data, room_file, indent=4)
                            print("somethings missing here")
                    return redirect(url_for('user_join_room', username=username, selected='hostroom', roomcode=roomcode))
            elif selected == "joinroom":
                roomcode = request.form.get('roomcode', "").strip()
                if request.form.get('but_room') == 'joinroomy' and roomcode != "":
                    room_data = {"rooms":[{"host": username, "roomcode": roomcode, "client":[]}]}
                    with open(rooms_file_path,'r+') as room_file:
                        try:
                            rooms_file_content = json.load(room_file)
                            room_exists = False
                            for room in rooms_file_content['rooms']:
                                if room['roomcode'] == room_data['rooms'][0]['roomcode']:
                                    room_exists = True
                                    break
                            if room_exists and room_data['rooms'][0]['host'] not in room['client']:
                                room['client'].append(username)
                                print(rooms_file_content)
                                room_file.seek(0)
                                json.dump(rooms_file_content, room_file, indent=4)
                            else:
                                print('Alreaty a member')
                        except json.JSONDecodeError:
                            print("no rooms are created yet")
                    return redirect(url_for('user_join_room', selected='joinroom', username=username, roomcode=roomcode))
            return render_template('homepage.html', Login=Login, selected=selected, username=username, roomcode=roomcode)
        return render_template('homepage.html', Login=Login, selected=selected, username=username, roomcode=roomcode)
    return render_template('base.html', Login=Login)

@app.route('/user/<username>/<selected>/<roomcode>', methods=['GET', 'POST'])
def user_join_room(username,selected, roomcode):
    Login = session.get('login', False)
    if Login != False:
        return render_template('homepage.html', Login=Login, selected = selected, username = username, roomcode = roomcode)
    return render_template('base.html',Login=Login)

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_connect():
    print('Client disconnected')

@socketio.on('join')
def on_join(data):
    username = data['username']
    roomcode = data['roomcode']
    if roomcode != "":
        join_room(roomcode)
        print(f'{username} joined {roomcode}')
        send(f'{username} has joined the room', broadcast=True, to=roomcode)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    roomcode = data['roomcode']
    if roomcode != "":
        leave_room(roomcode)
        send(f"{username} has left the room!", to=roomcode)

@socketio.on('message')
def handle_message(data):
    print(f"Received data: {data}")
    roomcode = data.get('roomcode')
    username = data.get('username')
    message = data.get('message')
    fullmsg = f'{username} : {message}'
    print('received message: ' + message)
    send(fullmsg, broadcast = True, to=roomcode)