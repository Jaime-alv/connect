import sys
import re
import json
import pathlib
import secrets
import flask
import functions
from flask import Flask

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


@app.route('/profile')
def go_to_profile():
    if 'user' in flask.session:
        return functions.show_profile(flask.session['user'])
    else:
        return functions.error('You are not logged in', 'login')


@app.route('/log_in', methods=['POST'])
def log_in():
    user = flask.request.form.get('email')
    if not pathlib.Path(f'..\\data\\user\\{user}').exists():
        return functions.error('No user with that email', 'sign_up')
    else:
        with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('r') as file:
            file = json.load(file)
        if file['password'] == flask.request.form.get('password'):
            flask.session['user'] = user
            return functions.show_profile(user)
        else:
            return functions.error('Incorrect password', 'login')


@app.route('/logout')
def log_ou():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('index'))


@app.route('/sign_up_form', methods=['POST'])
def sign_up_form():
    missing_field = []
    fields = ['email', 'password', 'password_confirm']

    # check if all fields are complete -> form validation
    for field in fields:
        value = flask.request.form.get(field)
        if value == '':
            missing_field.append(field)
    if missing_field:
        return functions.error(f'Missing inputs in {missing_field}', 'sign_up')

    # check if email is already registered
    new_user = flask.request.form.get('email')
    organization = flask.request.form.get('organization')
    if pathlib.Path(f'..\\data\\user\\{new_user}').exists():
        return functions.error('User already exits', 'sign_up')

    # check if email is valid
    email_regex = re.compile(r"[a-zA-Z0-9_.]+@[a-zA-Z0-9_.+]+")
    email = email_regex.search(new_user)
    if email is None:
        return functions.error('email is not valid', 'sign_up')

    # check if password is valid
    password = flask.request.form.get('password')
    password_confirm = flask.request.form.get('password_confirm')
    if (any(character.islower() for character in password)
            and any(character.isupper() for character in password)
            and any(character.isdigit() for character in password)
            and password == password_confirm):
        functions.create_new_user(organization, new_user, password)
        flask.session['user'] = new_user
        return functions.show_profile(new_user)
    else:
        return functions.error('Password needs at least 1 upper, 1 digit and 1 punctuation', 'index')


secret_key = secrets.token_hex()
app.secret_key = secret_key
if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
