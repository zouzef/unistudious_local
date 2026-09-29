import logging
import os
import sys
import json
import requests
from core.auth import get_token

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


def _send_create_formation_api(settings, payload, files=None):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/create-formation"
		logger.debug("POST %s | payload: %s", url, payload)
		response = requests.post(url, data=payload, files=files, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				print("\n \n Response_data: ",response_data)
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False, None

			if not response_data.get('status'):
				logger.error("API returned status=false: %s", response_data)
				return False, None

			formation_data = response_data.get('data') or {}

			if formation_data.get('id') is None:
				logger.error("No 'id' in response data: %s", response_data)
				return False, None

			logger.info("Formation created - id %s", formation_data.get('id'))
			return True, formation_data
		elif response.status_code == 400:
			logger.error("Api Error 400: %s", response.text)
			return False, None
		elif response.status_code == 403:
			logger.error("Access denied (403): %s", response.text)
			return False, None
		else:
			logger.error("Unexpected status %s: %s", response.status_code, response.text)
			return False, None
	except requests.exceptions.Timeout:
		logger.error("Request timeout (10s) — %s", url)
		return False, None
	except Exception as e:
		logger.exception("Remote API error in create Formation: %s", e)
		return False, None


def _send_update_formation_api(settings, payload, formationId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/update-formation/{formationId}"
		response = requests.post(url, data=payload, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Formation updated - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_update_formation_api: %s", e)
		return False


def _send_delete_formation_api(settings, formationId):
	try:
		token = get_token()
		headers = {"Authorization": f"Bearer {token}"}
		url = f"{settings.api_base_url}/slc/delete-formation/{formationId}"
		response = requests.post(url, headers=headers, timeout=10)
		if response.status_code == 200:
			try:
				response_data = response.json()
				logger.info("Formation delete - %s", response_data)
				return True
			except Exception:
				logger.error("Invalid JSON response: %s", response.text)
				return False
		else:
			logger.error("Remote API returned %s: %s", response.status_code, response.text)
			return False
	except Exception as e:
		logger.exception("Remote API error in _send_delete_formation_api: %s", e)
		return False


def push_formationAdd(db, settings, row):
	files = None
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		local_formation_id = new_data.get('id')

		cursor = db.connection.cursor(dictionary=True)

		# ---- Already pushed? (avoid duplicates on retry) ----
		cursor.execute("SELECT id_prod FROM formation WHERE id = %s", (local_formation_id,))
		result = cursor.fetchone()
		if result and result['id_prod']:
			cursor.close()
			return True

		# ---- Resolve id_prod for level / section ----
		cursor.execute(
			"SELECT id_prod FROM account_level WHERE id = %s",
			(new_data.get('account_level_id'),)
		)
		result = cursor.fetchone()
		LevelIdProd = result['id_prod'] if result else None

		cursor.execute(
			"SELECT id_prod FROM account_section WHERE id = %s",
			(new_data.get('account_section_id'),)
		)
		result = cursor.fetchone()
		SectionIdProd = result['id_prod'] if result else None

		# ---- Resolve sub subjects: id_prod if set, otherwise the local id ----
		subjects = new_data.get('subjects') or []
		sub_subject_remote_id = {}

		for subject in subjects:
			local_id = subject.get('account_sub_subject_id')
			cursor.execute(
				"SELECT id_prod FROM account_sub_subject WHERE id = %s",
				(local_id,)
			)
			result = cursor.fetchone()
			sub_subject_remote_id[local_id] = result['id_prod'] if result and result['id_prod'] else local_id

		# ---- Base fields ----
		data = [
			("name", new_data.get('name') or ''),
			("description", new_data.get('description') or ''),
			("typeDate", new_data.get('type_date') or ''),
			("typeSession", new_data.get('type_session') or ''),
			("conditionOfPassage", new_data.get('condition_of_passage') or 'Auto'),
		]

		if LevelIdProd:
			data.append(("accountLevelId", LevelIdProd))
		if SectionIdProd:
			data.append(("accountSectionId", SectionIdProd))

		if new_data.get('type_date') == 'total Duration':
			data.append(("numberDayDuration", new_data.get('number_day_duration')))
		elif new_data.get('type_date') == 'By Number Of Sessions':
			data.append(("numberSession", new_data.get('number_session')))

		# ---- Seasons ----
		seasons = new_data.get('seasons') or []
		season_ref_by_id = {}

		for season in seasons:
			season_ref_by_id[season.get('id')] = season.get('ref')
			data.append(("seasonTitle[]", season.get('title') or ''))
			data.append(("seasonDuration[]", season.get('number_duration') or ''))
			data.append(("seasonDescription[]", season.get('description') or ''))
			data.append(("seasonReference[]", season.get('ref') or ''))

		# ---- Subjects + relations ----
		for subject in subjects:
			data.append(("subSubjectId[]", sub_subject_remote_id[subject.get('account_sub_subject_id')]))
			data.append(("subSubjectNbHours[]", subject.get('number_hours') or ''))
			data.append(("subSubjectDescription[]", subject.get('description') or ''))
			data.append(("subSubjectReference[]", subject.get('ref') or ''))

			for season_id in subject.get('season_ids') or []:
				season_ref = season_ref_by_id.get(season_id)
				if not season_ref:
					continue
				data.append(("relationSubjectRefWithSeason[]", subject.get('ref')))
				data.append(("relationSeasonRefWithSubject[]", season_ref))

		cursor.close()

		# ---- Logo (optional) ----
		logo_path = new_data.get('img_link')
		if logo_path and os.path.isfile(logo_path):
			files = {"logoFile": (os.path.basename(logo_path), open(logo_path, 'rb'))}

		# ---- Send ----
		ok, remote = _send_create_formation_api(settings, data, files)
		if not ok:
			return False

		# ---- Store remote ids (formation + seasons + subjects + relations) in one commit ----
		cursor = db.connection.cursor(dictionary=True)

		cursor.execute(
			"UPDATE formation SET id_prod = %s WHERE id = %s",
			(remote.get('id'), local_formation_id)
		)

		for s in remote.get('seasons') or []:
			cursor.execute(
				"UPDATE season SET id_prod = %s WHERE ref = %s AND formation_id = %s",
				(s.get('id'), s.get('ref'), local_formation_id)
			)

		for sub in remote.get('subjects') or []:
			cursor.execute(
				"UPDATE formation_subject SET id_prod = %s WHERE ref = %s AND formation_id = %s",
				(sub.get('id'), sub.get('ref'), local_formation_id)
			)

		for rel in remote.get('seasonSubjectRelations') or []:
			cursor.execute(
				"""
				UPDATE season_sub_subject sss
				JOIN season s ON s.id = sss.season_id
				JOIN formation_subject fs ON fs.id = sss.formation_sub_subject
				SET sss.id_prod = %s
				WHERE s.ref = %s
				  AND fs.ref = %s
				  AND s.formation_id = %s
				  AND fs.formation_id = %s
				""",
				(
					rel.get('id'),
					rel.get('seasonRef'),
					rel.get('subjectRef'),
					local_formation_id,
					local_formation_id
				)
			)

		db.connection.commit()
		cursor.close()

		return True

	except Exception as e:
		logger.exception("Error in push_formationAdd: %s", e)
		return False

	finally:
		if files:
			files["logoFile"][1].close()


def push_formationUpdate(db, settings, row):
	FormationId = None
	try:
		new_data = json.loads(row.get('new_data', '{}'))
		FormationId = new_data.get('id')

		query = """
			SELECT id_prod
			FROM formation 
			WHERE id = %s
		"""
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(query, (FormationId,))
		result = cursor.fetchone()
		remote_formation_id = result['id_prod'] if result else None
		if remote_formation_id is None:
			return False

		return _send_create_formation_api(settings, remote_formation_id)

	except Exception as e:
		logger.exception("Error in push_formationUpdate (%s): %s", FormationId, e)
		return False


def push_formationDelete(db, settings, row):
	FormationId = None
	try:
		old_data = json.loads(row.get('old_data', '{}'))
		FormationId = old_data.get('id')
		cursor = db.connection.cursor(dictionary=True)
		cursor.execute(
			"""SELECT id_prod FROM formation WHERE id = %s""",
			(FormationId,)
		)
		result = cursor.fetchone()
		id_prod = result['id_prod'] if result else None
		if id_prod is None:
			return False
		print(id_prod)
		status = _send_delete_formation_api(settings, id_prod)
		return status
	except Exception as e:
		logger.exception("Error in push_formationDelete (%s): %s", FormationId, e)
		return False
