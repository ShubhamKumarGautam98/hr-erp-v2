from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.services.employee_service import EmployeeService
from app.utils.rbac import hr_only

employees_bp = Blueprint('employees', __name__)
_svc = EmployeeService()


@employees_bp.route('/employees')
@login_required
@hr_only
def index():
    return render_template('employees/index.html',
                           employees=_svc.get_all_employees())


@employees_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@hr_only
def add():
    if request.method == 'POST':
        emp = _svc.create_employee(request.form)
        flash(f'Employee {emp.full_name} added successfully!', 'success')
        return redirect(url_for('employees.index'))
    return render_template('employees/add.html',
                           departments=_svc.get_all_departments(),
                           designations=_svc.get_all_designations())


@employees_bp.route('/employees/<int:id>')
@login_required
@hr_only
def view(id):
    return render_template('employees/view.html',
                           emp=_svc.get_employee(id))


@employees_bp.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@hr_only
def edit(id):
    if request.method == 'POST':
        _svc.update_employee(id, request.form)
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees.view', id=id))
    return render_template('employees/edit.html',
                           emp=_svc.get_employee(id),
                           departments=_svc.get_all_departments(),
                           designations=_svc.get_all_designations())
