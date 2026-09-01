# run.py
"""Main Flask application for unistudious local web."""
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app import create_app, socketio
from config import Config

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug = True,
        ssl_context=(Config.CERTFILE, Config.KEYFILE),
        allow_unsafe_werkzeug=True,
        use_reloader=True
    )