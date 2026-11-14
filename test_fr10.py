import sqlite3
from datetime import datetime, timedelta
import db
import fr10

def test_fr10_data_retention_purge():
    print("Running test_fr10_data_retention_purge...")
    old_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S")
    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO orders (user_id, ship_name, ship_address, ship_city, ship_postal_code, 
                                subtotal_cents, tax_cents, shipping_cents, total_cents, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "Jane Doe", "456 Test Ave", "Toronto", "M5V 2H1", 10000, 1300, 1500, 12800, "Delivered", old_date)
        )
        order_id = cursor.lastrowid
        conn.commit()

    result = fr10.purge_expired_shipping_data(retention_days=30)
    assert result["success"] == True
    assert order_id in result["purged_order_ids"]

    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT ship_name, ship_address, total_cents FROM orders WHERE order_id = ?",
            (order_id,)
        ).fetchone()
        assert row["ship_name"] == "[ANONYMIZED]"
        assert row["ship_address"] == "[ANONYMIZED]"
        assert row["total_cents"] == 12800

    print("[PASS] FR-10 Data Retention Purge Test Passed Successfully!")

def test_fr10_breach_notification():
    print("Running test_fr10_breach_notification...")
    result = fr10.dispatch_breach_notifications("2020-01-01 00:00:00", "2030-12-31 23:59:59")
    assert result["success"] == True
    assert isinstance(result["notified_count"], int)
    print("[PASS] FR-10 Breach Notification Test Passed Successfully!")

if __name__ == "__main__":
    test_fr10_data_retention_purge()
    test_fr10_breach_notification()
    print("All FR-10 tests passed!")