"""
WebSocket module for real-time notifications
"""
from flask_socketio import SocketIO

# Initialize SocketIO instance (will be configured in app.py)
socketio = None

def init_socketio(app):
    """
    Initialize SocketIO with the Flask app

    Args:
        app: Flask application instance

    Returns:
        socketio: Configured SocketIO instance
    """
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # Allow all origins (adjust for production)
        async_mode='threading',     # Changed from 'eventlet' to 'threading'
        logger=True,                # Enable logging
        engineio_logger=True        # Enable engine.io logging
    )

    # Register event handlers
    from .events import register_socketio_events
    register_socketio_events(socketio)

    print("✅ SocketIO initialized successfully")

    return socketio

def get_socketio():
    """
    Get the current SocketIO instance

    Returns:
        socketio: Current SocketIO instance or None if not initialized
    """
    return socketio