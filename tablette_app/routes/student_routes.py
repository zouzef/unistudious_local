"""Student-related API endpoints."""
from flask import Blueprint, jsonify, request, send_from_directory
import os
from services.student_service import (
    get_unknown_students,
    get_unknown_student_attendance,
    associate_folder_to_user,
    get_new_group,
    get_students_list,
    add_student_to_attendance,
    delete_unknown_student,
    delete_image_from_folder,
    get_student_current_group
)

student_bp = Blueprint('student', __name__)


@student_bp.route('/api/show-attendance-unknown/<int:calendar_id>')
def show_attendance_unknown(calendar_id):
    """Get list of unknown students detected in a session."""
    try:
        result = get_unknown_students(calendar_id)
        return jsonify(result)
    except Exception as e:
        print(f"DEBUG: Exception in show_attendance_unknown: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/scl/unknown-image/<int:session_id>/<string:person_folder>/<string:filename>', methods=['GET'])
def serve_unknown_image(session_id, person_folder, filename):
    """Serve image files from the classified_unknown directory."""
    try:
        BASE_SESSIONS_DIR = "/home/khalil/Desktop/all_unistudious_project/academie_attendance_system/dataset"

        directory = os.path.join(
            BASE_SESSIONS_DIR,
            f"session_{session_id}",
            "face_crops",
            "classified_unknown",
            person_folder
        )

        print(f"Serving image from directory: {directory}")
        print(f"Filename: {filename}")

        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return jsonify({"error": "Image not found"}), 404

        return send_from_directory(directory, filename)

    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return jsonify({"error": str(e)}), 500


@student_bp.route('/api/get-unknown-student-attendance/<int:calendar_id>')
def get_unknown_student_attendance_route(calendar_id):
    """Get attendance records for unknown students."""
    try:
        result = get_unknown_student_attendance(calendar_id)
        return jsonify(result)
    except Exception as e:
        print(f"DEBUG: Exception in get_unknown_student_attendance_route: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/api/associate-known-student-attendance', methods=['POST'])
def associate_known_student_attendance():
    """Associate an unknown student folder to a known user."""
    try:
        data = request.get_json() or {}
        print(data)

        # Extract the data from request
        user_id = data.get('userId')
        folder = data.get('folder')
        calendar_id = data.get('calanderId')
        attendance_id = data.get('attendanceId')

        print(f"userId: {user_id}")
        print(f"folder: {folder}")
        print(f"calanderId: {calendar_id}")
        print(f"attendanceId: {attendance_id}")

        result = associate_folder_to_user(user_id, folder, calendar_id, attendance_id)

        return jsonify(result), 200

    except Exception as e:
        print(f"DEBUG: Exception in associate_known_student_attendance: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/api/get-new-group/<int:calendar_id>', methods=['POST'])
def get_new_group_route(calendar_id):
    """Get new group information for a calendar."""
    try:
        result = get_new_group(calendar_id)
        return jsonify(result)
    except Exception as e:
        print(f"Exception in get_new_group_route: {e}")
        return jsonify({"error": str(e)}), 500


@student_bp.route('/api/add-student-attendance', methods=['POST'])
def add_student_attendance_route():
    """Add a student to attendance."""
    try:
        from tablette_app import socketio  # Import here to avoid circular import

        # Get data from request (JS will send JSON)
        data = request.get_json()

        user_id = data.get('userId')
        calendar_id = data.get('calendarId')
        group_id = data.get('groupId')
        relation_id = data.get('relationId')
        checkbox1_checked = data.get('checkbox1', False)
        checkbox2_checked = data.get('checkbox2', False)
        selected_group_id = data.get('selectedGroupId')

        print(get_student_current_group(calendar_id, user_id))

        result = add_student_to_attendance(
            user_id, calendar_id, group_id, relation_id,
            checkbox1_checked, checkbox2_checked, selected_group_id
        )

        if result.get('success') == False:
            socketio.emit('status', {'message': '🎯There is no Place for this student'})
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        from tablette_app import socketio
        socketio.emit('status', {'message': 'cant add this user'}, namespace='/')
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@student_bp.route('/api/delete-unknown-student-attendance', methods=['POST'])
def delete_unknown_student_attendance_route():
    """Delete an unknown student folder."""
    try:
        data = request.get_json()
        calendar_id = data.get('calendarId')
        folder = data.get('folder')

        result = delete_unknown_student(calendar_id, folder)
        return jsonify(result)
    except Exception as e:
        print("DEBUG: Exception in delete_unknown_student_attendance_route:", e)
        return jsonify({"error": str(e)}), 500


@student_bp.route('/api/delete-image-from-folder', methods=['POST'])
def delete_image_from_folder_route():
    """Delete a specific image from an unknown student folder."""
    try:
        data = request.get_json()

        result = delete_image_from_folder(
            data.get('calendarId'),
            data.get('filename'),
            data.get('folder')
        )

        if result.get("status") == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@student_bp.route('/slc/list-add-student-attendance/<int:calendar_id>')
def list_add_student_attendance(calendar_id):
    """Get list of all students that can be added to attendance."""
    try:
        result = get_students_list(calendar_id)
        return jsonify(result)
    except Exception as e:
        print("Error:", e)
        return jsonify({"users": []}), 500


@student_bp.route("/slc/attendance-get-group-student-select/<int:calendar_id>/<int:user_id>")
def attendance_get_group_student_select(calendar_id, user_id):
    """Get current group for a student."""
    try:
        result = get_student_current_group(calendar_id, user_id)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Not found"}), 404
    except Exception as e:
        print("DEBUG: Exception in attendance_get_group_student_select:", e)
        return jsonify({"error": str(e)}), 404