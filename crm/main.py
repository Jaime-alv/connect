import sys
import re
import json
import pathlib
import secrets
import flask
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
def show_profile(user_email):
    with pathlib.Path(f'..\\data\\user\\{user_email}\\user_profile.txt').open('r+') as file:
        user_profile = json.load(file)
        user = user_profile['user']
        password = user_profile['password']
        organization = user_profile['organization']
    return flask.render_template('profile.html', user=user, password=password, organization=organization)


@app.route('/log_in', methods=['POST'])
def log_in():
    user = flask.request.form.get('email')
    if not pathlib.Path(f'..\\data\\user\\{user}').exists():
        return error('No user with that email', 'sign_up')
    else:
        with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('r') as file:
            file = json.load(file)
        if file['password'] == flask.request.form.get('password'):
            flask.session['user'] = user
            return show_profile(user)
        else:
            return error('Incorrect password', 'login')


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
        return error(f'Missing inputs in {missing_field}', 'sign_up')

    # check if email is already registered
    new_user = flask.request.form.get('email')
    organization = flask.request.form.get('organization')
    if pathlib.Path(f'..\\data\\user\\{new_user}').exists():
        return error('User already exits', 'sign_up')

    # check if email is valid
    email_regex = re.compile(r"[a-zA-Z0-9_.]+@[a-zA-Z0-9_.+]+")
    email = email_regex.search(new_user)
    if email is None:
        return error('email is not valid', 'sign_up')

    # check if password is valid
    password = flask.request.form.get('password')
    password_confirm = flask.request.form.get('password_confirm')
    if (any(character.islower() for character in password)
            and any(character.isupper() for character in password)
            and any(character.isdigit() for character in password)
            and password == password_confirm):
        create_new_user(organization, new_user, password)
        flask.session['user'] = new_user
        return show_profile(new_user)
    else:
        return error('Password needs at least 1 upper, 1 digit and 1 punctuation', 'index')


# create user folder and json file with all data
def create_new_user(organization, email, password):
    # create organization and add user as admin
    if organization != '' and not pathlib.Path(f'..\\data\\inc\\{organization}').exists():
        pathlib.Path(f'..\\data\\inc\\{organization}').mkdir(parents=True, exist_ok=True)
        data_inc = {'admin': [],
                    'employees': [],
                    'clients': [],
                    'client_data': {}}
        with pathlib.Path(f'..\\data\\inc\\{organization}\\inc_profile.txt').open('w') as w:
            data_inc['admin'].append(email)
            data_inc['employees'].append(email)
            json.dump(data_inc, w)

    # create user profile
    pathlib.Path(f'..\\data\\user\\{email}').mkdir(parents=True)
    data_user = {'organization': organization,
                 'user': email,
                 'password': password,
                 'messages': {},
                 'contacts': [],
                 }
    with pathlib.Path(f'..\\data\\user\\{email}\\user_profile.txt').open('w') as f:
        json.dump(data_user, f)


# generic error message, redirect to 'next_url'
def error(message, next_url):
    return flask.render_template('error.html', error_message=message, next=flask.url_for(next_url))


secret_key = secrets.token_hex()
app.secret_key = secret_key
if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
