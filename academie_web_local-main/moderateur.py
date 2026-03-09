import eventlet
eventlet.monkey_patch()
from flask import Flask
from datetime import timedelta  # ← ADD THIS IMPORT
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create Flask app
app = Flask(__name__, template_folder="template")
app.secret_key = "a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5"

# ============================================
# SESSION CONFIGURATION - ADD THIS SECTION
# ============================================
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = True  # False because self-signed cert
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
    eventlet.wsgi.server(
        eventlet.wrap_ssl(
            eventlet.listen(('192.168.1.246', 5015)),
            certfile='cert.pem',
            keyfile='key.pem',
            server_side=True
        ),
        app
    )