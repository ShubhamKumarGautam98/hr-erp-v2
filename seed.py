"""
Seed script — run this once to populate demo data.
Usage: python seed.py
"""
from app import create_app
from app.models.models import (db, User, Department, Designation, Employee,
                                 LeaveType, LeaveRequest, Attendance,
                                 Lead, Client, Contact, Opportunity, Activity)
from datetime import date, timedelta, datetime
import random

app = create_app()

with app.app_context():
    db.create_all()

    # ── Users ────────────────────────────────────────────────────────
    users_data = [
        ('admin',      'admin@erp.com',    'admin123',  'admin'),
        ('hr_manager', 'hr@erp.com',       'hr123',     'hr_manager'),
        ('bd_manager', 'bd@erp.com',       'bd123',     'bd_manager'),
        ('rahul_bd',   'rahul@erp.com',    'rahul123',  'bd_executive'),
        ('priya_bd',   'priya@erp.com',    'priya123',  'bd_executive'),
        ('employee',   'emp@erp.com',      'emp123',    'employee'),
    ]
    users = {}
    for username, email, pwd, role in users_data:
        u = User.query.filter_by(username=username).first()
        if not u:
            u = User(username=username, email=email, role=role)
            u.set_password(pwd)
            db.session.add(u)
        users[username] = u
    db.session.flush()

    # ── Departments ──────────────────────────────────────────────────
    dept_names = ['Engineering', 'Human Resources', 'Sales & BD', 'Finance', 'Operations', 'Marketing']
    depts = {}
    for name in dept_names:
        d = Department.query.filter_by(name=name).first()
        if not d:
            d = Department(name=name)
            db.session.add(d)
        depts[name] = d
    db.session.flush()

    # ── Designations ─────────────────────────────────────────────────
    desig_names = ['Software Engineer', 'Senior Developer', 'HR Executive', 'BD Executive',
                   'BD Manager', 'Accounts Manager', 'Team Lead', 'Operations Executive']
    desigs = {}
    for name in desig_names:
        d = Designation.query.filter_by(name=name).first()
        if not d:
            d = Designation(name=name)
            db.session.add(d)
        desigs[name] = d
    db.session.flush()

    # ── Leave Types ──────────────────────────────────────────────────
    leave_types_data = [
        ('Casual Leave', 12, True),
        ('Sick Leave', 12, True),
        ('Annual Leave', 15, True),
        ('Maternity Leave', 180, True),
        ('Paternity Leave', 15, True),
        ('Loss of Pay', 0, False),
    ]
    leave_types = {}
    for name, days, paid in leave_types_data:
        lt = LeaveType.query.filter_by(name=name).first()
        if not lt:
            lt = LeaveType(name=name, days_allowed=days, is_paid=paid)
            db.session.add(lt)
        leave_types[name] = lt
    db.session.flush()

    # ── Employees ────────────────────────────────────────────────────
    employees_data = [
        ('EMP001', 'Amit',    'Sharma',   'amit@demo.com',   '9876543210', 'Male',   'Engineering',     'Software Engineer', 12000, 5000, 2000, 1500, date(2022, 3, 1),  'UAN100001', 'ESIC100001', 'ABCPS1234A'),
        ('EMP002', 'Sunita',  'Verma',    'sunita@demo.com', '9876543211', 'Female', 'Human Resources', 'HR Executive',      14000, 5600, 2000, 1500, date(2021, 6, 15), 'UAN100002', 'ESIC100002', 'BCDQV5678B'),
        ('EMP003', 'Rohit',   'Gupta',    'rohit@demo.com',  '9876543212', 'Male',   'Sales & BD',      'BD Executive',      18000, 7200, 3000, 2000, date(2023, 1, 10), 'UAN100003', None,         'CDERS9012C'),
        ('EMP004', 'Kavita',  'Patel',    'kavita@demo.com', '9876543213', 'Female', 'Finance',         'Accounts Manager',  22000, 8800, 4000, 2000, date(2020, 9, 1),  None,        None,         'DEFGT3456D'),
        ('EMP005', 'Vikram',  'Singh',    'vikram@demo.com', '9876543214', 'Male',   'Engineering',     'Senior Developer',  25000, 10000,5000, 2500, date(2019, 4, 20), None,        None,         'EFGHU7890E'),
        ('EMP006', 'Meena',   'Nair',     'meena@demo.com',  '9876543215', 'Female', 'Marketing',       'BD Manager',        15000, 6000, 2500, 1500, date(2022, 8, 5),  'UAN100006', 'ESIC100006', 'FGHIV2345F'),
        ('EMP007', 'Arjun',   'Reddy',    'arjun@demo.com',  '9876543216', 'Male',   'Operations',      'Team Lead',         20000, 8000, 3500, 2000, date(2021, 2, 14), None,        None,         'GHIJW6789G'),
        ('EMP008', 'Pooja',   'Mishra',   'pooja@demo.com',  '9876543217', 'Female', 'Engineering',     'Software Engineer', 13000, 5200, 2000, 1000, date(2023, 6, 1),  'UAN100008', 'ESIC100008', 'HIJKX1234H'),
    ]

    emps = []
    for code, fn, ln, email, phone, gender, dept, desig, basic, hra, sa, ta, jd, uan, esic_ip, pan in employees_data:
        e = Employee.query.filter_by(employee_code=code).first()
        if not e:
            e = Employee(
                employee_code=code, first_name=fn, last_name=ln,
                email=email, phone=phone, gender=gender,
                department_id=depts[dept].id,
                designation_id=desigs[desig].id,
                joining_date=jd,
                basic_salary=basic, hra=hra,
                special_allowance=sa, travel_allowance=ta,
                uan_number=uan, esic_ip_number=esic_ip, pan_number=pan,
                status='active'
            )
            e.epf_applicable = basic <= 15000
            e.esic_applicable = (basic + hra + sa + ta) <= 21000
            db.session.add(e)
        emps.append(e)
    db.session.flush()

    # ── Attendance (last 10 days) ────────────────────────────────────
    today = date.today()
    for emp in emps:
        for i in range(10, 0, -1):
            d = today - timedelta(days=i)
            if d.weekday() < 5:  # weekday only
                existing = Attendance.query.filter_by(employee_id=emp.id, date=d).first()
                if not existing:
                    choices = ['present', 'present', 'present', 'present', 'absent', 'half_day', 'wfh']
                    att = Attendance(employee_id=emp.id, date=d, status=random.choice(choices))
                    db.session.add(att)

    # ── Leave Requests ───────────────────────────────────────────────
    if LeaveRequest.query.count() == 0:
        lr_data = [
            (emps[0].id, leave_types['Casual Leave'].id,  today - timedelta(days=5), today - timedelta(days=4), 'pending'),
            (emps[1].id, leave_types['Sick Leave'].id,    today - timedelta(days=3), today - timedelta(days=3), 'approved'),
            (emps[2].id, leave_types['Annual Leave'].id,  today + timedelta(days=5), today + timedelta(days=9), 'pending'),
            (emps[3].id, leave_types['Casual Leave'].id,  today - timedelta(days=8), today - timedelta(days=7), 'rejected'),
            (emps[4].id, leave_types['Sick Leave'].id,    today - timedelta(days=2), today - timedelta(days=2), 'approved'),
        ]
        for eid, ltid, fd, td, status in lr_data:
            days = (td - fd).days + 1
            lr = LeaveRequest(employee_id=eid, leave_type_id=ltid, from_date=fd, to_date=td, days=days, status=status, reason='Personal work')
            db.session.add(lr)

    # ── BD: Leads ─────────────────────────────────────────────────────
    if Lead.query.count() == 0:
        leads_data = [
            ('TechSolutions Pvt Ltd', 'Rajesh Kumar',    'rk@techsol.com',  '9812345670', 'LinkedIn',  'IT / Technology',  'qualified'),
            ('GreenMart Retail',      'Priya Khanna',    'pk@greenmart.com', '9812345671', 'Referral',  'Retail',           'contacted'),
            ('HealthFirst Clinics',   'Dr. Suresh',      'ds@hfc.com',       '9812345672', 'Website',   'Healthcare',       'new'),
            ('FinancePro Ltd',        'Anita Shah',      'as@fpro.com',      '9812345673', 'Cold Call', 'Finance',          'qualified'),
            ('BuildCo Infra',         'Mahesh Patil',    'mp@buildco.com',   '9812345674', 'Exhibition','Real Estate',      'new'),
            ('EduTech Academy',       'Shruti Gupta',    'sg@edut.com',      '9812345675', 'LinkedIn',  'Education',        'converted'),
            ('Manuf Industries',      'Ravi Shankar',    'rs@manuf.com',     '9812345676', 'Referral',  'Manufacturing',    'lost'),
        ]
        bd_user = users.get('rahul_bd')
        for cn, contact, email, phone, src, industry, status in leads_data:
            l = Lead(
                company_name=cn, contact_name=contact, email=email, phone=phone,
                source=src, industry=industry, status=status,
                assigned_to=bd_user.id if bd_user else None,
                next_followup=today + timedelta(days=random.randint(1, 7))
            )
            db.session.add(l)
    db.session.flush()

    # ── BD: Clients ──────────────────────────────────────────────────
    if Client.query.count() == 0:
        clients_data = [
            ('EduTech Academy', 'Education',    'www.edutech.com', 'Shruti Gupta',  'Director',  'sg@edut.com',     '9812345675'),
            ('Alpha Corp',      'IT / Technology','www.alphacorp.in', 'Nitin Joshi', 'CTO',       'nj@alpha.com',    '9812345680'),
            ('Beta Pharma',     'Healthcare',   'www.betarx.com', 'Sneha Mehta',   'HR Head',   'sm@betarx.com',   '9812345681'),
        ]
        for cn, industry, web, contact_name, contact_desig, contact_email, contact_phone in clients_data:
            c = Client(company_name=cn, industry=industry, website=web)
            db.session.add(c)
            db.session.flush()
            contact = Contact(client_id=c.id, name=contact_name, designation=contact_desig,
                              email=contact_email, phone=contact_phone, is_primary=True)
            db.session.add(contact)
    db.session.flush()

    # ── BD: Opportunities ────────────────────────────────────────────
    if Opportunity.query.count() == 0:
        clients = Client.query.all()
        bd_user = users.get('bd_manager')
        opp_data = [
            ('ERP Implementation — EduTech',   clients[0].id if clients else None, 'won',         350000, 80),
            ('CRM Setup — Alpha Corp',         clients[1].id if len(clients)>1 else None, 'proposal', 180000, 60),
            ('HR Software — Beta Pharma',      clients[2].id if len(clients)>2 else None, 'negotiation',250000, 75),
            ('Cloud Migration — TechSolutions', None,                                'prospect',   500000, 20),
            ('Website Redesign — GreenMart',   None,                                'proposal',    80000, 50),
        ]
        for title, cid, stage, value, prob in opp_data:
            o = Opportunity(
                title=title, client_id=cid, stage=stage, value=value,
                probability=prob,
                expected_close_date=today + timedelta(days=random.randint(15, 60)),
                assigned_to=bd_user.id if bd_user else None,
                description='Demo opportunity created by seed script.'
            )
            db.session.add(o)

    # ── BD: Activities ────────────────────────────────────────────────
    if Activity.query.count() == 0:
        leads = Lead.query.limit(3).all()
        bd_user = users.get('rahul_bd')
        act_data = [
            ('call',    'Initial discovery call',         leads[0].id if leads else None, False),
            ('meeting', 'Product demo scheduled',         leads[1].id if len(leads)>1 else None, False),
            ('email',   'Sent proposal PDF',              leads[2].id if len(leads)>2 else None, True),
            ('followup','Follow up on pricing discussion',leads[0].id if leads else None, False),
        ]
        for atype, subject, lid, completed in act_data:
            a = Activity(
                type=atype, subject=subject, lead_id=lid,
                assigned_to=bd_user.id if bd_user else None,
                scheduled_at=datetime.now() + timedelta(days=random.randint(1, 5)),
                completed=completed
            )
            db.session.add(a)

    # ── Link employee user to EMP001 so self-service portal works ───
    emp_user = User.query.filter_by(username='employee').first()
    emp001   = Employee.query.filter_by(employee_code='EMP001').first()
    if emp_user and emp001:
        emp_user.employee_id = emp001.id

    db.session.commit()
    print("✅ Database seeded successfully!")
    print("\n📋 Login Credentials:")
    print("  admin      / admin123  → Full Access")
    print("  hr_manager / hr123     → HR Manager")
    print("  bd_manager / bd123     → BD Manager")
    print("  employee   / emp123    → Employee View")
    print("\n🚀 Run: python run.py")
    print("🌐 Open: http://localhost:5000")
