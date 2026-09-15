"""
Account Sub Subject Data Processor
Handle inserting and updating account_sub_subject records in the database
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date

def insert_subsubjects(db, subsubject_data):
	"""
	Handle 'created' account_sub_subjects from API
	Logic:
	- Check if id_prod already exists (avoid duplicates from local pushes)
	- If record exists in DB by id → UPDATE it
	- If record does NOT exist → INSERT it

	Args:
		db: Database instance
		subsubject_data: Dictionary with 'created' key

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
		created_subsubjects = subsubject_data.get("created", [])
		result["total_processed"] = len(created_subsubjects)

		if not created_subsubjects:
			print("   ℹ️  No sub_subjects in 'created'")
			return result

		print(f"   Processing {len(created_subsubjects)} sub_subject(s) from 'created'...")

		for i, subsubject in enumerate(created_subsubjects, 1):
			try:
				subsubject_id = subsubject.get("id")
				if not subsubject_id:
					raise ValueError("Missing required field: id")

				# ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
				check_prod_query = "SELECT id FROM account_sub_subject WHERE id_prod = %s"
				existing_by_prod = db.fetch_query(check_prod_query, (subsubject_id,))

				if existing_by_prod:
					print(f"   [{i}/{len(created_subsubjects)}] SubSubject ID {subsubject_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
					result["skipped"] += 1
					continue

				# Prepare new data
				new_data = {
					"id_prod":            subsubject.get("id"),
					"account_id":         subsubject.get("accountId"),
					"account_section_id": subsubject.get("sectionId"),
					"account_level_id":   subsubject.get("levelId"),
					"account_subject_id": subsubject.get("subjectId"),
					"name":               subsubject.get("name"),
					"status":             1 if subsubject.get("status", True) else 0,
					"description":        subsubject.get("description", ""),
					"enabled":            1 if subsubject.get("enabled", True) else 0,
					"release_token":      1 if subsubject.get("releaseToken", False) else 0,
					"use_token":          subsubject.get("useToken"),
					"created_at":         format_date(subsubject.get("createdAt")),
					"updated_at":         format_date(subsubject.get("updatedAt")),
					"timestamp":          format_date(subsubject.get("timestamp"))
				}

				# Check if record exists by id
				select_query = "SELECT * FROM account_sub_subject WHERE id = %s"
				existing_records = db.fetch_query(select_query, (subsubject_id,))

				print(f"   [{i}/{len(created_subsubjects)}] SubSubject ID {subsubject_id}...")

				if existing_records:
					# EXISTS → Compare and UPDATE if different
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
						UPDATE account_sub_subject SET
							id_prod            = %s,
							account_id         = %s,
							account_section_id = %s,
							account_level_id   = %s,
							account_subject_id = %s,
							name               = %s,
							status             = %s,
							description        = %s,
							enabled            = %s,
							release_token      = %s,
							use_token          = %s,
							created_at         = %s,
							updated_at         = %s,
							timestamp          = %s
						WHERE id = %s
					"""

					db.execute_query(update_query, (
						new_data["id_prod"],
						new_data["account_id"],
						new_data["account_section_id"],
						new_data["account_level_id"],
						new_data["account_subject_id"],
						new_data["name"],
						new_data["status"],
						new_data["description"],
						new_data["enabled"],
						new_data["release_token"],
						new_data["use_token"],
						new_data["created_at"],
						new_data["updated_at"],
						new_data["timestamp"],
						subsubject_id
					))

					result["updated"] += 1
					print(f"      ✅ Updated successfully")

				else:
					# DOES NOT EXIST → INSERT
					print(f"      ✨ New record - inserting...")

					insert_query = """
						INSERT INTO account_sub_subject (
							id, id_prod, account_id, account_section_id, account_level_id, account_subject_id, name,
							status, description, enabled, release_token, use_token,
							created_at, updated_at, timestamp
						) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					"""

					db.execute_query(insert_query, (
						subsubject_id,
						new_data["id_prod"],
						new_data["account_id"],
						new_data["account_section_id"],
						new_data["account_level_id"],
						new_data["account_subject_id"],
						new_data["name"],
						new_data["status"],
						new_data["description"],
						new_data["enabled"],
						new_data["release_token"],
						new_data["use_token"],
						new_data["created_at"],
						new_data["updated_at"],
						new_data["timestamp"]
					))

					result["inserted"] += 1
					print(f"      ✅ Inserted successfully")

			except Exception as err:
				print(f"      ❌ Error processing sub_subject ID {subsubject.get('id', 'unknown')}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
		      f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
		      f"Errors: {result['errors']}")

	except Exception as err:
		print(f"   💥 Unexpected error in insert_subsubjects: {err}")

	return result


def update_subsubjects(db, subsubject_data):
	"""
	Handle 'updated' account_sub_subjects from API
	Logic:
	- If record exists in DB → UPDATE it
	- If record does NOT exist → INSERT it (don't skip!)

	Args:
		db: Database instance
		subsubject_data: Dictionary with 'updated' key

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
		updated_subsubjects = subsubject_data.get("updated", [])
		result["total_processed"] = len(updated_subsubjects)

		if not updated_subsubjects:
			print("   ℹ️  No sub_subjects in 'updated'")
			return result

		print(f"   Processing {len(updated_subsubjects)} sub_subject(s) from 'updated'...")

		for i, subsubject in enumerate(updated_subsubjects, 1):
			try:
				subsubject_id = subsubject.get("id")
				if not subsubject_id:
					raise ValueError("Missing required field: id")

				# Prepare new data
				new_data = {
					"id_prod":            subsubject.get("id"),
					"account_id":         subsubject.get("accountId"),
					"account_section_id": subsubject.get("sectionId"),
					"account_level_id":   subsubject.get("levelId"),
					"account_subject_id": subsubject.get("subjectId"),
					"name":               subsubject.get("name"),
					"status":             1 if subsubject.get("status", True) else 0,
					"description":        subsubject.get("description", ""),
					"enabled":            1 if subsubject.get("enabled", True) else 0,
					"release_token":      1 if subsubject.get("releaseToken", False) else 0,
					"use_token":          subsubject.get("useToken"),
					"updated_at":         format_date(subsubject.get("updatedAt")),
					"timestamp":          format_date(subsubject.get("timestamp"))
				}

				# ✅ Check by id_prod first, then fall back to id
				check_prod_query = "SELECT * FROM account_sub_subject WHERE id_prod = %s"
				existing_records = db.fetch_query(check_prod_query, (subsubject_id,))

				if not existing_records:
					select_query = "SELECT * FROM account_sub_subject WHERE id = %s"
					existing_records = db.fetch_query(select_query, (subsubject_id,))

				print(f"   [{i}/{len(updated_subsubjects)}] SubSubject ID {subsubject_id}...")

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
						UPDATE account_sub_subject SET
							id_prod            = %s,
							account_id         = %s,
							account_section_id = %s,
							account_level_id   = %s,
							account_subject_id = %s,
							name               = %s,
							status             = %s,
							description        = %s,
							enabled            = %s,
							release_token      = %s,
							use_token          = %s,
							updated_at         = %s,
							timestamp          = %s
						WHERE id = %s
					"""

					db.execute_query(update_query, (
						new_data["id_prod"],
						new_data["account_id"],
						new_data["account_section_id"],
						new_data["account_level_id"],
						new_data["account_subject_id"],
						new_data["name"],
						new_data["status"],
						new_data["description"],
						new_data["enabled"],
						new_data["release_token"],
						new_data["use_token"],
						new_data["updated_at"],
						new_data["timestamp"],
						existing["id"]  # ← use actual local id (handles both cases)
					))

					result["updated"] += 1
					print(f"      ✅ Updated successfully")

				else:
					# DOES NOT EXIST → INSERT (don't skip!)
					print(f"      ⚠️  Record not found in DB - inserting...")

					insert_query = """
						INSERT INTO account_sub_subject (
							id, id_prod, account_id, account_section_id, account_level_id, account_subject_id, name,
							status, description, enabled, release_token, use_token,
							created_at, updated_at, timestamp
						) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					"""

					db.execute_query(insert_query, (
						subsubject_id,
						new_data["id_prod"],
						new_data["account_id"],
						new_data["account_section_id"],
						new_data["account_level_id"],
						new_data["account_subject_id"],
						new_data["name"],
						new_data["status"],
						new_data["description"],
						new_data["enabled"],
						new_data["release_token"],
						new_data["use_token"],
						new_data["updated_at"],  # fallback for created_at
						new_data["updated_at"],
						new_data["timestamp"]
					))

					result["inserted"] += 1
					print(f"      ✅ Inserted successfully")

			except Exception as err:
				print(f"      ❌ Error processing sub_subject ID {subsubject.get('id', 'unknown')}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Updated section → Inserted: {result['inserted']}, "
		      f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
		      f"Errors: {result['errors']}")

	except Exception as err:
		print(f"   💥 Unexpected error in update_subsubjects: {err}")

	return result


def process_subsubject(db, subsubject_data):
	"""
	Process account_sub_subject data (handles both 'created' and 'updated' sections)

	Args:
		db: Database instance
		subsubject_data: Dictionary with 'created' and/or 'updated' keys

	Returns:
		dict: Combined statistics
	"""
	print("\n📌 PROCESSING SUB_SUBJECTS")
	print("=" * 60)

	results = {
		"created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
		"updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
	}

	# Process 'created' section
	if subsubject_data.get("created"):
		print(f"\n✨ Processing 'created' section ({len(subsubject_data['created'])} records)...")
		results["created_section"] = insert_subsubjects(db, subsubject_data)

	# Process 'updated' section
	if subsubject_data.get("updated"):
		print(f"\n🔄 Processing 'updated' section ({len(subsubject_data['updated'])} records)...")
		results["updated_section"] = update_subsubjects(db, subsubject_data)

	# Print total summary
	total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
	total_updated  = results["created_section"]["updated"]  + results["updated_section"]["updated"]
	total_skipped  = results["created_section"]["skipped"]  + results["updated_section"]["skipped"]
	total_errors   = results["created_section"]["errors"]   + results["updated_section"]["errors"]

	print("\n" + "=" * 60)
	print("📊 SUB_SUBJECTS - TOTAL SUMMARY")
	print("=" * 60)
	print(f"   ✨ Total Inserted: {total_inserted}")
	print(f"   🔄 Total Updated:  {total_updated}")
	print(f"   ⏭️  Total Skipped:  {total_skipped}")
	print(f"   ❌ Total Errors:   {total_errors}")
	print("=" * 60)

	return results