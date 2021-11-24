# Copyright (C) 2021 Jaime Alvarez Fernandez
import pathlib
import main
from modules import general
import flask
import shutil


# load profile user and send it to profile page
def show_profile(user):
    user_profile = general.load_user(user)
    email = user_profile['email']
    first_name = user_profile['first_name']
    last_name = user_profile['last_name']
    nickname = user_profile['nickname']
    bio = user_profile['bio']
    profile_picture = user_profile["profile_picture"]
    return flask.render_template('profile.html', email=email, first_name=first_name, last_name=last_name, bio=bio,
                                 nickname=nickname, profile_picture=profile_picture)


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
    path = pathlib.Path(f'..\\data\\user\\{user}')
    user_db = general.load_user_db()
    user_db['users'].remove(user)
    general.save_user_db(user_db)
    shutil.rmtree(path, ignore_errors=True)
    main.log_out()


# print profile info for editing, just PRINT
def edit_profile_template(user):
    user_profile = general.load_user(user)
    nickname = user_profile['nickname']
    first_name = user_profile['first_name']
    last_name = user_profile['last_name']
    bio = user_profile['bio']
    return flask.render_template('edit_profile.html', nickname=nickname, first_name=first_name, last_name=last_name,
                                 bio=bio)


def submit_data():
    user_file = general.load_user(flask.session['user'])
    user_file['nickname'] = flask.request.form.get('nickname')
    user_file['first_name'] = flask.request.form.get('first_name')
    user_file['last_name'] = flask.request.form.get('last_name')
    user_file['bio'] = flask.request.form.get('bio')
    general.save_user(user_file, flask.session['user'])
    return show_profile(flask.session['user'])
