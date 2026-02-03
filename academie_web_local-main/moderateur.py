from flask import Flask
from flask_socketio import SocketIO
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create Flask app
app = Flask(__name__, template_folder="template")
app.secret_key = "application"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import and register blueprints
from routes.authentification import auth_bp
from routes.dashboard import dashboard_bp


app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# Add more blueprints as you create them:
# from routes.dashboard import dashboard_bp
# app.register_blueprint(dashboard_bp)

# from routes.students import students_bp
# app.register_blueprint(students_bp)


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5015,
        debug=True,
        ssl_context=('cert.pem', 'key.pem'),
        allow_unsafe_werkzeug=True
    )