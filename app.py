from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from functools import wraps
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_products, get_product
from datetime import datetime
import config
import razorpay

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

client = razorpay.Client(auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET))

# ---- Helper Decorators ----
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('is_admin', 0) != 1:
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---- Routes ----
@app.route('/')
def index():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    message = session.pop('flash_message', None)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if search:
        sql += " AND name LIKE %s"
        params.append(f"%{search}%")
    if category:
        sql += " AND category = %s"
        params.append(category)
    cursor.execute(sql, params)
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', products=products, search=search, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, phone, password, is_admin) VALUES (%s, %s, %s, %s, %s)", (username, email, phone, hashed_password, 0))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Username might already exist. Try another.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', 0)
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(next_page or url_for('index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product(product_id):
    product = get_product(product_id)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    qty = int(request.args.get('qty', 1))
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session['cart'] = cart
    flash("Added to cart.", "success")
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    products = [get_product(int(pid)) for pid in cart]
    total = sum(p['price'] * cart[str(p['id'])] for p in products)
    return render_template('cart.html', products=products, cart=cart, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = str(request.form['product_id'])
    action = request.form['action']
    cart = session.get('cart', {})

    if product_id in cart:
        if action == 'increment':
            cart[product_id] += 1
        elif action == 'decrement':
            cart[product_id] -= 1
            if cart[product_id] <= 0:
                del cart[product_id]

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')
    if product_id and 'cart' in session:
        session['cart'].pop(product_id, None)
        session.modified = True
        flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash("All items removed from cart.", "info")
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, phone FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    cart_items = []
    total = 0
    for pid_str, qty in cart.items():
        product = get_product(int(pid_str))
        if not product:
            continue
        item_total = product['price'] * qty
        total += item_total
        cart_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'quantity': qty,
            'price': product['price'],
            'total': item_total
        })

    amount = int(total * 100)
    order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": "1"})

    return render_template(
        'checkout.html',
        user=user,
        order=order,
        razorpay_key=config.RAZORPAY_KEY_ID,
        razorpay_order_id=order['id'],
        total=total,
        cart_items=cart_items
    )

@app.route('/payment_success', methods=['POST'])
@login_required
def payment_success():
    data = request.get_json()
    user_id = session['user_id']
    cart = session.get('cart', {})
    total_amount = 0

    # Extract Razorpay details
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')

    # Calculate amount
    for pid, qty in cart.items():
        product = get_product(int(pid))
        if product:
            total_amount += product['price'] * qty
    amount_in_paise = int(total_amount)

    order_status = 'failed'
    try:
        # Attempt Razorpay signature verification
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        order_status = 'paid'
    except razorpay.errors.SignatureVerificationError:
        print("❌ Signature verification failed")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert order record (always)
        cursor.execute("""
            INSERT INTO orders (user_id, razorpay_order_id, total_amount, status)
            VALUES (%s, %s, %s, %s)
        """, (user_id, razorpay_order_id, amount_in_paise, order_status))
        order_id = cursor.lastrowid

        # Insert payment record (always, even if failed)
        cursor.execute("""
            INSERT INTO payments (user_id, order_id, payment_id, amount, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, order_id, razorpay_payment_id or 'N/A', amount_in_paise, order_status))

        # Insert order_items (always, even if failed)
        for pid, qty in cart.items():
            product = get_product(int(pid))
            if product:
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, product['id'], product['name'], qty, product['price']))

                # Only reduce stock if paid
                if order_status == 'paid':
                    cursor.execute("""
                        UPDATE products
                        SET stock = stock - %s
                        WHERE id = %s AND stock >= %s
                    """, (qty, product['id'], qty))
            else:
            # Even on failure, store order_items
                for pid, qty in cart.items():
                    product = get_product(int(pid))
                    if product:
                        cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                        """, (order_id, product['id'], product['name'], qty, product['price']))
        conn.commit()

    except Exception as e:
        print("❌ Database error:", e)
        flash("Something went wrong while saving your order.", "danger")
    finally:
        cursor.close()
        conn.close()

    if order_status == 'paid':
        session.pop('cart', None)
        flash("✅ Order placed successfully!", "success")
    else:
        flash("❌ Order failed or was not completed.", "danger")

    return jsonify({'status': order_status, 'redirect': url_for('index')})

@app.route('/payment_failed_record', methods=['POST'])
@login_required
def payment_failed_record():
    import traceback
    data = request.get_json()
    razorpay_order_id = data.get('razorpay_order_id')
    user_id = session['user_id']
    cart = session.get('cart', {})

    if not razorpay_order_id:
        return jsonify({'error': 'Missing order ID'}), 400

    total_amount = 0
    for pid, qty in cart.items():
        product = get_product(int(pid))
        if product:
            total_amount += product['price'] * qty
    amount_in_paise = int(total_amount)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Check or insert order
        cursor.execute("SELECT id FROM orders WHERE razorpay_order_id = %s", (razorpay_order_id,))
        order = cursor.fetchone()

        if order:
            order_id = order['id']
        else:
            cursor.execute("""
                INSERT INTO orders (user_id, razorpay_order_id, total_amount, status)
                VALUES (%s, %s, %s, %s)
            """, (user_id, razorpay_order_id, amount_in_paise, 'failed'))
            order_id = cursor.lastrowid

        # 2. Check or insert payment
        cursor.execute("SELECT id FROM payments WHERE order_id = %s", (order_id,))
        payment = cursor.fetchone()
        if not payment:
            cursor.execute("""
                INSERT INTO payments (user_id, order_id, payment_id, amount, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, order_id, None, amount_in_paise, 'failed'))

        # 3. Insert order items if missing
        cursor.execute("SELECT COUNT(*) AS count FROM order_items WHERE order_id = %s", (order_id,))
        count = cursor.fetchone()['count']
        if count == 0:
            for pid, qty in cart.items():
                product = get_product(int(pid))
                if product:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, product['id'], product['name'], qty, product['price']))

        conn.commit()
        return jsonify({'message': 'Recorded failed payment successfully'})

    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/payment_failed')
@login_required
def payment_failed():
    flash("❌Payment failed or cancelled.", "danger")
    return redirect(url_for('index'))

@app.route('/orders')
@login_required
def order_history():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT o.id, 
    GROUP_CONCAT(oi.product_name SEPARATOR ', ') AS product_name, 
    o.total_amount, 
    o.status, 
    o.created_at
    FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    WHERE o.user_id = %s
    GROUP BY o.id ,o.total_amount, o.status, o.created_at
    ORDER BY o.created_at DESC
    """, (session['user_id'],))
    
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('orders.html', orders=orders)

@app.route('/admin/payments')
@admin_required
def admin_payments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p.*, u.username FROM payments p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC")
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_payments.html', payments=payments)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')  # safely get the user_id from session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch username, email, and phone
    cursor.execute("SELECT id, username, email, phone FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/admin/products')
@admin_required
def admin_products():
    products = get_products()
    return render_template('admin_products.html', products=products)

@app.route('/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT IGNORE INTO wishlist (user_id, product_id)
            VALUES (%s, %s)
        """, (user_id, product_id))
        conn.commit()
        flash("❤️ Added to wishlist!", "success")
    except Exception as e:
        flash("Error adding to wishlist.", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Removed from wishlist.", "info")
    return redirect(request.referrer or url_for('wishlist'))

@app.route('/wishlist')
@login_required
def wishlist():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.name, p.price, p.image_url
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        WHERE w.user_id = %s
    """, (user_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('wishlist.html', wishlist_items=items)

@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True)