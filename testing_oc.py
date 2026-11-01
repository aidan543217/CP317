import sqlite3
from pathlib import Path

# --- 1. Database Setup & Helpers ---
DB_PATH = Path(__file__).parent / "carco-db" / "carco.db"
TAX_RATE = 0.13  # Ontario HST


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def get_cart_total(cart_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(p.price_cents * ci.quantity), 0) AS subtotal "
            "FROM cart_items ci JOIN products p ON p.product_id = ci.product_id "
            "WHERE ci.cart_id = ?", (cart_id,)
        ).fetchone()
    subtotal = row["subtotal"]
    tax = round(subtotal * TAX_RATE)
    return {"subtotal_cents": subtotal, "tax_cents": tax, "total_cents": subtotal + tax}


def save_order(cart_id, full_name, email, address, totals):
    with get_connection() as conn:
        # Fetch items from the cart
        items = [dict(r) for r in conn.execute(
            "SELECT ci.product_id, p.name, ci.quantity, p.price_cents "
            "FROM cart_items ci JOIN products p ON p.product_id = ci.product_id "
            "WHERE ci.cart_id = ?", (cart_id,)
        )]

        if not items:
            return None

        # Insert into orders table
        cursor = conn.execute(
            """INSERT INTO orders (full_name, email, address, subtotal_cents, tax_cents, total_cents, status)
               VALUES (?, ?, ?, ?, ?, ?, 'Processing')""",
            (full_name, email, address, totals["subtotal_cents"], totals["tax_cents"], totals["total_cents"])
        )
        order_id = cursor.lastrowid

        # Insert into order_items table
        for item in items:
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_cents) VALUES (?, ?, ?, ?)",
                (order_id, item["product_id"], item["quantity"], item["price_cents"])
            )

        # Clear cart items after successful order placement
        conn.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))

        return {
            "order_id": order_id,
            "full_name": full_name,
            "email": email,
            "address": address,
            "items": items,
            **totals
        }


# --- 2. Service Layer: Order Confirmation ---
def process_order_confirmation(cart_id, full_name, email, address, card_number):

    totals = get_cart_total(cart_id)
    if totals["subtotal_cents"] == 0:
        return {"success": False, "message": "Cart is empty. Cannot process confirmation."}

    # Save order and clear cart
    order = save_order(cart_id, full_name, email, address, totals)
    if not order:
        return {"success": False, "message": "Failed to save order to database."}

    # Format monetary values for presentation
    order["subtotal_formatted"] = f"${order['subtotal_cents'] / 100:.2f}"
    order["tax_formatted"] = f"${order['tax_cents'] / 100:.2f}"
    order["total_formatted"] = f"${order['total_cents'] / 100:.2f}"
    order["masked_card"] = f"****-****-****-{card_number[-4:]}" if len(card_number) >= 4 else "****"

    # Build Confirmation Email Content
    email_body = (
        f"========================================\n"
        f"         CARCO E-STORE RECEIPT          \n"
        f"========================================\n"
        f"Hello {full_name},\n\n"
        f"Thank you for your purchase! Your order has been successfully placed.\n"
        f"Order ID: #{order['order_id']}\n\n"
        f"--- Shipping Details ---\n"
        f"Address: {address}\n\n"
        f"--- Order Totals ---\n"
        f"Subtotal: {order['subtotal_formatted']}\n"
        f"Tax (Ontario 13%): {order['tax_formatted']}\n"
        f"Total Charged: {order['total_formatted']}\n\n"
        f"We will notify you via email when your items ship."
    )

    order["email_confirmation"] = {
        "recipient": email,
        "subject": f"Carco Order Confirmation #{order['order_id']}",
        "body": email_body
    }
    order["success"] = True
    return order


# --- 3. Interactive CLI Execution ---
def main():
    print("========================================")
    print("    ORD-1: ORDER CONFIRMATION MODULE    ")
    print("========================================")

    cart_id_input = input("Enter Cart ID to Checkout (e.g., 1): ").strip()
    cart_id = int(cart_id_input) if cart_id_input.isdigit() else 1

    name = input("Enter Customer Full Name: ").strip()
    email = input("Enter Customer Email Address: ").strip()
    address = input("Enter Shipping Address: ").strip()
    card = input("Enter Credit Card Number (Simulated): ").strip()

    print("\nProcessing Order...")
    result = process_order_confirmation(cart_id, name, email, address, card)

    if result.get("success"):
        print("\n[+] ORDER PLACED SUCCESSFULLY!")
        print(f"  Order ID     : #{result['order_id']}")
        print(f"  Customer     : {result['full_name']} ({result['email']})")
        print(f"  Ship To      : {result['address']}")
        print(f"  Payment      : Charged to card ending in {result['masked_card']}")
        print(f"  Subtotal     : {result['subtotal_formatted']}")
        print(f"  Tax (13%)    : {result['tax_formatted']}")
        print(f"  Total        : {result['total_formatted']}")

        print("\n----------------------------------------")
        print("[+] SIMULATED CONFIRMATION EMAIL DISPATCHED:")
        print("----------------------------------------")
        print(result["email_confirmation"]["body"])
        print("----------------------------------------")
    else:
        print(f"\n[-] Error: {result.get('message')}")


if __name__ == "__main__":
    main()