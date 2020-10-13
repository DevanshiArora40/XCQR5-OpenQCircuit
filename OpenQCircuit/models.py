# -*- coding: utf-8 -*-

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from OpenQCircuit.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    circuits = db.relationship('Circuit', back_populates='author', cascade='all')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Circuit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    body = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='circuits')
