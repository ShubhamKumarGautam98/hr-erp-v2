from datetime import date
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.employee_repository import EmployeeRepository


class AttendanceService:

    def __init__(self):
        self.attendance_repo = AttendanceRepository()
        self.employee_repo   = EmployeeRepository()

    def get_today_attendance(self):
        today   = date.today()
        records = self.attendance_repo.get_by_date(today)
        return {r.employee_id: r for r in records}

    def get_active_employees(self):
        return self.employee_repo.get_all_active()

    def get_present_today_count(self):
        return self.attendance_repo.count_today_present()

    def get_employee_for_user(self, user):
        if user.employee_id:
            return self.employee_repo.get_by_id(user.employee_id)
        return None

    def get_employee_monthly_attendance(self, employee_id, month, year):
        return self.attendance_repo.get_by_employee_month(employee_id, month, year)

    def get_last7_days_chart_data(self):
        from datetime import timedelta
        today = date.today()
        chart = []
        for i in range(6, -1, -1):
            d       = today - timedelta(days=i)
            records = self.attendance_repo.get_by_date(d)
            chart.append({
                'date':    d.strftime('%d %b'),
                'present': sum(1 for r in records if r.status == 'present'),
                'absent':  sum(1 for r in records if r.status == 'absent'),
            })
        return chart

    def get_monthly_report(self, month, year):
        employees = self.employee_repo.get_all_active()
        return self.attendance_repo.monthly_summary(employees, month, year)

    def mark_attendance(self, form_data, target_date=None):
        target_date  = target_date or date.today()
        employee_ids = form_data.getlist('employee_id')
        entries = [
            {
                'employee_id': int(emp_id),
                'date':        target_date,
                'status':      form_data.get(f'status_{emp_id}', 'absent'),
            }
            for emp_id in employee_ids
        ]
        self.attendance_repo.bulk_upsert_commit(entries)
