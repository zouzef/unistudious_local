from flask import Flask
from datetime import timedelta  # ← ADD THIS IMPORT
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create Flask app
app = Flask(__name__, template_folder="template")
app.secret_key = "application"

# ============================================
# SESSION CONFIGURATION - ADD THIS SECTION
# ============================================
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = False  # False because self-signed cert
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# ============================================

# Import and register blueprints
from routes.authentification import auth_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# Initialize WebSocket
from websockets import init_socketio

socketio = init_socketio(app)

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5015,
        debug=True,
        ssl_context=('cert.pem', 'key.pem'),
        allow_unsafe_werkzeug=True
    )