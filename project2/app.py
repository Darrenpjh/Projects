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

""""
@app.route('/history')
def order_history():
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    search_date = request.args.get('date')

    db_manager.connect()
    try:
        # Get completed orders (status 1)
        completed_orders = db_manager.get_completed_orders(search_date)
        return render_template('history.html', orders=completed_orders)
    except Exception as e:
        return jsonify({'error': f"Failed to fetch history: {str(e)}"}), 500
    finally:
        db_manager.disconnect()
"""


@app.route('/history', methods=['GET', 'POST'])
def order_history():
    # Establish connection
    db_manager.connect()

    if request.method == 'POST':
        order_id = request.form.get('order_id')

        if order_id:
            try:
                order_id = int(order_id)
            except ValueError:
                return render_template('history.html', orders=[], error="Invalid order ID")

            # Fetch the order by order_id where status is 1 (completed)
            order = db_manager.db.orders.find_one({'order_id': order_id, 'status': 1})
            orders = [order] if order else []
        else:
            # Fetch all completed orders
            orders = list(db_manager.db.orders.find({'status': 1}))
    else:
        # Fetch all completed orders
        orders = list(db_manager.db.orders.find({'status': 1}))

    return render_template('history.html', orders=orders)

@app.route('/complete_order/<order_id>', methods=['POST'])
def complete_order(order_id):
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        db_manager.connect()
        if db_manager.mark_order_complete(order_id):
            return redirect(url_for('staff_info'))
        return "Order not found", 404
    except Exception as e:
        print(f"Error completing order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.disconnect()


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
        if db_manager.delete_orderrow(order_id):
            return redirect(url_for('staff_info'))
        return "Order not found", 404
    except Exception as e:
        print(f"Error deleting order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
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


if __name__ == '__main__':
    app.run(debug=True)