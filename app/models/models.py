from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ─── AUTH ────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role          = db.Column(db.String(20),  default='employee')
    # roles: admin | hr_manager | employee | bd_manager | bd_executive
    employee_id   = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


# ─── HR CORE ─────────────────────────────────────────────────────────────────

class Department(db.Model):
    __tablename__ = 'departments'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    employees   = db.relationship('Employee', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'


class Designation(db.Model):
    __tablename__ = 'designations'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    employees   = db.relationship('Employee', backref='designation', lazy=True)

    def __repr__(self):
        return f'<Designation {self.name}>'


class Employee(db.Model):
    __tablename__ = 'employees'

    id              = db.Column(db.Integer, primary_key=True)
    employee_code   = db.Column(db.String(20),  unique=True, nullable=False)
    first_name      = db.Column(db.String(50),  nullable=False)
    last_name       = db.Column(db.String(50),  nullable=False)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    phone           = db.Column(db.String(15))
    date_of_birth   = db.Column(db.Date)
    gender          = db.Column(db.String(10))
    address         = db.Column(db.Text)
    department_id   = db.Column(db.Integer, db.ForeignKey('departments.id'))
    designation_id  = db.Column(db.Integer, db.ForeignKey('designations.id'))
    joining_date    = db.Column(db.Date, nullable=False)
    employment_type = db.Column(db.String(20), default='full_time')
    status          = db.Column(db.String(20), default='active')
    # Salary components
    basic_salary       = db.Column(db.Float, default=0.0)
    hra                = db.Column(db.Float, default=0.0)
    special_allowance  = db.Column(db.Float, default=0.0)
    travel_allowance   = db.Column(db.Float, default=0.0)
    # Compliance numbers
    uan_number      = db.Column(db.String(20))   # EPF Universal Account Number
    esic_ip_number  = db.Column(db.String(20))   # ESIC Insured Person Number
    epf_applicable  = db.Column(db.Boolean, default=True)
    esic_applicable = db.Column(db.Boolean, default=True)
    # Identity
    pan_number      = db.Column(db.String(10))
    aadhaar_number  = db.Column(db.String(12))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    leave_requests    = db.relationship('LeaveRequest', backref='employee', lazy=True)
    attendance_records= db.relationship('Attendance',   backref='employee', lazy=True)
    payroll_records   = db.relationship('Payroll',      backref='employee', lazy=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def gross_salary(self):
        return (self.basic_salary + self.hra +
                self.special_allowance + self.travel_allowance)

    def __repr__(self):
        return f'<Employee {self.employee_code} – {self.full_name}>'


# ─── LEAVE ───────────────────────────────────────────────────────────────────

class LeaveType(db.Model):
    __tablename__ = 'leave_types'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(50), nullable=False)
    days_allowed = db.Column(db.Integer, default=0)
    is_paid      = db.Column(db.Boolean, default=True)
    description  = db.Column(db.Text)

    def __repr__(self):
        return f'<LeaveType {self.name}>'


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id            = db.Column(db.Integer, primary_key=True)
    employee_id   = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    from_date     = db.Column(db.Date,    nullable=False)
    to_date       = db.Column(db.Date,    nullable=False)
    days          = db.Column(db.Integer, nullable=False)
    reason        = db.Column(db.Text)
    status        = db.Column(db.String(20), default='pending')
    # pending | approved | rejected
    applied_on    = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_on   = db.Column(db.DateTime, nullable=True)
    remarks       = db.Column(db.Text)

    leave_type    = db.relationship('LeaveType', backref='requests')

    def __repr__(self):
        return f'<LeaveRequest emp={self.employee_id} {self.from_date}→{self.to_date}>'


# ─── ATTENDANCE ───────────────────────────────────────────────────────────────

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id          = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date        = db.Column(db.Date,    nullable=False)
    status      = db.Column(db.String(20), default='absent')
    # present | absent | half_day | wfh | on_leave
    check_in    = db.Column(db.Time, nullable=True)
    check_out   = db.Column(db.Time, nullable=True)
    remarks     = db.Column(db.String(200))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance emp={self.employee_id} {self.date} {self.status}>'


# ─── PAYROLL ──────────────────────────────────────────────────────────────────

class Payroll(db.Model):
    __tablename__ = 'payroll'

    id          = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month       = db.Column(db.Integer, nullable=False)
    year        = db.Column(db.Integer, nullable=False)

    # ── Earnings
    basic_salary      = db.Column(db.Float, default=0.0)
    hra               = db.Column(db.Float, default=0.0)
    special_allowance = db.Column(db.Float, default=0.0)
    travel_allowance  = db.Column(db.Float, default=0.0)
    gross_salary      = db.Column(db.Float, default=0.0)

    # ── Employee deductions
    epf_employee      = db.Column(db.Float, default=0.0)   # 12 % of basic
    esic_employee     = db.Column(db.Float, default=0.0)   # 0.75 % of gross
    professional_tax  = db.Column(db.Float, default=0.0)
    tds               = db.Column(db.Float, default=0.0)
    total_deductions  = db.Column(db.Float, default=0.0)
    net_pay           = db.Column(db.Float, default=0.0)

    # ── Employer statutory contributions (not deducted from salary)
    epf_employer      = db.Column(db.Float, default=0.0)   # 12 % of basic
    eps_employer      = db.Column(db.Float, default=0.0)   # 8.33 % of basic
    epf_deposit       = db.Column(db.Float, default=0.0)   # 3.67 % of basic
    esic_employer     = db.Column(db.Float, default=0.0)   # 3.25 % of gross

    # ── Attendance summary
    working_days = db.Column(db.Integer, default=26)
    present_days = db.Column(db.Integer, default=26)
    absent_days  = db.Column(db.Integer, default=0)
    lop_days     = db.Column(db.Integer, default=0)

    status        = db.Column(db.String(20), default='draft')
    processed_on  = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payroll emp={self.employee_id} {self.month}/{self.year}>'


# ─── COMPLIANCE ───────────────────────────────────────────────────────────────

class EPFRecord(db.Model):
    __tablename__ = 'epf_records'

    id             = db.Column(db.Integer, primary_key=True)
    month          = db.Column(db.Integer, nullable=False)
    year           = db.Column(db.Integer, nullable=False)
    employee_id    = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    uan_number     = db.Column(db.String(20))
    basic_wages    = db.Column(db.Float, default=0.0)
    epf_employee   = db.Column(db.Float, default=0.0)
    epf_employer   = db.Column(db.Float, default=0.0)
    eps_employer   = db.Column(db.Float, default=0.0)
    total_epf      = db.Column(db.Float, default=0.0)
    deposit_status = db.Column(db.String(20), default='pending')
    deposit_date   = db.Column(db.Date,   nullable=True)
    challan_number = db.Column(db.String(50), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='epf_records')


class ESICRecord(db.Model):
    __tablename__ = 'esic_records'

    id             = db.Column(db.Integer, primary_key=True)
    month          = db.Column(db.Integer, nullable=False)
    year           = db.Column(db.Integer, nullable=False)
    employee_id    = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    ip_number      = db.Column(db.String(20))
    gross_wages    = db.Column(db.Float, default=0.0)
    esic_employee  = db.Column(db.Float, default=0.0)
    esic_employer  = db.Column(db.Float, default=0.0)
    total_esic     = db.Column(db.Float, default=0.0)
    deposit_status = db.Column(db.String(20), default='pending')
    deposit_date   = db.Column(db.Date,   nullable=True)
    challan_number = db.Column(db.String(50), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='esic_records')


# ─── BD MODULE ────────────────────────────────────────────────────────────────

class Client(db.Model):
    __tablename__ = 'clients'

    id           = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    industry     = db.Column(db.String(100))
    website      = db.Column(db.String(200))
    address      = db.Column(db.Text)
    status       = db.Column(db.String(20), default='active')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    contacts      = db.relationship('Contact',     backref='client', lazy=True)
    opportunities = db.relationship('Opportunity', backref='client', lazy=True)

    def __repr__(self):
        return f'<Client {self.company_name}>'


class Contact(db.Model):
    __tablename__ = 'contacts'

    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    email       = db.Column(db.String(120))
    phone       = db.Column(db.String(15))
    is_primary  = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name}>'


class Lead(db.Model):
    __tablename__ = 'leads'

    id           = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(100))
    email        = db.Column(db.String(120))
    phone        = db.Column(db.String(15))
    source       = db.Column(db.String(50))
    industry     = db.Column(db.String(100))
    status       = db.Column(db.String(30), default='new')
    # new | contacted | qualified | unqualified | converted | lost
    assigned_to  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes        = db.Column(db.Text)
    next_followup= db.Column(db.Date, nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    assigned_user = db.relationship('User', backref='leads',
                                    foreign_keys=[assigned_to])

    def __repr__(self):
        return f'<Lead {self.company_name} [{self.status}]>'


class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id                 = db.Column(db.Integer, primary_key=True)
    title              = db.Column(db.String(200), nullable=False)
    client_id          = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    lead_id            = db.Column(db.Integer, db.ForeignKey('leads.id'),   nullable=True)
    stage              = db.Column(db.String(30), default='prospect')
    # prospect | proposal | negotiation | won | lost
    value              = db.Column(db.Float, default=0.0)
    expected_close_date= db.Column(db.Date,  nullable=True)
    probability        = db.Column(db.Integer, default=0)
    assigned_to        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    description        = db.Column(db.Text)
    win_loss_reason    = db.Column(db.Text, nullable=True)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime, default=datetime.utcnow,
                                   onupdate=datetime.utcnow)

    assigned_user = db.relationship('User', backref='opportunities',
                                    foreign_keys=[assigned_to])
    lead          = db.relationship('Lead', backref='opportunities')

    def __repr__(self):
        return f'<Opportunity {self.title} [{self.stage}]>'


class Proposal(db.Model):
    __tablename__ = 'proposals'

    id             = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    title          = db.Column(db.String(200), nullable=False)
    value          = db.Column(db.Float, default=0.0)
    status         = db.Column(db.String(20), default='draft')
    sent_date      = db.Column(db.Date, nullable=True)
    valid_until    = db.Column(db.Date, nullable=True)
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    opportunity = db.relationship('Opportunity', backref='proposals')

    def __repr__(self):
        return f'<Proposal {self.title}>'


class Activity(db.Model):
    __tablename__ = 'activities'

    id             = db.Column(db.Integer, primary_key=True)
    type           = db.Column(db.String(30), nullable=False)
    # call | meeting | email | demo | followup
    subject        = db.Column(db.String(200), nullable=False)
    lead_id        = db.Column(db.Integer, db.ForeignKey('leads.id'),          nullable=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'),  nullable=True)
    client_id      = db.Column(db.Integer, db.ForeignKey('clients.id'),        nullable=True)
    assigned_to    = db.Column(db.Integer, db.ForeignKey('users.id'),          nullable=True)
    scheduled_at   = db.Column(db.DateTime, nullable=True)
    completed      = db.Column(db.Boolean, default=False)
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_user = db.relationship('User', backref='activities',
                                    foreign_keys=[assigned_to])

    def __repr__(self):
        return f'<Activity {self.type}: {self.subject}>'


class RevenueTarget(db.Model):
    __tablename__ = 'revenue_targets'

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month    = db.Column(db.Integer, nullable=False)
    year     = db.Column(db.Integer, nullable=False)
    target   = db.Column(db.Float, default=0.0)
    achieved = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='revenue_targets')

    def __repr__(self):
        return f'<RevenueTarget user={self.user_id} {self.month}/{self.year}>'
