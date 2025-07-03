create database ecommerce;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL
);

ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NOT NULL;
ALTER TABLE users ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN email varchar(255) NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN phone varchar(255) NOT NULL DEFAULT 0;
describe users;

update users
set phone = '9685473695'
where id = 1;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    price DECIMAL(10,2),
    image_url VARCHAR(255)
);

INSERT INTO products (name, description, price, image_url) VALUES
('Laptop', 'A fast laptop.', 50000.00, 'laptop.jpg'),
('Phone', 'A smart phone.', 20000.00, 'phone.jpg'),
('Headphones', 'Wireless headphones.', 3000.00, 'headphones.jpg');

describe products;

ALTER TABLE products
  ADD COLUMN category VARCHAR(100) DEFAULT '',
  ADD COLUMN brand VARCHAR(100) DEFAULT '',
  ADD COLUMN stock INT DEFAULT 0,
  MODIFY COLUMN image_url VARCHAR(255) NOT NULL;

INSERT INTO products (name, description, category, brand, price, stock, image_url) VALUES
('Gaming Laptop', 'High-end gaming laptop with RTX 3060.', 'Electronics', 'BrandX', 120000.00, 5, 'gaming_laptop.jpg'),
('Running Shoes', 'Comfortable shoes for running.', 'Footwear', 'BrandY', 3500.00, 20, 'running_shoes.jpg'),
('Smart Watch', 'Feature-packed smartwatch.', 'Accessories', 'BrandZ', 9999.00, 10, 'smart_watch.jpg');

INSERT INTO products (name, description, category, brand, price, stock, image_url) VALUES
('Bluetooth Speaker', 'Portable Bluetooth speaker with powerful bass.', 'Electronics', 'SoundCore', 2499.00, 15, 'bluetooth_speaker.jpg'),
('Air Conditioner', '1.5 Ton Split AC with energy saving mode.', 'Home Appliances', 'CoolAir', 35000.00, 8, 'air_conditioner.jpg'),
('Wireless Mouse', 'Ergonomic wireless mouse with long battery life.', 'Accessories', 'LogiTech', 899.00, 30, 'wireless_mouse.jpg'),
('Mechanical Keyboard', 'RGB mechanical keyboard for gamers.', 'Accessories', 'HyperX', 4999.00, 12, 'mechanical_keyboard.jpg'),
('Video Game - FIFA 25', 'Football video game for consoles.', 'Gaming', 'EA Sports', 3999.00, 25, 'fifa25.jpg'),
('CCTV Camera', 'HD CCTV camera with night vision.', 'Security', 'SecureCam', 1999.00, 20, 'cctv_camera.jpg'),
('Fitness Band', 'Track your steps, heart rate, and sleep.', 'Accessories', 'FitTrack', 1699.00, 25, 'fitness_band.jpg'),
('Wi-Fi Router', 'Dual-band Wi-Fi router with 1 Gbps speed.', 'Electronics', 'NetGen', 2299.00, 16, 'wifi_router.jpg'),
('Refrigerator 260L', 'Frost-free double door refrigerator.', 'Home Appliances', 'FridgeCo', 28999.00, 5, 'refrigerator_260l.jpg'),
('Security Alarm System', 'Smart home security alarm system with app alerts.', 'Security', 'SafeHome', 6999.00, 10, 'alarm_system.jpg');

INSERT INTO products (name, description, category, brand, price, stock, image_url) VALUES
('Electric Kettle', '1.7L electric kettle with auto shut-off.', 'Home Appliances', 'KitchenPro', 1599.00, 35, 'electric_kettle.jpg'),
('Air Fryer', 'Oil-less cooking air fryer with digital controls.', 'Home Appliances', 'HomeChef', 7499.00, 10, 'air_fryer.jpg');

update products
set stock = 1
where id = 4; 

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    razorpay_order_id VARCHAR(100) NOT NULL,
    total_amount INT NOT NULL,
    status ENUM('created', 'paid', 'failed') DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

describe orders;

ALTER TABLE orders
MODIFY COLUMN razorpay_order_id varchar(255);

ALTER TABLE order_items
MODIFY COLUMN order_id varchar(255);

CREATE TABLE payments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  order_id INT,
  amount DECIMAL(10, 2),
  status VARCHAR(20), -- 'success', 'failed', 'pending'
  razorpay_payment_id VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

describe payments;

SHOW COLUMNS FROM payments;
ALTER TABLE payments ADD COLUMN payment_id varchar(255);
ALTER TABLE payments DROP COLUMN signature;
ALTER TABLE payments DROP COLUMN razorpay_payment_id;
ALTER TABLE payments
MODIFY COLUMN user_id varchar(255);
ALTER TABLE payments
MODIFY COLUMN order_id varchar(255);
ALTER TABLE payments
ADD CONSTRAINT fk_payments_order_id
FOREIGN KEY (order_id) REFERENCES orders(id);
ALTER TABLE payments ADD UNIQUE (order_id);

CREATE TABLE order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id varchar(255),
  product_id INT,
  quantity INT,
  price DECIMAL(10,2)
);

describe order_items;

ALTER TABLE payments ADD INDEX (order_id);

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_order_id
FOREIGN KEY (order_id) REFERENCES payments(order_id)
ON DELETE CASCADE;

ALTER TABLE order_items DROP FOREIGN KEY fk_order_items_order_id;

ALTER TABLE order_items
MODIFY COLUMN order_id int;

ALTER TABLE order_items ADD COLUMN product_name VARCHAR(255);

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_order_id
FOREIGN KEY (order_id) REFERENCES orders(id)
ON DELETE CASCADE;

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_product_name
FOREIGN KEY (product_id) REFERENCES products(id);

ALTER TABLE order_items ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE KEY unique_wishlist (user_id, product_id)
);

describe wishlist;

use ecommerce;
select * from users;
select * from products;
select * from orders;
select * from order_items;
select * from payments;