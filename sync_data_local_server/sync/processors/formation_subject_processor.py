"""
Formation Subject Data Processor
Handles inserting and updating formation_subject records in the database
"""
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def _now():
	"""Fallback value for NOT NULL datetime columns (created_at, timestamp)
	when the API gives us nothing to derive them from."""
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def insert_formation_subjects(db, formation_subject_data):
	"""
	Handle 'created' formation_subjects from API
	Logic:
	- Check if id_prod already exists (avoid duplicates from local pushes)
	- If record exists in DB by id → UPDATE it
	- If record does NOT exist → INSERT it

	Args:
		db: Database instance
		formation_subject_data: Dictionary with 'created' key

	Returns:
		dict: Statistics (inserted, updated, skipped, errors)
	"""
	result = {
		"inserted": 0,
		"updated": 0,
		"skipped": 0,
		"errors": 0,
		"total_processed": 0
	}

	try:
		created_formation_subjects = formation_subject_data.get("created", [])
		result["total_processed"] = len(created_formation_subjects)

		if not created_formation_subjects:
			print("   ℹ️  No formation_subjects in 'created'")
			return result

		print(f"   Processing {len(created_formation_subjects)} formation_subject(s) from 'created'...")

		for i, formation_subject in enumerate(created_formation_subjects, 1):
			try:
				formation_subject_id = formation_subject.get("id")
				if not formation_subject_id:
					raise ValueError("Missing required field: id")

				# ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
				check_prod_query = "SELECT id FROM formation_subject WHERE id_prod = %s"
				existing_by_prod = db.fetch_query(check_prod_query, (formation_subject_id,))

				if existing_by_prod:
					print(f"   [{i}/{len(created_formation_subjects)}] Formation Subject ID {formation_subject_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
					result["skipped"] += 1
					continue

				# Prepare new data
				# NOTE: adjust the .get(...) key names below (description / numberOfHours)
				# to match whatever your remote API actually sends if they differ.
				new_data = {
					"id_prod":                 formation_subject_id,
					"account_sub_subject_id":  formation_subject.get("subSubjectId"),
					"formation_id":            formation_subject.get("formationId"),
					"description":             formation_subject.get("description"),
					"number_hours":         formation_subject.get("numberHours"),
					"status":                  1 if formation_subject.get("status", True) else 0,
					"enabled":                 1 if formation_subject.get("enabled", True) else 0,
					"created_at":              format_date(formation_subject.get("createdAt")) or _now(),
					"timestamp":               format_date(formation_subject.get("timestamp") or formation_subject.get("createdAt") or formation_subject.get("updatedAt")) or _now(),
					"updated_at":              format_date(formation_subject.get("updatedAt")),
					"ref":                     formation_subject.get("ref"),
					"release_token":           1 if formation_subject.get("releaseToken", False) else 0,
					"use_token":               formation_subject.get("useToken"),
				}

				# Check if record exists by id
				select_query = "SELECT * FROM formation_subject WHERE id = %s"
				existing_records = db.fetch_query(select_query, (formation_subject_id,))

				print(f"   [{i}/{len(created_formation_subjects)}] Formation Subject ID {formation_subject_id}...")

				if existing_records:
					existing = existing_records[0]

					has_changes = False
					for key, value in new_data.items():
						old_value = str(existing.get(key)) if existing.get(key) is not None else None
						new_value = str(value) if value is not None else None
						if old_value != new_value:
							has_changes = True
							break

					if not has_changes:
						print(f"      ⏭️  Already exists with same data - skipped")
						result["skipped"] += 1
						continue

					print(f"      🔄 Already exists but data changed - updating...")

					update_query = """
						UPDATE formation_subject SET
							id_prod                = %s,
							account_sub_subject_id  = %s,
							formation_id            = %s,
							description             = %s,
							number_hours         = %s,
							status                  = %s,
							enabled                 = %s,
							created_at              = %s,
							timestamp               = %s,
							updated_at              = %s,
							ref                     = %s,
							release_token           = %s,
							use_token               = %s
						WHERE id = %s
					"""

					db.execute_query(update_query, (
						new_data["id_prod"],
						new_data["account_sub_subject_id"],
						new_data["formation_id"],
						new_data["description"],
						new_data["number_hours"],
						new_data["status"],
						new_data["enabled"],
						new_data["created_at"],
						new_data["timestamp"],
						new_data["updated_at"],
						new_data["ref"],
						new_data["release_token"],
						new_data["use_token"],
						formation_subject_id
					))

					result["updated"] += 1
					print(f"      ✅ Updated successfully")

				else:
					print(f"      ✨ New record - inserting...")

					insert_query = """
						INSERT INTO formation_subject (
							id, id_prod, account_sub_subject_id, formation_id,
							description, number_hours,
							status, enabled, created_at, timestamp, updated_at,
							ref, release_token, use_token
						) VALUES (
							%s, %s, %s, %s,
							%s, %s,
							%s, %s, %s, %s, %s,
							%s, %s, %s
						)
					"""

					db.execute_query(insert_query, (
						formation_subject_id,
						new_data["id_prod"],
						new_data["account_sub_subject_id"],
						new_data["formation_id"],
						new_data["description"],
						new_data["number_hours"],
						new_data["status"],
						new_data["enabled"],
						new_data["created_at"],
						new_data["timestamp"],
						new_data["updated_at"],
						new_data["ref"],
						new_data["release_token"],
						new_data["use_token"],
					))

					result["inserted"] += 1
					print(f"      ✅ Inserted successfully")

			except Exception as err:
				print(f"      ❌ Error processing formation_subject ID {formation_subject.get('id', 'unknown')}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
			  f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
			  f"Errors: {result['errors']}")

	except Exception as err:
		print(f"   💥 Unexpected error in insert_formation_subjects: {err}")

	return result


def update_formation_subjects(db, formation_subject_data):
	"""
	Handle 'updated' formation_subjects from API
	Logic:
	- If record exists in DB → UPDATE it
	- If record does NOT exist → INSERT it (don't skip!)

	Args:
		db: Database instance
		formation_subject_data: Dictionary with 'updated' key

	Returns:
		dict: Statistics (inserted, updated, skipped, errors)
	"""
	result = {
		"inserted": 0,
		"updated": 0,
		"skipped": 0,
		"errors": 0,
		"total_processed": 0
	}

	try:
		updated_formation_subjects = formation_subject_data.get("updated", [])
		result["total_processed"] = len(updated_formation_subjects)

		if not updated_formation_subjects:
			print("   ℹ️  No formation_subjects in 'updated'")
			return result

		print(f"   Processing {len(updated_formation_subjects)} formation_subject(s) from 'updated'...")

		for i, formation_subject in enumerate(updated_formation_subjects, 1):
			try:
				formation_subject_id = formation_subject.get("id")
				if not formation_subject_id:
					raise ValueError("Missing required field: id")

				# Prepare new data
				# NOTE: adjust the .get(...) key names below (description / numberOfHours)
				# to match whatever your remote API actually sends if they differ.
				new_data = {
					"id_prod":                 formation_subject_id,
					"account_sub_subject_id":  formation_subject.get("subSubjectId"),
					"formation_id":            formation_subject.get("formationId"),
					"description":             formation_subject.get("description"),
					"number_hours":         formation_subject.get("numberHours"),
					"status":                  1 if formation_subject.get("status", True) else 0,
					"enabled":                 1 if formation_subject.get("enabled", True) else 0,
					"timestamp":               format_date(formation_subject.get("timestamp") or formation_subject.get("updatedAt")) or _now(),
					"updated_at":              format_date(formation_subject.get("updatedAt")),
					"ref":                     formation_subject.get("ref"),
					"release_token":           1 if formation_subject.get("releaseToken", False) else 0,
					"use_token":               formation_subject.get("useToken"),
				}

				# ✅ Check by id_prod first, then fall back to id
				check_prod_query = "SELECT * FROM formation_subject WHERE id_prod = %s"
				existing_records = db.fetch_query(check_prod_query, (formation_subject_id,))

				if not existing_records:
					select_query = "SELECT * FROM formation_subject WHERE id = %s"
					existing_records = db.fetch_query(select_query, (formation_subject_id,))

				print(f"   [{i}/{len(updated_formation_subjects)}] Formation Subject ID {formation_subject_id}...")

				if existing_records:
					existing = existing_records[0]

					has_changes = False
					for key, value in new_data.items():
						old_value = str(existing.get(key)) if existing.get(key) is not None else None
						new_value = str(value) if value is not None else None
						if old_value != new_value:
							has_changes = True
							break

					if not has_changes:
						print(f"      ⏭️  Data is identical - skipped")
						result["skipped"] += 1
						continue

					print(f"      🔄 Data changed - updating...")

					update_query = """
						UPDATE formation_subject SET
							id_prod                = %s,
							account_sub_subject_id  = %s,
							formation_id            = %s,
							description             = %s,
							number_hours         = %s,
							status                  = %s,
							enabled                 = %s,
							timestamp               = %s,
							updated_at              = %s,
							ref                     = %s,
							release_token           = %s,
							use_token               = %s
						WHERE id = %s
					"""

					db.execute_query(update_query, (
						new_data["id_prod"],
						new_data["account_sub_subject_id"],
						new_data["formation_id"],
						new_data["description"],
						new_data["number_hours"],
						new_data["status"],
						new_data["enabled"],
						new_data["timestamp"],
						new_data["updated_at"],
						new_data["ref"],
						new_data["release_token"],
						new_data["use_token"],
						existing["id"]  # ← use actual local id (handles both cases)
					))

					result["updated"] += 1
					print(f"      ✅ Updated successfully")

				else:
					print(f"      ⚠️  Record not found in DB - inserting...")

					insert_query = """
						INSERT INTO formation_subject (
							id, id_prod, account_sub_subject_id, formation_id,
							description, number_hours,
							status, enabled, created_at, timestamp, updated_at,
							ref, release_token, use_token
						) VALUES (
							%s, %s, %s, %s,
							%s, %s,
							%s, %s, %s, %s, %s,
							%s, %s, %s
						)
					"""

					db.execute_query(insert_query, (
						formation_subject_id,
						new_data["id_prod"],
						new_data["account_sub_subject_id"],
						new_data["formation_id"],
						new_data["description"],
						new_data["number_hours"],
						new_data["status"],
						new_data["enabled"],
						new_data["timestamp"],  # fallback for created_at
						new_data["timestamp"],
						new_data["updated_at"],
						new_data["ref"],
						new_data["release_token"],
						new_data["use_token"],
					))

					result["inserted"] += 1
					print(f"      ✅ Inserted successfully")

			except Exception as err:
				print(f"      ❌ Error processing formation_subject ID {formation_subject.get('id', 'unknown')}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
			  f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
			  f"Errors: {result['errors']}")

	except Exception as err:
		print(f"   💥 Unexpected error in update_formation_subjects: {err}")

	return result


def process_formation_subjects(db, formation_subject_data):
	"""
	Process formation_subject data (handles both 'created' and 'updated' sections)

	Args:
		db: Database instance
		formation_subject_data: Dictionary with 'created' and/or 'updated' keys

	Returns:
		dict: Combined statistics
	"""
	print("\n📌 PROCESSING FORMATION SUBJECTS")
	print("=" * 60)

	results = {
		"created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
		"updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
	}

	# Process 'created' section
	if formation_subject_data.get("created"):
		print(f"\n✨ Processing 'created' section ({len(formation_subject_data['created'])} records)...")
		results["created_section"] = insert_formation_subjects(db, formation_subject_data)

	# Process 'updated' section
	if formation_subject_data.get("updated"):
		print(f"\n🔄 Processing 'updated' section ({len(formation_subject_data['updated'])} records)...")
		results["updated_section"] = update_formation_subjects(db, formation_subject_data)

	# Print total summary
	total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
	total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
	total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
	total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

	print("\n" + "=" * 60)
	print("📊 FORMATION SUBJECTS - TOTAL SUMMARY")
	print("=" * 60)
	print(f"   ✨ Total Inserted: {total_inserted}")
	print(f"   🔄 Total Updated:  {total_updated}")
	print(f"   ⏭️  Total Skipped:  {total_skipped}")
	print(f"   ❌ Total Errors:   {total_errors}")
	print("=" * 60)

	return results