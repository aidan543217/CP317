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

def test_admin_list_products():
    """FR-8: admin should see every product, including inactive ones."""
    products = services.admin_list_products()
    assert len(products) == 6, f"Expected 6 products for admin, got {len(products)}"
    for p in products:
        assert "price_formatted" in p
        assert "status" in p
        assert p['status'] in ['Active', 'Inactive']
        assert p["price_formatted"].startswith("$")

    print("[PASS] FR-8 Admin Product Listing Tests Passed Successfully!")

def test_admin_add_product():
    """FR-8: adding a product makes it visible in customer + admin views."""
    before = len(services.search_catalog())
    new_id = services.admin_add_product(
        name = "Test Coil Pack",
        price = 55.00,
        category_id = 1,
        brand_id = 1,
        stock = 4
        description = "Test description",
        install_instructions = "Test install instructions"
    )
    assert isinstance(new_id,int) and new_id > 0

    # Visible to the customer catalog (FR-1)
    after = services.search_catalog()
    assert len(after) == before + 1
    created = next((p for p in after if p["product_id"] == new_id), None)
    assert created is not None
    assert created["name"] == "Test Coil Pack"
    assert created["price_cents"] == 5500

    # Visible to the product details view (FR-2)
    detail = services.get_product_details(new_id)
    assert detail is not None
    assert detail["price_formatted"] == "$55.00"

    # Visible to the admin list (FR-8)
    admin_view = services.admin_list_products()
    assert any(p["product_id"] == new_id and p["status"] == "Active"
               for p in admin_view)

    print("[PASS] FR-8 Admin Add Tests Passed Successfully!")

def test_admin_edit_product():
    """FR-8: editing a product updates the DB and all views."""
    new_id = services.admin_add_product(
        name="Edit Me", price=10.00, category_id=1, brand_id=1, stock=1)

    ok = services.admin_edit_product(
        new_id,
        name="Edited Name",
        price=42.50,
        stock=7,
        description="Edited description",
    )
    assert ok is True

    detail = services.get_product_details(new_id)
    assert detail is not None
    assert detail["name"] == "Edited Name"
    assert detail["price_formatted"] == "$42.50"
    assert detail["stock"] == 7
    assert detail["description"] == "Edited description"

    # Nonexistent product → no-op
    assert services.admin_edit_product(99999, name="Ghost") is False

    print("[PASS] FR-8 Admin Edit Tests Passed Successfully!")

def test_admin_delete_product():
    """FR-8: deleting hides the product from customers but keeps it admin-visible."""
    new_id = services.admin_add_product(
        name="Delete Me", price=5.00, category_id=1, brand_id=1, stock=1)

    assert services.get_product_details(new_id) is not None

    ok = services.admin_delete_product(new_id)
    assert ok is True

    # Hidden from customer-facing views
    assert services.get_product_details(new_id) is None
    assert all(p["product_id"] != new_id for p in services.search_catalog())

    # Still visible to the admin, but flagged Inactive
    admin_view = services.admin_list_products()
    entry = next((p for p in admin_view if p["product_id"] == new_id), None)
    assert entry is not None
    assert entry["status"] == "Inactive"

    # Deleting again reports no row changed
    assert services.admin_delete_product(99999) is False

    print("[PASS] FR-8 Admin Delete Tests Passed Successfully!")

def test_admin_validation():
    """FR-8: invalid inputs are rejected with ValueError."""
    def expect_value_error(fn, label):
        try:
            fn()
        except ValueError:
            return
        raise AssertionError(f"Expected ValueError for {label}")

    expect_value_error(
        lambda: services.admin_add_product(
            name="", price=10, category_id=1, brand_id=1),
        "empty name")
    expect_value_error(
        lambda: services.admin_add_product(
            name="X", price=-1, category_id=1, brand_id=1),
        "negative price")
    expect_value_error(
        lambda: services.admin_add_product(
            name="X", price=10, category_id=1, brand_id=1, stock=-5),
        "negative stock")

    new_id = services.admin_add_product(
        name="Valid", price=10, category_id=1, brand_id=1)
    expect_value_error(
        lambda: services.admin_edit_product(new_id, price=-3),
        "negative price on edit")
    expect_value_error(
        lambda: services.admin_edit_product(new_id, stock=-2),
        "negative stock on edit")
    expect_value_error(
        lambda: services.admin_edit_product(new_id, bogus_field="x"),
        "unknown column")

    print("[PASS] FR-8 Admin Validation Tests Passed Successfully!")


if __name__ == "__main__":
    print("Running Automated Tests...")
    global_setup()
    test_filtering()
    test_product_details()
    test_admin_add_product()
    test_admin_edit_product()
    test_admin_delete_product()
    test_admin_validation()
    print("\nAll systems operational! FR-1 and FR-2 are fully verified.")