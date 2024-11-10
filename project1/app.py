from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db_manager import DBManager
import os
import psutil
import time

app = Flask(__name__)

app.secret_key = os.urandom(24)  # This generates a random secret key

# Initialize your DBManager instance
db_manager = DBManager(host='localhost', user='root', password='1234', database='project')

staff_modification_lock = {"staff_id": None, "timestamp" : None}

@app.route('/')
def index():
    query = """
    SELECT 
        t.name, t.category, t.ingredients,
        GROUP_CONCAT(CONCAT(o.size, ':', o.price) ORDER BY FIELD(o.size, 'S', 'M', 'L'))
        as size_prices, t.image_path
    FROM pizza_type t 
    JOIN pizza_order o ON t.pizza_type_id = o.pizza_type_id
    GROUP BY t.pizza_type_id
    ORDER BY t.name;
    """

    try:
        db_manager.connect()
        raw_pizzas = db_manager.execute_query(query)


        # Process the raw data into a more usable format
        pizzas = []
        for pizza in raw_pizzas:
            name, category, ingredients, size_prices, image_path = pizza

            # Parse the size_prices string into a dictionary
            sizes = {}
            for size_price in size_prices.split(','):
                size, price = size_price.split(':')
                sizes[size] = float(price)

            pizzas.append({
                'name': name,
                'category': category,
                'ingredients': ingredients,
                'sizes': sizes,
                'image_path': image_path
            })

        return render_template('index.html', pizzas=pizzas)
    except Exception as e:
        print(f"Error fetching pizza data: {e}")
        return render_template('index.html', pizzas=[], error="Unable to load pizza menu")
    finally:
        db_manager.disconnect()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    print(f"Attempting login with username: {username} and password: {password}")

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400


    db_manager.connect()
    user = db_manager.db_login(username, password)
    db_manager.disconnect()
    
    if user and isinstance(user, (list, tuple)):
        print(f"User found: {user}")
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        if user[3] == 0:
            return jsonify({'success': True, 'role': user[3], 'redirect_url': '/staff'})
        elif user[3] == 1:
             return jsonify({'success': True, 'role': user[3], 'redirect_url': '/'})
    else:
        print("Login Failed")
        return jsonify({'success': False, 'message':'Invalid credentials'})

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    
    db_manager.disconnect()

    # Return a success message or redirect to another page
    return jsonify({'success': True, 'redirect_url': '/'})


@app.route('/staff')
def staff_info():
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        db_manager.connect()
        # Get pending orders
        orders_query = """
        SELECT oi.order_id, pt.name, oi.quantity, oi.status
        FROM order_info oi
        JOIN pizza_order po ON oi.pizza_id = po.pizza_id
        JOIN pizza_type pt ON po.pizza_type_id = pt.pizza_type_id
        WHERE oi.status = 0
        ORDER BY oi.order_id;
        """
        # Get pizza types for editing
        pizzas_query = """
        SELECT pt.pizza_type_id, pt.name, pt.category, pt.ingredients
        FROM pizza_type pt
        ORDER BY pt.name;
        """
        pizza_orders = db_manager.execute_query(orders_query)
        pizza_types = db_manager.execute_query(pizzas_query)
        return render_template('staff.html',
                             pizza_orders=pizza_orders,
                             pizza_types=pizza_types)
    except Exception as e:
        return jsonify({'error': f"Failed to fetch data: {str(e)}"}), 500
    finally:
        db_manager.disconnect()
"""
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    try:
        db_manager.connect()
    except Exception as e:
        print(f"Error in establishing connection: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    
    if db_manager.delete_orderrow(order_id):
        db_manager.disconnect()
        return redirect(url_for('staff_info'))
    else:
        return "Order not found", 404
"""


@app.route('/update_pizza/<int:pizza_id>', methods=['POST'])
def update_pizza(pizza_id):
    try:
        db_manager.connect()
        new_name = request.form.get('name')
        new_category = request.form.get('category')
        new_ingredients = request.form.get('ingredients')

        if db_manager.update_pizza(pizza_id, new_name, new_category, new_ingredients):
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Failed to update pizza'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db_manager.disconnect()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    try:
        db_manager.connect()
        if db_manager.add_user(username, password):
            return jsonify({'success': True, 'message': 'User created successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create user'}), 500
    finally:
        db_manager.disconnect()


@app.route('/complete_order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    try:
        db_manager.connect()
        if db_manager.update_order_status(order_id, 1):  # 1 for completed
            return redirect(url_for('staff_info'))
        return jsonify({'success': False, 'message': 'Order not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db_manager.disconnect()

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    try:
        db_manager.connect()
        if db_manager.delete_orderrow(order_id):
            return redirect(url_for('staff_info'))
        return jsonify({'success': False, 'message': 'Order not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db_manager.disconnect()

@app.route('/start_transaction', methods=['POST'])
def start_transaction():
    try:
        db_manager.connect()
        db_manager.start_transaction()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Modify your existing submit_order route to handle transactions
@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = request.json
    if not order_items:
        return jsonify({'success': False, 'message': 'No items in the order'})

    try:
        db_manager.connect()
        for item in order_items:
            pizza_name = item['pizza_name']
            size = item['size']
            quantity = item['quantity']

            if quantity <= 0:
                continue

            db_manager.add_order_info(pizza_name, size, quantity)

        db_manager.commit_transaction()
        return jsonify({'success': True, 'message': 'Order submitted successfully'})
    except Exception as e:
        db_manager.rollback_transaction()
        print(f"Error processing order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.disconnect()


@app.route('/history', methods=['GET', 'POST'])
def order_history():
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        db_manager.connect()
        search_order_id = request.form.get('order_id')

        if search_order_id:
            # Measure performance for indexed search
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            completed_orders = db_manager.search_completed_orders(search_order_id)
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            indexed_performance = {
                'execution_time': end_time - start_time,
                'memory_used': end_memory - start_memory
            }

            # Measure performance for non-indexed search
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            completed_orders_non_indexed = db_manager.search_completed_orders_non_indexed(search_order_id)
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            non_indexed_performance = {
                'execution_time': end_time - start_time,
                'memory_used': end_memory - start_memory
            }

            performance = {
                'order_id_search': {
                    'indexed': indexed_performance,
                    'non_indexed': non_indexed_performance
                }
            }
        else:
            completed_orders = db_manager.get_completed_orders()
            performance = None

        return render_template('history.html',
                               orders=completed_orders,
                               performance=performance)
    except Exception as e:
        return jsonify({'error': f"Failed to fetch history: {str(e)}"}), 500
    finally:
        db_manager.disconnect()


@app.route('/check_staff_lock', methods=['POST'])
def check_staff_lock():
    global staff_modification_lock
    data = request.json
    current_staff_id = data.get('staff_id')

    # Clear expired locks (15 minutes timeout)
    if staff_modification_lock['staff_id'] and time.time() - staff_modification_lock['timestamp'] >= 900:
        staff_modification_lock['staff_id'] = None
        staff_modification_lock['timestamp'] = None

    # Check if lock exists and is valid
    if staff_modification_lock['staff_id'] and staff_modification_lock['staff_id'] != current_staff_id:
        return jsonify({
            'locked': True,
            'message': f"Another staff member is currently modifying pizzas."
        })

    # Update or set new lock
    staff_modification_lock['staff_id'] = current_staff_id
    staff_modification_lock['timestamp'] = time.time()

    return jsonify({'locked': False})


@app.route('/release_staff_lock', methods=['POST'])
def release_staff_lock():
    global staff_modification_lock
    data = request.json
    current_staff_id = data.get('staff_id')

    if staff_modification_lock['staff_id'] == current_staff_id:
        staff_modification_lock['staff_id'] = None
        staff_modification_lock['timestamp'] = None

    return jsonify({'success': True})

@app.route('/batch_update_orders', methods=['POST'])
def batch_update_orders():
    try:
        db_manager.connect()
        data = request.json
        for order_id, updates in data.items():
            db_manager.update_order(order_id, updates['quantity'], updates['status'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db_manager.disconnect()


def get_memory_usage():
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # Convert to MB


def calculate_earnings():
    query = """
    SELECT 
        pt.name,
        po.size,
        po.price,
        SUM(oi.quantity) as total_quantity,
        SUM(po.price * oi.quantity) as total_earnings
    FROM order_info oi
    JOIN pizza_order po ON oi.pizza_id = po.pizza_id
    JOIN pizza_type pt ON po.pizza_type_id = pt.pizza_type_id
    GROUP BY pt.name, po.size, po.price
    ORDER BY total_earnings DESC
    """
    return db_manager.execute_query(query)
    
if __name__ == '__main__':
    app.run(debug=True)
