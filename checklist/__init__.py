import os
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('S_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ectokktnuzoxgk:49839418061ca6f8a81effed6c5b615347538421ff9685ea63de579e4bfdafb4@ec2-174-129-255-72.compute-1.amazonaws.com:5432/d73s4m5nr6ortt'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from checklist import routes