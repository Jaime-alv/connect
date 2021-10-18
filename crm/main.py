import sys
import re
import json
import pathlib
import secrets
import flask
import functions
from flask import Flask
import datetime

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
        return error('You are not logged in', 'login')


# clients page
@app.route('/clients')
def access_to_client():
    if 'user' in flask.session:
        return flask.render_template('clients.html')
    else:
        return error('You are not logged in', 'login')


# load messages' page
@app.route('/messages', methods=['POST', 'GET'])
def access_to_messages():
    if 'user' in flask.session:
        return flask.render_template('messages.html')
    else:
        return error('You are not logged in', 'login')


# process and save message
@app.route('/new_message', methods=['POST'])
def new_message():
    user = flask.session['user']
    message = flask.request.form.get('new_message')
    user_profile = functions.load_user(user)
    today = str(datetime.date.today().strftime('%d-%m-%Y'))
    time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    if user_profile['messages'].get(today, None) is None:
        user_profile['messages'].setdefault(today, {})
        user_profile['messages'][today].setdefault(time, message)
        with pathlib.Path(f'..\\data\\user\\{user_profile}\\user_profile.txt').open('w') as new:
            json.dump(user_profile, new)
        return flask.render_template('messages.html')
    else:
        user_profile['messages'][today].setdefault(time, message)
        with pathlib.Path(f'..\\data\\user\\{user_profile}\\user_profile.txt').open('w') as new:
            json.dump(user_profile, new)
        return flask.render_template('messages.html')


# save client data
@app.route('/new_client', methods=['POST'])
def new_client():
    user = flask.session['user']
    user_profile = functions.load_user(user)
    organization = user_profile['organization']
    inc_profile = functions.load_organization(organization)
    missing_field = []
    must_have_fields = ['name', 'email', 'phone']

    # form validation
    for field in must_have_fields:
        if flask.request.form.get(field) == '':
            missing_field.append(field)
    if missing_field:
        return error(f'Missing inputs in {missing_field}', 'clients')
    if flask.request.form.get('name') in inc_profile['clients']:
        return error(f'Client already exits', 'clients')

    # get all fields and added to client's profile
    inc_profile['clients'].append(flask.request.form.get('name'))
    inc_profile['client_data'].setdefault('name', flask.request.form.get('name'))
    inc_profile['client_data'].setdefault('email', flask.request.form.get('email'))
    inc_profile['client_data'].setdefault('phone', flask.request.form.get('phone'))
    inc_profile['client_data'].setdefault('telegram', flask.request.form.get('telegram', None))
    inc_profile['client_data'].setdefault('organization', flask.request.form.get('organization', None))
    with pathlib.Path(f'..\\data\\inc\\{organization}\\inc_profile.txt').open('w') as new:
        json.dump(inc_profile, new)
    return flask.render_template('clients.html')


# log in form into app
@app.route('/log_in', methods=['POST'])
def log_in():
    user = flask.request.form.get('email')
    if not pathlib.Path(f'..\\data\\user\\{user}').exists():
        return error('No user with that email', 'sign_up')
    else:
        file = functions.load_user(user)
        if file['password'] == flask.request.form.get('password'):
            flask.session['user'] = user
            return functions.show_profile(user)
        else:
            return error('Incorrect password', 'login')


# log out from session
@app.route('/logout')
def log_out():
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
        functions.create_new_user(organization, new_user, password)
        flask.session['user'] = new_user
        return functions.show_profile(new_user)
    else:
        return error('Password needs at least 1 upper, 1 digit and 1 punctuation', 'index')


# change password
@app.route('/new_password', methods=['POST'])
def change_password():
    new_password = flask.request.form.get('new_password')
    confirm_new_password = flask.request.form.get('confirm_new_password')
    user = flask.session['user']
    user_file = functions.load_user(user)
    if new_password == user_file['password']:
        return error('Password already used, choose new password', 'go_to_profile')
    elif new_password != user_file['password'] and (any(character.islower() for character in new_password)
                                                    and any(character.isupper() for character in new_password)
                                                    and any(character.isdigit() for character in new_password)
                                                    and new_password == confirm_new_password):
        user_file['password'] = new_password
        with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('w') as write:
            json.dump(user_file, write)
        return go_to_profile()
    elif new_password != confirm_new_password:
        return error('Both password fields needs to be equal', 'go_to_profile')


# delete profile
@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user = flask.session['user']
    user_profile = functions.load_user(user)
    organization = user_profile['organization']
    inc_profile = functions.load_organization(organization)
    if len(inc_profile['admin']) == 1:
        functions.remove_all(f'..\\data\\inc\\{organization}')
        functions.remove_all(f'..\\data\\user\\{user}')
    else:
        del inc_profile['employees'][user]
        if user in inc_profile['admin']:
            del inc_profile['admin'][user]
        functions.remove_all(f'..\\data\\user\\{user}')
    return log_out()


# load organization profile
@app.route('/inc', methods=['GET'])
def show_inc_profile():
    if 'user' in flask.session:
        user = flask.session['user']
        user_profile = functions.load_user(user)
        organization = user_profile['organization']
        inc_profile = functions.load_organization(organization)
        name = inc_profile['name']
        admin = inc_profile['admin']
        employees = inc_profile['employees']
        clients = inc_profile['clients']
        return flask.render_template('organization.html', name=name, admin=admin, employees=employees, clients=clients)
    else:
        return error('You are not logged in', 'login')


# clients html


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
