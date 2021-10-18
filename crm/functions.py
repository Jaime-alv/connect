import json
import pathlib
import flask


# load profile user and send it to profile page
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
    with pathlib.Path(f'..\\data\\user\\{email}\\user_profile.txt').open('w') as f:
        json.dump(data_user, f)


# load user
def load_user(user):
    with pathlib.Path(f'..\\data\\user\\{user}\\user_profile.txt').open('r') as f:
        user_profile = json.load(f)
    return user_profile


# load inc
def load_organization(organization):
    with pathlib.Path(f'..\\data\\inc\\{organization}\\inc_profile.txt').open('r') as f:
        inc_profile = json.load(f)
    return inc_profile


# remove directory and contents
def remove_all(path):
    path = pathlib.Path(path)
    for item in path.iterdir():
        if item.is_dir():
            remove_all(item)
        else:
            item.unlink()
    path.rmdir()
