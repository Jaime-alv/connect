#  connect. Build your own private social net
#  Copyright (C) 2021 Jaime Alvarez Fernandez
#  Contact info: jaime.af.git@gmail.com
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging import handlers
import pathlib


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'  # where should the app look if login is required

from connect import routing, models, errors

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = handlers.SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Failure in Connect app',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    # create log folder
    if not pathlib.Path('logs').exists():
        pathlib.Path('logs').mkdir(parents=True, exist_ok=True)
    # create file connect.log with a maximum file size of 10kb
    file_handler = handlers.RotatingFileHandler('logs/connect.log', maxBytes=10240, backupCount=10)
    # set the format for each logging message with datetime, level and in which file and line it's called
    logging_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(module)s:line%(lineno)d]')
    file_handler.setFormatter(logging_format)
    # set logging level to INFO
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Connect startup')
