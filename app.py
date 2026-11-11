import services
import db
from pathlib import Path
import tkinter as tk
DEFAULT_CART_ID = 1  

def initialize_database_if_needed():
    """Helper to ensure the SQLite database is created and seeded if missing."""
    db_file = db.DB_PATH
    if not db_file.exists():
        print("[*] Initializing database from database.sql...")
        db_file.parent.mkdir(parents=True, exist_ok=True)
        # Point to database.sql inside the carco-db folder
        schema_path = Path(__file__).parent / "carco-db" / "database.sql"
        schema_sql = schema_path.read_text()
        with db.get_connection() as conn:
            conn.executescript(schema_sql)
        print("[+] Database initialized successfully.")


def main():
    initialize_database_if_needed()
    while True:
        print("\n==============================")
        print("      CARCO E-STORE (CLI)     ")
        print("==============================")
        print("1. Browse & Filter Products (FR-1)")
        print("2. Find Parts by Vehicle (FR-1)")
        print("3. View Product Details (FR-2)")
        print("4. Add to cart (FR-3)")
        print("5. View current total (FR-3)")
        print("6. Admin: List All Products (FR-8)")
        print("7. Admin: Add Product (FR-8)")
        print("8. Admin: Edit Product (FR-8)")
        print("9. Admin: Delete Product (FR-8)")
        print("0. Exit")

        
        choice = input("\nSelect an option (0-9): ").strip()
        
        while choice not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            print("[-] Invalid selection. Choose 0-9.")
            choice = input("\nSelect an option (0-9): ").strip()

        if choice == "1":
            browse()
                
        elif choice == "2":
            findParts()
                
        elif choice == "3":
            prodView()
                
        elif choice == "4":
            addCart()

        elif choice == "5":
            disTotal()

        elif choice == "6":
            adminListProducts()

        elif choice == "7":
            adminAddProduct()

        elif choice == "8":
            adminEditProduct()

        elif choice == "9":
            adminDeleteProduct()

        elif choice == "0":
            print("Exited. Goodbye.")
            break
    return


def browse():
    print("\n--- Browse & Filter Products ---")
    cat_input = input("Category ID (Leave blank for all): ").strip()
    brand_input = input("Brand ID (Leave blank for all): ").strip()
    max_input = input("Max Price in $ (e.g., 150, leave blank for any): ").strip()
    
    cat_id = int(cat_input) if cat_input.isdigit() else None
    brand_id = int(brand_input) if brand_input.isdigit() else None
    max_p = float(max_input) if max_input else None
    
    results = services.search_catalog(category_id=cat_id, brand_id=brand_id, max_price=max_p)
    
    print(f"\nFound {len(results)} product(s):")
    for p in results:
        print(f"  ID: {p['product_id']} | {p['name']} ({p['brand']} - {p['category']}) - {p['price_formatted']}") 

def findParts():
    print("\n--- Fitment Search ---")
    make = input("Vehicle Make (e.g., Honda): ").strip()
    model = input("Vehicle Model (e.g., Civic): ").strip()
    year_str = input("Vehicle Year (e.g., 2022): ").strip()
    
    if year_str.isdigit():
        parts = services.get_filtered_parts_by_vehicle(make, model, int(year_str))
        print(f"\nParts fitting {year_str} {make} {model}:")
        for p in parts:
            print(f"  ID: {p['product_id']} | {p['name']} - {p['price_formatted']}")
    else:
        print("[-] Invalid year format.")

def prodView():
    print("\n--- Product Details View ---")
    pid_str = input("Enter Product ID: ").strip()
    if pid_str.isdigit():
        prod = services.get_product_details(int(pid_str))
        if prod:
            print(f"\n=== {prod['name']} ===")
            print(f"Brand: {prod.get('brand', 'N/A')}")
            print(f"Price: {prod['price_formatted']}")
            print(f"Status: {prod['availability_status']} ({prod['stock']} units left)")
            print(f"Description: {prod['description']}")
            print(f"Install Instructions: {prod['install_instructions']}")
            print("Vehicle Fitment:")
            if prod["fitment"]:
                for f in prod["fitment"]:
                    print(f"  - {f['year']} {f['make']} {f['model']}")
            else:
                print("  - Universal / No specific fitment listed")
        else:
            print("[-] Product not found or inactive.")
    else:
        print("[-] Invalid ID.")

def addCart():
    """UI-3: Prompt for product and quantity, then insert/update cart."""

    print("\n--- Add Item to Cart ---")
    pid_input = input("Enter Product ID: ").strip()
    if not pid_input.isdigit():
        print("[-] Invalid Product ID. Must be an integer.")
        return

    product_id = int(pid_input)

    qty_input = input("Enter Quantity (default 1): ").strip()
    if not qty_input:
        quantity = 1
    elif qty_input.isdigit() and int(qty_input) > 0:
        quantity = int(qty_input)
    else:
        print("[-] Quantity must be a positive integer.")
        return
    cart_id = input("Enter the cart ID you want to add this to: ")
    if not cart_id.isdigit():
        print("[-] Invalid cart ID. Must be an integer.")
        return

    cart_id = int(cart_id)

    try:
        services.add_to_cart(cart_id, product_id, quantity)

    except Exception as e:
        print(f"[-] Could not add product: {e}")

    return

def disTotal():
    cart_id = input("Which cart would you like to see the total for?: ")        
    if not cart_id.isdigit():
        print("[-] Invalid cart ID. Must be an integer.")
        return
    
    services.display_total(cart_id)

def adminListProducts():
    """FR-8: display all products (active + inactive) in a table."""
    print("\n--- Admin: Product Management ---")
    products = services.admin_list_products()
    if not products:
        print("No products in catalog.")
        return
    print(f"{'ID':<5}{'Name':<24}{'Price':<10}{'Stock':<7}{'Status':<10}{'Category':<15}Brand")
    print("-" * 80)
    for p in products:
        print(f"{p['product_id']:<5}{p['name'][:23]:<24}"
              f"{p['price_formatted']:<10}{p['stock']:<7}"
              f"{p['status']:<10}{(p['category'] or '')[:14]:<15}"
              f"{p['brand'] or 'N/A'}")

def adminAddProduct():
    """FR-8: prompt for required fields and create a listing."""
    print("\n--- Admin: Add New Product ---")
    name = input("Product name: ").strip()
    price_input = input("Price ($, e.g., 129.99): ").strip()
    cat_input = input("Category ID: ").strip()
    brand_input = input("Brand ID: ").strip()
    stock_input = input("Initial stock (default 0): ").strip() or "0"
    desc = input("Description (optional): ").strip()
    inst = input("Install instructions (optional): ").strip()

    try:
        price = float(price_input)
        category_id = int(cat_input)
        brand_id = int(brand_input)
        stock = int(stock_input)
    except ValueError:
        print("[-] Invalid input. Price must be a number; IDs and stock must be integers.")
        return

    try:
        new_id = services.admin_add_product(
            name=name, price=price, category_id=category_id,
            brand_id=brand_id, stock=stock, description=desc,
            install_instructions=inst)
        print(f"[+] Product created with ID {new_id}.")
    except Exception as e:
        print(f"[-] Could not create product: {e}")

def adminEditProduct():
    """FR-8: update chosen fields of an existing product."""
    print("\n--- Admin: Edit Product ---")
    pid_input = input("Product ID to edit: ").strip()
    if not pid_input.isdigit():
        print("[-] Invalid product ID.")
        return
    product_id = int(pid_input)

    existing = services.get_product_details(product_id)
    if not existing:
        print("[-] Product not found.")
        return
    print(f"Editing: {existing['name']} ({existing['price_formatted']})")

    fields = {}

    new_name = input("New name (blank to keep): ").strip()
    if new_name:
        fields["name"] = new_name

    new_price = input("New price in $ (blank to keep): ").strip()
    if new_price:
        try:
            fields["price"] = float(new_price)
        except ValueError:
            print("[-] Invalid price."); return

    new_stock = input("New stock (blank to keep): ").strip()
    if new_stock:
        try:
            fields["stock"] = int(new_stock)
        except ValueError:
            print("[-] Invalid stock."); return

    new_cat = input("New category ID (blank to keep): ").strip()
    if new_cat:
        if not new_cat.isdigit():
            print("[-] Invalid category ID."); return
        fields["category_id"] = int(new_cat)

    new_brand = input("New brand ID (blank to keep): ").strip()
    if new_brand:
        if not new_brand.isdigit():
            print("[-] Invalid brand ID."); return
        fields["brand_id"] = int(new_brand)

    new_desc = input("New description (blank to keep): ").strip()
    if new_desc:
        fields["description"] = new_desc

    if not fields:
        print("[*] No changes made.")
        return

    try:
        ok = services.admin_edit_product(product_id, **fields)
        print("[+] Product updated." if ok else "[-] Product not found.")
    except Exception as e:
        print(f"[-] Update failed: {e}")

def adminDeleteProduct():
    """FR-8: soft-delete a product listing after confirmation."""
    print("\n--- Admin: Delete Product ---")
    pid_input = input("Product ID to delete: ").strip()
    if not pid_input.isdigit():
        print("[-] Invalid product ID.")
        return
    product_id = int(pid_input)

    existing = services.get_product_details(product_id)
    if not existing:
        print("[-] Product not found.")
        return
    print(f"You are about to remove: {existing['name']} ({existing['price_formatted']})")
    confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
    if confirm != "yes":
        print("[*] Deletion cancelled.")
        return

    ok = services.admin_delete_product(product_id)
    print("[+] Product removed from catalog." if ok else "[-] Product not found.")
    
     
if __name__ == "__main__":
    main()
