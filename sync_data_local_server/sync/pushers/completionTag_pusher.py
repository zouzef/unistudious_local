import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


logger = logging.getLogger(__name__)

# Remote understood the request and refused the data -> undo the local action, no retry
# (401/403 are NOT here: auth/permission problems, not bad data, so we keep the local data and retry)
REJECT_CODES = {400, 404, 409, 422}


def _rejected(response):
	"""Returned instead of None when the remote refuses the data."""
	return {
		"rejected": True,
		"status_code": response.status_code,
		"reason": response.text,
	}


# ─────────────────────────────────────────────
# Local rollback
# ─────────────────────────────────────────────

def _rollback_local_completionTag(db, local_id):
	"""Delete the local completion tag that the remote refused.
	Only deletes when id_prod IS NULL, so an already-synced tag is never removed."""
	cursor = None
	try:
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute("SELECT id_prod FROM completion_tag_account WHERE id = %s", (local_id,))
		row = cursor.fetchone()
		if not row:
			logger.warning("Rollback: local completion tag id=%s already gone", local_id)
			return True
		if row.get("id_prod"):
			logger.error("Rollback skipped: completion tag id=%s already has id_prod=%s", local_id, row["id_prod"])
			return False

		cursor.execute("DELETE FROM completion_tag_account WHERE id = %s AND id_prod IS NULL", (local_id,))
		db.connection.commit()

		logger.warning("🗑️ Local completion tag id=%s deleted: remote rejected it", local_id)
		return True
	except Exception as e:
		db.connection.rollback()
		logger.exception("Rollback failed for local completion tag id=%s: %s", local_id, e)
		return False
	finally:
		if cursor:
			cursor.close()


# ─────────────────────────────────────────────
# Internal API calls
# ─────────────────────────────────────────────

def _send_create_completionTag_api(settings, payload):
	url = f"{settings.api_base_url}/slc/create-completion-tag-account"
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
			completionTagId = response_data.get('id')
			logger.info("CompletionTag created")
			return True, completionTagId
		elif response.status_code in REJECT_CODES:
			logger.error("Create completion tag REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None
	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in create CompletionTag: %s", e)
		return False, None


def _send_update_completionTag_api(settings, payload, completionTag):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-completion-tag-account/{completionTag}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountSubject updated  - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON  response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_update_completionTag: %s", e)
		return False


def _send_delete_completionTag_api(settings, completionTagId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-completion-tag-account/{completionTagId}"

		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("CompletionTag deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON reponse: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_completionTag_api: %s", e)
		return False


# ─────────────────────────────────────────────
# Push functions (called by pusher dispatcher)
# ─────────────────────────────────────────────

def push_completionTagAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		Name = new_data.get('name')
		Description = new_data.get('description') or None
		CompletionTagIdLocal = new_data.get('id')
		payload = {
			"name": Name,
			"description": Description
		}
		status, result = _send_create_completionTag_api(settings, payload)

		if not status:
			# Remote refused the data -> undo the local action
			if isinstance(result, dict) and result.get("rejected"):
				logger.error(
					"Remote rejected completion tag local=%s [%s]: %s",
					CompletionTagIdLocal, result.get("status_code"), result.get("reason")
				)
				_rollback_local_completionTag(db, CompletionTagIdLocal)
				return True  # handled: the audit row must not be retried
			return False  # network / 5xx / auth error: retry later

		CompletionTagId = result
		if CompletionTagId:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE completion_tag_account SET id_prod = %s WHERE id = %s",
				(CompletionTagId, CompletionTagIdLocal)
			)
			db.connection.commit()
			cursor.close()
			logger.info("✅ CompletionTag synced: local=%s remote=%s", CompletionTagIdLocal, CompletionTagId)
		else:
			logger.error("CompletionTag local=%s created on remote but no id returned", CompletionTagIdLocal)

		return status
	except Exception as e:
		logger.exception("Error in push CompletionTagAdd: %s", e)
		return False


def push_completionTagUpdate(db, settings, row):
	CompletionTagId = None
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		CompletionTagId = new_data.get('id')
		Name = new_data.get('name')
		Description = new_data.get('description') or None
		payload = {
			"name": Name,
			"description": Description
		}
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"SELECT id_prod FROM completion_tag_account WHERE id = %s",
			(CompletionTagId,)
		)
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("CompletionTag not found locally for id %s", CompletionTagId)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			logger.error("CompletionTag local=%s has no id_prod yet, skipping update", CompletionTagId)
			return False

		return _send_update_completionTag_api(settings, payload, id_prod)
	except Exception as e:
		logger.exception("Error in push_completionTagUpdate (id=%s): %s", CompletionTagId, e)
		return False


def push_completionTagDelete(db, settings, row):
	CompletionTag = None
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		CompletionTag = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"SELECT id_prod FROM completion_tag_account WHERE id = %s",
			(CompletionTag,)
		)
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("CompletionTag not found locally for id %s", CompletionTag)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			# Never reached the remote (or its create was rolled back): nothing to delete there
			logger.warning("CompletionTag local=%s has no id_prod, nothing to delete on remote", CompletionTag)
			return True

		return _send_delete_completionTag_api(settings, id_prod)
	except Exception as e:
		logger.exception("Error in push_completionTagDelete (id=%s): %s", CompletionTag, e)
		return False