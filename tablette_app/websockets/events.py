"""WebSocket event handlers for SocketIO."""
import threading
import time
from datetime import datetime
from flask import request
from flask_socketio import emit, join_room, leave_room
from services.attendance_service import get_calendar_details

# Store active connections
active_connections = {}


def register_socketio_events(socketio):
    """Register all SocketIO event handlers."""

    @socketio.on('connect')
    def handle_connect():
        try:
            print(f'Client connected: {request.sid}')
        except Exception as e:
            print(f"DEBUG: Exception in handle_connect: {e}")
            emit('status', {'message': f'Failed to connect client {request.sid}'})

    @socketio.on('disconnect')
    def handle_disconnect():
        try:
            print(f'Client disconnected: {request.sid}')
            if request.sid in active_connections:
                del active_connections[request.sid]
        except Exception as e:
            print(f"DEBUG: Exception in handle_disconnect: {e}")
            emit('status', {'message': f'Failed to disconnect client {request.sid}'})

    @socketio.on('join_session')
    def handle_join_session(data):
        try:
            session_id = data.get('session_id')
            tablet_id = data.get('tablet_id')
            if session_id:
                join_room(f'session_{session_id}')
                active_connections[request.sid] = {
                    'session_id': session_id,
                    'tablet_id': tablet_id,
                    'room': f'session_{session_id}'
                }
                print(f'Client {request.sid} joined session {session_id}')
                emit('status', {'message': f'Joined session {session_id}'})
        except Exception as e:
            print(f"DEBUG: Exception in handle_join_session: {e}")
            emit('status', {'message': f'Failed to join session {session_id}'})

    @socketio.on('leave_session')
    def handle_leave_session(data):
        try:
            session_id = data.get('session_id')
            if session_id:
                leave_room(f'session_{session_id}')
                print(f'Client {request.sid} left session {session_id}')
        except Exception as e:
            print(f"DEBUG: Exception in handle_leave_session: {e}")
            emit('status', {'message': f'Failed to leave session {session_id}'})

    @socketio.on('some_event')
    def handle_some_event():
        """Placeholder for custom events."""
        pass

    @socketio.on('join_calendar_room')
    def handle_join_calendar_room(data):
        room_id = str(data.get('room_id'))
        room_name = f'calendar_room_{room_id}'

        join_room(room_name)

        print("---- SOCKET DEBUG ----")
        print("SID:", request.sid)

        print("----------------------")

        emit('status', {'message': f'Joined {room_name}'})

    @socketio.on('leave_calandar_room')
    def handle_leave_calendar_room(data):
        try:
            room_id = data.get('room_id')
            if room_id:
                leave_room(f'calendar_room_{room_id}')
                print(f'Client {request.sid} left calendar room {room_id}')

        except Exception as e:
            print(f"DEBUG: Exception in handle_leaver_calendar_room: {e}")
            emit('status',{'message': f'Failed to leave calendar room {room_id}'})


def background_attendance_checker(socketio):
    """Background thread to check for attendance updates."""
    previous_data = {}

    while True:
        try:
            active_sessions = set()
            for conn_data in active_connections.values():
                if 'session_id' in conn_data:
                    active_sessions.add(conn_data['session_id'])

            for session_id in active_sessions:
                try:
                    current_data = get_calendar_details(session_id)
                    if current_data and "attendance" in current_data:
                        attendance_data = current_data["attendance"]
                        session_key = f"session_{session_id}"

                        if session_key in previous_data:
                            if previous_data[session_key] != attendance_data:
                                socketio.emit('attendance_update',
                                              {
                                                  'session_id': session_id,
                                                  'attendance': attendance_data,
                                                  'timestamp': datetime.now().isoformat()
                                              },
                                              room=session_key)

                        previous_data[session_key] = attendance_data
                except Exception as e:
                    print(f"Error checking session {session_id}: {e}")
        except Exception as e:
            print(f"Error in background checker: {e}")

        time.sleep(5)


def start_background_tasks(socketio):
    """Start all background tasks for WebSocket."""
    try:
        # Start attendance checker
        background_thread = threading.Thread(
            target=background_attendance_checker,
            args=(socketio,),
            daemon=True
        )
        background_thread.start()

        print("✅ Background attendance checker started")
    except Exception as e:
        print(f"DEBUG: Exception in start_background_tasks: {e}")