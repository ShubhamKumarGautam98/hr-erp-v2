from app.models.models import db, Payroll, EPFRecord, ESICRecord
from app.repositories.base_repository import BaseRepository


class PayrollRepository(BaseRepository):

    def get_by_month_year(self, month: int, year: int):
        return Payroll.query.filter_by(month=month, year=year).all()

    def get_by_employee_month_year(self, employee_id, month: int, year: int):
        return Payroll.query.filter_by(
            employee_id=employee_id, month=month, year=year
        ).first()

    def get_by_id(self, payroll_id):
        return Payroll.query.get_or_404(payroll_id)

    def create(self, data: dict):
        p = Payroll(**data)
        return self.save(p)

    def exists(self, employee_id, month: int, year: int) -> bool:
        return self.get_by_employee_month_year(employee_id, month, year) is not None


class EPFRepository(BaseRepository):

    def get_by_month_year(self, month: int, year: int):
        return EPFRecord.query.filter_by(month=month, year=year).all()

    def create(self, data: dict):
        rec = EPFRecord(**data)
        return self.save(rec)

    def totals(self, month: int, year: int) -> dict:
        records = self.get_by_month_year(month, year)
        return {
            'epf_employee': sum(r.epf_employee for r in records),
            'epf_employer': sum(r.epf_employer for r in records),
            'eps_employer': sum(r.eps_employer for r in records),
            'total_epf':    sum(r.total_epf    for r in records),
        }


class ESICRepository(BaseRepository):

    def get_by_month_year(self, month: int, year: int):
        return ESICRecord.query.filter_by(month=month, year=year).all()

    def create(self, data: dict):
        rec = ESICRecord(**data)
        return self.save(rec)

    def totals(self, month: int, year: int) -> dict:
        records = self.get_by_month_year(month, year)
        return {
            'esic_employee': sum(r.esic_employee for r in records),
            'esic_employer': sum(r.esic_employer for r in records),
            'total_esic':    sum(r.total_esic    for r in records),
        }
