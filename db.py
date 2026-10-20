import sqlite3
from pathlib import Path

# Works no matter which folder the app is started from
DB_PATH = Path(__file__).parent / "carco-db" / "carco.db"
TAX_RATE = 0.13  # Ontario HST


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")   # must be set on every connection
    conn.row_factory = sqlite3.Row             # read columns by name
    return conn


def get_products(category_id=None, brand_id=None, min_cents=None, max_cents=None):
    """UI-1: browse + filter. Pass None to skip a filter."""
    sql = """
        SELECT p.product_id, p.name, p.price_cents, p.image_url,
               c.name AS category, b.name AS brand
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        LEFT JOIN brands b ON b.brand_id = p.brand_id
        WHERE p.is_active = 1
          AND (? IS NULL OR p.category_id = ?)
          AND (? IS NULL OR p.brand_id = ?)
          AND (? IS NULL OR p.price_cents >= ?)
          AND (? IS NULL OR p.price_cents <= ?)
        ORDER BY p.name
    """
    params = (category_id, category_id, brand_id, brand_id,
              min_cents, min_cents, max_cents, max_cents)
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, params)]


def find_parts(make, model, year):
    """UI-1: parts that fit a vehicle."""
    sql = """
        SELECT p.product_id, p.name, p.price_cents
        FROM products p
        JOIN product_fitment f ON f.product_id = p.product_id
        JOIN vehicles v ON v.vehicle_id = f.vehicle_id
        WHERE p.is_active = 1 AND v.make = ? AND v.model = ? AND v.year = ?
    """
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, (make, model, year))]


def get_product(product_id):
    """UI-2: one product with availability and fitment list."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT *, (stock > 0) AS in_stock FROM products "
            "WHERE product_id = ? AND is_active = 1", (product_id,)).fetchone()
        if row is None:
            return None
        product = dict(row)
        product["fitment"] = [dict(r) for r in conn.execute(
            "SELECT v.make, v.model, v.year FROM product_fitment f "
            "JOIN vehicles v ON v.vehicle_id = f.vehicle_id "
            "WHERE f.product_id = ?", (product_id,))]
        return product


def add_to_cart(cart_id, product_id, quantity=1):
    """UI-3: add item, or increase quantity if already in the cart."""
    with get_connection() as conn:   # 'with' commits the change
        conn.execute(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?) "
            "ON CONFLICT(cart_id, product_id) "
            "DO UPDATE SET quantity = quantity + excluded.quantity",
            (cart_id, product_id, quantity))


def get_cart_total(cart_id):
    """UI-3: subtotal and tax in cents."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(p.price_cents * ci.quantity), 0) AS subtotal "
            "FROM cart_items ci JOIN products p ON p.product_id = ci.product_id "
            "WHERE ci.cart_id = ?", (cart_id,)).fetchone()
    subtotal = row["subtotal"]
    tax = round(subtotal * TAX_RATE)
    return {"subtotal_cents": subtotal, "tax_cents": tax, "total_cents": subtotal + tax}