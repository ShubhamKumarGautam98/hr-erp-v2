# 🏢 HR ERP System v2

> Full-stack enterprise HR & Business Development management platform built with Flask, SQLAlchemy, and Role-Based Access Control.

---

## 🎯 Overview

A production-grade HR ERP system covering the complete employee lifecycle — from onboarding to payroll, attendance, leave management, and compliance. Includes a Business Development pipeline module for managing leads, clients, and opportunities.

Built with a clean **Service Layer + Repository Pattern** architecture for maintainability and testability.

---

## ✨ Modules

| Module | Description |
|---|---|
| 👤 **Employee Management** | Add, edit, view employees with department and designation |
| 💰 **Payroll** | Payslip generation, salary management, PDF export |
| 🕐 **Attendance** | Track daily attendance, generate reports |
| 🏖️ **Leave Management** | Apply, approve, and track leave requests |
| ✅ **Compliance** | Regulatory and HR compliance tracking |
| 📊 **Dashboard** | HR dashboard + Employee self-service dashboard |
| 🤝 **BD Pipeline** | Leads, clients, opportunities, and activity tracking |
| 📤 **Exports** | Excel and PDF export for all reports |

---

## 🔐 Role-Based Access Control (RBAC)

| Role | Access |
|---|---|
| `admin` | Full system access |
| `hr_manager` | All HR modules — employees, payroll, attendance, leave, compliance |
| `employee` | Self-service — own attendance, payslips, leave applications |
| `bd_manager` | Full BD pipeline — leads, clients, opportunities |
| `bd_executive` | BD pipeline — assigned leads and activities |

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **Framework** | Flask 3.0 |
| **Database ORM** | Flask-SQLAlchemy |
| **Authentication** | Flask-Login |
| **Forms** | Flask-WTF + WTForms |
| **PDF Generation** | ReportLab |
| **Excel Export** | openpyxl |
| **Architecture** | Service Layer + Repository Pattern |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Templates** | Jinja2 |

---

## 🏗️ Architecture

```
hr_erp_v2/
├── run.py                     # Application entry point
├── config.py                  # Environment configuration
├── seed.py                    # Database seeding script
├── requirements.txt
└── app/
    ├── __init__.py            # App factory (create_app)
    ├── models/
    │   └── models.py          # SQLAlchemy models (User, Employee, Payroll, etc.)
    ├── routes/                # Flask Blueprints
    │   ├── auth.py            # Login / logout
    │   ├── employees.py       # Employee CRUD
    │   ├── payroll.py         # Payroll management
    │   ├── attendance.py      # Attendance tracking
    │   ├── leave.py           # Leave management
    │   ├── compliance.py      # Compliance module
    │   ├── dashboard.py       # HR + Employee dashboards
    │   ├── bd.py              # Business Development pipeline
    │   └── exports.py         # PDF and Excel exports
    ├── services/              # Business logic layer
    │   ├── employee_service.py
    │   ├── payroll_service.py
    │   ├── attendance_service.py
    │   ├── leave_service.py
    │   ├── compliance_service.py
    │   ├── dashboard_service.py
    │   └── bd_service.py
    ├── repositories/          # Data access layer
    │   ├── base_repository.py
    │   ├── employee_repository.py
    │   ├── payroll_repository.py
    │   ├── attendance_repository.py
    │   ├── leave_repository.py
    │   └── bd_repository.py
    ├── utils/
    │   ├── rbac.py            # Role-based access decorators
    │   ├── pdf_generator.py   # ReportLab PDF generation
    │   └── excel_exporter.py  # openpyxl Excel export
    └── templates/             # Jinja2 HTML templates
```

---

## 🚀 Running Locally

```bash
# Clone the repo
git clone https://github.com/ShubhamKumarGautam98/hr-erp-v2.git
cd hr-erp-v2

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data
python seed.py

# Run the application
python run.py
```

Opens at [http://localhost:5000](http://localhost:5000)

---

## 🔑 Default Login Credentials

After running `seed.py`:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| HR Manager | `hr_manager` | `hr123` |
| Employee | `employee1` | `emp123` |
| BD Manager | `bd_manager` | `bd123` |

---

## 🗺️ Roadmap

- [ ] Migrate from SQLite to PostgreSQL
- [ ] Add REST API layer with FastAPI
- [ ] JWT authentication for API access
- [ ] React frontend to replace Jinja2 templates
- [ ] Docker + CI/CD deployment pipeline
- [ ] Email notifications for leave approvals
- [ ] Multi-company / multi-tenant support

---

## 📬 Contact

**Shubham Kumar** — AI Automation Developer

- 🌐 [Portfolio](https://shubham-kumar.vercel.app)
- 💼 [LinkedIn](https://linkedin.com/in/shubham-kumar-395b89386)
- 📧 shubhamkmmmr@gmail.com

---

<p align="center">Built with ❤️ using Flask + SQLAlchemy + ReportLab</p>