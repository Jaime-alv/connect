import re
import json
import pathlib
import flask
from flask import Flask


# load profile user
def show_profile(user_email):
    with pathlib.Path(f'..\\data\\user\\{user_email}\\user_profile.txt').open('r+') as file:
        user_profile = json.load(file)
        user = user_profile['user']
        password = user_profile['password']
        organization = user_profile['organization']
    return flask.render_template('profile.html', user=user, password=password, organization=organization)


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
