# Copyright (C) 2021 Jaime Alvarez Fernandez
import re
import flask
import pathlib
from modules import general
from modules import profile
import json


def sign_up_form():
    missing_field = []
    fields = ['email', 'password', 'password_confirm', 'nickname']

    # check if all fields are complete -> form validation
    for field in fields:
        value = flask.request.form.get(field)
        if value == '':
            missing_field.append(field)
    if missing_field:
        return general.error(f'Missing inputs in {missing_field}', 'sign_up')

    # check if email is already registered
    new_user = flask.request.form.get('email')
    nickname = flask.request.form.get('nickname')
    if pathlib.Path(f'..\\data\\user\\{new_user}').exists():
        return general.error('User already exits', 'sign_up')

    # check if email is valid
    email_regex = re.compile(r"[a-zA-Z0-9_.]+@[a-zA-Z0-9_.+]+")
    email = email_regex.search(new_user)
    if email is None:
        return general.error('email is not valid', 'sign_up')

    # check if password is valid
    password = flask.request.form.get('password')
    password_confirm = flask.request.form.get('password_confirm')
    if (any(character.islower() for character in password)
            and any(character.isupper() for character in password)
            and any(character.isdigit() for character in password)
            and password == password_confirm):
        create_new_user(nickname, new_user, password)
        flask.session['user'] = new_user
        return profile.show_profile(new_user)
    else:
        return general.error('Password needs at least 1 upper, 1 digit and 1 punctuation', 'index')


# create user folder and json file with all data
def create_new_user(nickname, email, password):
    # create user profile
    pathlib.Path(f'..\\data\\user\\{email}').mkdir(parents=True)
    data_user = {'nickname': nickname,
                 'email': email,
                 'password': password,
                 'first_name': '',
                 'last_name': '',
                 'bio': '',
                 'messages': {},
                 'friends': [],
                 'groups': {}
                 }
    with pathlib.Path(f'..\\data\\user\\{email}\\user_profile.txt').open('w') as write:
        json.dump(data_user, write)
