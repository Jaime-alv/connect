# Copyright (C) 2021 Jaime Álvarez Fernández
# This file is in charge of routing and create server
import sys
import secrets
import flask
import functions
from flask import Flask
import fill_in_forms

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/login')
def login():
    return app.send_static_file('login.html')


@app.route('/sign_up')
def sign_up():
    return app.send_static_file('sign_up.html')


# load profile page
@app.route('/profile')
def go_to_profile():
    if 'user' in flask.session:
        return functions.show_profile(flask.session['user'])
    else:
        return functions.error('You are not logged in', 'login')


# clients page
@app.route('/clients')
def access_to_client():
    if 'user' in flask.session:
        return flask.render_template('clients.html')
    else:
        return functions.error('You are not logged in', 'login')


# load messages' page
@app.route('/messages', methods=['POST', 'GET'])
def access_to_messages():
    if 'user' in flask.session:
        return flask.render_template('messages.html')
    else:
        return functions.error('You are not logged in', 'login')


# process and save message
@app.route('/new_message', methods=['POST'])
def new_message():
    user = flask.session['user']
    fill_in_forms.new_message(user)


# save client data
@app.route('/new_client', methods=['POST'])
def new_client():
    user = flask.session['user']
    fill_in_forms.new_client(user)


# log in form into app
@app.route('/log_in', methods=['POST'])
def log_in():
    fill_in_forms.log_in()


# log out from session
@app.route('/logout')
def log_out():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('index'))


@app.route('/sign_up_form', methods=['POST'])
def sign_up_form():
    fill_in_forms.sign_up()


# change password
@app.route('/new_password', methods=['POST'])
def change_password():
    user = flask.session['user']
    fill_in_forms.change_password(user)


# delete profile
@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user = flask.session['user']
    functions.remove_all(user)


# load organization profile
@app.route('/inc', methods=['GET'])
def show_inc_profile():
    if 'user' in flask.session:
        user = flask.session['user']
        functions.show_inc_profile(user)
    else:
        return functions.error('You are not logged in', 'login')


secret_key = secrets.token_hex()
app.secret_key = secret_key
if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
