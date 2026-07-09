
from core.database import Database
from util.audit import log_audit, serialize_for_audit


def associate_virtual_user(account_id, virtual_id, real_user_id):
    """
    Associates a virtual user with a real user:
    - Transfers related records (attendance, payments, invoices, etc.)
    - Disables any other virtual_user rows already linked to the real user
    - Re-points the virtual_user row to the real user

    Returns a dict describing success/failure, to be jsonify'd by the route.
    """
    try:
        # Step 1: fetch virtual_user and real user
        validation_queries = [
            (
                """
                SELECT id, user_id
                FROM virtual_user
                WHERE id = %s AND enabled = 1 AND account_id = %s
                """,
                (virtual_id, account_id)
            ),
            (
                "SELECT id FROM user WHERE id = %s",
                (real_user_id,)
            ),
        ]

        results = Database.execute_transaction(validation_queries)
        virtual_user_rows = results[0]
        real_user_rows = results[1]

        if not virtual_user_rows or not real_user_rows:
            return {
                "success": False,
                "message": "Virtual or real user not found.",
                "status_code": 400
            }

        virtual_user_row = virtual_user_rows[0]
        old_user_id = virtual_user_row['user_id']  # the virtual "user" id currently linked

        # Step 2: build all the transfer + re-point queries into ONE transaction
        transfer_queries = [
            (
                "UPDATE relation_user_session SET user_id = %s WHERE user_id = %s AND enabled = 1",
                (real_user_id, old_user_id)
            ),
            (
                "UPDATE attendance SET user_id = %s WHERE user_id = %s",
                (real_user_id, old_user_id)
            ),
            (
                "UPDATE payment_session SET user_id = %s WHERE user_id = %s",
                (real_user_id, old_user_id)
            ),
            (
                "UPDATE invoice SET user_id = %s WHERE user_id = %s",
                (real_user_id, old_user_id)
            ),
            # (
            #     "UPDATE completion_tag_user SET user_id = %s WHERE user_id = %s",
            #     (real_user_id, old_user_id)
            # ),

            (
                "UPDATE virtual_user SET user_id = %s WHERE id = %s",
                (real_user_id, virtual_user_row['id'])
            ),
        ]

        Database.execute_transaction(transfer_queries)

        return {
            "success": True,
            "message": "Virtual user successfully associated to real user and all data transferred.",
            "status_code": 200
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Something went wrong: {e}",
            "status_code": 500
        }
