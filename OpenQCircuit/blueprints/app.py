# -*- coding: utf-8 -*-

from flask import render_template, request, Blueprint, jsonify, redirect
from flask_babel import _
from flask_login import current_user, login_required

from OpenQCircuit.extensions import db
from OpenQCircuit.models import Circuit

app_bp = Blueprint('app', __name__)


@app_bp.route('/app')
@login_required
def app():
    # all_count = Circuit.query.with_parent(current_user).count()
    active_count = Circuit.query.with_parent(current_user).filter_by(done=False).count()
    completed_count = Circuit.query.with_parent(current_user).filter_by(done=True).count()
    return render_template('_app.html', items=current_user.circuits, active_count=active_count, completed_count=completed_count)


@app_bp.route('/circuit', methods=['GET', 'POST'])
@login_required
def launch():
    if request.method == 'POST':
        data = request.get_json()
        item_id = data['itemID']
        item = Circuit.query.get_or_404(item_id)
        if current_user != item.author:
            return jsonify(message=_('Permission denied.')), 403
        return render_template('_circuit.html', circuit=item)
    return jsonify(message=_('Something went wrong~'))

@app_bp.route('/circuit/<int:item_id>/edit', methods=['PUT'])
@login_required
def edit_circuit(item_id):
    item = Circuit.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    data = request.get_json()
    if data is None or data['playgroundInput'].strip() == '':
        return jsonify(message=_('Invalid item name.')), 400
    item.body = data['playgroundInput']
    print(item.body)
    db.session.commit()
    return jsonify(message=_('Circuit updated.'))

@app_bp.route('/items/new', methods=['POST'])
@login_required
def new_item():
    data = request.get_json()
    if data is None or data['name'].strip() == '':
        return jsonify(message=_('Invalid item name.')), 400
    item = Circuit(name=data['name'], body="X-I\nI-I", author=current_user._get_current_object())
    db.session.add(item)
    db.session.commit()
    return jsonify(html=render_template('_item.html', item=item), message='Success')


@app_bp.route('/item/<int:item_id>/edit', methods=['PUT'])
@login_required
def edit_item(item_id):
    item = Circuit.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    data = request.get_json()
    if data is None or data['name'].strip() == '':
        return jsonify(message=_('Invalid item name.')), 400
    item.name = data['name']
    db.session.commit()
    return jsonify(message=_('Circuit updated.'))


@app_bp.route('/item/<int:item_id>/toggle', methods=['PATCH'])
@login_required
def toggle_item(item_id):
    item = Circuit.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    item.done = not item.done
    db.session.commit()
    return jsonify(message=_('Circuit toggled.'))


@app_bp.route('/item/<int:item_id>/delete', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = Circuit.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('Permission denied.')), 403

    db.session.delete(item)
    db.session.commit()
    return jsonify(message=_('Circuit deleted.'))


@app_bp.route('/item/clear', methods=['DELETE'])
@login_required
def clear_items():
    items = Circuit.query.with_parent(current_user).filter_by(done=True).all()
    for item in items:
        db.session.delete(item)
    db.session.commit()
    return jsonify(message=_('All clear!'))
