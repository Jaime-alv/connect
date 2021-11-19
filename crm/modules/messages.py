# Copyright (C) 2021 Jaime Alvarez Fernandez
import flask
import datetime
import pathlib
import json
from modules import general


# process and save message
def new_message(user):
    message = flask.request.form.get('new_message')
    user_profile = general.load_user(user)
    today = str(datetime.date.today().strftime('%d-%m-%Y'))
    time = str(datetime.datetime.now().strftime('%H:%M:%S'))
    if user_profile['messages'].get(today, None) is None:
        user_profile['messages'].setdefault(today, {})
        user_profile['messages'][today].setdefault(time, message)
        with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('w') as new:
            json.dump(user_profile, new)
    else:
        user_profile['messages'][today].setdefault(time, message)
        general.save_user(user_profile, user)
