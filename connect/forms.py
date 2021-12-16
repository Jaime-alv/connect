#  connect. Build your own private social net
#  Copyright (C) 2021 Jaime Alvarez Fernandez
#  Contact info: jaime.af.git@gmail.com
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import flask_login
import wtforms
from flask_wtf import FlaskForm
from connect import models
from wtforms import validators


# login.html
class LoginForm(FlaskForm):
    username = wtforms.StringField('Username', validators=[validators.DataRequired()])
    password = wtforms.PasswordField('Password', validators=[validators.DataRequired()])
    remember_me = wtforms.BooleanField('Remember me')
    submit = wtforms.SubmitField('Log In')


# sign_in.html
class RegisterForm(FlaskForm):
    username = wtforms.StringField('Username', validators=[validators.DataRequired()])
    user_email = wtforms.StringField('Email', validators=[validators.DataRequired(),
                                                          validators.Regexp(r'^[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]+$',
                                                                            message='Please enter a valid email')])
    password = wtforms.PasswordField('Password',
                                     validators=[validators.DataRequired(),
                                                 validators.EqualTo('repeat_password',
                                                                    message='Passwords must match.')])
    repeat_password = wtforms.PasswordField('Repeat Password',
                                            validators=[validators.DataRequired(),
                                                        validators.EqualTo('password',
                                                                           message='Passwords must match.')])
    submit = wtforms.SubmitField('Sign In')

    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user is not None:
            raise validators.ValidationError('Please use a different username.')

    def validate_user_email(self, user_email):
        user = models.User.query.filter_by(email=user_email.data).first()
        if user is not None:
            raise validators.ValidationError('Please use a different email address.')


# profile.html
class EditProfileForm(FlaskForm):
    user_email = wtforms.StringField('Email', validators=[validators.Optional(),
                                                          validators.Regexp(r'^[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]+$',
                                                                            message='Please enter a valid email')])
    about_me = wtforms.TextAreaField('About me', validators=[validators.Length(min=0, max=140)])
    nickname = wtforms.StringField('Nickname', validators=[validators.Length(min=0, max=25)])
    submit = wtforms.SubmitField('Save changes')
    location = wtforms.StringField('Location', validators=[validators.Optional()])
    website = wtforms.StringField('Website', validators=[validators.Optional()])

    def validate_user_email(self, user_email):
        user = models.User.query.filter_by(email=user_email.data).first()
        if user is not None:
            raise validators.ValidationError('Please use a different email address.')

    def validate_website(self, website):
        if not website.data.startswith(r'http'):
            raise validators.ValidationError('Url needs to start with http')


# change_password.html
class ChangePasswordForm(FlaskForm):
    old_password = wtforms.PasswordField('Old password', validators=[validators.DataRequired()])
    new_password = wtforms.PasswordField('New password',
                                         validators=[validators.DataRequired(),
                                                     validators.EqualTo('repeat_new_password',
                                                                        message='Passwords must match.')])
    repeat_new_password = wtforms.PasswordField('Confirm new password',
                                                validators=[validators.DataRequired(),
                                                            validators.EqualTo('new_password',
                                                                               message='Passwords must match.')])
    submit = wtforms.SubmitField('Save changes')
    cancel = wtforms.SubmitField('Cancel')

    def validate_old_password(self, old_password):
        user = models.User.query.filter_by(username=flask_login.current_user.username).first()
        if user.check_password(old_password.data) is False:
            raise validators.ValidationError("Old password doesn't match")
        if old_password.data == self.new_password.data:
            raise validators.ValidationError("New password can't be equal to old password")


# following.html
class AddFriend(FlaskForm):
    friend_id = wtforms.StringField('Follow new user', validators=[validators.DataRequired()])
    submit = wtforms.SubmitField('Submit')

    def validate_friend_id(self, friend_id):
        if friend_id.data.startswith(r"@"):
            self.friend_id.data = friend_id.data[1:]
        friend_id = models.User.query.filter_by(username=self.friend_id.data).first()
        if friend_id is None:
            raise validators.ValidationError(f"No user with id: {self.friend_id.data}")
        if friend_id == flask_login.current_user:
            raise validators.ValidationError("Add a different user.")
        if flask_login.current_user.is_following(friend_id):
            raise validators.ValidationError(f"Already following user: {self.friend_id.data}!")


# user.html
class WriteMessage(FlaskForm):
    message = wtforms.StringField('New message', validators=[validators.Length(min=1, max=140)])
    submit = wtforms.SubmitField('Send')


# user.html_profile.html
class EmptyForm(FlaskForm):
    submit = wtforms.SubmitField('Submit')


# profile.html
class DeleteProfile(FlaskForm):
    delete = wtforms.SubmitField('Delete account')
    cancel = wtforms.SubmitField('Cancel')
