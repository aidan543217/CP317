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