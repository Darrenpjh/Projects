from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db_manager import DBManager
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)  # This generates a random secret key


# Initialize your DBManager instance
db_manager = DBManager(host='localhost', user='root', password='root', database='projectdb')

@app.route('/')
def index():
    # Sample pizza data (in reality, you'd fetch this from your database)
    query = """ SELECT t.name AS 'name', t.category AS 'category', t.ingredients AS 'ingredients', o.size AS 'size', o.price AS 'price' 
            FROM pizza_type t JOIN pizza_order o  
            ON t.pizza_type_id = o.pizza_type_id; """
    
    pizzas = db_manager.execute_query(query)

    if pizzas is None:
        pizzas = []
        
    return render_template('index.html', pizzas=pizzas)

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
    
    if user:
        print(f"User found: {user}")
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        return jsonify({'success': True, 'role': user[3], 'redirect_url': '/staff' if user[3] == 0 else '/'})
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
    # Check if the user is logged in and has a staff role (role == 0)
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Fetch pizza data
    db_manager.connect()

    try:
        pizza_types = db_manager.execute_query("SELECT * FROM pizza_type") or []
        pizza_orders = db_manager.execute_query("SELECT * FROM pizza_order") or []
    
    except Exception as e:
        return jsonify({'error': f"Failed to fetch data: {str(e)}"}), 500
    
    finally:
        db_manager.disconnect()
    
    # Render the staff.html template and pass the pizza data
    return render_template('staff.html', pizza_types=pizza_types, pizza_orders=pizza_orders)

#

@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = request.form
    order_details = []

    for pizza_id, quantity in order_items.items():
        if quantity.isdigit() and int(quantity) > 0:
            order_details.append({'pizza_id': pizza_id, 'quantity': int(quantity)})

    if not order_details:
        return jsonify({'success': False, 'message': 'No valid items ordered'}), 400

    try:
        db_manager.connect()
        for order_item in order_details:
            query = "INSERT INTO order_info (pizza_id, quantity) VALUES (%s, %s)"
            db_manager.execute_query(query, (order_item['pizza_id'], order_item['quantity']))
        db_manager.disconnect()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error processing order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
