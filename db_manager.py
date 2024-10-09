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

    def disconnect(self):
        """Close the connection to the database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=()):
        """Execute a query and return results if it's a SELECT query."""
        if self.connection is None or not self.connection.is_connected():
            self.connect()
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error while executing query: {e}")
            raise e
        finally:
            cursor.close()
            self.disconnect()

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

    def delete_orderrow(self, order_id, order_detail):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM order_info WHERE order_id = %s AND order_detail = %s", (order_id, order_detail))
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
        
    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                print('Database connection closed.')
            except mysql.connector.Error as e:
                print(f"Error closing database connection: {str(e)}")
                