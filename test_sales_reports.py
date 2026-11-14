import sqlite3
from datetime import datetime
import db
import services

def test_sales():
    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO orders (user_id, subtotal_cents, tax_cents, shipping_cents, total_cents, status, created_at)
            VALUES (1, 10000, 1300, 0, 11300, 'Delivered', datetime('now'))
            """
        )
        conn.commit()

    daily = services.admin_daily_sales_report()
    assert isinstance(daily, list)
    assert len(daily) > 0
    assert "date" in daily[0]
    assert "total_formatted" in daily[0]

    monthly = services.admin_monthly_sales_report()
    assert isinstance(monthly, list)
    assert len(monthly) > 0
    assert "month" in monthly[0]  # <-- Fixed from "monthly" to "month"
    assert "total_formatted" in monthly[0]


if __name__ == "__main__":
    test_sales()