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
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                collation = "utf8mb4_general_ci"
            )
            if self.connection.is_connected():
                print("Successfully connected to the database.")
        except Error as e:
            print(f"Error while connecting to database: {e}")
            raise e

    def disconnect(self):
        """Close the connection to the database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query):
        """Execute a SELECT query and return the results."""
        if self.connection is None or not self.connection.is_connected():
            raise Exception("Database connection is not established.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = cursor.column_names
            return results, column_names
        except Error as e:
            print(f"Error while executing query: {e}")
            raise e
        finally:
            cursor.close()

    def db_login(self, username, password):
        """Execute a SELECT query and return the results if matched."""
        query = "SELECT * FROM login_info WHERE username=%s AND password=%s"
        cursor = self.connection.cursor()

        if self.connection is None or not self.connection.is_connected():
            raise Exception("Database connection is not established.")

        try:
            cursor.execute(query, (username, password))
            results = cursor.fetchone()
            cursor.close()

            return results is not None
        except Error as e:
            print(f"Error while executing query: {e}")
            raise e
    
    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                print('Database connection closed.')
            except mysql.connector.Error as e:
                print(f"Error closing database connection: {str(e)}")