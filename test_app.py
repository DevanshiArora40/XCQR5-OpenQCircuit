# -*- coding: utf-8 -*-

from OpenQCircuit import create_app, db
from OpenQCircuit.models import User, Circuit 

app = create_app('testing')

with app.app_context():
    db.create_all()

    user = User(username='grey')
    user.set_password('123')
    db.session.add(user)

    circuit1 = Circuit(name=_('Bell State'), body=_('I-I-I---I-I-I\nI-H-X#0-I-I-I\nI-I-X#1-I-I-I\nI-I-I---I-I-I'), author=user)
    circuit2 = Circuit(name=_('Deutsch Oracle'), body=_('H-I-X#0-I---I-H\nH-I-I---X#0-I-H\nX-H-X#1-X#1-H-X'), author=user)
    circuit3 = Circuit(name=_('Teleportation'), body=_(''),author=user, done=True)

    user.circuits = [circuit1, circuit2, circuit3]

    db.session.commit()
