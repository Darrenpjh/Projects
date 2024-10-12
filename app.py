from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db_manager import DBManager
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)  # This generates a random secret key

# Initialize your DBManager instance
db_manager = DBManager(host='localhost', user='root', password='1234', database='project')


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

        # Debug print
        print(f"Raw pizzas data: {raw_pizzas}")  # Add this line to check the data

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
    # Check if the user is logged in and has a staff role (role == 0)
    if 'user_id' not in session or session['role'] != 0:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Fetch pizza data
    db_manager.connect()

    try:
        pizza_types = db_manager.execute_query("SELECT * FROM pizza_type") or []
        pizza_orders = db_manager.execute_query("SELECT * FROM order_info") or []
        earnings_data = calculate_earnings()
        total_earnings = sum(row[4] for row in earnings_data) if earnings_data else 0
    except Exception as e:
        return jsonify({'error': f"Failed to fetch data: {str(e)}"}), 500
    
    finally:
        db_manager.disconnect()
    
    # Render the staff.html template and pass the pizza data
    return render_template('staff.html', pizza_types=pizza_types, pizza_orders=pizza_orders,
                           earnings_data=earnings_data,total_earnings=total_earnings)


@app.route('/submit_order', methods=['POST'])
def submit_order():
    order_items = request.json
    if not order_items:
        return jsonify({'success': False, 'message': 'No items in the order'}), 400

    try:
        db_manager.connect()
        for item in order_items:
            pizza_name = item['pizza_name']
            size = item['size']
            quantity = item['quantity']

            if quantity <= 0:
                continue

            db_manager.add_order_info(pizza_name, size, quantity)

        return jsonify({'success': True, 'message': 'Order submitted successfully'})
    except Exception as e:
        print(f"Error processing order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.disconnect()

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
    
@app.route('/update_pizza/<pizza_id>', methods=['POST'])
def update_pizza(pizza_id):

    new_name = request.form['name']
    new_category = request.form['category']
    new_ingredients = request.form['ingre']

    try:
        db_manager.connect()
    except Exception as e:
        print(f"Error in establishing connection: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    
    if db_manager.update_pizza(pizza_id, new_name=new_name, new_category=new_category, new_ingre=new_ingredients):
        db_manager.disconnect()
        return redirect(url_for('staff_info'))
    else:
        return "An error occurred while updating pizza", 404

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
