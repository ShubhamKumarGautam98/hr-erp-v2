from app.repositories.employee_repository import EmployeeRepository
from app.repositories.leave_repository import LeaveRepository
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.payroll_repository import PayrollRepository
from app.repositories.bd_repository import LeadRepository, OpportunityRepository
from app.services.attendance_service import AttendanceService
from app.services.bd_service import BDService
from datetime import date


class DashboardService:
    """Aggregates data from all modules for the main dashboard."""

    def __init__(self):
        self.employee_repo   = EmployeeRepository()
        self.leave_repo      = LeaveRepository()
        self.attendance_repo = AttendanceRepository()
        self.payroll_repo    = PayrollRepository()
        self.lead_repo       = LeadRepository()
        self.opp_repo        = OpportunityRepository()
        self.attendance_svc  = AttendanceService()
        self.bd_svc          = BDService()

    def get_data(self) -> dict:
        today = date.today()
        return {
            # HR stats
            'total_employees':       self.employee_repo.count_active(),
            'present_today':         self.attendance_repo.count_today_present(),
            'pending_leaves':        self.leave_repo.count_pending(),
            'current_month_payroll': len(self.payroll_repo.get_by_month_year(
                                         today.month, today.year)),
            # BD stats
            'total_leads':           self.lead_repo.count_all(),
            'active_opportunities':  self.opp_repo.count_active(),
            'won_deals':             self.opp_repo.count_won(),
            'pipeline_value':        self.opp_repo.pipeline_value(),
            # Charts
            'attendance_data':       self.attendance_svc.get_last7_days_chart_data(),
            'dept_data':             self._dept_headcount(),
            # Recent records
            'recent_leaves':         self.leave_repo.get_all()[:5],
            'recent_leads':          self.lead_repo.get_recent(5),
            'today':                 today,
        }

    def _dept_headcount(self):
        from app.repositories.employee_repository import DepartmentRepository
        return DepartmentRepository().headcount_per_department()
