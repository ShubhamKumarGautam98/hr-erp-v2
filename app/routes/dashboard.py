from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.dashboard_service import DashboardService
from app.services.bd_service import BDService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    role = current_user.role

    if role == 'admin':
        return render_template('dashboard/index.html',
                               **DashboardService().get_data())

    if role == 'hr_manager':
        return render_template('dashboard/hr_dashboard.html',
                               **DashboardService().get_data())

    if role in ('bd_manager', 'bd_executive'):
        return render_template('bd/index.html',
                               **BDService().get_dashboard_data())

    if role == 'employee':
        return render_template('dashboard/employee_dashboard.html',
                               user=current_user)

    # fallback
    return render_template('dashboard/index.html',
                           **DashboardService().get_data())
