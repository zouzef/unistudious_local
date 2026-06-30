"""
All Table Models
Each class = one table. Edit columns here, changes apply on next run automatically.
"""
from email.policy import default

from core.models.base_model import BaseModel, Column

# from sync_data_local_server.utils.helpers import format_date


# ----------------------------------- Account Models -----------------------------------
class AccountModel(BaseModel):
	table_name = "account"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_type_id", "INT(11)"),
		Column("file_link", "VARCHAR(255)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("status", "TINYINT(1)", nullable=False, default="0"),
		Column("other_type", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("slc_use", "INT(11)", default="0"),
	]
class AccountAuditModel(BaseModel):
	table_name = "account_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class AccountSubjectModel(BaseModel):
	table_name = "account_subject"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("subject_config_id", "INT(11)"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("other_subject", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("slc_use", "INT(11)", default="0"),
		Column("id_prod", "INT(11)", default=None)
	]
class AccountSubjectAuditModel(BaseModel):
	table_name = "account_subject_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class RelationTeacherAccount(BaseModel):
	table_name = "relation_teacher_account"
	columns = [
        Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
        Column("account_id", "INT(11)", default=None),
        Column("user_id", "INT(11)", default=None),
        Column("status", "TINYINT(1)", nullable=False, default=0),
        Column("enabled", "TINYINT(1)", nullable=False, default=1),
        Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
        Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
        Column("updated_at", "DATETIME", default=None),
        Column("uuid", "VARCHAR(255)", nullable=False),
        Column("release_token", "TINYINT(1)", nullable=False, default=0),
        Column("use_token", "VARCHAR(255)", default=None),
        Column("access_permissions", "LONGTEXT", default=None),
        Column("invitation_relation_teacher_account_id", "INT(11)", default=None),
        Column("cloud_path", "VARCHAR(255)", default=None),
        Column("access_session", "LONGTEXT", default=None),
		Column("door_id", "VARCHAR(255)", default=None),
		Column("id_prod", "INT(11)", default=None)
	]
class RelationTeacherAccountAudit(BaseModel):
	table_name = "relation_teacher_account_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ----------------------------------- TAG Models -----------------------------------
class TagConfigModel(BaseModel):
	table_name = "tag_config"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("title", "VARCHAR(255)", nullable=False),  # SQL uses "title", not "name"
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
	]

class AccountTagModel(BaseModel):
	table_name = "account_tag"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("tag_config_id", "INT(11)"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("other_tag", "VARCHAR(255)"),
		Column("public", "TINYINT(1)", nullable=False, default="1"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod", "INT(11)", default=None)
	]
class AccountTagAuditModel(BaseModel):
	table_name = "account_tag_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class RelationCompletionTag(BaseModel):
	table_name = "relation_completion_tag"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("tag_id", "INT(11)", nullable=None),
		Column("account_id", "INT(11)", nullable=None),
		Column("calander_group_id", "INT(11)", nullable=None),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("release_token", "TINYINT(1)", nullable=False, default="0"),
		Column("use_token", "VARCHAR(255)"),
		Column("id_prod", "INT(11)", default=None)
	]
class RelationCompletionTagAudit(BaseModel):
	table_name = "relation_completion_tag_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class CompletionTagAccount(BaseModel):
	table_name = "completion_tag_account"
	collate = "utf8mb4_general_ci"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("name", "VARCHAR(255)"),
		Column("description", "LONGTEXT"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("img_link", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("release_token", "TINYINT(1)", nullable=False, default="0"),
		Column("use_token", "VARCHAR(255)"),
		Column("id_prod", "INT(11)", default=None)
	]
class CompletionTagAudit(BaseModel):
	table_name = "completion_tag_account_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class CompletionTagUser(BaseModel):
	table_name = "completion_tag_user"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("user_id", "INT(11)", default=None),
		Column("tag_id", "INT(11)", default=None),
		Column("session_id", "INT(11)", default=None),
		Column("account_id", "INT(11)", default=None),
		Column("group_calander_id", "INT(11)", default=None),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("release_token", "TINYINT(1)", nullable=False, default="0"),
		Column("use_token", "VARCHAR(255)", default=None),
		Column("id_prod", "INT(11)", default=None)

	]
class CompletionTagUserAudit(BaseModel):
	table_name = "completion_tag_user_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ------------------------------------ CALANDER Models -----------------------------------
class RelationCalanderGroupAuditModel(BaseModel):
	table_name = "relation_calander_group_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "VARCHAR(30)"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
		Column("id_calander", "INT(11)"),
	]
class RelationCalanderGroupSessionModel(BaseModel):
	table_name = "relation_calander_group_session"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("session_id", "INT(11)"),
		Column("account_id", "INT(11)"),
		Column("local_id", "INT(11)"),
		Column("group_session_id", "INT(11)"),
		Column("room_id", "INT(11)"),
		Column("teacher_id", "INT(11)"),
		Column("subject_id", "INT(11)"),
		Column("color", "VARCHAR(255)"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("start_time", "DATETIME"),
		Column("end_time", "DATETIME"),
		Column("ref", "VARCHAR(255)"),
		Column("date", "DATETIME"),
		Column("refresh", "TINYINT(1)", nullable=False, default="0"),
		Column("title", "VARCHAR(255)", nullable=False),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("type", "VARCHAR(255)"),
		Column("teacher_present", "TINYINT(1)", nullable=False, default="0"),
		Column("force_teacher_present", "TINYINT(1)", nullable=False, default="0"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("slc_use", "INT(11)", default="0"),
		Column("id_prod", "INT(11)"),
	]

class RelationGroupLocalSessionModel(BaseModel):
	table_name = "relation_group_local_session"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("session_id", "INT(11)"),
		Column("local_id", "INT(11)"),
		Column("account_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("capacity", "VARCHAR(255)"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("special_group", "TINYINT(1)"),
		Column("access_type", "TINYINT(1)"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("slc_use", "INT(11)", default="0"),
		Column("id_prod", "INT(11)"),
	]
class RelationGroupLocalSessionAuditModel(BaseModel):
	table_name = "relation_group_local_session_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class CalendarRequestModel(BaseModel):
	table_name = "calendar_request"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("session_id", "INT(11)", nullable=False),
		Column("group_id", "INT(11)", nullable=False),
		Column("type", "CHAR(1)", nullable=False),
		Column("room_id", "INT(11)", nullable=False),
		Column("subject_id", "INT(11)"),
		Column("user_id", "INT(11)"),
		Column("completion_tags", "VARCHAR(255)"),
		Column("duplicate", "VARCHAR(20)", default="'none'"),
		Column("start_time", "TIME", nullable=False),
		Column("end_time", "TIME", nullable=False),
		Column("end_date", "DATE"),
		Column("description", "TEXT"),
		Column("account_id", "INT(11)", nullable=False),
		Column("accepted", "TINYINT(1)", default="0"),
		Column("created_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("updated_at", "TIMESTAMP", nullable=False, default="current_timestamp()",
			   on_update="current_timestamp()"),
		Column("enabled", "INT(11)", default="1"),
		Column("start_date", "DATE", nullable=False),
		Column("slc_edit", "INT(11)", default="0"),
	]

class RelationCalanderAuditModel(BaseModel):
	table_name = "relation_calander_audit"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("calander_id", "INT(11)", nullable=False),
		Column("unknown_folder_path", "VARCHAR(800)"),
		Column("is_synced", "INT(11)", default="0"),
		Column("created_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("synced_at", "TIMESTAMP"),
	]


# ------------------------------------ Attendance Models -----------------------------------
class AttendanceModel(BaseModel):
	table_name = "attendance"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("user_id", "INT(11)"),
		Column("session_id", "INT(11)"),
		Column("account_id", "INT(11)"),
		Column("group_session_id", "INT(11)"),
		Column("calander_id", "INT(11)"),
		Column("payment_session_id", "INT(11)"),
		Column("is_present", "TINYINT(1)", nullable=False, default="0"),
		Column("day", "DATETIME"),
		Column("note", "LONGTEXT"),
		Column("is_editable", "TINYINT(1)", nullable=False, default="1"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("is_sync", "INT(11)", default="0"),
		Column("slc_edit", "INT(11)", default="0"),
		Column("id_prod", "INT(11)"),
	]
class AttendanceAuditModel(BaseModel):
	table_name = "attendance_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "VARCHAR(30)"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
		Column("id_attendance", "INT(11)"),
		Column("id_calander", "INT(11)"),
	]


# ------------------------------------ SLC Models -----------------------------------
class CameraModel(BaseModel):
	table_name = "camera"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("slc_id", "INT(11)"),
		Column("room_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("mac_id", "VARCHAR(255)"),
		Column("username", "VARCHAR(255)"),
		Column("password", "VARCHAR(255)"),
		Column("type", "VARCHAR(50)", nullable=False, default="'webcam'"),
		Column("status", "VARCHAR(50)", nullable=False, default="'Active'"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod", "INT(11)", default=None)
	]
class CameraAuditModel(BaseModel):
	table_name = "camera_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class LocalModel(BaseModel):
	table_name = "local"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("address", "LONGTEXT", nullable=False),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("gps", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("default_local", "TINYINT(1)", nullable=False, default="0"),
	]
class LocalAuditModel(BaseModel):
	table_name = "local_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


class RoomModel(BaseModel):
	table_name = "room"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("local_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("capacity", "VARCHAR(255)", nullable=False),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("slc_use", "INT(11)", default="0"),
	]
class RoomAuditModel(BaseModel):
	table_name = "room_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class SlcModel(BaseModel):
	table_name = "slc"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("uuid", "VARCHAR(255)"),
		Column("username", "VARCHAR(255)"),
		Column("slc_username", "VARCHAR(255)"),
		Column("slc_password", "VARCHAR(255)"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("account_id", "INT(11)"),
	]
class SlcAuditModel(BaseModel):
	table_name = "slc_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class SlcLocalModel(BaseModel):
	table_name = "slc_local"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("slc_id", "INT(11)"),
		Column("account_id", "INT(11)"),
		Column("local_id", "INT(11)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
	]
class SlcLocalAuditModel(BaseModel):
	table_name = "slc_local_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class TabletModel(BaseModel):
	table_name = "tablet"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("slc_id", "INT(11)"),
		Column("room_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("mac_id", "VARCHAR(255)", nullable=False),
		Column("password", "VARCHAR(255)", nullable=False),
		Column("status", "VARCHAR(50)", nullable=False, default="'Active'"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("slc_edit", "TINYINT(1)", default="0"),
		Column("id_prod", "INT(11)", default=None)
	]
class TabletAuditModel(BaseModel):
	table_name = "tablet_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class SlcDoorModel(BaseModel):
	table_name = "slc_door"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("slc_id", "INT(11)"),
		Column("room_id", "INT(11)"),
		Column("local_id", "INT(11)"),
		Column("mac_id", "VARCHAR(255)", nullable=False),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("password", "VARCHAR(255)", nullable=False),
		Column("status", "VARCHAR(50)", nullable=False, default="'False'"),
		Column("oc", "BOOLEAN", nullable=False, default="0"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod","TINYINT(1)", default="0")
	]
class SlcDoorAuditModel(BaseModel):
	table_name = "slc_door_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

# ------------------------------------ SESSION Models -----------------------------------
class RelationUserSessionModel(BaseModel):
	table_name = "relation_user_session"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("user_id", "INT(11)"),
		Column("session_id", "INT(11)"),
		Column("relation_group_local_session_id", "INT(11)"),
		Column("ref", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("slc_use", "INT(11)", default="0"),
	]
class RelationUserSessionAuditModel(BaseModel):
	table_name = "relation_user_session_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class SessionModel(BaseModel):
	table_name = "session"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("formation_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("description", "LONGTEXT"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("img_link", "VARCHAR(255)"),
		Column("start_date", "DATETIME", nullable=False),
		Column("end_date", "DATETIME", nullable=False),
		Column("capacity", "VARCHAR(255)", nullable=False),
		Column("price", "VARCHAR(255)"),
		Column("currency", "VARCHAR(255)"),
		Column("type_pay", "VARCHAR(255)", nullable=False),
		Column("request_change_group", "TINYINT(1)"),
		Column("max_group_change", "VARCHAR(255)"),
		Column("payment_methode", "VARCHAR(255)"),
		Column("number_session_for_pay", "VARCHAR(255)"),
		Column("price_student_absent", "VARCHAR(255)"),
		Column("user_register_after_start", "TINYINT(1)", nullable=False, default="1"),
		Column("public_resource", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("uuid", "VARCHAR(255)", nullable=False),
		Column("price_presence", "VARCHAR(255)"),
		Column("price_online", "VARCHAR(255)"),
		Column("special_group", "TINYINT(1)"),
		Column("passage", "TINYINT(1)"),
		Column("season_id", "INT(11)"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("slc_use", "INT(11)", default="0"),
		Column("id_prod", "INT(11)")
	]
class SessionAuditModel(BaseModel):
	table_name = "session_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
		Column("id_session", "INT(11)"),
	]

class RelationLocalSession(BaseModel):
	table_name = "relation_local_session"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("local_id", "INT(11)", default=None),
		Column("session_id", "INT(11)", default=None),
		Column("enabled", "TINYINT(1)", default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod", "INT(11)", default=None)
	]
class RelationLocalSessionAudit(BaseModel):
	table_name = "relation_local_session_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ------------------------------------ PAYMENT Models -----------------------------------
class PaymentSessionModel(BaseModel):
	table_name = "payment_session"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("session_id", "INT(11)"),
		Column("user_id", "INT(11)"),
		Column("type", "VARCHAR(255)", nullable=False),
		Column("type_date", "VARCHAR(255)"),
		Column("type_number_session", "VARCHAR(255)"),
		Column("date_payment", "DATETIME"),
		Column("status", "VARCHAR(255)", default="'Pending'"),
		Column("amount", "VARCHAR(255)"),
		Column("created_by", "VARCHAR(255)"),
		Column("price", "VARCHAR(255)"),
		Column("description", "LONGTEXT"),
		Column("forcing", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("uuid", "VARCHAR(255)", nullable=False),
	]
class PaymentSessionAuditModel(BaseModel):
	table_name = "payment_session_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "VARCHAR(30)"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class InvoiceModel(BaseModel):
	table_name = "invoice"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("user_id", "INT(11)"),
		Column("session_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("type", "VARCHAR(255)", nullable=False),
		Column("file_link", "VARCHAR(255)", nullable=False),
		Column("description", "LONGTEXT"),
		Column("is_status", "TINYINT(1)", nullable=False, default="1"),
		Column("created_by", "VARCHAR(255)"),
		Column("total_amount", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("payment_session_id", "INT(11)"),
	]


# ------------------------------------ FORMATION Models -----------------------------------
class FormationModel(BaseModel):
	table_name = "formation"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("account_level_id", "INT(11)"),
		Column("account_section_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("description", "LONGTEXT"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("type_date", "VARCHAR(255)", nullable=False),
		Column("other_type_date", "VARCHAR(255)"),
		Column("type_session", "VARCHAR(255)", nullable=False),
		Column("other_type_session", "VARCHAR(255)"),
		Column("number_day_duration", "VARCHAR(255)"),
		Column("number_session", "VARCHAR(255)"),
		Column("condition_of_passage", "VARCHAR(255)", nullable=False),
		Column("condition_of_passage_formule", "VARCHAR(255)"),
		Column("condition_of_passage_formule_by_note", "VARCHAR(255)"),
		Column("condition_of_passage_formule_by_present", "VARCHAR(255)"),
		Column("condition_of_passage_formule_by_note_present", "VARCHAR(255)"),
		Column("img_link", "VARCHAR(255)"),
		Column("public_resource", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()", on_update="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod", "INT(11)", default=None)
	]
class FormationAuditModel(BaseModel):
	table_name = "formation_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ------------------------------------ LEVEL Models -----------------------------------
class LevelConfigModel(BaseModel):
	table_name = "level_config"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
	]

class AccountLevelModel(BaseModel):
	table_name = "account_level"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("level_config_id", "INT(11)"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("other_level", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		# FIX: SQL uses release_token (snake_case) and use_token + slc_edit, not releaseToken/useToken
		Column("release_token", "TINYINT(1)", nullable=False, default="0"),
		Column("use_token", "VARCHAR(255)"),
		Column("slc_edit", "INT(11)", default="0"),
		Column("id_prod", "INT(11)", default=None)
	]
class AccountLevel_Audit(BaseModel):
	table_name = "account_level_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ----------------------------------- SUBJECT Models -----------------------------------
class SubjectConfigModel(BaseModel):
	table_name = "subject_config"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("description", "LONGTEXT"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
	]
class SubjectConfigAuditModel(BaseModel):
	table_name = "subject_config_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class RelationTeacherToSubjectGroupModel(BaseModel):
	table_name = "relation_teacher_to_subject_group"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("relation_group_local_session_id", "INT(11)"),
		Column("subject_id", "INT(11)"),
		Column("user_id", "INT(11)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("releaseToken", "TINYINT(1)"),
		Column("useToken", "VARCHAR(255)"),
		Column("slc_use", "INT(11)", default="0"),
		Column("id_prod", "INT(11)"),
	]
class RelationTeacherToSubjectGroupAuditModel(BaseModel):
	table_name = "relation_teacher_to_subject_group_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ----------------------------------- USER Models -----------------------------------
class UserModel(BaseModel):
    table_name = "user"
    columns = [
        Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
        Column("account_id", "INT(11)"),
        Column("username", "VARCHAR(180)", nullable=False),
        Column("email", "VARCHAR(255)", nullable=False),
        Column("full_name", "VARCHAR(255)"),
        Column("roles", "LONGTEXT", nullable=False),
        Column("img_link", "VARCHAR(255)"),
        Column("reset_token", "VARCHAR(255)"),
        Column("status", "TINYINT(1)", nullable=False, default="1"),  # ✅ was "0", string "Active" caused error
        Column("created_by", "INT(11)", nullable=False, default="0"), # ✅ added default
        Column("password", "VARCHAR(255)", nullable=False),
        Column("birth_date", "DATE"),                                  # ✅ was DATETIME, birth date doesn't need time
        Column("birth_place", "VARCHAR(255)"),
        Column("phone", "VARCHAR(255)"),
        Column("address", "VARCHAR(255)"),
        Column("grand", "TINYINT(1)", default="0"),                   # ✅ was VARCHAR(255), semantically a flag
        Column("access_type", "VARCHAR(255)"),
        Column("access_type_date", "DATETIME"),
        Column("enabled", "TINYINT(1)", nullable=False, default="1"),
        Column("created_at", "DATETIME", nullable=True, default="current_timestamp()"),
        Column("timestamp", "DATETIME", nullable=True, default="current_timestamp()"),
        Column("updated_at", "DATETIME"),
        Column("uuid", "VARCHAR(255)", nullable=True),
        Column("facebook_id", "VARCHAR(255)"),
        Column("google_id", "VARCHAR(255)"),
        Column("mastodon_access_token", "VARCHAR(255)"),
        Column("general_notification", "TINYINT(1)", nullable=False, default="1"),
        Column("message_notification", "TINYINT(1)", nullable=False, default="1"),
        Column("calendar_notification", "TINYINT(1)", nullable=False, default="1"),
        Column("push_notification", "TINYINT(1)", nullable=False, default="1"),
        Column("sms_notification", "TINYINT(1)", nullable=False, default="1"),
        Column("login_notification", "TINYINT(1)", nullable=False, default="1"),
        Column("horsline", "TINYINT(1)", nullable=False, default="0"),
        Column("ref_slc", "VARCHAR(255)"),
        Column("apple_id", "VARCHAR(255)"),
        Column("open_source_user_name", "VARCHAR(255)"),
        Column("rocket_chat_user_id", "VARCHAR(255)"),
        Column("fcm_web", "VARCHAR(255)"),
        Column("fcm_android", "VARCHAR(255)"),
        Column("fcm_ios", "VARCHAR(255)"),
        Column("releaseToken", "TINYINT(1)", default="0"),            # ✅ added default
        Column("useToken", "VARCHAR(255)"),
        Column("slc_use", "INT(11)", default="0"),
        Column("isvirtual", "TINYINT(1)", default="0"),
        Column("door_id", "VARCHAR(255)", default="0"),
        Column("slc_edit", "INT(11)", default="0"),
		Column("id_prod", "INT(11)",default=None)
    ]
class UserAuditModel(BaseModel):
	table_name = "user_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True),
		Column("user_id", "INT(11)", nullable=False),  # FK to user.id
		Column("role", "VARCHAR(255)", nullable=False),  # e.g. ROLE_TEACHER, ROLE_MANAGER_ADMINISTRATIVE
		Column("action_type", "VARCHAR(50)", nullable=False),  # CREATE, UPDATE, DELETE
		Column("payload", "LONGTEXT"),  # JSON snapshot of the user data
		Column("is_synced", "TINYINT(1)", default="0"),  # 0 = pending, 1 = pushed
		Column("created_at", "DATETIME", default="current_timestamp()"),
	]

class VirtualUserModel(BaseModel):
	table_name = "virtual_user"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("user_id", "INT(11)"),
		Column("created_by_id", "INT(11)"),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("data", "LONGTEXT"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("uuid", "VARCHAR(255)", nullable=False),
		Column("phone", "VARCHAR(255)"),
		Column("email", "VARCHAR(255)"),
		Column("status", "TINYINT(1)", default="1"),
		Column("release_token", "TINYINT(1)", nullable=False, default="0"),
		Column("use_token", "VARCHAR(255)"),
		Column("slc_edit", "INT(11)", default="0"),
	]
class VirtualUserAuditModel(BaseModel):
	table_name = "virtual_user_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "VARCHAR(10)", nullable=False),
		Column("record_id", "INT(11)", nullable=False),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", nullable=False, default="0"),
	]


# ----------------------------------- SEASON Models -----------------------------------
class Season(BaseModel):
	table_name = "season"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("formation_id", "INT(11)"),
		Column("account_id", "INT(11)"),
		Column("title", "VARCHAR(255)"),
		Column("description", "LONGTEXT"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("type_duration", "VARCHAR(255)", nullable=False),
		Column("number_duration", "VARCHAR(255)", nullable=False),
		Column("enabled", "TINYINT(1)", default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod", "INT(11)", default=None),
		Column("ref", "VARCHAR(255)", default=None)
	]
class SeasonAudit(BaseModel):
	table_name = "season_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class SeasonSubSubject(BaseModel):
	table_name = "season_sub_subject"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("season_id", "INT(11)", default=None),
		Column("formation_sub_subject", "INT(11)", default=None),
		Column("enabled", "TINYINT(1)", default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("ref", "VARCHAR(255)", default=None),
		Column("id_prod", "INT(11)", default=None)
	]
class SeasonSubSubjectAudit(BaseModel):
	table_name = "SeasonSubSubject_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]


# ----------------------------------- SECTION Models -----------------------------------
class SectionConfigModel(BaseModel):
	table_name = "section_config"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("name", "VARCHAR(255)", nullable=False),
		Column("description", "LONGTEXT"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
	]

class AccountSectionModel(BaseModel):
	table_name = "account_section"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("account_id", "INT(11)"),
		Column("section_config_id", "INT(11)"),
		Column("status", "TINYINT(1)", nullable=False, default="1"),
		Column("description", "LONGTEXT"),
		Column("other_section", "VARCHAR(255)"),
		Column("enabled", "TINYINT(1)", nullable=False, default="1"),
		Column("created_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("timestamp", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("updated_at", "DATETIME"),
		Column("id_prod", "INT(11)", default=None)
	]
class AccountSectionAuditModel(BaseModel):
	table_name = "account_section_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "VARCHAR(10)", nullable=False),
		Column("record_id", "INT(11)", nullable=False),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "DATETIME", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", nullable=False, default="0"),
	]


# ----------------------------------- LOCAL SPECIAL Models -----------------------------------
class AssociationAuditModel(BaseModel):
	table_name = "association_audit"
	collate = "utf8mb4_general_ci"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("user_id", "INT(11)", nullable=False),
		Column("folder_id", "INT(11)", nullable=False),
		Column("calander_id", "INT(11)", nullable=False),
		Column("is_synced", "INT(11)", default="0"),
		Column("created_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("synced_at", "TIMESTAMP"),
	]

class NotificationModel(BaseModel):
	table_name = "notification"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("user_id", "INT(11)", nullable=False),
		Column("title", "VARCHAR(255)", nullable=False),
		Column("message", "TEXT", nullable=False),
		Column("type", "VARCHAR(50)"),
		Column("is_read", "TINYINT(1)", default="0"),
		Column("created_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("notif_data", "LONGTEXT"),
		Column("enabled", "INT(11)", default="1"),
	]

class PushedRecordsTrackingModel(BaseModel):
	table_name = "pushed_records_tracking"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("table_name", "VARCHAR(255)", nullable=False),
		Column("audit_id", "INT(11)", nullable=False),
		Column("pushed_at", "DATETIME", default="current_timestamp()"),
	]

class SpecialTableModel(BaseModel):
	table_name = "special_table"
	columns = [
		Column("id_slc", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("mac_slc", "VARCHAR(30)", nullable=False),
		Column("pass", "VARCHAR(100)", nullable=False),
	]

class SyncImagesModel(BaseModel):
	table_name = "sync_images"
	columns = [
       Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),  # ← rename id to audit_id
       Column("user_id", "INT(11)"),
       Column("images_path", "TEXT"),
       Column("calendar_id", "INT(11)"),
       Column("action_type", "VARCHAR(20)", default="'INSERT'"),  # ← add action column
       Column("is_synced", "INT(11)", default="0"),
       Column("created_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
       Column("synced_at", "TIMESTAMP"),
    ]

class SyncStatusModel(BaseModel):
	table_name = "sync_status"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("last_sync_time", "DATETIME"),
		Column("created_at", "DATETIME", default="current_timestamp()"),
		Column("is_sync", "INT(11)", default="0"),
	]

class SyncStatusAuditModel(BaseModel):
	table_name = "sync_status_audit"
	columns = [
		Column("audit_id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("action_type", "ENUM('INSERT','UPDATE','DELETE')"),
		Column("old_data", "LONGTEXT"),
		Column("new_data", "LONGTEXT"),
		Column("changed_at", "TIMESTAMP", nullable=False, default="current_timestamp()"),
		Column("is_synced", "TINYINT(1)", default="0"),
	]

class YourTableModel(BaseModel):
	table_name = "your_table"
	collate = "utf8mb4_general_ci"
	columns = [
		Column("id", "INT(11)", primary_key=True, auto_increment=True, nullable=False),
		Column("data", "LONGTEXT"),  # JSON-validated in SQL (CHECK json_valid)
		Column("settings", "LONGTEXT"),  # JSON-validated in SQL
		Column("metadata", "LONGTEXT"),  # JSON-validated in SQL
	]

class SyncFoldersModel(BaseModel):
	table_name = "sync_folders"
	collate = "utf8mb4_general_ci"
	columns = [
        Column("audit_id",          "INT(11)",      primary_key=True, auto_increment=True, nullable=False),
        Column("folder_name", "VARCHAR(255)", nullable=False),
        Column("images_path", "LONGTEXT",     nullable=False),   # JSON array of image paths
        Column("calendar_id", "INT(11)",      nullable=False),
        Column("is_synced",   "INT(11)",      default=0),
        Column("created_at",  "TIMESTAMP",    default="current_timestamp()"),
        Column("synced_at",   "TIMESTAMP",    nullable=True),
		Column("action_type", "VARCHAR(20)", default="'INSERT'"),

	]


# ============================================================= CREATION OF THE MODELS =============================================================
ALL_MODELS = [
	AccountModel,
	AccountAuditModel,
	AccountLevelModel,
	AccountLevel_Audit,
	AccountSubjectModel,
	AccountSectionAuditModel,
	AccountSubjectAuditModel,
	AssociationAuditModel,
	AttendanceModel,
	AttendanceAuditModel,
	CalendarRequestModel,
	CameraModel,
	CameraAuditModel,
	FormationModel,
	InvoiceModel,
	LevelConfigModel,
	LocalModel,
	LocalAuditModel,
	NotificationModel,
	PaymentSessionModel,
	PaymentSessionAuditModel,
	PushedRecordsTrackingModel,
	RelationCalanderAuditModel,
	RelationCalanderGroupAuditModel,
	RelationCalanderGroupSessionModel,
	RelationGroupLocalSessionModel,
	RelationGroupLocalSessionAuditModel,
	RelationTeacherToSubjectGroupModel,
	RelationTeacherToSubjectGroupAuditModel,
	RelationUserSessionModel,
	RelationUserSessionAuditModel,
	RoomModel,
	RoomAuditModel,
	SessionModel,
	SessionAuditModel,
	SlcModel,
	SlcAuditModel,
	SlcLocalModel,
	SlcLocalAuditModel,
	SpecialTableModel,
	SubjectConfigModel,
	SubjectConfigAuditModel,
	SyncImagesModel,
	SyncStatusModel,
	SyncStatusAuditModel,
	TabletModel,
	TabletAuditModel,
	UserModel,
	UserAuditModel,
	VirtualUserModel,
	VirtualUserAuditModel,
	CompletionTagAccount,
	CompletionTagAudit,
	SectionConfigModel,
	AccountSectionModel,
	TagConfigModel,
	AccountTagModel,
	AccountTagAuditModel,
	YourTableModel,
	FormationAuditModel,
	Season,
	SeasonAudit,
	SeasonSubSubject,
	SeasonSubSubjectAudit,
	RelationLocalSession,
	RelationLocalSessionAudit,
	RelationTeacherAccount,
	RelationTeacherAccountAudit,
	RelationCompletionTag,
	RelationCompletionTagAudit,
	SyncFoldersModel,
	SlcDoorModel,
	SlcDoorAuditModel
]
