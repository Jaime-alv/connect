# Copyright (C) 2021 Jaime Alvarez Fernandez

from modules import general
import main
import flask


def load_friends(user):
    user_profile = general.load_user(user)
    friends = user_profile['friends']
    return flask.render_template('friends.html', friend_list=friends)


def delete_all(user):
    user_profile = general.load_user(user)
    user_profile['friends'].clear()
    general.save_user(user_profile, user)
    return main.show_friends()


def add_new_friend():
    friend_id = flask.request.form.get('friend_id')
    user_db = general.load_user_db()
    if friend_id not in user_db['users']:
        return general.error('No user found with that id', 'show_friends')
    elif friend_id in user_db['users']:
        user_profile = general.load_user(flask.session['user'])
        if friend_id in user_profile['friends']:
            return general.error("Already in your friend's list", 'show_friends')
        else:
            user_profile['friends'].append(friend_id)
            general.save_user(user_profile, flask.session['user'])
            friend_profile = general.load_user(friend_id)
            friend_profile['friends'].append(flask.session['user'])
            general.save_user(friend_profile, friend_id)
            return main.show_friends()

