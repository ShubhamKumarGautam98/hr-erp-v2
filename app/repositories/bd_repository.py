from app.models.models import db, Lead, Client, Contact, Opportunity, Activity, User
from app.repositories.base_repository import BaseRepository


class LeadRepository(BaseRepository):

    def get_all(self):
        return Lead.query.order_by(Lead.created_at.desc()).all()

    def get_by_id(self, lead_id):
        return Lead.query.get_or_404(lead_id)

    def count_all(self):
        return Lead.query.count()

    def count_by_status(self, status):
        return Lead.query.filter_by(status=status).count()

    def get_recent(self, limit=5):
        return Lead.query.order_by(Lead.created_at.desc()).limit(limit).all()

    def create(self, data: dict):
        lead = Lead(**data)
        return self.save(lead)

    def update_status(self, lead, status, notes=None):
        lead.status = status
        if notes:
            lead.notes = notes
        self.commit()
        return lead


class ClientRepository(BaseRepository):

    def get_all(self):
        return Client.query.order_by(Client.company_name).all()

    def get_by_id(self, client_id):
        return Client.query.get_or_404(client_id)

    def count_active(self):
        return Client.query.filter_by(status='active').count()

    def create(self, client_data: dict, contact_data: dict):
        client = Client(**client_data)
        self.save(client)          # gets client.id
        contact = Contact(client_id=client.id, **contact_data, is_primary=True)
        db.session.add(contact)
        self.commit()
        return client


class OpportunityRepository(BaseRepository):

    STAGES = ['prospect', 'proposal', 'negotiation', 'won', 'lost']

    def get_all(self):
        return Opportunity.query.order_by(Opportunity.created_at.desc()).all()

    def get_by_id(self, opp_id):
        return Opportunity.query.get_or_404(opp_id)

    def get_recent(self, limit=5):
        return Opportunity.query.order_by(Opportunity.created_at.desc()).limit(limit).all()

    def get_by_stage(self, stage):
        return Opportunity.query.filter_by(stage=stage).all()

    def count_active(self):
        return Opportunity.query.filter(
            Opportunity.stage.in_(['prospect', 'proposal', 'negotiation'])
        ).count()

    def count_won(self):
        return Opportunity.query.filter_by(stage='won').count()

    def count_by_stage(self):
        return {s: Opportunity.query.filter_by(stage=s).count()
                for s in self.STAGES}

    def pipeline_value(self):
        result = (db.session.query(db.func.sum(Opportunity.value))
                  .filter(Opportunity.stage.in_(
                      ['prospect', 'proposal', 'negotiation']))
                  .scalar())
        return result or 0.0

    def won_value(self):
        result = (db.session.query(db.func.sum(Opportunity.value))
                  .filter_by(stage='won')
                  .scalar())
        return result or 0.0

    def create(self, data: dict):
        opp = Opportunity(**data)
        return self.save(opp)

    def move_stage(self, opportunity, stage, reason=''):
        opportunity.stage = stage
        if stage in ('won', 'lost'):
            opportunity.win_loss_reason = reason
        self.commit()
        return opportunity


class ActivityRepository(BaseRepository):

    def get_all(self):
        return Activity.query.order_by(Activity.scheduled_at.desc()).all()

    def get_by_id(self, activity_id):
        return Activity.query.get_or_404(activity_id)

    def count_pending(self):
        return Activity.query.filter_by(completed=False).count()

    def create(self, data: dict):
        act = Activity(**data)
        return self.save(act)

    def mark_complete(self, activity):
        activity.completed = True
        self.commit()
        return activity
