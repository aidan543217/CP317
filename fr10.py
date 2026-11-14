import sqlite3
from datetime import datetime, timedelta
import db


def purge_expired_shipping_data(retention_days=30):
    """
    FR-10: Purges or anonymizes sensitive customer PII (ship_name, ship_address, ship_city, ship_postal_code)
    from orders older than the specified refund window (default 30 days).
    Retains financial totals for FR-9 sales reporting.
    """
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")

    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT order_id
            FROM orders
            WHERE created_at < ?
              AND ship_address != '[ANONYMIZED]'
            """,
            (cutoff_str,)
        )
        expired_orders = [row["order_id"] for row in cursor.fetchall()]

        conn.execute(
            """
            UPDATE orders
            SET ship_name        = '[ANONYMIZED]',
                ship_address     = '[ANONYMIZED]',
                ship_city        = '[ANONYMIZED]',
                ship_postal_code = '[ANONYMIZED]'
            WHERE created_at < ?
            """,
            (cutoff_str,)
        )
        conn.commit()

    return {
        "success": True,
        "purged_count": len(expired_orders),
        "purged_order_ids": expired_orders
    }


def dispatch_breach_notifications(start_date, end_date):
    """
    FR-10: Queries customers affected by a security incident within a given timeframe
    and generates automated security alert emails by joining orders and users.
    """
    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT DISTINCT o.order_id,
                            o.order_number,
                            o.created_at,
                            COALESCE(o.ship_name, 'Customer')        AS ship_name,
                            COALESCE(u.email, 'unknown@example.com') AS email
            FROM orders o
                     LEFT JOIN users u ON u.user_id = o.user_id
            WHERE o.created_at BETWEEN ? AND ?
              AND COALESCE(o.ship_address, '') != '[ANONYMIZED]'
            """,
            (start_date, end_date)
        )
        affected_customers = [dict(row) for row in cursor.fetchall()]

    notifications = []
    for customer in affected_customers:
        email_body = (
            f"SECURITY ALERT - CARCO E-STORE\n\n"
            f"Hello {customer['ship_name']},\n\n"
            f"We are writing to inform you of a recent security incident involving our system "
            f"affecting your order #{customer['order_number'] or customer['order_id']} placed on {customer['created_at']}.\n"
            f"While payment data remains secure through Shopify tokenization, your shipping "
            f"and contact details may have been exposed.\n\n"
            f"Please update your account credentials immediately and monitor your financial statements.\n"
            f"We sincerely apologize for this incident."
        )
        notifications.append({
            "recipient": customer["email"],
            "subject": f"URGENT: Security Notice Regarding Carco Order #{customer['order_number'] or customer['order_id']}",
            "body": email_body
        })

    return {
        "success": True,
        "notified_count": len(notifications),
        "notifications": notifications
    }