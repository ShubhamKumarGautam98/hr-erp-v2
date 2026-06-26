from flask import Flask
from flask_login import LoginManager
from app.models.models import db, User
from config import config

login_manager = LoginManager()


def create_app(env='development'):
    app = Flask(__name__)
    app.config.from_object(config[env])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth       import auth_bp
    from app.routes.dashboard  import dashboard_bp
    from app.routes.employees  import employees_bp
    from app.routes.leave      import leave_bp
    from app.routes.attendance import attendance_bp
    from app.routes.payroll    import payroll_bp
    from app.routes.compliance import compliance_bp
    from app.routes.bd         import bd_bp
    from app.routes.exports    import exports_bp

    for bp in (auth_bp, dashboard_bp, employees_bp, leave_bp,
               attendance_bp, payroll_bp, compliance_bp, bd_bp, exports_bp):
        app.register_blueprint(bp)

    return app
