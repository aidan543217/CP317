import db

def search_catalog(category_id=None, brand_id=None, min_price=None, max_price=None):
    """
    FR-1: Browse and filter available products.
    Accepts human-friendly price inputs (in dollars) and converts them to cents.
    """
    min_cents = int(min_price * 100) if min_price is not None else None
    max_cents = int(max_price * 100) if max_price is not None else None
    
    products = db.get_products(
        category_id=category_id, 
        brand_id=brand_id, 
        min_cents=min_cents, 
        max_cents=max_cents
    )
    
    # Format prices for clean presentation
    for p in products:
        p["price_formatted"] = f"${p['price_cents'] / 100:.2f}"
        
    return products

def get_filtered_parts_by_vehicle(make, model, year):
    """
    FR-1 Variant: Filter parts specifically fitting a user's vehicle.
    """
    parts = db.find_parts(make, model, year)
    for p in parts:
        p["price_formatted"] = f"${p['price_cents'] / 100:.2f}"
    return parts

def get_product_details(product_id):
    """
    FR-2: Show product details including price, description, installation instructions,
    availability status, stock count, and fitment list.
    """
    product = db.get_product(product_id)
    if not product:
        return None
        
    product["price_formatted"] = f"${product['price_cents'] / 100:.2f}"
    product["availability_status"] = "In Stock" if product["in_stock"] else "Out of Stock"
    
    return product

def add_to_cart(cart_id, product_id, quantity):
    db.add_to_cart(cart_id, product_id, quantity)

    return

def display_total(cart_id):
    """UI-3: Query cart summary and display formatted currency values."""
    

    totals = db.get_cart_total(cart_id)

    subtotal = totals["subtotal_cents"] / 100
    tax = totals["tax_cents"] / 100
    total = totals["total_cents"] / 100

    
    return subtotal, tax, total


def admin_list_products():
    """ADM-1: return all products with formatted price + status."""
    products = db.get_all_products_admin()
    for p in products:
        p["price_formatted"] = f"${p['price_cents'] / 100:.2f}"
        p["status"] = "Active" if p["is_active"] else "Inactive"
    return products

def admin_add_product(name, price, category_id, brand_id,
                      stock=0, description="", install_instructions="",
                      image_url=""):
    """ADM-1: validate and create a product. price is in dollars."""
    if not name.strip():
        raise ValueError("Product name cannot be empty.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    if stock < 0:
        raise ValueError("Stock cannot be negative.")
    return db.create_product(
        name=name.strip(),
        price_cents=int(price * 100),
        category_id=category_id,
        brand_id=brand_id,
        stock=stock,
        description=description,
        install_instructions=install_instructions,
        image_url=image_url or None,
    )

def admin_edit_product(product_id, **fields):
    """ADM-1: validate & update a product. price may be passed in dollars."""
    if "price" in fields:
        p = fields.pop("price")
        if p is None or p < 0:
            raise ValueError("Price cannot be negative.")
        fields["price_cents"] = int(round(p * 100))
    if "stock" in fields and fields["stock"] < 0:
        raise ValueError("Stock cannot be negative.")
    return db.update_product(product_id, **fields)

def admin_delete_product(product_id):
    """ADM-1: delete a product."""
    return db.delete_product(product_id)
