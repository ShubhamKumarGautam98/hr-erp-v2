import calendar
from datetime import date
from app.repositories.payroll_repository import EPFRepository, ESICRepository
from app.repositories.employee_repository import EmployeeRepository


class ComplianceService:
    """
    Surfaces EPF & ESIC data for the compliance dashboard
    and generates the ECR (Electronic Challan cum Return) file.
    """

    def __init__(self):
        self.epf_repo      = EPFRepository()
        self.esic_repo     = ESICRepository()
        self.employee_repo = EmployeeRepository()

    def get_dashboard_data(self, month: int, year: int) -> dict:
        epf_records  = self.epf_repo.get_by_month_year(month, year)
        esic_records = self.esic_repo.get_by_month_year(month, year)
        epf_totals   = self.epf_repo.totals(month, year)
        esic_totals  = self.esic_repo.totals(month, year)

        next_month   = (month % 12) + 1
        next_year    = year if month < 12 else year + 1
        due_date_str = f"15 {calendar.month_name[next_month]} {next_year}"

        return {
            'epf_records':        epf_records,
            'esic_records':       esic_records,
            # flat variables — matches what the template expects
            'total_epf_employee': epf_totals.get('epf_employee', 0.0),
            'total_epf_employer': epf_totals.get('epf_employer', 0.0),
            'total_eps':          epf_totals.get('eps_employer', 0.0),
            'total_epf':          epf_totals.get('total_epf',    0.0),
            'total_esic_employee':esic_totals.get('esic_employee', 0.0),
            'total_esic_employer':esic_totals.get('esic_employer', 0.0),
            'total_esic':         esic_totals.get('total_esic',    0.0),
            'month':              month,
            'year':               year,
            'month_name':         calendar.month_name[month],
            'epf_due_date':       due_date_str,
            'esic_due_date':      due_date_str,
        }

    def generate_ecr(self, month: int, year: int) -> str:
        """
        Produces the EPF ECR text content in the EPFO-prescribed
        '#~#' delimited format.
        Returns the raw string (caller handles HTTP response).
        """
        records = self.epf_repo.get_by_month_year(month, year)
        header  = '#~#'.join([
            'UAN', 'Member Name', 'Gross Wages', 'EPF Wages',
            'EPS Wages', 'EPF Contribution EE', 'EPS Contribution ER',
            'EPF Contribution ER', 'NCP Days', 'Refund of Advances',
        ])
        lines = [header]
        for r in records:
            emp  = self.employee_repo.get_by_id(r.employee_id)
            line = '#~#'.join([
                r.uan_number or '',
                emp.full_name,
                str(r.basic_wages),
                str(r.basic_wages),
                str(r.basic_wages),
                str(r.epf_employee),
                str(r.eps_employer),
                str(r.epf_employer),
                '0', '0',
            ])
            lines.append(line)
        return '\n'.join(lines)
