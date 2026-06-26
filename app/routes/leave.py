from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.leave_service import LeaveService
from app.utils.rbac import roles_required

leave_bp = Blueprint('leave', __name__)
_svc = LeaveService()


@leave_bp.route('/leave')
@login_required
@roles_required('admin', 'hr_manager')
def index():
    """HR sees all leave requests."""
    return render_template('leave/index.html',
                           leaves=_svc.get_all_leaves())


@leave_bp.route('/leave/apply', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'hr_manager', 'employee')
def apply():
    """HR applies on behalf of anyone; employee applies for themselves."""
    if request.method == 'POST':
        try:
            _svc.apply_leave(request.form)
            flash('Leave request submitted successfully!', 'success')
            # Employee goes to their own view; HR goes to full list
            if current_user.role == 'employee':
                return redirect(url_for('leave.my_leaves'))
            return redirect(url_for('leave.index'))
        except ValueError as e:
            flash(str(e), 'danger')

    # Employee can only apply for themselves
    if current_user.role == 'employee':
        emp = _svc.get_employee_for_user(current_user)
        employees = [emp] if emp else []
    else:
        employees = _svc.get_active_employees()

    return render_template('leave/apply.html',
                           employees=employees,
                           leave_types=_svc.get_all_leave_types(),
                           is_employee=(current_user.role == 'employee'))


@leave_bp.route('/leave/my-leaves')
@login_required
@roles_required('employee')
def my_leaves():
    """Employee sees only their own leave history."""
    emp    = _svc.get_employee_for_user(current_user)
    leaves = _svc.get_leaves_for_employee(emp.id) if emp else []
    return render_template('leave/my_leaves.html',
                           leaves=leaves, emp=emp)


@leave_bp.route('/leave/<int:id>/approve', methods=['POST'])
@login_required
@roles_required('admin', 'hr_manager')
def approve(id):
    try:
        _svc.approve_leave(id, current_user.id,
                           request.form.get('remarks', ''))
        flash('Leave approved successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    return redirect(url_for('leave.index'))


@leave_bp.route('/leave/<int:id>/reject', methods=['POST'])
@login_required
@roles_required('admin', 'hr_manager')
def reject(id):
    try:
        _svc.reject_leave(id, current_user.id,
                          request.form.get('remarks', ''))
        flash('Leave rejected.', 'warning')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('leave.index'))


@leave_bp.route('/leave/<int:id>/void', methods=['POST'])
@login_required
@roles_required('admin', 'hr_manager')
def void(id):
    """HR/Admin can void any leave regardless of status."""
    try:
        _svc.void_leave(id, current_user.id,
                        request.form.get('remarks', ''))
        flash('Leave has been voided.', 'warning')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('leave.index'))


@leave_bp.route('/leave/<int:id>/cancel', methods=['POST'])
@login_required
@roles_required('employee')
def cancel(id):
    """Employee can cancel only their own pending leaves."""
    try:
        _svc.cancel_leave(id, current_user)
        flash('Your leave request has been cancelled.', 'warning')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('leave.my_leaves'))
