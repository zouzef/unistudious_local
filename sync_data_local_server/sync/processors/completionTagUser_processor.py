import sys
import os
from utils.helpers import format_date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def insert_completionTagUser(db, completionTag):
	result = {
		"inserted": 0,
		"updated": 0,
		"skipped": 0,
		"errors": 0,
		"total_processed": 0
	}
	try:
		created_records = completionTag.get("created", [])
		result["total_processed"] = len(created_records)
		if not created_records:
			print("   ℹ️  No completionTagUser records in 'created'")
			return result

		print(f"     Processing {len(created_records)} completionTagUser record(s) from 'created' ...")
		for i, record in enumerate(created_records, 1):
			try:
				record_id = record.get("id")
				if not record_id:
					raise ValueError("Missing required field: id")

				# ✅ FIRST: Check if this remote ID already exists as id_prod (from local push)
				check_prod_query = "SELECT id FROM completion_tag_user WHERE id_prod = %s"
				existing_by_prod = db.fetch_query(check_prod_query, (record_id,))
				if existing_by_prod :
					print(f"   [{i}/{len(created_records)}] CompletionTagUser ID {record_id} already exists as id_prod (local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
					result["skipped"] += 1
					continue

				# Prepare new data — map API fields → DB columns
				new_data = {
					"id_prod": record_id,
					"user_id": record.get("")
				}
			except Exception as err:
				print(f"      ❌ Error processing completionTagUser ID {record.get('id', 'unknown')}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Created section → Inserted: {result['inserted']}, "
			  f"Updated: {result['updated']}, Skipped: {result['skipped']}, "
			  f"Errors: {result['errors']}")
	except Exception as err:
		print(f"   💥 Unexpected error in completionTagUser: {err}")

	return result

def update_completionTagUser(db, completionTag):
	pass


def process_completionTaguser(db, completionTag):
	"""
	Process completionTagUser data (handles both 'created' and 'updated' sections)

	Args:
	    db: Database instance
	    completionTag: Dictionary with 'created' and/or 'updated' keys

	Returns:
	    dict: Combined statistics
	"""

	print("\n📌 PROCESSING COMPLETION TAG USER")
	print("=" * 60)

	results = {
		"created_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
		"updated_section": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
	}

	if completionTag.get("created"):
		print(f"\n✨ Processing 'created' section ({len(completionTag['created'])} records)...")
		results["created_section"] = insert_completionTagUser(db, completionTag)

	if completionTag.get("updated"):
		print(f"\n🔄 Processing 'updated' section ({len(completionTag['updated'])} records)...")
		results["updated_section"] = update_completionTagUser(db, completionTag)

	total_inserted = results["created_section"]["inserted"] + results["updated_section"]["inserted"]
	total_updated = results["created_section"]["updated"] + results["updated_section"]["updated"]
	total_skipped = results["created_section"]["skipped"] + results["updated_section"]["skipped"]
	total_errors = results["created_section"]["errors"] + results["updated_section"]["errors"]

	print("\n" + "=" * 60)
	print("📊 RELATION COMPLETION TAG - TOTAL SUMMARY")
	print("=" * 60)
	print(f"   ✨ Total Inserted: {total_inserted}")
	print(f"   🔄 Total Updated:  {total_updated}")
	print(f"   ⏭️  Total Skipped:  {total_skipped}")
	print(f"   ❌ Total Errors:   {total_errors}")
	print("=" * 60)

	return results