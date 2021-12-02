import wtforms
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = wtforms.StringField('Username', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Password', validators=[wtforms.validators.DataRequired()])
    remember_me = wtforms.BooleanField('Remember me')
    submit = wtforms.SubmitField('Sign In')


class SignInForm(FlaskForm):
    username = wtforms.StringField('Username', validators=[wtforms.validators.DataRequired()])
    user_email = wtforms.StringField('Email', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Password',
                                     validators=[wtforms.validators.DataRequired(),
                                                 wtforms.validators.EqualTo('repeat_password',
                                                                            message='Passwords must match.')])
    repeat_password = wtforms.PasswordField('Repeat Password',
                                            validators=[wtforms.validators.DataRequired(),
                                                        wtforms.validators.EqualTo('password',
                                                                                   message='Passwords must match.')])
    submit = wtforms.SubmitField('Sign In')
