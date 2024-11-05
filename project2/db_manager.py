from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime


class DBManager:
    def __init__(self, host='localhost', port=27017, database='project'):
        self.client = None
        self.db = None
        self.host = host
        self.port = port
        self.database = database
        #self.background_queue = Queue()
        #self._start_background_worker()

        #create Indexes when initializing
        #self._setup_indexes()


    def connect(self):
        """Establish a connection to MongoDB."""
        try:
            self.client = MongoClient(f'mongodb://{self.host}:{self.port}/')
            self.db = self.client[self.database]
            print("Connected to MongoDB successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None

    def disconnect(self):
        """Close the connection to MongoDB."""
        if  self.client:
            self.client.close()
            self.client = None
            self.db = None
            print("MongoDB connection closed")

    def _setup_indexes(self):
        """Create indexes for collections."""
        # Index on 'status' and 'order_id' fields in the 'orders' collection
        self.db.orders.create_index([('status', 1)])  # Index on status
        self.db.orders.create_index([('order_id', 1)])  # Index on order_id
        self.db.orders.create_index([('status', 1), ('order_id', 1)])  # Compound index

    def search_pending_orders(self, status=0, limit=10):
        """
        Search for pending orders with the given status.

        :param status: The order status to filter by (default is 0 for pending).
        :param limit: The maximum number of orders to return.
        :return: List of pending orders.
        """
        # Query the orders collection for pending orders
        pending_orders = list(self.db.orders.find({'status': status}).limit(limit))
        return pending_orders

    def db_login(self, username, password):
        """Authenticate user login."""
        user = self.db.User.find_one({'username': username, 'password': password})
        if user:
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role']
            }
        return None

    def get_all_pizzas(self):
        """Get all pizzas with their types and prices."""
        pipeline = [
            {
                '$lookup': {
                    'from': 'pizza_types',
                    'localField': 'pizza_type_id',
                    'foreignField': 'pizza_type_id',
                    'as': 'type_info'
                }
            },
            {'$unwind': '$type_info'},
            {
                '$group': {
                    '_id': '$pizza_type_id',
                    'name': {'$first': '$type_info.name'},
                    'category': {'$first': '$type_info.category'},
                    'ingredients': {'$first': '$type_info.ingredients'},
                    'image_path': {'$first': '$type_info.image_path'},
                    'sizes': {
                        '$push': {
                            'size': '$size',
                            'price': '$price'
                        }
                    }
                }
            }
        ]
        pizzas = list(self.db.pizza.aggregate(pipeline))

        for pizza in pizzas:
            pizza['sizes'] = {size['size']: float(size['price']) for size in pizza['sizes']}
        return pizzas

    def get_pizza_id_by_name_and_size(self, full_name, size):
        """Fetch the pizza_id based on pizza type name and size."""

        # First, get the pizza_type_id from the pizza_types collection
        pizza_type = self.db.pizza_types.find_one({'name': full_name})
        if not pizza_type:
            raise ValueError(f"Pizza type '{full_name}' not found in the pizza_types collection.")

        pizza_type_id = pizza_type['pizza_type_id']

        # Then, get the pizza_id from the pizza collection using pizza_type_id and size
        pizza = self.db.pizza.find_one({'pizza_type_id': pizza_type_id, 'size': size})
        if pizza:
            return pizza['pizza_id']
        else:
            raise ValueError(f"Pizza with type '{full_name}' and size '{size}' not found in the pizza collection.")

    def get_pending_orders(self):
        """Get all pending orders with pizza details."""
        pipeline = [
            {'$match': {'status': 0}},  # Get only pending orders
            {
                '$lookup': {
                    'from': 'pizza',
                    'localField': 'pizza_id',
                    'foreignField': 'pizza_id',
                    'as': 'pizza_info'
                }
            },
            {'$unwind': '$pizza_info'},
            {
                '$lookup': {
                    'from': 'pizza_types',
                    'localField': 'pizza_info.pizza_type_id',
                    'foreignField': 'pizza_type_id',
                    'as': 'type_info'
                }
            },
            {'$unwind': '$type_info'},
            {
                '$project': {
                    'order_id': 1,
                    'pizza_name': '$type_info.name',
                    'quantity': 1,
                    'size': '$pizza_info.size',
                    '_id': 1
                }
            }
        ]
        return list(self.db.orders.aggregate(pipeline))

    def add_order_info(self, pizza_id, quantity):
        """Add a new order."""
        order = {
            'order_id': self.db.orders.count_documents({}) + 1,
            'pizza_id': pizza_id,
            'quantity': quantity,
            'status': 0,  # 0 for pending, 1 for completed
        }
        return self.db.orders.insert_one(order)

    def mark_order_complete(self, order_id):
        """Mark an order as complete."""
        result = self.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': 1
                }
            }
        )
        return result.modified_count > 0

    def get_completed_orders(self, search_date=None):
        """Get completed orders with optional date filter."""
        query = {'status': 1}

        completed_orders = self.db.orders.find(query).sort('completed_at', -1)

        result = []
        for order in completed_orders:
            # Get pizza details
            pizza = self.db.pizza.find_one({'pizza_id': order['pizza_id']})
            if pizza:
                pizza_type = self.db.pizza_types.find_one({'pizza_type_id': pizza['pizza_type_id']})
                if pizza_type:
                    result.append({
                        'order_id': order['order_id'],
                        'pizza_name': pizza_type['name'],
                        'quantity': order['quantity'],
                        #'total_price': float(pizza['price'] * order['quantity']),
                        #'completed_at': order['completed_at']
                    })

        return result

    def delete_orderrow(self, order_id):
        """Delete an order by ID."""
        result = self.db.orders.delete_one({'_id': ObjectId(order_id)})
        return result.deleted_count > 0

    def update_pizza_type(self, pizza_type_id, new_name, new_category, new_ingredients):
        """Update pizza type information."""
        try:
            result = self.db.pizza_types.update_one(
                {'pizza_type_id': pizza_type_id},  # Remove the int() conversion
                {
                    '$set': {
                        'name': new_name,
                        'category': new_category,
                        'ingredients': new_ingredients
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating pizza type: {e}")
            return False

    def add_user(self, username, password):
        """Add a new user."""
        try:
            user_id = self.db.User.count_documents({})
            new_user = {
                'user_id': user_id,
                'username': username,
                'password': password,
                'role': 1
            }
            self.db.User.insert_one(new_user)
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    def calculate_earnings(self):
        """Calculate earnings for each pizza type and size."""
        pipeline = [
            {
                '$lookup': {
                    'from': 'pizza',
                    'localField': 'pizza_id',
                    'foreignField': 'pizza_id',
                    'as': 'pizza_info'
                }
            },
            {'$unwind': '$pizza_info'},
            {
                '$lookup': {
                    'from': 'pizza_types',
                    'localField': 'pizza_info.pizza_type_id',
                    'foreignField': 'pizza_type_id',
                    'as': 'type_info'
                }
            },
            {'$unwind': '$type_info'},
            {
                '$group': {
                    '_id': {
                        'pizza_type': '$type_info.name',
                        'size': '$pizza_info.size'
                    },
                    'total_quantity': {'$sum': '$quantity'},
                    'total_earnings': {
                        '$sum': {'$multiply': ['$quantity', '$pizza_info.price']}
                    }
                }
            },
            {'$sort': {'total_earnings': -1}}
        ]
        return list(self.db.orders.aggregate(pipeline))