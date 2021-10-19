# Copyright (C) 2021 Jaime Álvarez Fernández
# This file process forms

import re
import json
import pathlib
import flask
import functions
import datetime
import main


# log in form into app
def log_in():
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


# process and save message
def new_message(user):
    message = flask.request.form.get('new_message')
    user_profile = functions.load_user(user)
    today = str(datetime.date.today().strftime('%d-%m-%Y'))
    time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    if user_profile['messages'].get(today, None) is None:
        user_profile['messages'].setdefault(today, {})
        user_profile['messages'][today].setdefault(time, message)
        with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('w') as new:
            json.dump(user_profile, new)
        return flask.render_template('messages.html')
    else:
        user_profile['messages'][today].setdefault(time, message)
        functions.save_user(user_profile, user)
        return flask.render_template('messages.html')


# new client data form
def new_client(user):
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
        return functions.error(f'Missing inputs in {missing_field}', 'clients')
    if flask.request.form.get('name') in inc_profile['clients']:
        return functions.error(f'Client already exits', 'clients')

    # get all fields and added to client's profile
    inc_profile['clients'].append(flask.request.form.get('name'))
    inc_profile['client_data'].setdefault('name', flask.request.form.get('name'))
    inc_profile['client_data'].setdefault('email', flask.request.form.get('email'))
    inc_profile['client_data'].setdefault('phone', flask.request.form.get('phone'))
    inc_profile['client_data'].setdefault('telegram', flask.request.form.get('telegram', None))
    inc_profile['client_data'].setdefault('organization', flask.request.form.get('organization', None))
    functions.save_inc(inc_profile, organization)
    return flask.render_template('clients.html')


# sign up form
def sign_up():
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
def change_password(user):
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
        return main.go_to_profile()
    elif new_password != confirm_new_password:
        return functions.error('Both password fields needs to be equal', 'go_to_profile')
