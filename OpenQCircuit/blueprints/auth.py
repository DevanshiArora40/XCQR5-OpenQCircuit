# -*- coding: utf-8 -*-

from faker import Faker
from flask import render_template, redirect, url_for, Blueprint, request, jsonify
from flask_babel import _
from flask_login import login_user, logout_user, login_required, current_user

from OpenQCircuit.extensions import db
from OpenQCircuit.models import User, Circuit

auth_bp = Blueprint('auth', __name__)
fake = Faker()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app.app'))

    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.validate_password(password):
            login_user(user)
            return jsonify(message=_('Login success.'))
        return jsonify(message=_('Invalid username or password.')), 400
    return render_template('_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message=_('Logout success.'))


@auth_bp.route('/register')
def register():
    # generate a random account for demo use
    username = fake.user_name()
    # make sure the generated username was not in database
    while User.query.filter_by(username=username).first() is not None:
        username = fake.user_name()
    password = fake.word()
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    circuit1 = Circuit(name=_('Bell State'), body=_('I-I-I---I-I-I\nI-H-X#0-I-I-I\nI-I-X#1-I-I-I\nI-I-I---I-I-I'), author=user)
    circuit2 = Circuit(name=_('Deutsch Oracle'), body=_('H-I-X#0-I---I-H\nH-I-I---X#0-I-H\nX-H-X#1-X#1-H-X'), author=user)
    circuit3 = Circuit(name=_('Simons Algorithm'),
                body=_('H-X#0-I---I---I---I---H-I\nH-I---X#0-I---X#0-X#0-H-I\nH-I---I---X#0-I---I---H-I\nI-X#1-I---I---I---I---I-I\nI-I---X#1-I---X#1-I---I-I\nI-I---I---X#1-I---X#1-I-I'),
                author=user, done=True)

    db.session.add_all([circuit1, circuit2, circuit3])
    db.session.commit()

    return jsonify(username=username, password=password, message=_('Generate success.'))
