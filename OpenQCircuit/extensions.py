# -*- coding: utf-8 -*-

from flask import request, current_app
from flask_babel import Babel, lazy_gettext as _l
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
babel = Babel()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please login to access this page.')


@login_manager.user_loader
def load_user(user_id):
    from OpenQCircuit.models import User
    return User.query.get(int(user_id))
