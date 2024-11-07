from pymongo import MongoClient
from bson.objectid import ObjectId
import time
import psutil
import os


class DBManager:
    def __init__(self, host='localhost', port=27017, database='project'):
        self.client = None
        self.db = None
        self.host = host
        self.port = port
        self.database = database

    def connect(self):
        """Establish a connection to MongoDB."""
        try:
            self.client = MongoClient(f'mongodb://{self.host}:{self.port}/')
            self.db = self.client[self.database]
            self._setup_indexes()  # Setup indexes on connection
            print("Connected to MongoDB successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None

    def disconnect(self):
        """Close the connection to MongoDB."""
        if self.client:
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

    def measure_performance(self, func):
        """Measure execution time and memory usage of a function."""
        process = psutil.Process(os.getpid())

        # Memory before
        mem_before = process.memory_info().rss / 1024 / 1024  # Convert to MB

        # Time measurement
        start_time = time.time()
        result = func()
        end_time = time.time()

        # Memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # Convert to MB

        return {
            'execution_time': end_time - start_time,
            'memory_used': mem_after - mem_before,
            'result': result
        }

    def search_order_by_id_indexed(self, order_id):
        """Search for an order using the indexed order_id field."""

        def search():
            return list(self.db.orders.find({'order_id': order_id}))

        return self.measure_performance(search)

    def search_order_by_id_non_indexed(self, order_id):
        """Search for an order without using the index."""

        def search():
            # Hint forces MongoDB to NOT use the index
            return list(self.db.orders.find({'order_id': order_id}).hint([('$natural', 1)]))

        return self.measure_performance(search)

    def search_by_status_indexed(self, status):
        """Search orders by status using the index."""

        def search():
            return list(self.db.orders.find({'status': status}))

        return self.measure_performance(search)

    def search_by_status_non_indexed(self, status):
        """Search orders by status without using the index."""

        def search():
            # Hint forces MongoDB to NOT use the index
            return list(self.db.orders.find({'status': status}).hint([('$natural', 1)]))

        return self.measure_performance(search)

    def compare_search_performance(self, order_id=None, status=None):
        """Compare performance between indexed and non-indexed searches."""
        results = {}

        if order_id is not None:
            results['order_id_search'] = {
                'indexed': self.search_order_by_id_indexed(order_id),
                'non_indexed': self.search_order_by_id_non_indexed(order_id)
            }

        if status is not None:
            results['status_search'] = {
                'indexed': self.search_by_status_indexed(status),
                'non_indexed': self.search_by_status_non_indexed(status)
            }

        return results

    def db_login(self, username, password):
        """Authenticate user login."""
        user = self.db.User.find_one({'username': username, 'password': password})
        if user:
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role']
            }
        print("User not found")
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
        pizza_type = self.db.pizza_types.find_one({'name': full_name})
        if not pizza_type:
            raise ValueError(f"Pizza type '{full_name}' not found in the pizza_types collection.")

        pizza_type_id = pizza_type['pizza_type_id']
        pizza = self.db.pizza.find_one({'pizza_type_id': pizza_type_id, 'size': size})
        if pizza:
            return pizza['pizza_id']
        else:
            raise ValueError(f"Pizza with type '{full_name}' and size '{size}' not found in the pizza collection.")

    def get_pending_orders(self):
        """Get all pending orders with pizza details."""
        pipeline = [
            {'$match': {'status': 0}},
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
            {'$set': {'status': 1}}
        )
        return result.modified_count > 0

    def delete_orderrow(self, order_id):
        """Delete an order by ID."""
        result = self.db.orders.delete_one({'_id': ObjectId(order_id)})
        return result.deleted_count > 0

    def update_pizza_type(self, pizza_type_id, new_name, new_category, new_ingredients):
        """Update pizza type information."""
        try:
            result = self.db.pizza_types.update_one(
                {'pizza_type_id': pizza_type_id},
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