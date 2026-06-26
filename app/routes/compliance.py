from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from app.services.compliance_service import ComplianceService
from app.utils.rbac import hr_only
from datetime import date

compliance_bp = Blueprint('compliance', __name__)
_svc = ComplianceService()


@compliance_bp.route('/compliance')
@login_required
@hr_only
def index():
    month = request.args.get('month', date.today().month, type=int)
    year  = request.args.get('year',  date.today().year,  type=int)
    return render_template('compliance/index.html',
                           **_svc.get_dashboard_data(month, year))


@compliance_bp.route('/compliance/epf-ecr')
@login_required
@hr_only
def epf_ecr():
    month   = request.args.get('month', date.today().month, type=int)
    year    = request.args.get('year',  date.today().year,  type=int)
    content = _svc.generate_ecr(month, year)
    response = make_response(content)
    response.headers['Content-Type']        = 'text/plain'
    response.headers['Content-Disposition'] = (
        f'attachment; filename=EPF_ECR_{month}_{year}.txt'
    )
    return response
