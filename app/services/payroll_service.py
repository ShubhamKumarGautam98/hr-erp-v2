"""
PayrollService — EPF & ESIC rules + employee self-service
"""
from datetime import datetime
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.payroll_repository  import (
    PayrollRepository, EPFRepository, ESICRepository
)

EPF_EMPLOYEE_RATE  = 0.12
EPF_EMPLOYER_RATE  = 0.12
EPS_RATE           = 0.0833
EPF_DEPOSIT_RATE   = 0.0367
ESIC_EMPLOYEE_RATE = 0.0075
ESIC_EMPLOYER_RATE = 0.0325
EPF_WAGE_CEILING   = 15_000
PROFESSIONAL_TAX   = 200


class PayrollService:

    def __init__(self):
        self.employee_repo = EmployeeRepository()
        self.payroll_repo  = PayrollRepository()
        self.epf_repo      = EPFRepository()
        self.esic_repo     = ESICRepository()

    def get_payrolls(self, month, year):
        return self.payroll_repo.get_by_month_year(month, year)

    def get_payslip(self, payroll_id):
        return self.payroll_repo.get_by_id(payroll_id)

    def get_employee_for_user(self, user):
        if user.employee_id:
            return self.employee_repo.get_by_id(user.employee_id)
        return None

    def get_payrolls_for_employee(self, employee_id):
        from app.models.models import Payroll
        return (Payroll.query
                .filter_by(employee_id=employee_id)
                .order_by(Payroll.year.desc(), Payroll.month.desc())
                .all())

    def generate_payroll(self, month, year):
        employees = self.employee_repo.get_all_active()
        generated = 0
        for emp in employees:
            if self.payroll_repo.exists(emp.id, month, year):
                continue
            calc = self._calculate(emp)
            self._save_payroll(emp, month, year, calc)
            self._save_epf_record(emp, month, year, calc)
            self._save_esic_record(emp, month, year, calc)
            generated += 1
        return generated

    def _calculate(self, emp):
        basic = emp.basic_salary
        gross = emp.gross_salary

        epf_employee = epf_employer = eps_employer = epf_deposit = 0.0
        if emp.epf_applicable:
            epf_wage     = min(basic, EPF_WAGE_CEILING)
            epf_employee = round(epf_wage * EPF_EMPLOYEE_RATE, 2)
            epf_employer = round(epf_wage * EPF_EMPLOYER_RATE, 2)
            eps_employer = round(epf_wage * EPS_RATE,          2)
            epf_deposit  = round(epf_employer - eps_employer,  2)

        esic_employee = esic_employer = 0.0
        if emp.esic_applicable:
            esic_employee = round(gross * ESIC_EMPLOYEE_RATE, 2)
            esic_employer = round(gross * ESIC_EMPLOYER_RATE, 2)

        prof_tax         = PROFESSIONAL_TAX if gross > 10_000 else 0.0
        total_deductions = epf_employee + esic_employee + prof_tax
        net_pay          = round(gross - total_deductions, 2)

        return {
            'basic_salary': basic, 'hra': emp.hra,
            'special_allowance': emp.special_allowance,
            'travel_allowance': emp.travel_allowance,
            'gross_salary': gross,
            'epf_employee': epf_employee, 'epf_employer': epf_employer,
            'eps_employer': eps_employer, 'epf_deposit': epf_deposit,
            'esic_employee': esic_employee, 'esic_employer': esic_employer,
            'professional_tax': prof_tax, 'tds': 0.0,
            'total_deductions': total_deductions, 'net_pay': net_pay,
        }

    def _save_payroll(self, emp, month, year, calc):
        self.payroll_repo.create({
            'employee_id': emp.id, 'month': month, 'year': year,
            'status': 'processed', 'processed_on': datetime.utcnow(), **calc,
        })

    def _save_epf_record(self, emp, month, year, calc):
        if not emp.epf_applicable:
            return
        self.epf_repo.create({
            'month': month, 'year': year, 'employee_id': emp.id,
            'uan_number': emp.uan_number, 'basic_wages': emp.basic_salary,
            'epf_employee': calc['epf_employee'],
            'epf_employer': calc['epf_deposit'],
            'eps_employer': calc['eps_employer'],
            'total_epf': calc['epf_employee'] + calc['epf_deposit'],
        })

    def _save_esic_record(self, emp, month, year, calc):
        if not emp.esic_applicable:
            return
        self.esic_repo.create({
            'month': month, 'year': year, 'employee_id': emp.id,
            'ip_number': emp.esic_ip_number, 'gross_wages': emp.gross_salary,
            'esic_employee': calc['esic_employee'],
            'esic_employer': calc['esic_employer'],
            'total_esic': calc['esic_employee'] + calc['esic_employer'],
        })
