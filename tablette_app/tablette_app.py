"""Main Flask application for tablet attendance system."""
from flask import Flask
from flask_socketio import SocketIO

# Import configuration
from utils.config import config

# Import token manager
from auth.token_manager import token_manager

# Import routes
from routes.tablet_routes import tablet_bp
from routes.attendance_routes import attendance_bp
from routes.student_routes import student_bp

# Import websocket handlers
from websockets.events import register_socketio_events, start_background_tasks

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============= Flask App Initialization =============
app = Flask(__name__, template_folder='templates')
app.secret_key = config["config"]["SECRET_KEY"]

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============= Register Blueprints =============
app.register_blueprint(tablet_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(student_bp)

# ============= Register WebSocket Events =============
register_socketio_events(socketio)


# ============= Initialize Token and Background Tasks =============
def initialize_app():
    """Initialize token and start background tasks."""
    # Initialize token
    token_manager.initialize()

    # Start background tasks (attendance checker)
    start_background_tasks(socketio)

    print("✅ Application initialized successfully")


# ============= Main Entry Point =============
if __name__ == "__main__":
    initialize_app()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5012,
        debug=True,
        ssl_context=('cert.pem', 'key.pem'),
        allow_unsafe_werkzeug=True
    )