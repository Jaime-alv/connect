import sys
import re
import json
import pathlib
import flask
from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/login')
def login():
    return app.send_static_file('login.html')


@app.route('/sign_up')
def sign_up():
    return app.send_static_file('sign_up.html')


@app.route('/sign_up_form', methods=['POST'])
def sign_up_form():
    missing_field = []
    fields = ['email', 'password', 'password_confirm']
    # check if all fields are complete -> form validation
    for field in fields:
        value = flask.request.form.get(field, None)
        if value is None or value == '':
            missing_field.append(field)
    if missing_field:
        return flask.render_template('sign up error.html', inputs=missing_field, next=flask.url_for('sign_up'))
    # check if email is valid
    email_regex = re.compile(r"[a-zA-Z0-9_.]+@[a-zA-Z0-9_.+]+")
    new_user = flask.request.form.get('email')
    email = email_regex.search(new_user)
    if email is None:
        print('no valid email')
    # check if password is valid
    password = flask.request.form.get('password')
    password_confirm = flask.request.form.get('password_confirm')
    if (any(character.islower() for character in password)
            and any(character.isupper() for character in password)
            and any(character.isdigit() for character in password)
            and password == password_confirm):
        return flask.render_template('profile.html')


if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
