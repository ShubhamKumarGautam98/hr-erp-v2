from app.models.models import db, Employee, Department, Designation
from app.repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository):

    def get_all(self):
        return Employee.query.order_by(Employee.first_name).all()

    def get_all_active(self):
        return Employee.query.filter_by(status='active').order_by(Employee.first_name).all()

    def get_by_id(self, employee_id):
        return Employee.query.get_or_404(employee_id)

    def get_by_code(self, code):
        return Employee.query.filter_by(employee_code=code).first()

    def get_by_email(self, email):
        return Employee.query.filter_by(email=email).first()

    def count_active(self):
        return Employee.query.filter_by(status='active').count()

    def get_by_department(self, department_id):
        return Employee.query.filter_by(
            department_id=department_id, status='active'
        ).all()

    def create(self, data: dict):
        emp = Employee(**data)
        return self.save(emp)

    def update(self, employee, data: dict):
        for key, value in data.items():
            setattr(employee, key, value)
        self.commit()
        return employee


class DepartmentRepository(BaseRepository):

    def get_all(self):
        return Department.query.order_by(Department.name).all()

    def get_by_id(self, dept_id):
        return Department.query.get_or_404(dept_id)

    def create(self, name, description=''):
        dept = Department(name=name, description=description)
        return self.save(dept)

    def headcount_per_department(self):
        """Returns list of (dept_name, count) for active employees."""
        results = (
            db.session.query(Department.name, db.func.count(Employee.id))
            .join(Employee, Employee.department_id == Department.id)
            .filter(Employee.status == 'active')
            .group_by(Department.name)
            .all()
        )
        return [{'name': r[0], 'count': r[1]} for r in results]


class DesignationRepository(BaseRepository):

    def get_all(self):
        return Designation.query.order_by(Designation.name).all()

    def get_by_id(self, desig_id):
        return Designation.query.get_or_404(desig_id)

    def create(self, name, description=''):
        desig = Designation(name=name, description=description)
        return self.save(desig)
