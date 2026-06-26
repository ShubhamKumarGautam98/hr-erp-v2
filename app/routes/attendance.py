from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.attendance_service import AttendanceService
from app.utils.rbac import roles_required
from datetime import date

attendance_bp = Blueprint('attendance', __name__)
_svc = AttendanceService()


@attendance_bp.route('/attendance')
@login_required
@roles_required('admin', 'hr_manager')
def index():
    """HR marks attendance for all employees."""
    return render_template('attendance/index.html',
                           employees=_svc.get_active_employees(),
                           attendance_today=_svc.get_today_attendance(),
                           today=date.today())


@attendance_bp.route('/attendance/mark', methods=['POST'])
@login_required
@roles_required('admin', 'hr_manager')
def mark():
    _svc.mark_attendance(request.form)
    flash('Attendance marked successfully!', 'success')
    return redirect(url_for('attendance.index'))


@attendance_bp.route('/attendance/report')
@login_required
@roles_required('admin', 'hr_manager')
def report():
    month = request.args.get('month', date.today().month, type=int)
    year  = request.args.get('year',  date.today().year,  type=int)
    return render_template('attendance/report.html',
                           report_data=_svc.get_monthly_report(month, year),
                           month=month, year=year)


@attendance_bp.route('/attendance/my-attendance')
@login_required
@roles_required('employee')
def my_attendance():
    """Employee sees only their own attendance."""
    month = request.args.get('month', date.today().month, type=int)
    year  = request.args.get('year',  date.today().year,  type=int)
    emp   = _svc.get_employee_for_user(current_user)
    records = _svc.get_employee_monthly_attendance(emp.id, month, year) if emp else []
    return render_template('attendance/my_attendance.html',
                           records=records, month=month,
                           year=year, emp=emp)
