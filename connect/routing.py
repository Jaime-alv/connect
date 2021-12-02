import flask
from connect import app
from connect import forms


@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html', title='Welcome to Connect!')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        return flask.redirect(flask.url_for('profile'))
    return flask.render_template('sign_in.html', title='Sign in', form=form)


@app.route('/profile')
def profile():
    user = {'username': 'Jaime',
            'email': 'jaime@socnet',
            'friends': ['John', 'Susan']}
    return flask.render_template('profile.html', user=user, title='profile')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        flask.flash(f'Login requested for user {form.username.data}, remember_me = {form.remember_me.data}')
        return flask.redirect(flask.url_for('profile'))
    return flask.render_template('login.html', title='Log In', form=form)


@app.route('/logout')
def logout():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('index'))
