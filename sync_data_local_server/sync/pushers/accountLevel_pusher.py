import sys
import os
import json
import logging

import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

# Remote understood the request and refused the data -> undo the local action, no retry
# (403 is NOT here: it is a permission problem, not bad data, so we keep the local data and retry)
REJECT_CODES = {400, 404, 409, 422}


def _rejected(response):
	"""Returned instead of None when the remote refuses the data."""
	return {
		"rejected": True,
		"status_code": response.status_code,
		"reason": response.text,
	}


# ---------------------------------------------------------------------------
# Local rollback
# ---------------------------------------------------------------------------

def _rollback_local_account_level(db, local_id):
	"""Delete the local account_level that the remote refused.
	Only deletes when id_prod IS NULL, so an already-synced row is never removed."""
	cursor = None
	try:
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute("SELECT id_prod FROM account_level WHERE id = %s", (local_id,))
		row = cursor.fetchone()
		if not row:
			logger.warning("Rollback: local account_level id=%s already gone", local_id)
			return True
		if row.get("id_prod"):
			logger.error("Rollback skipped: account_level id=%s already has id_prod=%s", local_id, row["id_prod"])
			return False

		cursor.execute("DELETE FROM account_level WHERE id = %s AND id_prod IS NULL", (local_id,))
		db.connection.commit()

		logger.warning("🗑️ Local account_level id=%s deleted: remote rejected it", local_id)
		return True
	except Exception as e:
		db.connection.rollback()
		logger.exception("Rollback failed for local account_level id=%s: %s", local_id, e)
		return False
	finally:
		if cursor:
			cursor.close()


# ---------------------------------------------------------------------------
# Remote API calls
# ---------------------------------------------------------------------------

def _send_create_accountLevel_api(settings, payload):
	url = None
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-account-level"

		logger.debug("POST %s | payload: %s", url, payload)

		response = requests.post(url, data=payload, headers=headers, timeout=10)

		if response.status_code == 200:
			try:
				response_data = response.json()
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None
			account_level_id = response_data.get('id')
			logger.info("AccountLevel created")
			return True, account_level_id

		elif response.status_code in REJECT_CODES:
			logger.error("Create accountLevel REJECTED %s: %s", response.status_code, response.text)
			return False, _rejected(response)

		elif response.status_code == 403:
			logger.error("Create accountLevel FORBIDDEN (token needs ROLE_SLC): %s", response.text)
			return False, None

		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None

	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None

	except Exception as e:
		logger.exception("Remote API error in create accountLevel: %s", e)
		return False, None


def _send_update_accountLevel_api(settings, payload, accountLevelId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-account-level/{accountLevelId}"

		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountLevel updated — %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False

	except Exception as e:
		logger.exception("Remote API error in _send_update_accountLevel_api: %s", e)
		return False


def _send_delete_accountLevel_api(settings, accountLevelId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-account-level/{accountLevelId}"
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("AccountLevel deleted - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		elif response.status_code == 404:
			# Already gone on remote -> remote already matches local
			logger.warning("Delete accountLevel %s: already gone on remote (%s)", accountLevelId, response.text)
			return True
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False

	except Exception as e:
		logger.exception("Remote API error in _send_delete_accountLevel_api: %s", e)
		return False


# ---------------------------------------------------------------------------
# Push functions (called by pusher dispatcher)
# ---------------------------------------------------------------------------

def push_accountLevelAdd(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_id = new_data.get('id')
		payload = {
			"levelId": new_data.get('level_config_id'),
			"otherLevel": new_data.get('other_level') or None,
			"description": new_data.get('description') or None
		}

		status, result = _send_create_accountLevel_api(settings, payload)

		if not status:
			# Remote refused the data -> undo the local action
			if isinstance(result, dict) and result.get("rejected"):
				logger.error(
					"Remote rejected accountLevel local=%s [%s]: %s",
					local_id, result.get("status_code"), result.get("reason")
				)
				_rollback_local_account_level(db, local_id)
				return True  # handled: the audit row must not be retried
			return False  # network / 403 / 5xx: retry later

		account_level_id = result
		if account_level_id:
			cursor = db.connection.cursor(dictionary=True)
			cursor.execute(
				"UPDATE account_level SET id_prod = %s WHERE id = %s",
				(account_level_id, local_id)
			)
			db.connection.commit()
			cursor.close()
			logger.info("✅ AccountLevel synced: local=%s remote=%s", local_id, account_level_id)
		else:
			logger.error("AccountLevel local=%s created on remote but no id returned", local_id)

		return status

	except Exception as e:
		logger.exception("Error in push_accountLevelAdd: %s", e)
		return False


def push_accountLevelUpdate(db, settings, row):
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_id = new_data.get('id')
		payload = {
			"levelId": new_data.get('level_config_id'),
			"otherLevel": new_data.get('other_level') or None,
			"description": new_data.get('description') or None
		}

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM account_level WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("AccountLevel not found locally for id %s", local_id)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			logger.error("AccountLevel local=%s has no id_prod yet, skipping update", local_id)
			return False

		return _send_update_accountLevel_api(settings, payload, id_prod)

	except Exception as e:
		logger.exception("Error in push_accountLevelUpdate: %s", e)
		return False


def push_accountLevelDelete(db, settings, row):
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		local_id = old_data.get('id')

		cursor = db.connection.cursor(dictionary=True)
		cursor.execute("SELECT id_prod FROM account_level WHERE id = %s", (local_id,))
		result = cursor.fetchone()
		cursor.close()

		if not result:
			logger.error("AccountLevel not found locally for id %s", local_id)
			return False

		id_prod = result['id_prod']
		if not id_prod:
			# Never reached the remote (or its create was rolled back): nothing to delete there
			logger.warning("AccountLevel local=%s has no id_prod, nothing to delete on remote", local_id)
			return True

		return _send_delete_accountLevel_api(settings, id_prod)

	except Exception as e:
		logger.exception("Error in push_accountLevelDelete: %s", e)
		return False