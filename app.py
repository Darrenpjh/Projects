from flask import Flask, render_template, request, jsonify
from db_manager import DBManager

app = Flask(__name__)

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

#

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    db_manager.connect()
    user = db_manager.db_login(username, password)
    db_manager.disconnect()
    
    if user and isinstance(user, (list, tuple)):
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        return jsonify({'success': True, 'role': user[3]})
    else:
        return jsonify({'success': True})

@app.route('/staff_info')
def staff_info():
    # Check if the user is logged in and has a staff role (role == 0)
    #if 'user_id' not in session or session['role'] != 0:
    #    return jsonify({'error': 'Unauthorized access'}), 403

    # Fetch pizza data
    db_manager.connect()
    pizza_types = db_manager.execute_query("SELECT * FROM pizza_type") or []
    pizza_orders = db_manager.execute_query("SELECT * FROM pizza_order") or []
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
