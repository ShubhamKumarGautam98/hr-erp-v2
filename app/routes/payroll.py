import calendar
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app.services.payroll_service import PayrollService
from app.utils.pdf_generator import generate_payslip_pdf
from app.utils.rbac import roles_required
from datetime import date

payroll_bp = Blueprint('payroll', __name__)
_svc = PayrollService()


@payroll_bp.route('/payroll')
@login_required
@roles_required('admin', 'hr_manager')
def index():
    month = request.args.get('month', date.today().month, type=int)
    year  = request.args.get('year',  date.today().year,  type=int)
    return render_template('payroll/index.html',
                           payrolls=_svc.get_payrolls(month, year),
                           month=month, year=year)


@payroll_bp.route('/payroll/generate', methods=['POST'])
@login_required
@roles_required('admin', 'hr_manager')
def generate():
    month = int(request.form['month'])
    year  = int(request.form['year'])
    count = _svc.generate_payroll(month, year)
    flash(f'Payroll generated for {count} employee(s)!', 'success')
    return redirect(url_for('payroll.index', month=month, year=year))


@payroll_bp.route('/payroll/<int:id>/payslip')
@login_required
@roles_required('admin', 'hr_manager', 'employee')
def payslip(id):
    p   = _svc.get_payslip(id)
    emp = p.employee

    # Employee can only view their own payslip
    if current_user.role == 'employee':
        user_emp = _svc.get_employee_for_user(current_user)
        if not user_emp or user_emp.id != emp.id:
            return render_template('errors/403.html'), 403

    return render_template('payroll/payslip.html',
                           p=p, emp=emp,
                           month_name=calendar.month_name[p.month])


@payroll_bp.route('/payroll/<int:id>/payslip/pdf')
@login_required
@roles_required('admin', 'hr_manager', 'employee')
def payslip_pdf(id):
    p   = _svc.get_payslip(id)
    emp = p.employee

    # Employee can only download their own payslip
    if current_user.role == 'employee':
        user_emp = _svc.get_employee_for_user(current_user)
        if not user_emp or user_emp.id != emp.id:
            return render_template('errors/403.html'), 403

    pdf      = generate_payslip_pdf(p, emp)
    response = make_response(pdf)
    response.headers['Content-Type']        = 'application/pdf'
    response.headers['Content-Disposition'] = (
        f'attachment; filename=payslip_{emp.employee_code}_{p.month}_{p.year}.pdf'
    )
    return response


@payroll_bp.route('/payroll/my-payslips')
@login_required
@roles_required('employee')
def my_payslips():
    """Employee sees list of their own payslips."""
    emp      = _svc.get_employee_for_user(current_user)
    payslips = _svc.get_payrolls_for_employee(emp.id) if emp else []
    return render_template('payroll/my_payslips.html',
                           payslips=payslips, emp=emp)
