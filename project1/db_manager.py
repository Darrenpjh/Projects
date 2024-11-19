import mysql.connector
from mysql.connector import Error
import time

class DBManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self._setup_indexes()

    def connect(self):
        """Establish a connection to the database."""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset="utf8mb4",
                    collation="utf8mb4_general_ci"
                )
            except Error as e:
                print(f"Error while connecting to MySQL: {e}")
                self.connection = None

    def ensure_connection(self):
        """Ensure that the connection to the database is active."""
        max_retries = 3
        retry_delay = 1  # second

        for attempt in range(max_retries):
            if self.connection is None or not self.connection.is_connected():
                print(f"Attempting to reconnect (attempt {attempt + 1}/{max_retries})...")
                self.connect()
                if self.connection and self.connection.is_connected():
                    return True
                time.sleep(retry_delay)
            else:
                return True

        print("Failed to establish a connection after multiple attempts.")
        return False

    def disconnect(self):
        """Close the connection to the database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def _setup_indexes(self):
        try:
            self.connect()
            queries = [
                "DROP INDEX IF EXISTS idx_order_id ON order_info",
                "DROP INDEX IF EXISTS idx_status ON order_info",
                "DROP INDEX IF EXISTS idx_pizza_id ON order_info",
                "CREATE INDEX idx_order_id ON order_info (order_id, status)",
                "CREATE INDEX idx_status ON order_info (status, order_id)",
                "CREATE INDEX idx_pizza_id ON order_info (pizza_id, status)"
            ]
            for query in queries:
                self.execute_query(query)
            print("Indexes setup completed successfully")
        except Error as e:
            print(f"Error setting up indexes: {e}")
        finally:
            self.disconnect()

    def execute_query(self, query, params=()):
        """Execute a query with connection check and return results if it's a SELECT query."""
        if not self.ensure_connection():
            raise ConnectionError("Unable to establish a database connection.")

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return None
        except Error as e:
            print(f"Error while executing query: {e}")
            if not self.connection.is_connected():
                print("Lost connection during query execution. Attempting to reconnect...")
                if self.ensure_connection():
                    print("Reconnected successfully. Retrying query...")
                    return self.execute_query(query, params)
            self.connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()

    def db_login(self, username, password):
        """Execute a SELECT query and return the results if matched."""
        query = "SELECT user_id, username, password, role FROM login_info WHERE username=%s"
        user_data = self.execute_query(query, (username,))

        if user_data:
            db_user_id, db_username, db_password, db_role = user_data[0]
            if db_password == password:
                return (db_user_id, db_username, db_password, db_role)
        return None

    def delete_orderrow(self, order_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM order_info WHERE order_id = %s", (order_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting data: {e}")
            return False
        finally:
            cursor.close()

    def update_pizza(self, pizza_id, new_name, new_category, new_ingredients):
        """Update pizza details."""
        query = """
        UPDATE pizza_type 
        SET name = %s, category = %s, ingredients = %s 
        WHERE pizza_type_id = %s
        """
        return self.execute_query(query, (new_name, new_category, new_ingredients, pizza_id))

    def get_pizza_id_by_name_and_size(self, pizza_name, size):
        """Fetch the pizza_id based on pizza_type.name and pizza_order.size."""
        query = """
        SELECT pizza_order.pizza_id 
        FROM pizza_order 
        JOIN pizza_type ON pizza_order.pizza_type_id = pizza_type.pizza_type_id 
        WHERE pizza_type.name = %s AND pizza_order.size = %s;
        """
        result = self.execute_query(query, (pizza_name, size))
        if result:
            return result[0][0]
        else:
            raise ValueError(f"Pizza '{pizza_name}' with size '{size}' not found in database.")

    def add_order_info(self, pizza_name, size, quantity, user_id):
        """Add a detail to an order by fetching pizza_id from pizza_name and size."""
        try:
            pizza_id = self.get_pizza_id_by_name_and_size(pizza_name, size)
            query = "INSERT INTO order_info (pizza_id, quantity, status, user_id) VALUES (%s, %s, 0, %s)"
            self.execute_query(query, (pizza_id, quantity, user_id))
            self.connection.commit()
            print(f"Order info added successfully for {pizza_name}, size {size}.")
        except Error as e:
            self.connection.rollback()
            print(f"Error adding order info: {e}")
            raise e

    def add_user(self, username, password):
        """Add a new user to the login_info table."""
        query = "INSERT INTO login_info (username, password, role) VALUES (%s, %s, 1)"
        try:
            self.execute_query(query, (username, password))
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False

    def update_order_status(self, order_id, status):
        """Update the status of an order."""
        query = "UPDATE order_info SET status = %s WHERE order_id = %s"
        try:
            self.execute_query(query, (status, order_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error updating order status: {e}")
            return False

    def get_completed_orders(self):
        """Get all completed orders (status = 1)."""
        query = """
        SELECT oi.order_id, pt.name, oi.quantity
        FROM order_info oi
        JOIN pizza_order po ON oi.pizza_id = po.pizza_id
        JOIN pizza_type pt ON po.pizza_type_id = pt.pizza_type_id
        WHERE oi.status = 1
        ORDER BY oi.order_id DESC
        """
        return self.execute_query(query)

    def search_completed_orders(self, order_id):
        query = """
        SELECT oi.order_id, pt.name, oi.quantity
        FROM order_info oi
        USE INDEX (idx_order_id)
        JOIN pizza_order po ON oi.pizza_id = po.pizza_id
        JOIN pizza_type pt ON po.pizza_type_id = pt.pizza_type_id
        WHERE oi.status = 1 AND oi.order_id = %s
        """
        return self.execute_query(query, (order_id,))

    def search_completed_orders_non_indexed(self, order_id):
        query = """
        SELECT oi.order_id, pt.name, oi.quantity
        FROM order_info oi IGNORE INDEX (idx_order_id, idx_status, idx_pizza_id)
        JOIN pizza_order po ON oi.pizza_id = po.pizza_id
        JOIN pizza_type pt ON po.pizza_type_id = pt.pizza_type_id
        WHERE oi.status = 1 AND oi.order_id = %s
        """
        return self.execute_query(query, (order_id,))

    def acquire_staff_lock(self, staff_id):
        """Acquire a table lock for staff modifications."""
        try:
            cursor = self.connection.cursor()

            # Lock the tables that will be modified
            cursor.execute("LOCK TABLES pizza_type WRITE, pizza_order WRITE")

            # Return success since we have the lock
            return True, None

        except Error as e:
            print(f"Error acquiring table lock: {e}")
            return False, str(e)
        finally:
            cursor.close()

    def release_staff_lock(self):
        """Release all table locks."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UNLOCK TABLES")
            return True
        except Error as e:
            print(f"Error releasing table lock: {e}")
            return False
        finally:
            cursor.close()

    def batch_update_orders(self, order_updates):
        """
        Perform batch order updates with table locking.

        Args:
            order_updates: dict of {order_id: {'quantity': int, 'status': str}}
        """
        try:
            cursor = self.connection.cursor()

            # Lock the order_info table for writing
            cursor.execute("LOCK TABLES order_info WRITE")

            self.start_transaction()

            for order_id, updates in order_updates.items():
                query = """
                    UPDATE order_info 
                    SET quantity = %s, status = %s 
                    WHERE order_id = %s
                """
                self.execute_query(query, (
                    updates['quantity'],
                    updates['status'],
                    order_id
                ))

            self.commit_transaction()
            return True

        except Error as e:
            self.rollback_transaction()
            print(f"Error in batch update: {e}")
            raise e
        finally:
            # Always release locks
            cursor.execute("UNLOCK TABLES")
            cursor.close()

    def start_transaction(self):
        """Start a new transaction."""
        self.connection.start_transaction()

    def commit_transaction(self):
        """Commit the current transaction."""
        self.connection.commit()

    def rollback_transaction(self):
        """Rollback the current transaction."""
        self.connection.rollback()

    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                print('Database connection closed.')
            except mysql.connector.Error as e:
                print(f"Error closing database connection: {str(e)}")