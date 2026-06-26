from app.models.models import db, LeaveRequest, LeaveType
from app.repositories.base_repository import BaseRepository
from datetime import datetime


class LeaveRepository(BaseRepository):

    def get_all(self):
        return LeaveRequest.query.order_by(LeaveRequest.applied_on.desc()).all()

    def get_by_id(self, leave_id):
        return LeaveRequest.query.get_or_404(leave_id)

    def get_pending(self):
        return LeaveRequest.query.filter_by(status='pending').all()

    def count_pending(self):
        return LeaveRequest.query.filter_by(status='pending').count()

    def get_by_employee(self, employee_id):
        return (LeaveRequest.query
                .filter_by(employee_id=employee_id)
                .order_by(LeaveRequest.applied_on.desc())
                .all())

    def create(self, data: dict):
        leave = LeaveRequest(**data)
        return self.save(leave)

    def approve(self, leave, approved_by_user_id, remarks=''):
        leave.status      = 'approved'
        leave.approved_by = approved_by_user_id
        leave.approved_on = datetime.utcnow()
        leave.remarks     = remarks
        self.commit()
        return leave

    def reject(self, leave, approved_by_user_id, remarks=''):
        leave.status      = 'rejected'
        leave.approved_by = approved_by_user_id
        leave.approved_on = datetime.utcnow()
        leave.remarks     = remarks
        self.commit()
        return leave

    def void(self, leave, voided_by_user_id, remarks=''):
        leave.status      = 'voided'
        leave.approved_by = voided_by_user_id
        leave.approved_on = datetime.utcnow()
        leave.remarks     = remarks
        self.commit()
        return leave


class LeaveTypeRepository(BaseRepository):

    def get_all(self):
        return LeaveType.query.all()

    def get_by_id(self, lt_id):
        return LeaveType.query.get_or_404(lt_id)

    def create(self, name, days_allowed, is_paid=True, description=''):
        lt = LeaveType(name=name, days_allowed=days_allowed,
                       is_paid=is_paid, description=description)
        return self.save(lt)
