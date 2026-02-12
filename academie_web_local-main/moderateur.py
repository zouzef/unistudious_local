from flask import Flask
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create Flask app
app = Flask(__name__, template_folder="template")
app.secret_key = "application"

# Import and register blueprints
from routes.authentification import auth_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# ============================================
# NEW: Initialize our WebSocket module
# ============================================
from websockets import init_socketio

socketio = init_socketio(app)

# ============================================
# Keep everything else the same
# ============================================

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5015,
        debug=True,
        ssl_context=('cert.pem', 'key.pem'),
        allow_unsafe_werkzeug=True
    )