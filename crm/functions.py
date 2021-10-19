# Copyright (C) 2021 Jaime Álvarez Fernández
# This file perform various basics tasks. (loading, saving, deleting)
import json
import pathlib
import flask


# generic error message, redirect to 'next_url'
def error(message, next_url):
    return flask.render_template('error.html', error_message=message, next=flask.url_for(next_url))


# load profile user and send it to profile page
def show_profile(user_email):
    with pathlib.Path(f'..\\data\\user\\{user_email}\\user_profile.txt').open('r+') as file:
        user_profile = json.load(file)
        user = user_profile['user']
        password = user_profile['password']
        organization = user_profile['organization']
    return flask.render_template('profile.html', user=user, password=password, organization=organization)


# show inc profile if user in admin group.
def show_inc_profile(user):
    user_profile = load_user(user)
    organization = user_profile['organization']
    inc_profile = load_organization(organization)
    if user_profile['name'] in inc_profile['admin']:
        name = inc_profile['name']
        admin = inc_profile['admin']
        employees = inc_profile['employees']
        clients = inc_profile['clients']
        return flask.render_template('organization.html', name=name, admin=admin, employees=employees, clients=clients)
    else:
        return error("You don't have permit to access this section", 'home')


# create user folder and json file with all data
def create_new_user(organization, email, password):
    # create organization and add user as admin
    if organization != '' and not pathlib.Path(f'..\\data\\inc\\{organization}').exists():
        pathlib.Path(f'..\\data\\inc\\{organization}').mkdir(parents=True, exist_ok=True)
        data_inc = {'name': organization,
                    'admin': [],
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
    with pathlib.Path(f'..\\data\\user\\{email}\\user_profile.txt').open('w') as write:
        json.dump(data_user, write)


# load user
def load_user(user):
    with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('r') as write:
        user_profile = json.load(write)
    return user_profile


# load inc
def load_organization(organization):
    with pathlib.Path(f'..\\data\\inc\\{organization}\\inc_profile.txt').open('r') as write:
        inc_profile = json.load(write)
    return inc_profile


# save user
def save_user(user_file, user):
    with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('w') as write:
        json.dump(user_file, write)


# save inc data
def save_inc(inc_file, organization):
    with pathlib.Path(f'..\\data\\inc\\{organization}\\inc_profile.txt').open('w') as write:
        json.dump(inc_file, write)


# remove directory and contents
def remove(user):
    import main
    user_profile = load_user(user)
    organization = user_profile['organization']
    inc_profile = load_organization(organization)
    if len(inc_profile['admin']) == 1:
        remove_all(f'..\\data\\inc\\{organization}')
        remove_all(f'..\\data\\user\\{user}')
    else:
        del inc_profile['employees'][user]
        if user in inc_profile['admin']:
            del inc_profile['admin'][user]
        remove_all(f'..\\data\\user\\{user}')
    return main.log_out()


def remove_all(path):
    path = pathlib.Path(path)
    for item in path.iterdir():
        if item.is_dir():
            remove_all(item)
        else:
            item.unlink()
    path.rmdir()
