from datetime import date
from app.repositories.leave_repository import LeaveRepository, LeaveTypeRepository
from app.repositories.employee_repository import EmployeeRepository


class LeaveService:
    """Handles leave application, approval workflow, and balance logic."""

    def __init__(self):
        self.leave_repo      = LeaveRepository()
        self.leave_type_repo = LeaveTypeRepository()
        self.employee_repo   = EmployeeRepository()

    # ── Reads ─────────────────────────────────────────────────────────

    def get_all_leaves(self):
        return self.leave_repo.get_all()

    def get_pending_count(self):
        return self.leave_repo.count_pending()

    def get_all_leave_types(self):
        return self.leave_type_repo.get_all()

    def get_active_employees(self):
        return self.employee_repo.get_all_active()

    def get_employee_for_user(self, user):
        """Returns the Employee record linked to a User account."""
        if user.employee_id:
            return self.employee_repo.get_by_id(user.employee_id)
        return None

    def get_leaves_for_employee(self, employee_id):
        return self.leave_repo.get_by_employee(employee_id)

    # ── Business Logic ────────────────────────────────────────────────

    def apply_leave(self, form_data: dict):
        from_date = date.fromisoformat(form_data['from_date'])
        to_date   = date.fromisoformat(form_data['to_date'])

        if to_date < from_date:
            raise ValueError('To date cannot be before From date.')

        days = (to_date - from_date).days + 1

        data = {
            'employee_id':   int(form_data['employee_id']),
            'leave_type_id': int(form_data['leave_type_id']),
            'from_date':     from_date,
            'to_date':       to_date,
            'days':          days,
            'reason':        form_data.get('reason', ''),
            'status':        'pending',
        }
        return self.leave_repo.create(data)

    def approve_leave(self, leave_id, approved_by_user_id, remarks=''):
        leave = self.leave_repo.get_by_id(leave_id)
        if leave.status != 'pending':
            raise ValueError('Only pending leaves can be approved.')
        return self.leave_repo.approve(leave, approved_by_user_id, remarks)

    def reject_leave(self, leave_id, approved_by_user_id, remarks=''):
        leave = self.leave_repo.get_by_id(leave_id)
        if leave.status != 'pending':
            raise ValueError('Only pending leaves can be rejected.')
        return self.leave_repo.reject(leave, approved_by_user_id, remarks)

    def void_leave(self, leave_id, voided_by_user_id, remarks=''):
        """HR/Admin voids a leave — works on any status."""
        leave = self.leave_repo.get_by_id(leave_id)
        return self.leave_repo.void(leave, voided_by_user_id, remarks)

    def cancel_leave(self, leave_id, current_user):
        """Employee cancels their own pending leave only."""
        leave = self.leave_repo.get_by_id(leave_id)
        emp   = self.get_employee_for_user(current_user)
        if not emp or leave.employee_id != emp.id:
            raise ValueError('You can only cancel your own leave requests.')
        if leave.status != 'pending':
            raise ValueError('Only pending leaves can be cancelled.')
        return self.leave_repo.void(leave, current_user.id, 'Cancelled by employee')
