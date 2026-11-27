import sqlite3
from datetime import datetime, timedelta
import json
from pathlib import Path
import db


def _ensure_database(conn):
    """Ensure the SQLite schema (including orders and users) exists before querying."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
    ).fetchone()
    if row is None:
        schema_path = Path(__file__).resolve().parent / "carco-db" / "database.sql"
        if schema_path.exists():
            conn.executescript(schema_path.read_text(encoding="utf-8"))


def _parse_timestamp(value, label):
    """Validate and normalize a datetime string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty date/datetime string.")
    cleaned = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            if fmt == "%Y-%m-%d":
                return dt.strftime("%Y-%m-%d 00:00:00")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise ValueError(
        f"Invalid {label} format '{value}'. Expected 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
    )


def ensure_audit_table(conn):
    """Create an audit table for FR-10 compliance actions if it does not exist yet."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fr10_audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            details TEXT NOT NULL,
            affected_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )


def _record_audit(conn, action_type, details_dict, affected_count):
    ensure_audit_table(conn)
    conn.execute(
        """
        INSERT INTO fr10_audit_log (action_type, details, affected_count, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            action_type,
            json.dumps(details_dict),
            affected_count,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )


def purge_expired_shipping_data(retention_days=30, dry_run=False):
    """
    FR-10 (Sprint 3): Purges or anonymizes sensitive shipping PII and clears
    stored order payment tokens for orders older than `retention_days` (default 30).
    Preserves monetary totals for FR-9 sales reporting and records an audit entry.
    """
    if isinstance(retention_days, bool) or not isinstance(retention_days, int) or retention_days < 0:
        raise ValueError("retention_days must be a non-negative integer.")

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")

    with db.get_connection() as conn:
        _ensure_database(conn)
        cursor = conn.execute(
            """
            SELECT order_id FROM orders
            WHERE created_at < ? AND COALESCE(ship_address, '') != '[ANONYMIZED]'
            """,
            (cutoff_str,),
        )
        expired_orders = [row["order_id"] for row in cursor.fetchall()]

        if not dry_run and expired_orders:
            conn.execute(
                """
                UPDATE orders
                SET ship_name = '[ANONYMIZED]',
                    ship_address = '[ANONYMIZED]',
                    ship_city = '[ANONYMIZED]',
                    ship_postal_code = '[ANONYMIZED]',
                    shopify_payment_token = NULL
                WHERE created_at < ?
                  AND COALESCE(ship_address, '') != '[ANONYMIZED]'
                """,
                (cutoff_str,),
            )

        if not dry_run:
            _record_audit(
                conn,
                action_type="DATA_RETENTION_PURGE",
                details_dict={
                    "retention_days": retention_days,
                    "cutoff_timestamp": cutoff_str,
                    "purged_order_ids": expired_orders,
                },
                affected_count=len(expired_orders),
            )
        conn.commit()

    return {
        "success": True,
        "dry_run": dry_run,
        "retention_days": retention_days,
        "cutoff_timestamp": cutoff_str,
        "purged_count": len(expired_orders),
        "purged_order_ids": expired_orders,
    }


def dispatch_breach_notifications(start_date, end_date, record_audit=True):
    """
    FR-10 (Sprint 3): Queries customers with orders inside [start_date, end_date]
    whose shipping records have not already been anonymized, builds urgent alert
    emails with protective guidance, and optionally logs the dispatch to audit history.
    """
    start_norm = _parse_timestamp(start_date, "start_date")
    end_norm = _parse_timestamp(end_date, "end_date")
    if len(end_date.strip()) == 10:
        end_norm = f"{end_date.strip()} 23:59:59"

    if start_norm > end_norm:
        raise ValueError("start_date cannot be later than end_date.")

    with db.get_connection() as conn:
        _ensure_database(conn)
        cursor = conn.execute(
            """
            SELECT DISTINCT o.order_id, o.order_number, o.created_at,
                   COALESCE(o.ship_name, 'Customer') AS ship_name,
                   COALESCE(u.email, 'unknown@example.com') AS email
            FROM orders o
            LEFT JOIN users u ON u.user_id = o.user_id
            WHERE o.created_at BETWEEN ? AND ?
              AND COALESCE(o.ship_address, '') != '[ANONYMIZED]'
            ORDER BY o.order_id
            """,
            (start_norm, end_norm),
        )
        affected_customers = [dict(row) for row in cursor.fetchall()]

        notifications = []
        for customer in affected_customers:
            order_ref = customer["order_number"] or customer["order_id"]
            email_body = (
                f"SECURITY ALERT - CARCO E-STORE\n\n"
                f"Hello {customer['ship_name']},\n\n"
                f"We are writing to inform you of a recent security incident involving our system "
                f"affecting your order #{order_ref} placed on {customer['created_at']}.\n"
                f"While card details are never stored locally and payments are processed through "
                f"Shopify tokenization, your shipping and contact details may have been affected.\n\n"
                f"Recommended Protective Actions:\n"
                f"1. Change your Carco account password immediately.\n"
                f"2. Monitor your account activity and financial statements for unauthorized changes.\n"
                f"3. Report any suspicious messages claiming to be from Carco support.\n\n"
                f"We sincerely apologize for this incident."
            )
            notifications.append(
                {
                    "order_id": customer["order_id"],
                    "recipient": customer["email"],
                    "subject": f"URGENT: Security Notice Regarding Carco Order #{order_ref}",
                    "body": email_body,
                }
            )

        if record_audit:
            _record_audit(
                conn,
                action_type="BREACH_NOTIFICATION_DISPATCH",
                details_dict={
                    "window_start": start_norm,
                    "window_end": end_norm,
                    "recipients": [n["recipient"] for n in notifications],
                },
                affected_count=len(notifications),
            )
            conn.commit()

    return {
        "success": True,
        "window_start": start_norm,
        "window_end": end_norm,
        "notified_count": len(notifications),
        "notifications": notifications,
    }


def get_audit_logs(limit=20):
    """Retrieve recent FR-10 audit log entries for compliance inspection."""
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer.")
    with db.get_connection() as conn:
        _ensure_database(conn)
        ensure_audit_table(conn)
        rows = conn.execute(
            """
            SELECT log_id, action_type, details, affected_count, created_at
            FROM fr10_audit_log
            ORDER BY log_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def run_fr10_cli():
    """Interactive CLI helper for demonstrating FR-10 features in Sprint 3."""
    while True:
        print("\n=== FR-10: DATA RETENTION & BREACH NOTIFICATION ===")
        print("1. Preview Expired Shipping Data Purge (Dry Run)")
        print("2. Execute Expired Shipping Data Purge")
        print("3. Dispatch Breach Notifications for Date Range")
        print("4. View FR-10 Audit Log")
        print("0. Return")
        choice = input("Select an option: ").strip()

        if choice == "1":
            days_in = input("Retention days (default 30): ").strip()
            days = int(days_in) if days_in else 30
            res = purge_expired_shipping_data(retention_days=days, dry_run=True)
            print(f"[DRY RUN] Orders eligible for purge: {res['purged_count']} -> {res['purged_order_ids']}")
        elif choice == "2":
            days_in = input("Retention days (default 30): ").strip()
            days = int(days_in) if days_in else 30
            res = purge_expired_shipping_data(retention_days=days, dry_run=False)
            print(f"[+] Purged {res['purged_count']} expired order(s): {res['purged_order_ids']}")
        elif choice == "3":
            start = input("Start date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS): ").strip()
            end = input("End date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS): ").strip()
            res = dispatch_breach_notifications(start, end)
            print(f"[+] Generated {res['notified_count']} breach notification(s).")
            for note in res["notifications"]:
                print(f"  -> To: {note['recipient']} | Subject: {note['subject']}")
        elif choice == "4":
            logs = get_audit_logs()
            print(f"\nRecent Audit Entries ({len(logs)}):")
            for entry in logs:
                print(f"  #{entry['log_id']} [{entry['created_at']}] {entry['action_type']} (affected={entry['affected_count']})")
        elif choice == "0":
            break
        else:
            print("[-] Invalid choice.")


if __name__ == "__main__":
    print("Testing FR-10 module standalone...")
    res_purge = purge_expired_shipping_data(30, dry_run=True)
    print("Dry-run purge result:", res_purge)
    res_breach = dispatch_breach_notifications("2020-01-01 00:00:00", "2030-12-31 23:59:59", record_audit=False)
    print("Breach notification result count:", res_breach["notified_count"])