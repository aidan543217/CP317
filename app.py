import services
import db
from pathlib import Path
import tkinter as tk
import accessibility

settings = accessibility.load_settings()
colors = accessibility.get_theme_colors(settings)
DEFAULT_CART_ID = 1  

ADMIN_PASSWORD = "cp317carco"
admin_attempts_left = 3
admin_btn = None

root = tk.Tk()
root.geometry("800x600")
root.configure(bg=colors["bg"])

def apply_theme_to_widget(widget):
    """Recursively apply current theme to a widget tree."""
    try:
        if isinstance(widget, tk.Label):
            widget.config(bg=colors["bg"], fg=colors["fg"],
                          font=accessibility.get_font(settings))
        elif isinstance(widget, tk.Button):
            widget.config(bg=colors["button_bg"], fg=colors["button_fg"],
                          font=accessibility.get_font(settings),
                          activebackground=colors["button_bg"],
                          activeforeground=colors["button_fg"])
        elif isinstance(widget, tk.Entry):
            widget.config(bg=colors["entry_bg"], fg=colors["entry_fg"],
                          font=accessibility.get_font(settings),
                          insertbackground=colors["fg"])
        elif isinstance(widget, (tk.Scale, tk.Radiobutton, tk.Checkbutton)):
            widget.config(bg=colors["bg"], fg=colors["fg"],
                          font=accessibility.get_font(settings),
                          selectcolor=colors["button_bg"],
                          activebackground=colors["bg"],
                          activeforeground=colors["fg"],
                          highlightbackground=colors["bg"])
        elif isinstance(widget, (tk.Toplevel, tk.Frame)):
            widget.config(bg=colors["bg"])
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        apply_theme_to_widget(child)

def apply_theme():
    """Re-read settings and recolor all open windows."""
    global colors
    colors = accessibility.get_theme_colors(settings)
    root.configure(bg=colors["bg"])
    apply_theme_to_widget(root)
    root.option_add("*Font", accessibility.get_font(settings))


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

def accessibilitySettings():
    """UI: Accessibility preferences (colors, font size, contrast)."""
    win = tk.Toplevel(root)
    win.title("Accessibility Settings")
    win.geometry("600x500")
    win.configure(bg=colors["bg"])

    tk.Label(win, text="Accessibility Settings",
             bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings, 16, True)).pack(pady=15)

    # --- Font size slider ---
    tk.Label(win, text="Font Size", bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings)).pack(pady=5)
    font_var = tk.DoubleVar(value=settings["font_scale"])
    font_slider = tk.Scale(win, from_=0.8, to=1.6, resolution=0.1,
                           orient="horizontal", variable=font_var,
                           bg=colors["bg"], fg=colors["fg"],
                           highlightbackground=colors["bg"],
                           troughcolor=colors["button_bg"], length=350)
    font_slider.pack(pady=5)

    # --- Theme selection ---
    tk.Label(win, text="Color Theme", bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings)).pack(pady=10)
    theme_var = tk.StringVar(value=settings["theme"])
    for label, value in [("Light", "light"), ("Dark", "dark")]:
        tk.Radiobutton(win, text=label, variable=theme_var, value=value,
                       bg=colors["bg"], fg=colors["fg"],
                       selectcolor=colors["button_bg"],
                       activebackground=colors["bg"],
                       activeforeground=colors["fg"],
                       font=accessibility.get_font(settings)).pack()

    # --- High contrast toggle ---
    contrast_var = tk.BooleanVar(value=settings["high_contrast"])
    tk.Checkbutton(win, text="Enable High Contrast Mode",
                   variable=contrast_var,
                   bg=colors["bg"], fg=colors["fg"],
                   selectcolor=colors["button_bg"],
                   activebackground=colors["bg"],
                   activeforeground=colors["fg"],
                   font=accessibility.get_font(settings)).pack(pady=10)

    def save_and_apply():
        settings["font_scale"] = round(font_var.get(), 2)
        settings["theme"] = theme_var.get()
        settings["high_contrast"] = contrast_var.get()
        accessibility.save_settings(settings)
        apply_theme()
        win.destroy()

    tk.Button(win, text="Apply & Save", command=save_and_apply,
              bg=colors["button_bg"], fg=colors["button_fg"],
              font=accessibility.get_font(settings)).pack(pady=20)
    tk.Button(win, text="Cancel", command=win.destroy,
              bg=colors["button_bg"], fg=colors["button_fg"],
              font=accessibility.get_font(settings)).pack()

def guidedTour():
    """Step-by-step walkthrough of the shopping flow."""
    tour_steps = [
        ("Welcome to Carco!",
         "This guided tour will walk you through shopping on our site.\n"
         "Click 'Next' to continue."),
        ("Step 1: Browse Products",
         "Use 'Browse & Filter Products' to view the catalog. You can filter\n"
         "by category, brand, and maximum price."),
        ("Step 2: Find Parts for Your Vehicle",
         "Click 'Find Parts by Vehicle' and enter your car's make, model, and\n"
         "year. We'll show only parts that fit."),
        ("Step 3: View Product Details",
         "Select 'View Product Details' and enter a product ID to see\n"
         "descriptions, installation instructions, price, and fitment info."),
        ("Step 4: Add to Cart",
         "Use 'Add to cart' with a Product ID and quantity. You'll need\n"
         "a cart ID — use 1 for the default cart."),
        ("Step 5: Check Totals",
         "Click 'View current total' to see your subtotal, HST (13%), and total."),
        ("Step 6: Track Your Order",
         "Use 'Track Order Status' with your order ID to see live\n"
         "progress: Confirmed → Processing → Shipping → Delivered."),
        ("You're all set!",
         "You now know how to shop on Carco. Enjoy!\n"
         "Tip: Visit 'Accessibility' anytime to adjust fonts and colors.")
    ]

    win = tk.Toplevel(root)
    win.title("Guided Site Tour")
    win.geometry("600x400")
    win.configure(bg=colors["bg"])

    title_var = tk.StringVar()
    body_var = tk.StringVar()
    step_var = tk.StringVar()

    tk.Label(win, textvariable=step_var, bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings, 9)).pack(pady=10)
    tk.Label(win, textvariable=title_var, bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings, 16, True)).pack(pady=5)
    tk.Label(win, textvariable=body_var, bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings), wraplength=520,
             justify="left").pack(pady=15, padx=20)

    index = tk.IntVar(value=0)
    btn_frame = tk.Frame(win, bg=colors["bg"])
    btn_frame.pack(side="bottom", pady=20)

    def show_step(i):
        t, body = tour_steps[i]
        title_var.set(t)
        body_var.set(body)
        step_var.set(f"Step {i + 1} of {len(tour_steps)}")
        prev_btn.config(state="normal" if i > 0 else "disabled")
        next_btn.config(text="Finish" if i == len(tour_steps) - 1 else "Next")

    def go_prev():
        if index.get() > 0:
            index.set(index.get() - 1)
            show_step(index.get())

    def go_next():
        if index.get() < len(tour_steps) - 1:
            index.set(index.get() + 1)
            show_step(index.get())
        else:
            win.destroy()

    prev_btn = tk.Button(btn_frame, text="Back", command=go_prev,
                         bg=colors["button_bg"], fg=colors["button_fg"],
                         font=accessibility.get_font(settings))
    prev_btn.pack(side="left", padx=10)
    next_btn = tk.Button(btn_frame, text="Next", command=go_next,
                         bg=colors["button_bg"], fg=colors["button_fg"],
                         font=accessibility.get_font(settings))
    next_btn.pack(side="left", padx=10)

    show_step(0)

def main():
    global admin_btn
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
        B5 = tk.Button(root, text="5. View current total (FR-3)", command=disTotal).pack(side="top", pady=5)
        B_track = tk.Button(root, text="6. Track Order Status", command=trackOrder).pack(side="top", pady=5)
        Badmin_btn = tk.Button(root, text="7. Admin options (FR-8)", command=adminOptions)
        Badmin_btn.pack(side="top", pady=5)
        B_tour = tk.Button(root, text="8. Guided Site Tour", command=guidedTour).pack(side="top", pady=5)
        B_a11y = tk.Button(root, text="9. Accessibility Settings", command=accessibilitySettings).pack(side="top", pady=5)
        B7 = tk.Button(root, text="0. Exit", command=root.destroy).pack(side="top", pady=5)

        apply_theme()          # <-- apply saved theme before showing window
        root.mainloop()

    else:
        print("\n==============================")
        print("      CARCO E-STORE (CLI)     ")
        print("==============================")

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
    sub_win.configure(bg=colors["bg"])
    for i in label:
        tk.Label(sub_win, text=i,
                 bg=colors["bg"], fg=colors["fg"],
                 font=accessibility.get_font(settings),
                 wraplength=xdim - 40, justify="left").pack(side="top", pady=25)

def inp_subwindow(title: str, label: str, target_var: tk.StringVar, xdim: int, ydim: int, show: str = ""):
    sub_win = tk.Toplevel(root)
    sub_win.title(title)
    sub_win.geometry(f"{xdim}x{ydim}")
    sub_win.configure(bg=colors["bg"])
    sub_win.transient(root)
    sub_win.grab_set()

    tk.Label(sub_win, text=label, bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings)).pack(side="top", pady=10)

    entry = tk.Entry(sub_win, width=30, show=show,
                     bg=colors["entry_bg"], fg=colors["entry_fg"],
                     insertbackground=colors["fg"],
                     font=accessibility.get_font(settings))
    entry.pack(side="top", pady=20)
    entry.focus_set()

    submitting = lambda: submit(entry, target_var, sub_win)
    tk.Button(sub_win, text="Enter", command=submitting,
              bg=colors["button_bg"], fg=colors["button_fg"],
              font=accessibility.get_font(settings)).pack(pady=10)

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

    track_win = tk.Toplevel(root)
    track_win.title(f"Order #{order_id} Tracking")
    track_win.geometry("800x600")
    track_win.configure(bg=colors["bg"])

    stages = ["Confirmed", "Processing", "Shipping", "Delivered"]
    status_var = tk.StringVar()
    progress_var = tk.StringVar()

    def refresh_display(current_status: str):
        status_var.set(f"Order #{order_id} — Current Status: {current_status.upper()}")
        norm_stages = [s.lower() for s in stages]
        curr_idx = norm_stages.index(current_status.lower()) if current_status.lower() in norm_stages else -1
        visual_steps = []
        for idx, stage in enumerate(stages):
            if idx < curr_idx:
                visual_steps.append(f"[✓] {stage}")
            elif idx == curr_idx:
                visual_steps.append(f"[●] {stage}")
            else:
                visual_steps.append(f"[ ] {stage}")
        progress_var.set("  ➔  ".join(visual_steps))

    refresh_display(order["status"])

    tk.Label(track_win, textvariable=status_var,
             bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings, 14, True)).pack(side="top", pady=30)
    tk.Label(track_win, textvariable=progress_var,
             bg=colors["bg"], fg=colors["fg"],
             font=accessibility.get_font(settings, 10),
             wraplength=750).pack(side="top", pady=20)

    def on_advance_click():
        new_status = services.advance_order_status(order_id)
        if new_status:
            refresh_display(new_status)
            if new_status == "Delivered":
                advance_btn.config(state="disabled", text="Package Delivered")

    advance_btn = tk.Button(
        track_win,
        text="Simulate Next Delivery Stage ➔",
        command=on_advance_click,
        bg=colors["button_bg"], fg=colors["button_fg"],
        font=accessibility.get_font(settings),
    )
    advance_btn.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    if order["status"].lower() == "delivered":
        advance_btn.config(state="disabled", text="Package Delivered")

def adminOptions():
    global admin_attempts_left
    if admin_attempts_left <= 0:
        return

    prompt = f"Enter Admin Password ({admin_attempts_left} attempt(s) left):"
    while admin_attempts_left > 0:
        pw_var = tk.StringVar(value="")
        entered = inp_subwindow("Admin Login", prompt, pw_var, 450, 220, show="*")

        if entered == ADMIN_PASSWORD:
            admin_attempts_left = 3
            break

        admin_attempts_left -= 1
        if admin_attempts_left == 0:
            if admin_btn is not None:
                admin_btn.destroy()
            subwindow("Access Denied", ["[-] Too many failed attempts. Admin access disabled."], root, 450, 200)
            return

        prompt = f"[-] Incorrect password. Try again ({admin_attempts_left} attempt(s) left):"

    sub_win = tk.Toplevel(root)
    sub_win.title("Admin Options")
    sub_win.geometry("800x600")
    sub_win.configure(bg=colors["bg"])

    for text, cmd in [
        ("List Products", adminListProducts),
        ("Add Products", adminAddProduct),
        ("Edit Products", adminEditProduct),
        ("Delete Products", adminDeleteProduct),
        ("Daily Sales Report (FR-9)", adminDailySales),
        ("Monthly Sales Report (FR-9)", adminMonthlySales),
        ("Go Back", sub_win.destroy),
    ]:
        tk.Button(sub_win, text=text, command=cmd,
                  bg=colors["button_bg"], fg=colors["button_fg"],
                  font=accessibility.get_font(settings)).pack(side="top", pady=10)
    
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