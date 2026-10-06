"""
Local and Room Data Processor
Handles inserting and updating local and room records in the database
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import format_date


def normalize_rooms(rooms):
	"""
	The API may return rooms as a list OR as a dict keyed by index
	({'0': {...}, '3': {...}}). Always return a list of room dicts.
	"""
	if not rooms:
		return []
	if isinstance(rooms, dict):
		rooms = list(rooms.values())
	return [r for r in rooms if isinstance(r, dict)]


def _empty_stats():
	return {
		"locals_inserted": 0,
		"locals_updated": 0,
		"locals_skipped": 0,
		"rooms_inserted": 0,
		"rooms_updated": 0,
		"rooms_skipped": 0,
		"errors": 0,
		"total_locals_processed": 0,
		"total_rooms_processed": 0
	}


def insert_local_and_rooms(db, local_data):
	"""
	Handle 'created' locals and rooms from API
	Logic:
	- If local exists in DB → UPDATE it (and its rooms)
	- If local does NOT exist → INSERT it (and its rooms)

	Args:
		db: Database instance
		local_data: Dictionary with 'created' key

	Returns:
		dict: Statistics (inserted, updated, skipped, errors) for locals and rooms
	"""
	result = _empty_stats()

	try:
		created_locals = local_data.get("created", [])
		result["total_locals_processed"] = len(created_locals)

		if not created_locals:
			print("   ℹ️  No locals in 'created'")
			return result

		print(f"   Processing {len(created_locals)} local(s) from 'created'...")

		for i, local in enumerate(created_locals, 1):
			try:
				local_id = local.get("id")
				if not local_id:
					raise ValueError("Missing required field: id")

				# Prepare new local data
				new_local_data = {
					"account_id": local.get("accountId"),
					"name": local.get("name", ""),
					"address": local.get("address", ""),
					"gps": local.get("gps", ""),
					"status": 1 if local.get("status", True) else 0,
					"enabled": 1 if local.get("enabled", True) else 0,
					"default_local": 1 if local.get("default", False) else 0,
					"created_at": format_date(local.get("createdAt")),
					"updated_at": format_date(local.get("updatedAt"))
				}

				# Get rooms data (dict or list → list)
				rooms = normalize_rooms(local.get("rooms"))
				result["total_rooms_processed"] += len(rooms)

				# Check if local exists
				select_query = "SELECT * FROM local WHERE id = %s"
				existing_local_records = db.fetch_query(select_query, (local_id,))

				print(f"   [{i}/{len(created_locals)}] Local ID {local_id}...")

				if existing_local_records:
					# LOCAL EXISTS → Compare and UPDATE if different
					existing_local = existing_local_records[0]

					# Compare local data
					local_has_changes = False
					for key, value in new_local_data.items():
						old_value = str(existing_local.get(key)) if existing_local.get(key) is not None else None
						new_value = str(value) if value is not None else None
						if old_value != new_value:
							local_has_changes = True
							break

					if not local_has_changes and not rooms:
						print(f"      ⏭️  Local already exists with same data and no rooms - skipped")
						result["locals_skipped"] += 1
						continue

					if local_has_changes:
						# Update local
						print(f"      🔄 Local data changed - updating...")
						update_query = """
							UPDATE local SET
								account_id = %s,
								name = %s,
								address = %s,
								gps = %s,
								status = %s,
								enabled = %s,
								default_local = %s,
								created_at = %s,
								updated_at = %s
							WHERE id = %s
						"""
						db.execute_query(update_query, (
							new_local_data["account_id"],
							new_local_data["name"],
							new_local_data["address"],
							new_local_data["gps"],
							new_local_data["status"],
							new_local_data["enabled"],
							new_local_data["default_local"],
							new_local_data["created_at"],
							new_local_data["updated_at"],
							local_id
						))
						result["locals_updated"] += 1
						print(f"      ✅ Local updated successfully")
					else:
						result["locals_skipped"] += 1
						print(f"      ⏭️  Local data identical - skipped update")

					# Process rooms for existing local
					room_stats = process_rooms_for_local(db, local_id, rooms, "created")
					result["rooms_inserted"] += room_stats["inserted"]
					result["rooms_updated"] += room_stats["updated"]
					result["rooms_skipped"] += room_stats["skipped"]
					result["errors"] += room_stats["errors"]

				else:
					# LOCAL DOES NOT EXIST → INSERT
					print(f"      ✨ New local - inserting...")

					insert_query = """
						INSERT INTO local (
							id, account_id, name, address, gps, status, enabled,
							default_local, created_at, updated_at
						) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					"""
					db.execute_query(insert_query, (
						local_id,
						new_local_data["account_id"],
						new_local_data["name"],
						new_local_data["address"],
						new_local_data["gps"],
						new_local_data["status"],
						new_local_data["enabled"],
						new_local_data["default_local"],
						new_local_data["created_at"],
						new_local_data["updated_at"]
					))
					result["locals_inserted"] += 1
					print(f"      ✅ Local inserted successfully")

					# Process rooms for new local
					room_stats = process_rooms_for_local(db, local_id, rooms, "created")
					result["rooms_inserted"] += room_stats["inserted"]
					result["rooms_updated"] += room_stats["updated"]
					result["rooms_skipped"] += room_stats["skipped"]
					result["errors"] += room_stats["errors"]

			except Exception as err:
				print(f"      ❌ Error processing local ID {local.get('id', 'unknown') if isinstance(local, dict) else local}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Created section → Locals: {result['locals_inserted']} inserted, "
			f"{result['locals_updated']} updated, {result['locals_skipped']} skipped | "
			f"Rooms: {result['rooms_inserted']} inserted, {result['rooms_updated']} updated, "
			f"{result['rooms_skipped']} skipped | Errors: {result['errors']}")

	except Exception as err:
		print(f"   💥 Unexpected error in insert_local_and_rooms: {err}")

	return result


def update_local_and_rooms(db, local_data):
	"""
	Handle 'updated' locals and rooms from API
	Logic:
	- If local exists in DB → UPDATE it
	- If local does NOT exist → INSERT it (don't skip!)

	Args:
		db: Database instance
		local_data: Dictionary with 'updated' key

	Returns:
		dict: Statistics (inserted, updated, skipped, errors) for locals and rooms
	"""
	result = _empty_stats()

	try:
		updated_locals = local_data.get("updated", [])
		result["total_locals_processed"] = len(updated_locals)

		if not updated_locals:
			print("   ℹ️  No locals in 'updated'")
			return result

		print(f"   Processing {len(updated_locals)} local(s) from 'updated'...")

		for i, local in enumerate(updated_locals, 1):
			try:
				local_id = local.get("id")
				if not local_id:
					raise ValueError("Missing required field: id")

				# Prepare new local data
				new_local_data = {
					"account_id": local.get("accountId"),
					"name": local.get("name", ""),
					"address": local.get("address", ""),
					"gps": local.get("gps", ""),
					"status": 1 if local.get("status", True) else 0,
					"enabled": 1 if local.get("enabled", True) else 0,
					"default_local": 1 if local.get("default", False) else 0,
					"updated_at": format_date(local.get("updatedAt"))
				}

				# Get rooms data (dict or list → list)
				rooms = normalize_rooms(local.get("rooms"))
				result["total_rooms_processed"] += len(rooms)

				# Check if local exists
				select_query = "SELECT * FROM local WHERE id = %s"
				existing_local_records = db.fetch_query(select_query, (local_id,))

				print(f"   [{i}/{len(updated_locals)}] Local ID {local_id}...")

				if existing_local_records:
					# LOCAL EXISTS → Compare and UPDATE if different
					existing_local = existing_local_records[0]

					# Compare local data
					local_has_changes = False
					for key, value in new_local_data.items():
						old_value = str(existing_local.get(key)) if existing_local.get(key) is not None else None
						new_value = str(value) if value is not None else None
						if old_value != new_value:
							local_has_changes = True
							break

					if not local_has_changes and not rooms:
						print(f"      ⏭️  Local data is identical and no rooms - skipped")
						result["locals_skipped"] += 1
						continue

					if local_has_changes:
						# Update local
						print(f"      🔄 Local data changed - updating...")
						update_query = """
							UPDATE local SET
								account_id = %s,
								name = %s,
								address = %s,
								gps = %s,
								status = %s,
								enabled = %s,
								default_local = %s,
								updated_at = %s
							WHERE id = %s
						"""
						db.execute_query(update_query, (
							new_local_data["account_id"],
							new_local_data["name"],
							new_local_data["address"],
							new_local_data["gps"],
							new_local_data["status"],
							new_local_data["enabled"],
							new_local_data["default_local"],
							new_local_data["updated_at"],
							local_id
						))
						result["locals_updated"] += 1
						print(f"      ✅ Local updated successfully")
					else:
						result["locals_skipped"] += 1
						print(f"      ⏭️  Local data identical - skipped update")

					# Process rooms for existing local
					room_stats = process_rooms_for_local(db, local_id, rooms, "updated")
					result["rooms_inserted"] += room_stats["inserted"]
					result["rooms_updated"] += room_stats["updated"]
					result["rooms_skipped"] += room_stats["skipped"]
					result["errors"] += room_stats["errors"]

				else:
					# LOCAL DOES NOT EXIST → INSERT (don't skip!)
					print(f"      ⚠️  Local not found in DB - inserting...")

					insert_query = """
						INSERT INTO local (
							id, account_id, name, address, gps, status, enabled,
							default_local, created_at, updated_at
						) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					"""
					# For records in 'updated' that don't exist, use updated_at as created_at
					db.execute_query(insert_query, (
						local_id,
						new_local_data["account_id"],
						new_local_data["name"],
						new_local_data["address"],
						new_local_data["gps"],
						new_local_data["status"],
						new_local_data["enabled"],
						new_local_data["default_local"],
						new_local_data["updated_at"],  # Use updated_at as created_at
						new_local_data["updated_at"]
					))
					result["locals_inserted"] += 1
					print(f"      ✅ Local inserted successfully")

					# Process rooms for new local
					room_stats = process_rooms_for_local(db, local_id, rooms, "updated")
					result["rooms_inserted"] += room_stats["inserted"]
					result["rooms_updated"] += room_stats["updated"]
					result["rooms_skipped"] += room_stats["skipped"]
					result["errors"] += room_stats["errors"]

			except Exception as err:
				print(f"      ❌ Error processing local ID {local.get('id', 'unknown') if isinstance(local, dict) else local}: {err}")
				result["errors"] += 1
				continue

		print(f"\n   📊 Updated section → Locals: {result['locals_inserted']} inserted, "
			f"{result['locals_updated']} updated, {result['locals_skipped']} skipped | "
			f"Rooms: {result['rooms_inserted']} inserted, {result['rooms_updated']} updated, "
			f"{result['rooms_skipped']} skipped | Errors: {result['errors']}")

	except Exception as err:
		print(f"   💥 Unexpected error in update_local_and_rooms: {err}")

	return result


def process_rooms_for_local(db, local_id, rooms, operation_type):
	"""
	Process rooms for a specific local (id_prod logic, same as tablets)

	'created':
	- If the remote id already exists as id_prod (from a local push) → skip (avoid duplicate)
	- Else look up by id → UPDATE if changed, INSERT if missing

	'updated':
	- Look up by id_prod first, then fall back to id
	- UPDATE if changed, INSERT if missing (don't skip!)

	Args:
		db: Database instance
		local_id: ID of the local
		rooms: List (or dict keyed by index) of room data
		operation_type: "created" or "updated"

	Returns:
		dict: Room statistics
	"""
	room_stats = {
		"inserted": 0,
		"updated": 0,
		"skipped": 0,
		"errors": 0
	}

	rooms = normalize_rooms(rooms)

	if not rooms:
		return room_stats

	print(f"      Processing {len(rooms)} room(s) for local {local_id}...")

	for room in rooms:
		room_id = room.get("id")
		try:
			if not room_id:
				continue

			# Prepare room data
			new_room_data = {
				"id_prod": room_id,
				"local_id": room.get("localId", local_id),  # Use local_id if localId not provided
				"name": room.get("name", ""),
				"capacity": room.get("capacity", ""),
				"updated_at": format_date(room.get("updatedAt"))
			}
			# 'updated' must never overwrite created_at
			if operation_type == "created":
				new_room_data["created_at"] = format_date(room.get("createdAt"))

			# ---------- FIND EXISTING ROOM ----------
			if operation_type == "created":
				# FIRST: does this remote ID already exist as id_prod (from a local push)?
				existing_by_prod = db.fetch_query(
					"SELECT id FROM room WHERE id_prod = %s", (room_id,)
				)
				if existing_by_prod:
					print(f"         ⏭️  Room ID {room_id} already exists as id_prod "
						f"(local id: {existing_by_prod[0]['id']}) - skipped to avoid duplicate")
					room_stats["skipped"] += 1
					continue

				existing_room_records = db.fetch_query(
					"SELECT * FROM room WHERE id = %s", (room_id,)
				)
			else:
				# Check by id_prod first, then fall back to id
				existing_room_records = db.fetch_query(
					"SELECT * FROM room WHERE id_prod = %s", (room_id,)
				)
				if not existing_room_records:
					existing_room_records = db.fetch_query(
						"SELECT * FROM room WHERE id = %s", (room_id,)
					)

			if existing_room_records:
				# ROOM EXISTS → Compare and UPDATE if different
				existing_room = existing_room_records[0]

				room_has_changes = False
				for key, value in new_room_data.items():
					old_value = str(existing_room.get(key)) if existing_room.get(key) is not None else None
					new_value = str(value) if value is not None else None
					if old_value != new_value:
						room_has_changes = True
						break

				if not room_has_changes:
					room_stats["skipped"] += 1
					continue

				# Update room (columns come from new_room_data, so created_at is only touched on 'created')
				set_clause = ", ".join(f"{col} = %s" for col in new_room_data)
				update_query = f"UPDATE room SET {set_clause} WHERE id = %s"
				db.execute_query(update_query, (
					*new_room_data.values(),
					existing_room["id"]  # actual local id (handles both id and id_prod lookup)
				))
				room_stats["updated"] += 1

			else:
				# ROOM DOES NOT EXIST → INSERT
				insert_data = {"id": room_id, **new_room_data}
				if "created_at" not in insert_data:
					# For 'updated' operation, use updated_at as created_at
					insert_data["created_at"] = new_room_data["updated_at"]

				columns = ", ".join(insert_data)
				placeholders = ", ".join(["%s"] * len(insert_data))
				insert_query = f"INSERT INTO room ({columns}) VALUES ({placeholders})"
				db.execute_query(insert_query, tuple(insert_data.values()))
				room_stats["inserted"] += 1

		except Exception as err:
			print(f"         ❌ Error processing room ID {room_id or 'unknown'}: {err}")
			room_stats["errors"] += 1
			continue

	return room_stats


def process_local_and_rooms(db, local_data):
	"""
	Process local and room data (handles both 'created' and 'updated' sections)

	Args:
		db: Database instance
		local_data: Dictionary with 'created' and/or 'updated' keys

	Returns:
		dict: Combined statistics
	"""
	print("\n📌 PROCESSING LOCALS AND ROOMS")
	print("=" * 60)

	results = {
		"created_section": _empty_stats(),
		"updated_section": _empty_stats()
	}

	# Process 'created' section
	if local_data.get("created"):
		print(f"\n✨ Processing 'created' section ({len(local_data['created'])} locals)...")
		results["created_section"] = insert_local_and_rooms(db, local_data)

	# Process 'updated' section
	if local_data.get("updated"):
		print(f"\n🔄 Processing 'updated' section ({len(local_data['updated'])} locals)...")
		results["updated_section"] = update_local_and_rooms(db, local_data)

	# Print total summary
	c = results["created_section"]
	u = results["updated_section"]

	total_locals_inserted = c["locals_inserted"] + u["locals_inserted"]
	total_locals_updated = c["locals_updated"] + u["locals_updated"]
	total_locals_skipped = c["locals_skipped"] + u["locals_skipped"]

	total_rooms_inserted = c["rooms_inserted"] + u["rooms_inserted"]
	total_rooms_updated = c["rooms_updated"] + u["rooms_updated"]
	total_rooms_skipped = c["rooms_skipped"] + u["rooms_skipped"]

	total_errors = c["errors"] + u["errors"]

	print("\n" + "=" * 60)
	print("📊 LOCALS AND ROOMS - TOTAL SUMMARY")
	print("=" * 60)
	print(f"   LOCALS:")
	print(f"     ✨ Inserted: {total_locals_inserted}")
	print(f"     🔄 Updated:  {total_locals_updated}")
	print(f"     ⏭️  Skipped:  {total_locals_skipped}")
	print(f"   ROOMS:")
	print(f"     ✨ Inserted: {total_rooms_inserted}")
	print(f"     🔄 Updated:  {total_rooms_updated}")
	print(f"     ⏭️  Skipped:  {total_rooms_skipped}")
	print(f"   ❌ Total Errors:   {total_errors}")
	print("=" * 60)

	return results