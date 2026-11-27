import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import db
import fr10


def _ensure_schema():
    with db.get_connection() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
        ).fetchone()
        if not exists:
            schema_sql = (Path(__file__).resolve().parent / "carco-db" / "database.sql").read_text(encoding="utf-8")
            conn.executescript(schema_sql)


def _expect_value_error(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(f"Expected ValueError for {label}")


def test_fr10_validation():
    print("Running test_fr10_validation...")
    _expect_value_error(lambda: fr10.purge_expired_shipping_data(-1), "negative retention_days")
    _expect_value_error(lambda: fr10.purge_expired_shipping_data(True), "boolean retention_days")
    _expect_value_error(lambda: fr10.dispatch_breach_notifications("bad-date", "2026-12-31"), "bad start_date")
    _expect_value_error(lambda: fr10.dispatch_breach_notifications("2026-12-01", "2026-11-01"), "start_date > end_date")
    print("[PASS] FR-10 Input Validation Tests Passed Successfully!")


def test_fr10_dry_run_and_data_retention_purge():
    print("Running test_fr10_dry_run_and_data_retention_purge...")
    _ensure_schema()
    old_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S")
    unique_order_num = f"ORD-FR10-TEST-{int(datetime.now().timestamp() * 1000)}"
    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO orders (user_id, order_number, ship_name, ship_address, ship_city, ship_postal_code,
                                subtotal_cents, tax_cents, shipping_cents, total_cents,
                                shopify_payment_token, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                unique_order_num,
                "Jane Doe",
                "456 Test Ave",
                "Toronto",
                "M5V 2H1",
                10000,
                1300,
                1500,
                12800,
                "tok_test_12345",
                "Delivered",
                old_date,
            ),
        )
        order_id = cursor.lastrowid
        conn.commit()

    preview = fr10.purge_expired_shipping_data(retention_days=30, dry_run=True)
    assert preview["success"] is True
    assert preview["dry_run"] is True
    assert order_id in preview["purged_order_ids"]

    with db.get_connection() as conn:
        before_row = conn.execute(
            "SELECT ship_name, shopify_payment_token FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()
        assert before_row["ship_name"] == "Jane Doe"
        assert before_row["shopify_payment_token"] == "tok_test_12345"

    result = fr10.purge_expired_shipping_data(retention_days=30, dry_run=False)
    assert result["success"] is True
    assert result["dry_run"] is False
    assert order_id in result["purged_order_ids"]

    with db.get_connection() as conn:
        row = conn.execute(
            """
            SELECT ship_name, ship_address, ship_city, ship_postal_code,
                   shopify_payment_token, total_cents
            FROM orders WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()
        assert row["ship_name"] == "[ANONYMIZED]"
        assert row["ship_address"] == "[ANONYMIZED]"
        assert row["ship_city"] == "[ANONYMIZED]"
        assert row["ship_postal_code"] == "[ANONYMIZED]"
        assert row["shopify_payment_token"] is None
        assert row["total_cents"] == 12800

    logs = fr10.get_audit_logs(limit=5)
    assert len(logs) >= 1
    assert any(entry["action_type"] == "DATA_RETENTION_PURGE" for entry in logs)

    print("[PASS] FR-10 Dry Run & Data Retention Purge Tests Passed Successfully!")


def test_fr10_breach_notification():
    print("Running test_fr10_breach_notification...")
    _ensure_schema()
    recent_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    unique_breach_num = f"ORD-FR10-BREACH-{int(datetime.now().timestamp() * 1000)}"
    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO orders (user_id, order_number, ship_name, ship_address, ship_city, ship_postal_code,
                                subtotal_cents, tax_cents, shipping_cents, total_cents, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                unique_breach_num,
                "Alex Smith",
                "789 King St",
                "Waterloo",
                "N2L 3G1",
                5000,
                650,
                1000,
                6650,
                "Processing",
                recent_date,
            ),
        )
        order_id = cursor.lastrowid
        conn.commit()

    start_str = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    end_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    result = fr10.dispatch_breach_notifications(start_str, end_str, record_audit=True)

    assert result["success"] is True
    assert result["notified_count"] >= 1
    matching = [n for n in result["notifications"] if n["order_id"] == order_id]
    assert len(matching) == 1
    assert "Alex Smith" in matching[0]["body"]
    assert "Recommended Protective Actions" in matching[0]["body"]

    print("[PASS] FR-10 Breach Notification Tests Passed Successfully!")


if __name__ == "__main__":
    test_fr10_validation()
    test_fr10_dry_run_and_data_retention_purge()
    test_fr10_breach_notification()
    print("All Sprint 3 FR-10 tests passed!")