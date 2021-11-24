# Copyright (C) 2021 Jaime Alvarez Fernandez
# This file is in charge of routing and create server
import json
import pathlib
import sys
import secrets
import flask
import logging
from flask import Flask
from modules import general
from modules import signup
from modules import profile
from modules import messages
from modules import friends

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    if 'user' in flask.session:
        return flask.render_template('home_template.html')
    else:
        return app.send_static_file('index.html')


@app.route('/login')
def login():
    return app.send_static_file('login.html')


# log in form into app
# static/login.html
@app.route('/log_in', methods=['POST'])
def log_in_server():
    user = flask.request.form.get('email')
    if not pathlib.Path(f'..\\data\\user\\{user}').exists():
        return general.error('No user with that email', 'sign_up')
    else:
        file = general.load_user(user)
        if file['password'] == flask.request.form.get('password'):
            flask.session['user'] = user
            logging.debug(f"Logged with: {user}")
            return profile.show_profile(user)
        else:
            return general.error('Incorrect password', 'login')


# log out from session
@app.route('/logout')
def log_out():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('index'))


@app.route('/sign_up')
def sign_up():
    return app.send_static_file('sign_up.html')


@app.route('/sign_up_form', methods=['POST'])
def sign_up_form():
    return signup.sign_up_form()


# load profile page
@app.route('/profile')
def go_to_profile():
    if 'user' in flask.session:
        return profile.show_profile(flask.session['user'])
    else:
        return general.error('You are not logged in', 'login')


# change password
@app.route('/new_password', methods=['POST'])
def change_password():
    return profile.change_password()


# delete profile
@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user = flask.session['user']
    profile.remove(user)
    return log_out()


# edit profile redirect
@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'user' in flask.session:
        return profile.edit_profile_template(flask.session['user'])
    else:
        return general.error('You are not logged in', 'login')


# submit data and save to profile file
@app.route('/submit_data', methods=['POST'])
def submit_data():
    if 'cancel' in flask.request.form:
        return go_to_profile()
    elif 'submit' in flask.request.form:
        return profile.submit_data()


# load messages' page
@app.route('/messages', methods=['POST', 'GET'])
def access_to_messages():
    if 'user' in flask.session:
        user = flask.session['user']
        user_profile = general.load_user(user)
        user_messages = user_profile['messages']
        return flask.render_template('messages.html', messages=user_messages)
    else:
        return general.error('You are not logged in', 'login')


# process and save message
@app.route('/new_message', methods=['POST'])
def new_message():
    user = flask.session['user']
    messages.new_message(user)
    return access_to_messages()


# add new customer
@app.route('/new_customer')
def access_to_client():
    if 'user' in flask.session:
        return flask.render_template('new_customer.html')
    else:
        return general.error('You are not logged in', 'login')


# display current friends
@app.route('/friends', methods=['GET'])
def show_friends():
    if 'user' in flask.session:
        return friends.load_friends(flask.session['user'])
    else:
        return general.error('You are not logged in', 'login')


# save client data
# template/new_customer.html
@app.route('/add_new_friend', methods=['POST'])
def add_new_friend():
    return friends.add_new_friend()


# delete all friends list
# template/friends.html
@app.route('/delete_all_friends', methods=['POST'])
def delete_all_friends():
    return friends.delete_all(flask.session['user'])


secret_key = secrets.token_hex()
app.secret_key = secret_key
if __name__ == '__main__':
    log_file = pathlib.Path('../tests/log.txt')
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(levelname)s - %(message)s')
    log_file.open('w')
    if not pathlib.Path('..\\data\\user\\user_db.txt').exists():
        pathlib.Path('..\\data\\user').mkdir(exist_ok=True, parents=True)
        with pathlib.Path('..\\data\\user\\user_db.txt').open('w') as write:
            json.dump({'users': []}, write)
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
