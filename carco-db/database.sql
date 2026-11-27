PRAGMA foreign_keys = ON;

-- ===== TABLES =====
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer','admin'))
);

CREATE TABLE categories (
  category_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE brands (
  brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  install_instructions TEXT,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
  stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  image_url TEXT,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  brand_id INTEGER REFERENCES brands(brand_id),
  is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
);

CREATE TABLE vehicles (
  vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
  make TEXT NOT NULL,
  model TEXT NOT NULL,
  year INTEGER NOT NULL,
  UNIQUE (make, model, year)
);

CREATE TABLE product_fitment (
  product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
  vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
  PRIMARY KEY (product_id, vehicle_id)
);

CREATE TABLE carts (
  cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(user_id)
);

CREATE TABLE cart_items (
  cart_id INTEGER NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(product_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  PRIMARY KEY (cart_id, product_id)
);

CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_number TEXT UNIQUE,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  ship_name TEXT, ship_address TEXT, ship_city TEXT, ship_postal_code TEXT,
  subtotal_cents INTEGER NOT NULL,
  tax_cents INTEGER NOT NULL,
  shipping_cents INTEGER NOT NULL,
  total_cents INTEGER NOT NULL,
  shopify_payment_token TEXT,   -- token only, never card data
  status TEXT NOT NULL DEFAULT 'Confirmed'
    CHECK (status IN ('Confirmed','Processing','Shipping','Delivered')),
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
  order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(product_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_cents INTEGER NOT NULL,
  PRIMARY KEY (order_id, product_id)
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price_cents);
CREATE INDEX idx_fitment_vehicle ON product_fitment(vehicle_id);

-- ===== SAMPLE DATA =====
INSERT INTO categories (name) VALUES ('Brakes'),('Seats'),('Steering'),('Filters'),('Ignition');
INSERT INTO brands (name) VALUES ('Brembo'),('Recaro'),('Momo'),('K&N'),('NGK');

INSERT INTO products (name, description, install_instructions, price_cents, stock, image_url, category_id, brand_id) VALUES
 ('Big Brake Kit','6-piston front calipers with 355mm two-piece rotors.','Remove wheel, caliper, and rotor; mount bracket and caliper; install rotor, bleed system, and torque hardware.',189900,3,'img/big-brake-kit.jpg',1,1),
 ('High-Temp Brake Fluid','DOT 4 synthetic racing brake fluid (1L).','Flush old fluid from master cylinder and calipers in sequence until clear fluid flows.',2499,45,'img/brake-fluid.jpg',1,1),
 ('Harness Bar','Bolt-in tubular steel 4-point harness bar.','Remove rear trim panels, bolt bar to OEM seatbelt mounting points, torque fasteners.',28900,8,'img/harness-bar.jpg',2,2),
 ('4-Point Racing Harness','FIA-style 3-inch cam-lock racing harness.','Anchor shoulder straps to harness bar or roll cage and lap belts to seat mounts; adjust tension.',19900,11,'img/racing-harness.jpg',2,2),
 ('Quick-Release Hub','CNC billet steering wheel quick-release adapter.','Disconnect battery, remove airbag and factory wheel, install splined hub and quick-release mechanism.',13900,14,'img/quick-release-hub.jpg',3,3),
 ('Steering Rack Bushings','Polyurethane steering rack mount bushing kit.','Support steering rack, unbolt OEM rubber bushings, press in polyurethane bushings and torque bolts.',5900,21,'img/rack-bushings.jpg',3,3),
 ('Turbo Inlet Pipe','Silicone high-flow turbocharger inlet hose.','Remove stock intake tube and clamps, fit silicone inlet pipe, tighten T-bolt clamps.',9499,15,'img/turbo-inlet.jpg',4,4),
 ('Blow-Off Valve','Recirculating or atmospheric billet blow-off valve.','Tap charge pipe or bolt onto flange, connect vacuum line, adjust spring tension if needed.',21900,9,'img/blow-off-valve.jpg',4,4),
 ('Ignition Coil Pack Set','High-output performance coil-on-plug set of 4.','Unplug electrical connectors, remove hold-down bolts and old coils, seat new coils and torque.',17900,12,'img/coil-packs.jpg',5,5),
 ('Aluminum Coolant Tank','Welded aluminum expansion reservoir tank.','Drain coolant slightly, unbolt plastic reservoir, mount aluminum tank and reconnect hoses.',14900,10,'img/coolant-tank.jpg',5,5),
 ('Camber Plates','Adjustable pillow-ball front camber caster plates.','Remove front strut assembly, compress spring, swap top mount for camber plate, reinstall and align.',22900,7,'img/camber-plates.jpg',6,6),
 ('Rear Trailing Arms','Adjustable spherical rear toe and trailing arms.','Lift rear suspension, unbolt factory arms, install adjustable arms and set initial length.',31900,6,'img/trailing-arms.jpg',6,6),
 ('Exhaust Header','4-to-1 tubular stainless steel performance header.','Disconnect O2 sensors and exhaust flange, unbolt stock manifold/header, install new header with gasket.',45900,5,'img/exhaust-header.jpg',7,7),
 ('Titanium Exhaust Tips','Burnt-finish dual-wall titanium exhaust tips (pair).','Measure outlet diameter, slip tips over tailpipes or weld in place, align evenly.',11900,17,'img/exhaust-tips.jpg',7,7),
 ('Short-Throw Shift Linkage','Solid spherical shifter cable and linkage bushings.','Lift vehicle, remove underbody heat shield, swap factory rubber linkage ends for solid bushings.',7900,19,'img/shift-linkage.jpg',8,8),
 ('Clutch Line Kit','Braided stainless steel hydraulic clutch line.','Bleed hydraulic system, route braided line from master cylinder to slave cylinder, refill and bleed.',5499,23,'img/clutch-line.jpg',8,8),
 ('Side Skirt Splitters','ABS gloss-black side rocker panel extensions.','Clean rocker panels, align splitters along lower edge, fasten with self-tapping screws.',16900,12,'img/side-skirts.jpg',9,9),
 ('GT Wing Spoiler','Adjustable carbon-fiber trunk mount rear wing.','Mark trunk mounting template, drill through trunk lid with reinforcement plates, bolt wing uprights.',59900,4,'img/gt-wing.jpg',9,9);

INSERT INTO vehicles (make, model, year) VALUES
 ('Honda','Civic Type R',2023),('Honda','Civic Type R',2024),
 ('Toyota','GR Corolla',2023),('Toyota','GR Corolla',2024),
 ('Toyota','GR Supra',2021),('Toyota','GR Supra',2022),('Toyota','GR Supra',2023),('Toyota','GR Supra',2024),
 ('Ford','Mustang Mach 1',2021),('Ford','Mustang Mach 1',2022),('Ford','Mustang Mach 1',2023),
 ('Hyundai','Veloster N',2020),('Hyundai','Veloster N',2021),('Hyundai','Veloster N',2022),
 ('Audi','RS3',2022),('Audi','RS3',2023),('Audi','RS3',2024),
 ('Porsche','718 Cayman',2020),('Porsche','718 Cayman',2021),('Porsche','718 Cayman',2022),('Porsche','718 Cayman',2023),('Porsche','718 Cayman',2024);

INSERT INTO product_fitment (product_id, vehicle_id)
SELECT 1, vehicle_id FROM vehicles WHERE make='Honda' AND model='Civic' AND year BETWEEN 2020 AND 2024;
INSERT INTO product_fitment VALUES (4,3),(4,6),(5,3),(5,8),(6,3);

-- Replace the placeholder hashes with real ones generated by the backend (e.g. bcrypt). Never store plain text.
INSERT INTO users (email, password_hash, role) VALUES
 ('admin@carco.test','REPLACE_WITH_REAL_HASH','admin'),
 ('customer@carco.test','REPLACE_WITH_REAL_HASH','customer');
