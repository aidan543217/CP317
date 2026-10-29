import services
import db
from pathlib import Path

def global_setup():
    """Initialize the test database once before running tests."""
    db_file = db.DB_PATH
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    if db_file.exists():
        try:
            db_file.unlink()
        except PermissionError:
            # If locked, we can safely reuse the existing fresh database
            pass
            
    schema_path = Path(__file__).parent / "carco-db" / "database.sql"
    schema_sql = schema_path.read_text()
    with db.get_connection() as conn:
        conn.executescript(schema_sql)

def test_filtering():
    all_products = services.search_catalog()
    assert len(all_products) == 6, f"Expected 6 products, got {len(all_products)}"
    
    brakes = services.search_catalog(category_id=1)
    assert len(brakes) == 2, f"Expected 2 brake products, got {len(brakes)}"
    
    cheap_items = services.search_catalog(max_price=100.0)
    for item in cheap_items:
        assert item['price_cents'] <= 10000
        
    print("[PASS] FR-1 Filtering Tests Passed Successfully!")

def test_product_details():
    product = services.get_product_details(1)
    assert product is not None
    assert product['name'] == 'Brake Pad Set'
    assert product['price_formatted'] == '$129.00'
    assert product['availability_status'] == 'In Stock'
    assert 'description' in product
    assert 'install_instructions' in product
    assert isinstance(product['fitment'], list)
    assert len(product['fitment']) > 0

    missing = services.get_product_details(9999)
    assert missing is None
    
    print("[PASS] FR-2 Product Details Tests Passed Successfully!")

if __name__ == "__main__":
    print("Running Automated Tests...")
    global_setup()
    test_filtering()
    test_product_details()
    print("\nAll systems operational! FR-1 and FR-2 are fully verified.")