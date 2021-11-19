# Copyright (C) 2021 Jaime Alvarez Fernandez
import pathlib
import json
import main
from modules import general
import flask


# load profile user and send it to profile page
def show_profile(user_email):
    with pathlib.Path(f'..\\data\\user\\{user_email}\\user_profile.txt').open('r+') as file:
        user_profile = json.load(file)
        user = user_profile['user']
        password = user_profile['password']
        organization = user_profile['organization']
    return flask.render_template('profile.html', user=user, password=password, organization=organization)


def change_password():
    user = flask.session['user']
    new_password = flask.request.form.get('new_password')
    confirm_new_password = flask.request.form.get('confirm_new_password')
    user_file = general.load_user(user)

    if new_password == user_file['password']:
        return general.error('Password already used, choose new password', 'go_to_profile')
    elif new_password != user_file['password'] and (any(character.islower() for character in new_password)
                                                    and any(character.isupper() for character in new_password)
                                                    and any(character.isdigit() for character in new_password)
                                                    and new_password == confirm_new_password):
        user_file['password'] = new_password
        general.save_user(user_file, user)
        return main.go_to_profile()
    elif new_password != confirm_new_password:
        return general.error('Both password fields needs to be equal', 'go_to_profile')


# remove directory and contents
def remove(user):
    user_profile = general.load_user(user)
    organization = user_profile['organization']
    inc_profile = general.load_organization(organization)
    if len(inc_profile['admin']) == 1:
        remove_all(f'..\\data\\inc\\{organization}')
        remove_all(f'..\\data\\user\\{user}')
    else:
        del inc_profile['employees'][user]
        if user in inc_profile['admin']:
            del inc_profile['admin'][user]
        remove_all(f'..\\data\\user\\{user}')


def remove_all(path):
    path = pathlib.Path(path)
    for item in path.iterdir():
        if item.is_dir():
            remove_all(item)
        else:
            item.unlink()
    path.rmdir()
