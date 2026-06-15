"""
SubSubject Data Processor
Handles inserting and updating SubSubject records in the database
"""

import sys
import os
from utils.helpers import format_date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def insert_subsubject(db, subsubject_data):
	pass


def update_subsubject(db, subsubject_data):
	pass

def process_subsubject(db, subsubject_data):
	"""
		Process Subsubject data (handles both 'created' and 'updated' subsubject)
	"""
	print("\n📌 PROCESSING SUBSUBJECT")
	print("=" * 60)

	results = {
		"created_subsubject": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0},
		"updated_subsubject": {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
	}
	if subsubject_data.get("created"):
		print(f"\n Processing 'created' subsubject ({len(subsubject_data['created'])} record(s)...")
		results['created_subsubject'] = insert_subsubject(db,subsubject_data)

	if subsubject_data.get("updated"):
		print(f"\n Processing 'updated' subsubject ({len(subsubject_data['updated'])} record(s)...")
		results['updated_subsubject'] = update_subsubject(db,subsubject_data)

	total_inserted = results["created_subsubject"]["inserted"] + results["updated_subsubject"]["inserted"]
	total_updated = results["created_subsubject"]["updated"] + results["updated_subsubject"]["updated"]
	total_skipped = results["created_subsubject"]["skipped"] + results["updated_subsubject"]["skipped"]
	total_errors = results["created_subsubject"]["errors"] + results["updated_subsubject"]["errors"]

	print("\n" + "=" * 60)
	print("📊 SubSubject - TOTAL SUMMARY")
	print("=" * 60)
	print(f"   ✨ Total Inserted: {total_inserted}")
	print(f"   🔄 Total Updated:  {total_updated}")
	print(f"   ⏭️  Total Skipped:  {total_skipped}")
	print(f"   ❌ Total Errors:   {total_errors}")

	return results