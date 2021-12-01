import flask
from connect import app
from connect import forms


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Jaime'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return flask.render_template('index.html', user=user, posts=posts, title=user['username'])


@app.route('/profile')
def profile():
    user = {'username': 'Jaime',
            'email': 'jaime@socnet',
            'friends': ['John', 'Susan']}
    return flask.render_template('profile.html', user=user, title=user['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        flask.flash(f'Login requested for user {form.username.data}, remember_me = {form.remember_me.data}')
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('login.html', title='Sign in', form=form)