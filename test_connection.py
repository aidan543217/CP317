import db

print("Database file:", db.DB_PATH)
print("File exists:", db.DB_PATH.exists())

print("\nAll products:")
for p in db.get_products():
    print(f"  {p['name']:<25} ${p['price_cents'] / 100:.2f}  ({p['category']})")

print("\nBrakes under $130:")
for p in db.get_products(category_id=1, max_cents=13000):
    print(f"  {p['name']} ${p['price_cents'] / 100:.2f}")

print("\nParts for Honda Civic 2022:")
for p in db.find_parts("Honda", "Civic", 2022):
    print("  ", p["name"])

print("\nProduct 1 details:")
print("  ", db.get_product(1))