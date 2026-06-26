from app.models.models import db, Attendance
from app.repositories.base_repository import BaseRepository
from datetime import date, timedelta


class AttendanceRepository(BaseRepository):

    def get_by_date(self, target_date: date):
        return Attendance.query.filter_by(date=target_date).all()

    def get_by_employee_and_date(self, employee_id, target_date: date):
        return Attendance.query.filter_by(
            employee_id=employee_id, date=target_date
        ).first()

    def get_by_employee_month(self, employee_id, month: int, year: int):
        return Attendance.query.filter(
            Attendance.employee_id == employee_id,
            db.extract('month', Attendance.date) == month,
            db.extract('year',  Attendance.date) == year,
        ).all()

    def count_today_present(self):
        return Attendance.query.filter_by(
            date=date.today(), status='present'
        ).count()

    def get_last_n_days(self, n: int = 7):
        """Returns attendance records for the last n working days."""
        today     = date.today()
        from_date = today - timedelta(days=n)
        return (Attendance.query
                .filter(Attendance.date >= from_date,
                        Attendance.date <= today)
                .all())

    def upsert(self, employee_id, target_date: date, status: str):
        """Insert or update attendance for a single employee on a date."""
        record = self.get_by_employee_and_date(employee_id, target_date)
        if record:
            record.status = status
        else:
            record = Attendance(employee_id=employee_id,
                                date=target_date, status=status)
            db.session.add(record)
        # caller must commit after batch upserts
        return record

    def bulk_upsert_commit(self, entries: list):
        """entries = [{'employee_id': x, 'date': d, 'status': s}, ...]"""
        for e in entries:
            self.upsert(e['employee_id'], e['date'], e['status'])
        self.commit()

    def monthly_summary(self, employees, month: int, year: int):
        """Returns a list of dicts with per-employee monthly attendance counts."""
        rows = []
        for emp in employees:
            records = self.get_by_employee_month(emp.id, month, year)
            rows.append({
                'employee': emp,
                'present':  sum(1 for r in records if r.status == 'present'),
                'absent':   sum(1 for r in records if r.status == 'absent'),
                'half_day': sum(1 for r in records if r.status == 'half_day'),
                'wfh':      sum(1 for r in records if r.status == 'wfh'),
                'total':    len(records),
            })
        return rows
