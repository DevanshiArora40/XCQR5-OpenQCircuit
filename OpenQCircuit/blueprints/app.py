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


def qasmConverter(circuit):
    gates = ["H", "Y", "Z", "P"]
    qasm_code = "OPENQASM 2.0;\ninclude \"qelib1.inc\";"
    wires = [i for i in circuit.split('\n')]
    classical_wires = len(wires)
    classical_pointer = 0
    instr = []
    for i in wires:
        i = i.split("-")
        while("" in i):
            i.remove("")
        instr.append(i)
    qasm_code += "\nqreg q[" + str(len(wires)) + "];\ncreg c[" + str(len(wires)) + "];\n"

    for idx in range(len(instr[0])):
        for idy in range(len(instr)):
            if instr[idy][idx] in gates:
                qasm_code += "\n" + ( "s" if instr[idy][idx].lower() == "p" else instr[idy][idx].lower()) + " q[" + str(idy) + "];"
            if instr[idy][idx][0] == "X" or instr[idy][idx][0] == "T":
                if len(instr[idy][idx]) > 2:
                    if instr[idy][idx][-1] == "0":
                        for i in range(idy + 1, len(instr)):
                            if instr[i][idx][-1] == "1" and instr[i][idx][-3] == instr[idy][idx][-3] :
                                qasm_code += "\ncx q[" + str(idy) + "], q[" + str(i) +"];" if instr[idy][idx][0] == "X" else "\ncr8 q[" + str(idy) + "], q[" + str(i) +"];"

                else:
                    qasm_code += "\n" + (instr[idy][idx][0].lower() if instr[idy][idx][0] == "X" else "r8") + " q[" + str(idy) + "];"
            if instr[idy][idx] == "M":
                if classical_pointer <= classical_wires:
                    qasm_code += "\nmeasure q[" + str(idy) + "] -> c[" + str(classical_pointer) + "];"
                    classical_pointer += 1

    return qasm_code


@app_bp.route('/circuit', methods=['GET', 'POST'])
@login_required
def launch():
    if request.method == 'POST':
        data = request.get_json()
        item_id = data['itemID']
        item = Circuit.query.get_or_404(item_id)
        if current_user != item.author:
            return jsonify(message=_('Permission denied.')), 403
        qasmCircuit = qasmConverter(item.body)
        return render_template('_circuit.html', circuit=item, qasmCir = qasmCircuit)
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
    qasmCircuit = qasmConverter(item.body)
    db.session.commit()
    return jsonify(message=_('Circuit updated.'), qasmCir = qasmCircuit)

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
