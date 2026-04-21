# test.py
from app import create_app

app = create_app()

with app.app_context():
    from app.groups.service import (
        get_groups,
        get_users_not_affected,
        get_subject_group
    )

    print("TEST 1 - Get groups")
    result = get_groups(3, 1)
    print(f"Count: {len(result)}\n")

    print("TEST 2 - Get users not affected")
    result = get_users_not_affected(1, 3)
    print(f"Count: {len(result)}\n")

    print("TEST 3 - Get subject group")
    result = get_subject_group(3)
    print(f"Result: {result}\n")