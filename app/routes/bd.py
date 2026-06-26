from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.services.bd_service import BDService
from app.utils.rbac import bd_only

bd_bp = Blueprint('bd', __name__)
_svc  = BDService()


@bd_bp.route('/bd')
@login_required
@bd_only
def index():
    return render_template('bd/index.html', **_svc.get_dashboard_data())


@bd_bp.route('/bd/leads')
@login_required
@bd_only
def leads():
    return render_template('bd/leads.html',
                           leads=_svc.get_all_leads(),
                           users=_svc.get_all_users())


@bd_bp.route('/bd/leads/add', methods=['GET', 'POST'])
@login_required
@bd_only
def add_lead():
    if request.method == 'POST':
        _svc.create_lead(request.form)
        flash('Lead added successfully!', 'success')
        return redirect(url_for('bd.leads'))
    return render_template('bd/add_lead.html',
                           users=_svc.get_all_users())


@bd_bp.route('/bd/leads/<int:id>/update-status', methods=['POST'])
@login_required
@bd_only
def update_lead_status(id):
    _svc.update_lead_status(id, request.form['status'],
                            request.form.get('notes'))
    flash('Lead status updated!', 'success')
    return redirect(url_for('bd.leads'))


@bd_bp.route('/bd/clients')
@login_required
@bd_only
def clients():
    return render_template('bd/clients.html',
                           clients=_svc.get_all_clients())


@bd_bp.route('/bd/clients/add', methods=['GET', 'POST'])
@login_required
@bd_only
def add_client():
    if request.method == 'POST':
        _svc.create_client(request.form)
        flash('Client added successfully!', 'success')
        return redirect(url_for('bd.clients'))
    return render_template('bd/add_client.html')


@bd_bp.route('/bd/pipeline')
@login_required
@bd_only
def pipeline():
    return render_template('bd/pipeline.html',
                           pipeline_data=_svc.get_pipeline_data(),
                           stages=['prospect','proposal','negotiation','won','lost'],
                           clients=_svc.get_all_clients(),
                           leads=_svc.get_all_leads(),
                           users=_svc.get_all_users())


@bd_bp.route('/bd/pipeline/add', methods=['GET', 'POST'])
@login_required
@bd_only
def add_opportunity():
    if request.method == 'POST':
        _svc.create_opportunity(request.form)
        flash('Opportunity added!', 'success')
        return redirect(url_for('bd.pipeline'))
    return render_template('bd/add_opportunity.html',
                           clients=_svc.get_all_clients(),
                           leads=_svc.get_all_leads(),
                           users=_svc.get_all_users())


@bd_bp.route('/bd/pipeline/<int:id>/move', methods=['POST'])
@login_required
@bd_only
def move_opportunity(id):
    _svc.move_opportunity(id, request.form['stage'],
                          request.form.get('reason', ''))
    flash('Opportunity updated!', 'success')
    return redirect(url_for('bd.pipeline'))


@bd_bp.route('/bd/activities')
@login_required
@bd_only
def activities():
    return render_template('bd/activities.html',
                           activities=_svc.get_all_activities(),
                           leads=_svc.get_all_leads(),
                           clients=_svc.get_all_clients(),
                           users=_svc.get_all_users())


@bd_bp.route('/bd/activities/add', methods=['POST'])
@login_required
@bd_only
def add_activity():
    _svc.create_activity(request.form)
    flash('Activity scheduled!', 'success')
    return redirect(url_for('bd.activities'))


@bd_bp.route('/bd/activities/<int:id>/complete', methods=['POST'])
@login_required
@bd_only
def complete_activity(id):
    _svc.complete_activity(id)
    flash('Activity marked complete!', 'success')
    return redirect(url_for('bd.activities'))
