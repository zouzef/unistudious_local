# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from config import Config

socketio = SocketIO(cors_allowed_origins="*",
                    async_mode='threading',
                    ping_timeout=60,
                    ping_interval=25)

def create_app():
    app = Flask(__name__,
                template_folder=Config.TEMPLATE_FOLDER,
                static_folder="../static")
    app.config.from_object(Config)

    socketio.init_app(app)

    from app.auth.routes import auth_bp
    from app.session.routes import session_bp
    from app.calendar.routes import calendar_bp
    from app.attendance.routes import attendance_bp
    from app.groups.routes import groups_bp
    from app.user.routes import user_bp
    from app.formation.routes import formation_bp



    # View Blueprints
    from app.session.views import session_view_bp
    from app.user.views import user_views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(formation_bp)
    app.register_blueprint(user_views_bp)
    app.register_blueprint(session_view_bp)
    return app