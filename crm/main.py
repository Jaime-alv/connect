# Copyright (C) 2021 Jaime Alvarez Fernandez
# This file is in charge of routing and create server
import pathlib
import sys
import secrets
import flask
import datetime
from flask import Flask
from modules import general
from modules import signup
from modules import profile
from modules import messages

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


@app.route('/sign_up')
def sign_up():
    return app.send_static_file('sign_up.html')


# load profile page
@app.route('/profile')
def go_to_profile():
    if 'user' in flask.session:
        return profile.show_profile(flask.session['user'])
    else:
        return general.error('You are not logged in', 'login')


# add new customer
@app.route('/new_customer')
def access_to_client():
    if 'user' in flask.session:
        return flask.render_template('new_customer.html')
    else:
        return general.error('You are not logged in', 'login')


# display current customers and their data
@app.route('/customers', methods=['GET'])
def show_customers():
    if 'user' in flask.session:
        user = flask.session['user']
        customers = general.load_inc_with(user)['client_data']
        return flask.render_template('customers.html', customers=customers)
    else:
        return general.error('You are not logged in', 'login')


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


# save client data
# template/new_customer.html
@app.route('/new_client', methods=['POST'])
def new_client():
    user = flask.session['user']
    inc_profile = general.load_inc_with(user)
    missing_field = []
    must_have_fields = ['first_name', 'email', 'last_name']

    # form validation
    for field in must_have_fields:
        if flask.request.form.get(field) == '':
            missing_field.append(field)
    if missing_field:
        return general.error(f'Missing inputs in {missing_field}', 'access_to_client')
    if flask.request.form.get('email') in inc_profile['client_data']:
        return general.error(f'Client already exits', 'access_to_client')

    # get all fields and added to client's profile
    email = flask.request.form.get('email')
    inc_profile['client_data'].setdefault(email, {})
    inc_profile['client_data'][email].setdefault('first_name', flask.request.form.get('first_name'))
    inc_profile['client_data'][email].setdefault('last_name', flask.request.form.get('last_name'))
    inc_profile['client_data'][email].setdefault('email', flask.request.form.get('email'))
    inc_profile['client_data'][email].setdefault('phone', flask.request.form.get('phone'))
    inc_profile['client_data'][email].setdefault('telegram', flask.request.form.get('telegram'))
    inc_profile['client_data'][email].setdefault('organization', flask.request.form.get('organization'))
    date_now = datetime.datetime.now()
    file_name = date_now.strftime(f"{flask.request.form.get('first_name')[0].lower()}"
                                  f"%f%Y%m%d"
                                  f"{flask.request.form.get('last_name')[0].lower()}")
    inc_profile['client_data'][email].setdefault('dialog_file', file_name)
    general.save_inc(inc_profile, inc_profile['name'])
    pathlib.Path(f'..\\data\\inc\\{inc_profile["name"]}\\customers\\{file_name}.txt').open('w')
    return flask.render_template('new_customer.html')


# delete all customer list
# template/customers.html
@app.route('/delete_all_customers', methods=['POST'])
def delete_all_customers():
    user = flask.session['user']
    inc_profile = general.load_inc_with(user)
    inc_profile['client_data'].clear()
    general.save_inc(inc_profile, inc_profile['name'])
    return flask.render_template('customers.html')


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
            return profile.show_profile(user)
        else:
            return general.error('Incorrect password', 'login')


# log out from session
@app.route('/logout')
def log_out():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('index'))


@app.route('/sign_up_form', methods=['POST'])
def sign_up_form():
    return signup.sign_up_form()


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


# load organization profile
@app.route('/inc', methods=['GET'])
def show_inc_profile():
    if 'user' in flask.session:
        user = flask.session['user']
        user_profile = general.load_user(user)
        organization = user_profile['organization']
        inc_profile = general.load_organization(organization)
        if user_profile['user'] in inc_profile['admin']:
            name = inc_profile['name']
            admin = inc_profile['admin']
            employees = inc_profile['employees']
            clients = inc_profile['client_data']
            return flask.render_template('organization.html', name=name, admin=admin, employees=employees,
                                         clients=clients)
        else:
            return general.error("You don't have permit to access this section", 'home')
    else:
        return general.error('You are not logged in', 'login')


secret_key = secrets.token_hex()
app.secret_key = secret_key
if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
