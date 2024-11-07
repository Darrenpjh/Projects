import mysql.connector
from mysql.connector import Error

class DBManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

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
                    collation = "utf8mb4_general_ci"
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
                return None  # For non-SELECT queries
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
            print(f"Found user: {db_username}, role: {db_role}")  # Debugging

            # Assuming you're using plain-text password comparison
            if db_password == password:
                return (db_user_id, db_username, db_password, db_role)
            else:
                print("Password Mismatched")
                return None  # Password does not match
        print("No user found with this username")
        return None  # Username not found

    def delete_orderrow(self, order_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM order_info WHERE order_id = %s ", (order_id,))
            self.connection.commit()
            return cursor.rowcount > 0  # Return True if a row was deleted
        except Error as e:
            print(f"Error deleting data: {e}")
            return False
        finally:
            cursor.close()
    
    def update_pizza(self, pizza_id, new_name, new_category, new_ingre):

        update_query = """UPDATE pizza_type SET name=%s, category=%s, ingredients=%s WHERE pizza_type_id = %s"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(update_query,(new_name, new_category, new_ingre, pizza_id))
            self.connection.commit()
            return cursor.rowcount > 0  # Return True if a row was deleted
        except Error as e:
            print(f"Error updating: {e}")
            return False
        finally:
            cursor.close()

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
            return result[0][0]  # Return the pizza_id
        else:
            raise ValueError(f"Pizza '{pizza_name}' with size '{size}' not found in database.")

    def add_order_info(self, pizza_name, size, quantity):
        """Add a detail to an order by fetching pizza_id from pizza_name and size."""
        try:
            pizza_id = self.get_pizza_id_by_name_and_size(pizza_name, size)
            query = "INSERT INTO order_info (pizza_id, quantity) VALUES (%s, %s)"
            self.execute_query(query, (pizza_id, quantity))
            self.connection.commit()  # Commit the transaction
            print(f"Order info added successfully for {pizza_name}, size {size}.")
        except Error as e:
            self.connection.rollback()  # Rollback in case of error
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

    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                print('Database connection closed.')
            except mysql.connector.Error as e:
                print(f"Error closing database connection: {str(e)}")
                