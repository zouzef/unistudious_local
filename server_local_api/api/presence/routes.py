from flask import Blueprint, request, jsonify
import os
import sys
import json
import mysql.connector
from pathlib import Path
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required

# Create blueprint
presence_bp = Blueprint('presence', __name__, url_prefix='/scl')

# Get absolute path relative to this file - pointing to academie_attendance_system
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_SESSIONS_DIR = os.path.abspath(os.path.join(
    CURRENT_FILE_DIR,
    "../../../../academie_attendance_system/dataset"
))
DESTINATION = os.path.abspath(os.path.join(
    CURRENT_FILE_DIR,
    "../../../../academie_attendance_system/user_students"
))
# Maximum images to return per folder
MAX_IMAGES_PER_FOLDER = 6


def get_file_type(filename):
    """Determine file type based on extension"""
    ext = filename.lower().split('.')[-1]
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
        return 'image'
    elif ext in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
        return 'video'
    else:
        return 'unknown'


def update_attendance(attendance_id):
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset=Config.DB_CHARSET,
        autocommit=True
    )
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            UPDATE attendance SET is_present = 1 , slc_edit=1 WHERE id = %s 
        """, (attendance_id,))

        if cursor.rowcount > 0:
            conn.commit()
            print(f"✓ Attendance updated for ID: {attendance_id}")
        else:
            print(f"⚠️  No attendance record found for ID: {attendance_id}")
    except Exception as e:
        print(f"❌ ERROR updating attendance: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def checking_params(user_id, calendar_id, attendance_id):
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            autocommit=True
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) as nbuser FROM user WHERE id = %s
        """, (user_id,))
        user_exists = cursor.fetchone()['nbuser'] > 0

        cursor.execute("""
            SELECT COUNT(*) as nbcalendar FROM relation_calander_group_session WHERE id = %s
        """, (calendar_id,))
        calendar_exists = cursor.fetchone()['nbcalendar'] > 0

        cursor.execute("""
            SELECT COUNT(*) AS nbattendance FROM attendance WHERE id = %s        
        """, (attendance_id,))
        attendance_exists = cursor.fetchone()['nbattendance'] > 0

        if user_exists and calendar_exists and attendance_exists:
            return True
        else:
            return False

    except Exception as e:
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def add_to_audit_image(list_path, user_id, calander_id):
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            autocommit=True
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO sync_images
             ( user_id, images_path, calendar_id)
             VALUES(%s,%s,%s)
        """, (user_id, json.dumps(list_path), calander_id))
        conn.commit()
        print(f"✓ Audit log added for user ID: {user_id}")

    except Exception as e:
        print(f"❌ ERROR connecting to database for audit log: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def add_audit_association(calander_id, user_id, folder_id):
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            autocommit=True
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO association_audit
            (user_id, folder_id, calander_id)
            VALUES(%s,%s,%s)
        """, (user_id, folder_id, calander_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(" INSERT successfully")
            return True
        else:
            return False

    except Exception as e:
        print(f" DEBUG: ERROR from add_audit_association! {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ========================================
# ENDPOINT 1: Associate known student attendance
# ========================================
@presence_bp.route('/associate-known-student-attendance/<int:session_id>', methods=['POST'])
# @token_required
def associate_image_to_user(session_id):
    try:
        print("=== Associate Student Request ===")
        directory = os.path.join(
            BASE_SESSIONS_DIR,
            f"session_{session_id}",
            "face_crops",
            "classified_unknown",
        )

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = data.get('userId')
        folder_name = data.get('folder')
        calendar_id = data.get('calanderId')
        attendance_id = data.get('attendanceId')

        if not (user_id) or not (folder_name) or not (calendar_id) or not (attendance_id):
            error_msg = "Missing required parameters"
            print(f"❌ ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400

        folder_unknown = Path(directory) / folder_name

        if not folder_unknown.exists():
            err_msg = f'Source folder not found: {folder_name}'
            return jsonify({'error': err_msg}), 404

        if not checking_params(user_id, calendar_id, attendance_id):
            err_msg = f'Invalid parameters provided'
            return jsonify({'error': err_msg}), 400

        user_folder = Path(DESTINATION) / str(user_id)

        # Create user folder if it doesn't exist, or use existing one
        if user_folder.exists():
            print(f"✓ User folder exists: {user_folder}")
            print(f"  Adding files to existing folder...")
        else:
            print(f"✓ Creating user folder: {user_folder}")
            user_folder.mkdir(parents=True, exist_ok=True)

        # Move all files from unknown folder to user folder
        moved_count = 0
        moved_files = []
        for file in folder_unknown.glob('*'):
            if file.is_file():
                dest_file = user_folder / file.name

                # Handle duplicate filenames
                if dest_file.exists():
                    counter = 1
                    base_name = file.stem
                    extension = file.suffix
                    while dest_file.exists():
                        new_name = f"{base_name}_{counter}{extension}"
                        dest_file = user_folder / new_name
                        counter += 1
                    print(f"  ⚠️  File exists, renaming to: {dest_file.name}")

                shutil.move(str(file), str(dest_file))
                moved_files.append(str(dest_file))
                moved_count += 1

        print(f"✓ Moved {moved_count} files")

        # Delete empty unknown folder
        try:
            folder_unknown.rmdir()
            print(f"✓ Deleted source folder: {folder_name}")
        except Exception as e:
            print(f"⚠️  Could not delete source folder: {e}")

        update_attendance(attendance_id)
        add_to_audit_image(moved_files, user_id, calendar_id)
        add_audit_association(calendar_id, user_id, folder_name)
        return jsonify({
            'success': True,
            'message': f'Successfully moved {moved_count} files from {folder_name} to user {user_id}',
            'filesMoved': moved_count
        }), 200

    except Exception as e:
        import traceback
        print(f"ERROR in associate_image_to_user: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ========================================
# ENDPOINT 2: Delete folder of unknown user
# ========================================
@presence_bp.route('/delete_folder_user/<int:calander_id>', methods=['DELETE'])
# @token_required
def delete_folder_user_function(calander_id):
    try:
        directory_path = os.path.join(
            BASE_SESSIONS_DIR,
            f"session_{calander_id}",
            "face_crops",
            "classified_unknown"
        )
        data = request.get_json()
        if not (data):
            return jsonify({'error': 'No data provided'}), 400

        folder_name = data.get('folderName')
        if not folder_name:
            return jsonify({'error': 'Missing userId or folderName'}), 400

        folder_name = Path(directory_path) / folder_name
        if not folder_name.exists():
            return jsonify({'error': 'Folder does not exist'}), 404

        shutil.rmtree(str(folder_name))
        return jsonify({'success': True, 'message': 'Folder deleted successfully'}), 200

    except Exception as e:
        return jsonify({"status": f"Error {e}", "message": "Invalid JSON data"}), 500


# ========================================
# ENDPOINT 3: Delete image from folder
# ========================================
@presence_bp.route('/delete_image_folder/<int:calander_id>', methods=['POST'])
# @token_required
def delete_image_from_folder(calander_id):
    try:
        data = request.get_json()
        print(data)
        folder = data.get('folder')
        file_name = data.get('file_name')
        image_path = os.path.join(
            BASE_SESSIONS_DIR,
            f"session_{calander_id}",
            "face_crops",
            "classified_unknown",
            f"{folder}",
            f"{file_name}"
        )
        if (Path(image_path).exists()):
            os.remove(str(image_path))
            return jsonify({'success': True, 'message': 'Image deleted successfully'}), 200
        else:
            return jsonify({'error': 'Image does not exist'}), 404

    except Exception as e:
        return jsonify({"status": f"Error {e}", "message": "Invalid JSON data"}), 500


# ========================================
# ENDPOINT 4: Get unknown student attendance
# ========================================
@presence_bp.route('/get-unknown-student-attendance/<int:calenderId>', methods=['GET'])
# @token_required
def get_unknown_student_attendance(calenderId):
    try:
        query = """
            SELECT at.id as attendanceId, u.id as id, u.full_name as name, u.email 
            FROM attendance as at
            JOIN user as u ON at.user_id = u.id
            WHERE at.calander_id = %s AND at.enabled = 1
        """
        result = Database.execute_query(query, (calenderId,))

        # Build response structure
        students = []
        for row in result:
            students.append({
                "id": row['id'],
                "name": row['name'],
                "email": row['email'],
                "attendanceId": row['attendanceId']
            })

        return jsonify({"success": True, "students": students}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


# ========================================
# ENDPOINT 5: Serve unknown image
# ========================================
@presence_bp.route('/unknown-image/<int:session_id>/<string:person_folder>/<string:filename>', methods=['GET'])
def serve_unknown_image(session_id, person_folder, filename):
    """Serve image files from the classified_unknown directory"""
    try:
        from flask import send_from_directory

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
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ========================================
# ENDPOINT 6: Show attendance unknown students
# ========================================
@presence_bp.route('/show-attendance-unknown/<int:calender_id>', methods=['GET'])
# @token_required
def show_attendance_unknown(calender_id):
    try:
        unknown_grouped = {}
        unknown_dir = os.path.join(
            BASE_SESSIONS_DIR,
            f"session_{calender_id}",
            "face_crops",
            "classified_unknown"
        )
        print(f"Unknown directory: {unknown_dir}")

        if not os.path.exists(unknown_dir):
            return jsonify({
                "unknownFilesGrouped": {},
                "calendarId": calender_id
            })

        for person_folder in sorted(os.listdir(unknown_dir)):
            person_path = os.path.join(unknown_dir, person_folder)

            if not os.path.isdir(person_path):
                continue

            print(f"Processing folder: {person_folder}")
            files = []

            # Get all files first
            all_files = sorted(os.listdir(person_path))

            # Only process up to MAX_IMAGES_PER_FOLDER
            for file in all_files[:MAX_IMAGES_PER_FOLDER]:
                if file.lower().endswith(
                        ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    file_type = get_file_type(file)
                    files.append({
                        "url": f"/scl/unknown-image/{calender_id}/{person_folder}/{file}",
                        "filename": file,
                        "type": file_type
                    })

            if files:
                folder_path = f"{person_folder}"
                unknown_grouped[folder_path] = files

                # Show how many images total vs sent
                total_files = len([f for f in all_files if f.lower().endswith(
                    ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.mp4', '.avi', '.mov', '.mkv', '.webm'))])
                print(f"  Added {len(files)} files for {folder_path} (total: {total_files} files)")

        print(f"Total folders processed: {len(unknown_grouped)}")

        return jsonify({
            "unknownFilesGrouped": unknown_grouped,
            "calendarId": calender_id
        })

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": str(e)}), 500