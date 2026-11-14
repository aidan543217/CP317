import services
import db
from pathlib import Path
import tkinter as tk
DEFAULT_CART_ID = 1  

root = tk.Tk()
root.geometry("800x600")

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
    funcchoice = input("\nNewer (1) or older (2) functions : ").strip()
            
    while funcchoice not in ["1", "2"]:
        print("[-] Invalid selection. Choose 1 or 2.")
        funcchoice = input("\nSelect an option (1 or 2): ").strip()
 
    if funcchoice == "1":
        
        header = (
            "=============================="
            "\n        CARCO E-STORE (CLI)     "
            "\n=============================="
        )
        h1 = tk.Label(root, text=header, wraplength=500)
        h1.pack(side="top")
        B1 = tk.Button(root, text="1. Browse & Filter Products (FR-1)", command=browse).pack(side="top", pady=10)
        B2 = tk.Button(root, text="2. Find Parts by Vehicle (FR-1)", command=findParts).pack(side="top", pady=5)
        B3 = tk.Button(root, text="3. View Product Details (FR-2)", command=prodView).pack(side="top", pady=5)
        B4 = tk.Button(root, text="4. Add to cart (FR-3)", command=addCart).pack(side="top", pady=5)
        B5= tk.Button(root, text="5. View current total (FR-3)", command=disTotal).pack(side="top", pady=5)
        B_track = tk.Button(root, text="6. Track Order Status", command=trackOrder).pack(side="top", pady=5)
        B6 = tk.Button(root, text="7. Admin options (FR-8)", command=adminOptions).pack(side="top", pady=5)
        B7 = tk.Button(root, text="0. Exit", command=root.destroy).pack(side="top", pady=5)
        root.mainloop()

  
    else:
        
        print("\n==============================")
        print("      CARCO E-STORE (CLI)     ")
        print("==============================")
    """
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
    """

    return


def browse():
    t1 = "-- Browse & Filter Products ---"
    l1 = "Enter Category ID (Leave blank for all): "
    l2 = "Brand ID (Leave blank for all): "
    l3 = "Max Price in $ (e.g., 150, leave blank for any): "
    cat_ID = tk.StringVar(value = "")
    cat_ID = inp_subwindow(t1, l1, cat_ID, 800, 600)
    cat_ID = int(cat_ID) if cat_ID.isdigit() else None

    brand_ID = tk.StringVar(value = "")
    brand_ID = inp_subwindow(t1, l2, brand_ID, 800, 600)
    brand_ID = int(brand_ID) if brand_ID.isdigit() else None
  
    max_p = tk.StringVar(value = "")
    max_p = inp_subwindow(t1, l3, max_p, 800, 600)
    max_p = float(max_p) if max_p.isdigit() else None
  
    results = services.search_catalog(category_id=cat_ID, brand_id=brand_ID, max_price=max_p)
        
    l4 = f"\nFound {len(results)} product(s):"
    l5 = ""
    for p in results:
        l5 += f"\n  ID: {p['product_id']} | {p['name']} ({p['brand']} - {p['category']}) - {p['price_formatted']}"

    subwindow(t1, [l4, l5], root, 800, 600)
    """
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
    """
    return
    
def findParts():
    t1 = "--- Fitment Search ---"
    l1 = "Input Vehicle Make (e.g., Honda):"
    make = tk.StringVar(value = "")
    make = inp_subwindow(t1, l1, make, 800, 600)



    l2 = "Input Vehicle Model (e.g., Civic): "
    model = tk.StringVar(value = "")
    model = inp_subwindow(t1, l2, model, 800, 600)



    l5 = "Input Vehicle Year (e.g., 2022): "
    year = tk.StringVar(value = "")
    year = inp_subwindow(t1, l5, year, 800, 600)

    l4 = ""

    if year.isdigit():
        parts = services.get_filtered_parts_by_vehicle(make, model, int(year))
        l3 = f"\nParts fitting {year} {make} {model}:"
        
        for p in parts:
            l4 += f"\n  ID: {p['product_id']} | {p['name']} - {p['price_formatted']}"
    else:
        l3 = "[-] Invalid year format."

    t2 = "2. Find Parts by Vehicle (FR-1)"

    subwindow(t2, [l3, l4], root, 800, 600)

    """
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
    """
    return

def prodView():
    t1 = "--- Product Details View ---"
    l1 = "Enter Product ID: "
    pID = tk.StringVar(value="")
    pID = inp_subwindow(t1, l1, pID, 800, 600)
  
    l2 = ""
    l3 = ""
    if pID.isdigit():
        prod = services.get_product_details(int(pID))
        if prod:
            l2 += f"\n=== {prod['name']} ==="
            l2 += f"\nBrand: {prod.get('brand', 'N/A')}"
            l2 += f"\nPrice: {prod['price_formatted']}"
            l2 += f"\nStatus: {prod['availability_status']} ({prod['stock']} units left)"
            l2 += f"\nDescription: {prod['description']}"
            l2 += f"\nInstall Instructions: {prod['install_instructions']}"
            l3 = "\nVehicle Fitment:"
            if prod["fitment"]:
                for f in prod["fitment"]:
                    l3 = f"\n  - {f['year']} {f['make']} {f['model']}"
            else:
                l3 = "  - Universal / No specific fitment listed"
        else:
            l2 = "[-] Product not found or inactive."
    else:
        l2 = "[-] Invalid ID."

    subwindow(t1, [l2, l3], root, 800, 600)
    
    """
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
    """
    return

def addCart():
    """UI-3: Prompt for product and quantity, then insert/update cart."""
    t1 = "\n--- Add Item to Cart ---"
    l1 = "Enter Product ID: "
    pid = tk.StringVar(value="")
    pid = inp_subwindow(t1, l1, pid, 800, 600)

    if not pid.isdigit():
        l2 = "[-] Invalid Product ID. Must be an integer."
        subwindow(t1, [l2], root, 800, 600)
        return 
    pid = int(pid)

    l3 = "Enter Quantity (default 1): "
    qty = tk.StringVar(value="")
    qty = inp_subwindow(t1, l3, qty, 800, 600)
    if not qty:
        qty = 1
    elif qty.isdigit() and int(qty) > 0:
        qty = int(qty)

    else:
        l4 = "[-] Quantity must be a positive integer."
        subwindow(t1, [l4], root, 800, 600)
        return

    l5 = "Enter the cart ID you want to add this to: "
    cartID = tk.StringVar(value="")
    cartID = inp_subwindow(t1, l5, cartID, 800, 600)

    if not cartID.isdigit():
        subwindow(t1, ["[-] Invalid cart ID. Must be an integer."], root, 800, 600)
        return

    cartID = int(cartID)

    try:
        services.add_to_cart(cartID, pid, qty)
        l6 = f"[+] Successfully added {qty} unit(s) of Product #{pid} to Cart #{cartID}."
        subwindow(t1, [l6], root, 800, 600)
    except Exception as e:
        l6 = f"[-] Could not add product: {e}"
        subwindow(t1, [l6], root, 800, 600)

    
    """

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
    """
    return

def disTotal():
    t1 = "Display total"
    l1 = "Which cart would you like to see the total for?: "  
    cartID = tk.StringVar(value="")
    cartID = inp_subwindow(t1, l1, cartID, 800, 600)

    if not cartID.isdigit():
        l2 = "[-] Invalid cart ID. Must be an integer."
        subwindow(t1, [l2], root, 800, 600)
        return
    try:
        subtotal, tax, total = services.display_total(cartID)
        l6 = f"\n--- Cart #{cartID} Summary ---"
        l3 = f"  Subtotal: ${subtotal:,.2f}"
        l4 = f"  HST (13%): ${tax:,.2f}"
        l5 = f"  Total:    ${total:,.2f}"
        subwindow(t1, [l6, l3, l4, l5], root, 800, 600)
            
    except Exception as e:
        l3 = f"[-] Failed to fetch cart total: {e}"
        subwindow(t1, [l3], root, 800, 600)
    """
    cart_id = input("Which cart would you like to see the total for?: ")        
    if not cart_id.isdigit():
        print("[-] Invalid cart ID. Must be an integer.")
        return
    
    services.display_total(cart_id)
    """
    return


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

def submit(entry, target_var, window):
    val = entry.get().strip()
    target_var.set(val)
    window.destroy()

def subwindow(title: str, label: list[str], prevwin, xdim: int, ydim: int):
    sub_win = tk.Toplevel(prevwin)
    sub_win.title(title)
    sub_win.geometry(f"{xdim}x{ydim}")
    for i in label:
        tk.Label(sub_win, text=i).pack(side="top", pady=25)

def inp_subwindow(title: str, label: str, target_var: tk.StringVar, xdim: int, ydim: int):
    sub_win = tk.Toplevel(root)
    sub_win.title(title)
    sub_win.geometry(f"{xdim}x{ydim}")

    sub_win.transient(root)
    sub_win.grab_set()

    

    tk.Label(sub_win, text=label).pack(side="top", pady=10)

    entry = tk.Entry(sub_win, width=30)
    entry.pack(side="top", pady=20)
    entry.focus_set()

    submitting = lambda: submit(entry, target_var, sub_win)
    tk.Button(sub_win, text="Enter", command=submitting).pack(pady=10)

    
    sub_win.wait_window()
    return target_var.get().strip()

def trackOrder():
    """Prompt for Order ID, display current delivery stage, and allow advancing stage."""
    t1 = "--- Track Order Delivery ---"
    l1 = "Enter your Order ID: "
    oid_var = tk.StringVar(value="")
    oid_str = inp_subwindow(t1, l1, oid_var, 800, 600)

    if not oid_str.isdigit():
        subwindow(t1, ["[-] Invalid Order ID. Must be an integer."], root, 800, 600)
        return

    order_id = int(oid_str)
    order = services.get_order_status(order_id)

    if not order:
        subwindow(t1, [f"[-] Order #{order_id} not found."], root, 800, 600)
        return

    # Build a custom subwindow so the corner button can dynamically update the label
    track_win = tk.Toplevel(root)
    track_win.title(f"Order #{order_id} Tracking")
    track_win.geometry("800x600")

    stages = ["Confirmed", "Processing", "Shipping", "Delivered"]
    status_var = tk.StringVar()
    progress_var = tk.StringVar()

    def refresh_display(current_status: str):
        status_var.set(f"Order #{order_id} — Current Status: {current_status.upper()}")
        # Build a visual progress bar string: [✓] Order Sent -> [●] Processing -> [ ] Shipping...
        visual_steps = []
        norm_stages = [s.lower() for s in stages]
        curr_idx = norm_stages.index(current_status.lower()) if current_status.lower() in norm_stages else -1

        for idx, stage in enumerate(stages):
            if idx < curr_idx:
                visual_steps.append(f"[✓] {stage}")
            elif idx == curr_idx:
                visual_steps.append(f"[●] {stage}")
            else:
                visual_steps.append(f"[ ] {stage}")
        progress_var.set("  ➔  ".join(visual_steps))

    refresh_display(order["status"])

    tk.Label(track_win, textvariable=status_var, font=("Arial", 14, "bold")).pack(side="top", pady=30)
    tk.Label(track_win, textvariable=progress_var, font=("Arial", 10), wraplength=750).pack(side="top", pady=20)

    def on_advance_click():
        new_status = services.advance_order_status(order_id)
        if new_status:
            refresh_display(new_status)
            if new_status == "Delivered":
                advance_btn.config(state="disabled", text="Package Delivered")

    # Bottom-right corner button to simulate package movement
    advance_btn = tk.Button(
        track_win,
        text="Simulate Next Delivery Stage ➔",
        command=on_advance_click
    )
    advance_btn.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    if order["status"].lower() == "delivered":
        advance_btn.config(state="disabled", text="Package Delivered")

def adminOptions():
    sub_win = tk.Toplevel(root)
    sub_win.title("Admin Options")
    sub_win.geometry(f"800x600")

    tk.Button(sub_win, text="List Products", command=adminListProducts).pack(side="top", pady=10)
    tk.Button(sub_win, text="Add Products", command=adminAddProduct).pack(side="top", pady=10)
    tk.Button(sub_win, text="Edit Products", command=adminEditProduct).pack(side="top", pady=10)
    tk.Button(sub_win, text="Delete Products", command=adminDeleteProduct).pack(side="top", pady=10)
    tk.Button(sub_win, text="Daily Sales Report (FR-9)", command=adminDailySales).pack(side="top", pady=10)
    tk.Button(sub_win, text="Monthly Sales Report (FR-9)", command=adminMonthlySales).pack(side="top", pady=10)
    tk.Button(sub_win, text="Go Back", command=sub_win.destroy).pack(side="top", pady=10)
    
def adminDailySales():
    t1 = "--- Admin: Daily Sales Summary (FR-9) ---"
    data = services.admin_daily_sales_report()
    lines = []
    if not data:
        lines.append("No sales records found.")
    else:
        lines.append(f"{'Date':<15} | {'Orders':<8} | {'Subtotal':<10} | {'Tax (13%)':<10} | {'Total Sales':<12}")
        lines.append("-" * 65)
        for row in data:
            lines.append(f"{row['date']:<15} | {row['orders']:<8} | {row['subtotal_formatted']:<10} | {row['tax_formatted']:<10} | {row['total_formatted']:<12}")
    subwindow(t1, lines, root, 850, 600)

def adminMonthlySales():
    t1 = "--- Admin: Monthly Sales Summary (FR-9) ---"
    data = services.admin_monthly_sales_report()
    lines = []
    if not data:
        lines.append("No sales records found.")
    else:
        lines.append(f"{'Month':<12} | {'Orders':<8} | {'Subtotal':<10} | {'Tax (13%)':<10} | {'Total Sales':<12}")
        lines.append("-" * 62)
        for row in data:
            lines.append(f"{row['month']:<12} | {row['orders']:<8} | {row['subtotal_formatted']:<10} | {row['tax_formatted']:<10} | {row['total_formatted']:<12}")
    subwindow(t1, lines, root, 850, 600)


if __name__ == "__main__":
    main()
