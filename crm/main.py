# Copyright (C) 2021 Jaime Alvarez Fernandez
# This file is in charge of routing and create server
import pathlib
import sys
import secrets
import flask
import re
import functions
from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    if 'user' in flask.session:
        return flask.render_template('general_template.html')
    else:
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


# add new customer
@app.route('/new_customer')
def access_to_client():
    if 'user' in flask.session:
        return flask.render_template('new_customer.html')
    else:
        return functions.error('You are not logged in', 'login')


# display current customers and their data
@app.route('/customers', methods=['GET'])
def show_customers():
    if 'user' in flask.session:
        user = flask.session['user']
        customers = functions.load_inc_with(user)['client_data']
        return flask.render_template('customers.html', customers=customers)
    else:
        return functions.error('You are not logged in', 'login')


# load messages' page
@app.route('/messages', methods=['POST', 'GET'])
def access_to_messages():
    if 'user' in flask.session:
        user = flask.session['user']
        user_profile = functions.load_user(user)
        messages = user_profile['messages']
        return flask.render_template('messages.html', messages=messages)
    else:
        return functions.error('You are not logged in', 'login')


# process and save message
@app.route('/new_message', methods=['POST'])
def new_message():
    user = flask.session['user']
    functions.new_message(user)
    return access_to_messages()


# save client data
@app.route('/new_client', methods=['POST'])
def new_client():
    user = flask.session['user']
    organization = functions.load_user(user)['organization']
    inc_profile = functions.load_inc_with(user)
    missing_field = []
    must_have_fields = ['name', 'email']

    # form validation
    for field in must_have_fields:
        if flask.request.form.get(field) == '':
            missing_field.append(field)
    if missing_field:
        return functions.error(f'Missing inputs in {missing_field}', 'new_customer')
    if flask.request.form.get('email') in inc_profile['client_data']:
        return functions.error(f'Client already exits', 'new_customer')

    # get all fields and added to client's profile
    email = flask.request.form.get('email')
    inc_profile['client_data'].setdefault(email, {})
    inc_profile['client_data'][email].setdefault('name', flask.request.form.get('name'))
    inc_profile['client_data'][email].setdefault('email', flask.request.form.get('email'))
    inc_profile['client_data'][email].setdefault('phone', flask.request.form.get('phone', None))
    inc_profile['client_data'][email].setdefault('telegram', flask.request.form.get('telegram', None))
    inc_profile['client_data'][email].setdefault('organization', flask.request.form.get('organization', None))
    functions.save_inc(inc_profile, organization)
    return flask.render_template('new_customer.html')


# log in form into app
@app.route('/log_in', methods=['POST'])
def log_in_server():
    user = flask.request.form.get('email')
    if not pathlib.Path(f'..\\data\\user\\{user}').exists():
        return functions.error('No user with that email', 'sign_up')
    else:
        file = functions.load_user(user)
        if file['password'] == flask.request.form.get('password'):
            flask.session['user'] = user
            return functions.show_profile(user)
        else:
            return functions.error('Incorrect password', 'login')


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


# change password
@app.route('/new_password', methods=['POST'])
def change_password():
    user = flask.session['user']
    new_password = flask.request.form.get('new_password')
    confirm_new_password = flask.request.form.get('confirm_new_password')
    user_file = functions.load_user(user)

    if new_password == user_file['password']:
        return functions.error('Password already used, choose new password', 'go_to_profile')
    elif new_password != user_file['password'] and (any(character.islower() for character in new_password)
                                                    and any(character.isupper() for character in new_password)
                                                    and any(character.isdigit() for character in new_password)
                                                    and new_password == confirm_new_password):
        user_file['password'] = new_password
        functions.save_user(user_file, user)
        return go_to_profile()
    elif new_password != confirm_new_password:
        return functions.error('Both password fields needs to be equal', 'go_to_profile')


# delete profile
@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user = flask.session['user']
    functions.remove(user)
    return log_out()


# load organization profile
@app.route('/inc', methods=['GET'])
def show_inc_profile():
    if 'user' in flask.session:
        user = flask.session['user']
        user_profile = functions.load_user(user)
        organization = user_profile['organization']
        inc_profile = functions.load_organization(organization)
        if user_profile['user'] in inc_profile['admin']:
            name = inc_profile['name']
            admin = inc_profile['admin']
            employees = inc_profile['employees']
            clients = inc_profile['clients']
            return flask.render_template('organization.html', name=name, admin=admin, employees=employees,
                                         clients=clients)
        else:
            return functions.error("You don't have permit to access this section", 'home')
    else:
        return functions.error('You are not logged in', 'login')


secret_key = secrets.token_hex()
app.secret_key = secret_key
if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
