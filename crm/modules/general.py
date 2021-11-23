# Copyright (C) 2021 Jaime Alvarez Fernandez
# This file performs various basics tasks. (loading, saving, deleting)
import json
import pathlib
import flask


# generic error message, redirect to 'next_url'
def error(message, next_url):
    return flask.render_template('error.html', error_message=message, next=flask.url_for(next_url))


# show inc profile if user in admin group.
def show_inc_profile(user):
    user_profile = load_user(user)
    organization = user_profile['organization']
    inc_profile = load_organization(organization)
    if user_profile['user'] in inc_profile['admin']:
        name = inc_profile['name']
        admin = inc_profile['admin']
        employees = inc_profile['employees']
        clients = inc_profile['client_data']
        return flask.render_template('organization.html', name=name, admin=admin, employees=employees, clients=clients)
    else:
        return error("You don't have permit to access this section", 'home')


# load user
def load_user(user):
    with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('r') as write:
        user_profile = json.load(write)
    return user_profile


# save user
def save_user(user_file, user):
    with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('w') as write:
        json.dump(user_file, write)


# load user database
def load_user_db():
    with pathlib.Path('..\\data\\user\\user_db.txt').open('r') as read:
        user_db = json.load(read)
    return user_db


# save user database
def save_user_db(user_db):
    with pathlib.Path('..\\data\\user\\user_db.txt').open('w') as write:
        json.dump(user_db, write)
