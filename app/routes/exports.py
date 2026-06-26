"""
exports.py
==========
All Excel download endpoints — one place, all reports.
"""
import calendar
from flask import Blueprint, make_response, request
from flask_login import login_required
from app.utils.rbac import roles_required, hr_only, bd_only
from app.utils.excel_exporter import (
    payroll_report, epf_report, esic_report,
    attendance_report, leave_report,
    employee_master, bd_pipeline_report
)
from app.repositories.payroll_repository import (
    PayrollRepository, EPFRepository, ESICRepository
)
from app.repositories.leave_repository import LeaveRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.bd_repository import OpportunityRepository
from app.services.attendance_service import AttendanceService
from datetime import date

exports_bp = Blueprint('exports', __name__)


def _xlsx_response(data: bytes, filename: str):
    """Wrap bytes in a proper Excel HTTP response."""
    response = make_response(data)
    response.headers['Content-Type'] = \
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = \
        f'attachment; filename={filename}'
    return response


# ── Payroll ───────────────────────────────────────────────────────────────────

@exports_bp.route('/exports/payroll')
@login_required
@hr_only
def export_payroll():
    month     = request.args.get('month', date.today().month, type=int)
    year      = request.args.get('year',  date.today().year,  type=int)
    payrolls  = PayrollRepository().get_by_month_year(month, year)
    month_name= calendar.month_name[month]
    data      = payroll_report(payrolls, month, year)
    return _xlsx_response(data,
        f'Payroll_Report_{month_name}_{year}.xlsx')


# ── EPF ───────────────────────────────────────────────────────────────────────

@exports_bp.route('/exports/epf')
@login_required
@hr_only
def export_epf():
    month   = request.args.get('month', date.today().month, type=int)
    year    = request.args.get('year',  date.today().year,  type=int)
    records = EPFRepository().get_by_month_year(month, year)
    month_name = calendar.month_name[month]
    data    = epf_report(records, month, year)
    return _xlsx_response(data,
        f'EPF_Report_{month_name}_{year}.xlsx')


# ── ESIC ──────────────────────────────────────────────────────────────────────

@exports_bp.route('/exports/esic')
@login_required
@hr_only
def export_esic():
    month   = request.args.get('month', date.today().month, type=int)
    year    = request.args.get('year',  date.today().year,  type=int)
    records = ESICRepository().get_by_month_year(month, year)
    month_name = calendar.month_name[month]
    data    = esic_report(records, month, year)
    return _xlsx_response(data,
        f'ESIC_Report_{month_name}_{year}.xlsx')


# ── Attendance ────────────────────────────────────────────────────────────────

@exports_bp.route('/exports/attendance')
@login_required
@hr_only
def export_attendance():
    month       = request.args.get('month', date.today().month, type=int)
    year        = request.args.get('year',  date.today().year,  type=int)
    svc         = AttendanceService()
    report_data = svc.get_monthly_report(month, year)
    month_name  = calendar.month_name[month]
    data        = attendance_report(report_data, month, year)
    return _xlsx_response(data,
        f'Attendance_Report_{month_name}_{year}.xlsx')


# ── Leave ─────────────────────────────────────────────────────────────────────

@exports_bp.route('/exports/leave')
@login_required
@hr_only
def export_leave():
    leaves = LeaveRepository().get_all()
    data   = leave_report(leaves)
    return _xlsx_response(data, 'Leave_Report.xlsx')


# ── Employee Master ───────────────────────────────────────────────────────────

@exports_bp.route('/exports/employees')
@login_required
@roles_required('admin')
def export_employees():
    employees = EmployeeRepository().get_all()
    data      = employee_master(employees)
    return _xlsx_response(data, 'Employee_Master.xlsx')


# ── BD Pipeline ───────────────────────────────────────────────────────────────

@exports_bp.route('/exports/pipeline')
@login_required
@bd_only
def export_pipeline():
    opportunities = OpportunityRepository().get_all()
    data          = bd_pipeline_report(opportunities)
    return _xlsx_response(data, 'BD_Pipeline_Report.xlsx')
