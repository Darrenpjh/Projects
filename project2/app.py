from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db_manager import DBManager
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize MongoDB manager
db_manager = DBManager(host='localhost', port=27017, database='project')


@app.route('/')
def index():
    try:
        db_manager.connect()
        pizzas = db_manager.get_all_pizzas()
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

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    db_manager.connect()
    user = db_manager.db_login(username, password)
    db_manager.disconnect()

    if user:
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            'success': True,
            'role': user['role'],
            'username': user['username'],
            'redirect_url': '/staff' if user['role'] == 0 else '/'
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'})


@app.route('/staff')
def staff_info():
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    db_manager.connect()
    try:
        pizza_types = db_manager.db.pizza_types.find()
        pending_orders = db_manager.get_pending_orders()
        earnings_data = db_manager.calculate_earnings()

        pizza_types_list = [[pt['pizza_type_id'], pt['name'], pt['category'], pt['ingredients']]
                           for pt in pizza_types]

        formatted_earnings = []
        total_earnings = 0
        for earning in earnings_data:
            row = [
                earning['_id']['pizza_type'],
                earning['_id']['size'],
                float(earning['total_earnings'] / earning['total_quantity']),
                earning['total_quantity'],
                earning['total_earnings']
            ]
            formatted_earnings.append(row)
            total_earnings += earning['total_earnings']

        return render_template('staff.html',
                           pizza_types=pizza_types_list,
                           pizza_orders=pending_orders,
                           earnings_data=formatted_earnings,
                           total_earnings=total_earnings)
    except Exception as e:
        return jsonify({'error': f"Failed to fetch data: {str(e)}"}), 500
    finally:
        db_manager.disconnect()


@app.route('/complete_order/<order_id>', methods=['POST'])
def complete_order(order_id):
    try:
        db_manager.connect()
        success = db_manager.complete_order(order_id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to complete order'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db_manager.disconnect()


@app.route('/history', methods=['GET', 'POST'])
def order_history():
    db_manager.connect()
    orders = []
    performance_results = None

    try:
        if request.method == 'POST':
            order_id = request.form.get('order_id')
            if order_id:
                try:
                    order_id = int(order_id)
                    # Get performance comparison
                    performance_results = db_manager.compare_search_performance(order_id=order_id)

                    # Use the results from the indexed search
                    orders = performance_results['order_id_search']['indexed']['result']
                except ValueError:
                    return render_template('history.html', orders=[], error="Invalid order ID")
            else:
                # Get all completed orders
                performance_results = db_manager.compare_search_performance(status=1)
                orders = performance_results['status_search']['indexed']['result']
        else:
            # For GET requests, get all completed orders with performance comparison
            performance_results = db_manager.compare_search_performance(status=1)
            orders = performance_results['status_search']['indexed']['result']

        # Retrieve pizza details for each order
        for order in orders:
            pizza = db_manager.db.pizza.find_one({'pizza_id': order['pizza_id']})
            if pizza:
                pizza_type = db_manager.db.pizza_types.find_one({'pizza_type_id': pizza['pizza_type_id']})
                if pizza_type:
                    order['pizza_name'] = pizza_type['name']

    except Exception as e:
        print(f"Error fetching order history: {e}")
        return render_template('history.html', orders=[], error="Failed to retrieve completed orders.")
    finally:
        db_manager.disconnect()

    return render_template('history.html', orders=orders, performance=performance_results)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = request.json
    if not order_items:
        return jsonify({'success': False, 'message': 'No items in the order'}), 400

    try:
        db_manager.connect()
        for item in order_items:
            if item['quantity'] <= 0:
                continue

            # Assuming `item` has 'pizza_name' and 'size' attributes
            pizza_id = db_manager.get_pizza_id_by_name_and_size(item['pizza_name'], item['size'])
            db_manager.add_order_info(
                pizza_id,  # Use the pizza_id here
                item['quantity']
            )
        return jsonify({'success': True, 'message': 'Order submitted successfully'})
    except Exception as e:
        print(f"Error processing order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.disconnect()


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'redirect_url': '/'})


@app.route('/delete_order/<order_id>', methods=['POST'])
def delete_order(order_id):
    try:
        db_manager.connect()
        success = db_manager.delete_order(order_id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to delete order'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db_manager.disconnect()


@app.route('/update_pizza/<pizza_id>', methods=['POST'])
def update_pizza(pizza_id):
    try:
        new_name = request.form.get('name')
        new_category = request.form.get('category')
        new_ingredients = request.form.get('ingredients')

        if not all([new_name, new_category, new_ingredients]):
            return "Missing required fields", 400

        db_manager.connect()
        success = db_manager.update_pizza_type(pizza_id, new_name, new_category, new_ingredients)
        if success:
            return redirect(url_for('staff_info'))
        return "Failed to update pizza", 404
    except Exception as e:
        print(f"Error updating pizza: {e}")
        return str(e), 500
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
        return jsonify({'success': False, 'message': 'Failed to create user'}), 500
    finally:
        db_manager.disconnect()


@app.route('/check_staff_lock', methods=['POST'])
def check_staff_lock():
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.json
    staff_id = data.get('staff_id')

    try:
        db_manager.connect()
        success, message = db_manager.acquire_staff_lock(staff_id)
        return jsonify({
            'locked': not success,
            'message': message
        })
    finally:
        db_manager.disconnect()


@app.route('/get_stats')
def get_stats():
    try:
        db_manager.connect()
        total_orders = len(db_manager.get_all_orders())
        total_earnings = db_manager.get_total_earnings()
        pizza_types = len(db_manager.get_pizza_types())

        return jsonify({
            'total_orders': total_orders,
            'total_earnings': total_earnings,
            'pizza_types': pizza_types
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db_manager.disconnect()


@app.route('/release_staff_lock', methods=['POST'])
def release_staff_lock():
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.json
    staff_id = data.get('staff_id')

    try:
        db_manager.connect()
        success = db_manager.release_staff_lock(staff_id)
        return jsonify({'success': success})
    finally:
        db_manager.disconnect()


if __name__ == '__main__':
    app.run(debug=True)