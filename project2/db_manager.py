from pymongo import MongoClient
from bson.objectid import ObjectId
import time
import psutil
import os
import bcrypt

class DBManager:
    def __init__(self, host='localhost', port=27017, database='project'):
        self.client = None
        self.db = None
        self.host = host
        self.port = port
        self.database = database

    def hashed_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

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
        user = self.db.User.find_one({'username': username})

        if user:
            stored_hash = user['password']
            valid = bcrypt.checkpw(password.encode(), stored_hash.encode())
            if valid:
             return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
            else:
                print('Password mismatch')
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

    def complete_order(self, order_id):
        """Mark an order as complete."""
        result = self.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': 1}}
        )
        return result.modified_count > 0

    def delete_order(self, order_id):
        """Delete an order."""
        try:
            result = self.db.orders.delete_one({"_id": ObjectId(order_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False

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
            hash = self.hashed_password(password) 
            user_id = self.db.User.count_documents({})
            new_user = {
                'user_id': user_id,
                'username': username,
                'password': hash,
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

    def get_total_earnings(self):
        """Calculate total earnings from all completed orders."""
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
        ]
        result = list(self.db.orders.aggregate(pipeline))
        return result[0]["total"] if result else 0

    def acquire_staff_lock(self, staff_id):
        """Acquire a lock for staff modifications using MongoDB."""
        try:
            # Try to create or update a lock document
            result = self.db.staff_locks.update_one(
                {'resource': 'menu_edit'},
                {
                    '$setOnInsert': {
                        'locked_by': staff_id,
                    }
                },
                upsert=True
            )

            # Check if we got the lock
            if result.upserted_id:
                return True, None

            # If lock exists, check who has it
            lock = self.db.staff_locks.find_one({'resource': 'menu_edit'})
            if lock and str(lock['locked_by']) != str(staff_id):
                return False, f"Menu is currently being edited by another staff member"

            return True, None

        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False, str(e)

    def release_staff_lock(self, staff_id):
        """Release the staff lock."""
        try:
            result = self.db.staff_locks.delete_one({
                'resource': 'menu_edit',
                'locked_by': staff_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error releasing lock: {e}")
            return False

    def batch_update_orders(self, order_updates):
        """Perform batch order updates with MongoDB transactions."""
        try:
            # Start a session for the transaction
            with self.client.start_session() as session:
                with session.start_transaction():
                    for order_id, updates in order_updates.items():
                        self.db.orders.update_one(
                            {'_id': ObjectId(order_id)},
                            {
                                '$set': {
                                    'quantity': updates['quantity'],
                                    'status': updates['status']
                                }
                            },
                            session=session
                        )
                    return True
        except Exception as e:
            print(f"Error in batch update: {e}")
            return False