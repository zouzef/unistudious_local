"""
WebSocket event handlers for admin notifications
"""
from flask import request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

# Store connected administrators by account_id
# Structure: {account_id: session_id}
connected_admins = {}


def register_socketio_events(socketio):
	"""
	Register all SocketIO event handlers for admin notifications

	Args:
		socketio: SocketIO instance
	"""

	@socketio.on('connect')
	def handle_connect():
		"""Handle client connection"""
		try:
			print(f'🔌 Client connected: {request.sid}')
			emit('connection_response', {
				'status': 'connected',
				'sid': request.sid,
				'timestamp': datetime.now().isoformat()
			})
		except Exception as e:
			print(f"❌ Error in handle_connect: {e}")
			emit('error', {'message': 'Connection failed', 'error': str(e)})

	@socketio.on('disconnect')
	def handle_disconnect():
		"""Handle client disconnection"""
		try:
			print(f'🔌 Client disconnected: {request.sid}')

			# Remove from connected admins if they were registered
			for account_id, sid in list(connected_admins.items()):
				if sid == request.sid:
					del connected_admins[account_id]
					print(f'👤 Admin {account_id} disconnected and removed')
					break

		except Exception as e:
			print(f"❌ Error in handle_disconnect: {e}")

	@socketio.on('register_admin')
	def handle_register_admin(data):
		"""
		Register an admin to receive notifications
		"""
		try:
			account_id = data.get('account_id')

			if not account_id:
				emit('registration_failed', {
					'error': 'account_id is required'
				})
				return

			# Convert to string for consistency
			account_id = str(account_id)  # ← ADD THIS LINE

			# Store the admin connection
			connected_admins[account_id] = request.sid

			# Join a room specific to this admin
			join_room(f'admin_{account_id}')

			print(f'✅ Admin {account_id} registered with SID {request.sid}')

			# Send success response
			emit('registration_success', {
				'account_id': account_id,
				'timestamp': datetime.now().isoformat(),
				'message': 'Successfully registered for notifications'
			})

		except Exception as e:
			print(f"❌ Error in handle_register_admin: {e}")
			emit('registration_failed', {
				'error': str(e),
				'timestamp': datetime.now().isoformat()
			})

	@socketio.on('unregister_admin')
	def handle_unregister_admin(data):
		"""
		Unregister an admin from receiving notifications

		Expected data: {
			'account_id': int
		}
		"""
		try:
			account_id = data.get('account_id')

			if account_id and account_id in connected_admins:
				# Leave the admin room
				leave_room(f'admin_{account_id}')

				# Remove from connected admins
				del connected_admins[account_id]

				print(f'👋 Admin {account_id} unregistered')

				emit('unregister_success', {
					'account_id': account_id,
					'message': 'Successfully unregistered'
				})
			else:
				emit('unregister_failed', {
					'error': 'Admin not found or not registered'
				})

		except Exception as e:
			print(f"❌ Error in handle_unregister_admin: {e}")
			emit('error', {'message': str(e)})

	@socketio.on('ping')
	def handle_ping():
		"""Handle ping from client to keep connection alive"""
		emit('pong', {'timestamp': datetime.now().isoformat()})

	print("✅ WebSocket event handlers registered")


def send_calendar_request_notification(socketio, account_id, notification_data):
	try:
		# Convert to string for consistency
		account_id = str(account_id)  # ← ADD THIS LINE

		print(f"🔍 Looking for admin {account_id} in {list(connected_admins.keys())}")  # Debug

		if account_id in connected_admins:
			formatted_notification = {
				'title': notification_data.get('description', 'New Calendar Request'),
				'time': notification_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
				'avatar': None,
				'request_id': notification_data.get('request_id'),
				'start_date': notification_data.get('start_date'),
				'start_time': notification_data.get('start_time'),
				'end_time': notification_data.get('end_time')
			}

			print(f"📤 Sending formatted notification: {formatted_notification}")

			socketio.emit(
				'calendar_notification',
				formatted_notification,
				room=f'admin_{account_id}'
			)

			print(f'✅ Notification sent to admin {account_id}')
			return True
		else:
			print(f'⚠️ Admin {account_id} is not currently connected')
			return False

	except Exception as e:
		print(f"❌ Error sending notification to admin {account_id}: {e}")
		import traceback
		print(traceback.format_exc())
		return False


def get_connected_admins():
	"""
	Get list of currently connected admin IDs

	Returns:
		list: List of connected admin account IDs
	"""
	return list(connected_admins.keys())


def is_admin_connected(account_id):
	"""
	Check if a specific admin is currently connected

	Args:
		account_id: ID of the admin to check

	Returns:
		bool: True if admin is connected, False otherwise
	"""
	return account_id in connected_admins