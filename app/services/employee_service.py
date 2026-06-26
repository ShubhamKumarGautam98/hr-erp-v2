from datetime import date
from app.repositories.employee_repository import (
    EmployeeRepository, DepartmentRepository, DesignationRepository
)


class EmployeeService:
    """Handles all employee-related business logic."""

    def __init__(self):
        self.employee_repo    = EmployeeRepository()
        self.department_repo  = DepartmentRepository()
        self.designation_repo = DesignationRepository()

    # ── Reads ─────────────────────────────────────────────────────────

    def get_all_employees(self):
        return self.employee_repo.get_all()

    def get_active_employees(self):
        return self.employee_repo.get_all_active()

    def get_employee(self, employee_id):
        return self.employee_repo.get_by_id(employee_id)

    def get_all_departments(self):
        return self.department_repo.get_all()

    def get_all_designations(self):
        return self.designation_repo.get_all()

    def get_headcount(self):
        return self.employee_repo.count_active()

    def get_dept_headcount(self):
        return self.department_repo.headcount_per_department()

    # ── Writes ────────────────────────────────────────────────────────

    def create_employee(self, form_data: dict):
        """
        Accepts raw form data, applies business rules,
        then delegates saving to the repository.
        """
        basic  = float(form_data.get('basic_salary') or 0)
        hra    = float(form_data.get('hra') or 0)
        sa     = float(form_data.get('special_allowance') or 0)
        ta     = float(form_data.get('travel_allowance') or 0)
        gross  = basic + hra + sa + ta

        data = {
            'employee_code':   form_data['employee_code'],
            'first_name':      form_data['first_name'],
            'last_name':       form_data['last_name'],
            'email':           form_data['email'],
            'phone':           form_data.get('phone'),
            'gender':          form_data.get('gender'),
            'address':         form_data.get('address'),
            'department_id':   form_data.get('department_id') or None,
            'designation_id':  form_data.get('designation_id') or None,
            'joining_date':    date.fromisoformat(form_data['joining_date']),
            'employment_type': form_data.get('employment_type', 'full_time'),
            'basic_salary':    basic,
            'hra':             hra,
            'special_allowance': sa,
            'travel_allowance':  ta,
            'uan_number':      form_data.get('uan_number'),
            'esic_ip_number':  form_data.get('esic_ip_number'),
            'pan_number':      form_data.get('pan_number'),
            'aadhaar_number':  form_data.get('aadhaar_number'),
            # Business rule: EPF/ESIC eligibility is auto-determined
            'epf_applicable':  basic <= 15000,
            'esic_applicable': gross <= 21000,
        }
        return self.employee_repo.create(data)

    def update_employee(self, employee_id, form_data: dict):
        emp    = self.employee_repo.get_by_id(employee_id)
        basic  = float(form_data.get('basic_salary') or 0)
        hra    = float(form_data.get('hra') or 0)
        sa     = float(form_data.get('special_allowance') or 0)
        ta     = float(form_data.get('travel_allowance') or 0)
        gross  = basic + hra + sa + ta

        data = {
            'first_name':       form_data['first_name'],
            'last_name':        form_data['last_name'],
            'phone':            form_data.get('phone'),
            'gender':           form_data.get('gender'),
            'address':          form_data.get('address'),
            'department_id':    form_data.get('department_id') or None,
            'designation_id':   form_data.get('designation_id') or None,
            'employment_type':  form_data.get('employment_type'),
            'status':           form_data.get('status'),
            'basic_salary':     basic,
            'hra':              hra,
            'special_allowance': sa,
            'travel_allowance':  ta,
            'uan_number':       form_data.get('uan_number'),
            'esic_ip_number':   form_data.get('esic_ip_number'),
            'pan_number':       form_data.get('pan_number'),
            # Re-evaluate eligibility on every update
            'epf_applicable':   basic <= 15000,
            'esic_applicable':  gross <= 21000,
        }
        return self.employee_repo.update(emp, data)
