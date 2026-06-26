from datetime import date
from app.repositories.bd_repository import (
    LeadRepository, ClientRepository,
    OpportunityRepository, ActivityRepository
)
from app.models.models import User


class BDService:
    """All Business Development logic lives here."""

    def __init__(self):
        self.lead_repo    = LeadRepository()
        self.client_repo  = ClientRepository()
        self.opp_repo     = OpportunityRepository()
        self.activity_repo= ActivityRepository()

    # ── Dashboard ─────────────────────────────────────────────────────

    def get_dashboard_data(self) -> dict:
        return {
            'total_leads':        self.lead_repo.count_all(),
            'new_leads':          self.lead_repo.count_by_status('new'),
            'qualified_leads':    self.lead_repo.count_by_status('qualified'),
            'total_clients':      self.client_repo.count_active(),
            'pipeline_value':     self.opp_repo.pipeline_value(),
            'won_value':          self.opp_repo.won_value(),
            'won_deals':          self.opp_repo.count_won(),
            'active_opportunities':self.opp_repo.count_active(),
            'pending_activities': self.activity_repo.count_pending(),
            'stage_counts':       self.opp_repo.count_by_stage(),
            'recent_leads':       self.lead_repo.get_recent(5),
            'opportunities':      self.opp_repo.get_recent(5),
        }

    # ── Leads ─────────────────────────────────────────────────────────

    def get_all_leads(self):
        return self.lead_repo.get_all()

    def get_all_users(self):
        return User.query.all()

    def create_lead(self, form_data: dict):
        nf = form_data.get('next_followup')
        data = {
            'company_name': form_data['company_name'],
            'contact_name': form_data.get('contact_name'),
            'email':        form_data.get('email'),
            'phone':        form_data.get('phone'),
            'source':       form_data.get('source'),
            'industry':     form_data.get('industry'),
            'status':       'new',
            'assigned_to':  form_data.get('assigned_to') or None,
            'notes':        form_data.get('notes'),
            'next_followup':date.fromisoformat(nf) if nf else None,
        }
        return self.lead_repo.create(data)

    def update_lead_status(self, lead_id, status, notes=None):
        lead = self.lead_repo.get_by_id(lead_id)
        return self.lead_repo.update_status(lead, status, notes)

    # ── Clients ───────────────────────────────────────────────────────

    def get_all_clients(self):
        return self.client_repo.get_all()

    def create_client(self, form_data: dict):
        client_data = {
            'company_name': form_data['company_name'],
            'industry':     form_data.get('industry'),
            'website':      form_data.get('website'),
            'address':      form_data.get('address'),
        }
        contact_data = {
            'name':        form_data['contact_name'],
            'designation': form_data.get('contact_designation'),
            'email':       form_data.get('contact_email'),
            'phone':       form_data.get('contact_phone'),
        }
        return self.client_repo.create(client_data, contact_data)

    # ── Pipeline / Opportunities ───────────────────────────────────────

    def get_pipeline_data(self) -> dict:
        all_opps = self.opp_repo.get_all()
        stages   = ['prospect', 'proposal', 'negotiation', 'won', 'lost']
        return {s: [o for o in all_opps if o.stage == s] for s in stages}

    def create_opportunity(self, form_data: dict):
        ecd = form_data.get('expected_close_date')
        data = {
            'title':               form_data['title'],
            'client_id':           form_data.get('client_id') or None,
            'lead_id':             form_data.get('lead_id')   or None,
            'stage':               form_data.get('stage', 'prospect'),
            'value':               float(form_data.get('value') or 0),
            'expected_close_date': date.fromisoformat(ecd) if ecd else None,
            'probability':         int(form_data.get('probability') or 0),
            'assigned_to':         form_data.get('assigned_to') or None,
            'description':         form_data.get('description'),
        }
        return self.opp_repo.create(data)

    def move_opportunity(self, opp_id, stage, reason=''):
        opp = self.opp_repo.get_by_id(opp_id)
        return self.opp_repo.move_stage(opp, stage, reason)

    # ── Activities ────────────────────────────────────────────────────

    def get_all_activities(self):
        return self.activity_repo.get_all()

    def create_activity(self, form_data: dict):
        from datetime import datetime
        sat = form_data.get('scheduled_at')
        data = {
            'type':           form_data['type'],
            'subject':        form_data['subject'],
            'lead_id':        form_data.get('lead_id')   or None,
            'client_id':      form_data.get('client_id') or None,
            'assigned_to':    form_data.get('assigned_to') or None,
            'scheduled_at':   datetime.fromisoformat(sat) if sat else None,
            'notes':          form_data.get('notes'),
        }
        return self.activity_repo.create(data)

    def complete_activity(self, activity_id):
        act = self.activity_repo.get_by_id(activity_id)
        return self.activity_repo.mark_complete(act)
