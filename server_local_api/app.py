from flask import Flask
from config import Config


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ========================================
    # REGISTER ALL BLUEPRINTS
    # ========================================

    # Authentication
    from api.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    # Attendance
    from api.attendance.routes import attendance_bp
    app.register_blueprint(attendance_bp)

    # Calendar
    from api.calendar.routes import calendar_bp
    app.register_blueprint(calendar_bp)

    # Devices (Cameras & Tablets)
    from api.devices.routes import devices_bp
    app.register_blueprint(devices_bp)

    # Moderator
    from api.moderator.routes import moderator_bp
    app.register_blueprint(moderator_bp)

    # Presence (Face Detection)
    from api.presence.routes import presence_bp
    app.register_blueprint(presence_bp)

    # Sessions
    from api.sessions.routes import sessions_bp
    app.register_blueprint(sessions_bp)

    # SLC (Physical Infrastructure)
    from api.slc.routes import slc_bp
    app.register_blueprint(slc_bp)

    # Users
    from api.users.routes import users_bp
    app.register_blueprint(users_bp)

    # ========================================
    # HOME ROUTE
    # ========================================
    @app.route('/')
    def home():
        return "Local Server is running!"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG,
        ssl_context=(Config.SSL_CERT, Config.SSL_KEY)
    )