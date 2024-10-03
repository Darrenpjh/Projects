import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTableWidget, QTableWidgetItem
import pymysql
from db_manager import DBManager

class LoginController(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.db_manager = DBManager(
            host="localhost",
            user="root",
            password="root",
            database="projectdb"
        )

    def init_ui(self):
        self.username = QLabel('Username:')
        self.password = QLabel('Password:')

        self.text_user = QLineEdit()
        self.text_pass = QLineEdit()
        self.text_pass.setEchoMode(QLineEdit.Password)  # Hide password input
        self.button_login = QPushButton('Login')
        self.button_login.clicked.connect(self.check_credentials)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.username)
        layout.addWidget(self.text_user)
        layout.addWidget(self.password)
        layout.addWidget(self.text_pass)
        layout.addWidget(self.button_login)
        
        self.setLayout(layout)
        self.setWindowTitle('Login Page')

    def check_credentials(self):
        username = self.text_user.text()
        password = self.text_pass.text()

        try:
            self.db_manager.connect()
        except Exception as e:
            QMessageBox.critical(self,'Error', f"Failed to connect to Database: {str(e)}")
            return
        
        if self.db_manager.db_login(username, password):
            QMessageBox.information(self, 'Login Success', 'Welcome!')
            self.open_menu()  # Open the menu page if login is successful
        else:
            QMessageBox.warning(self, 'Login Failed', 'Incorrect username or password')

        self.db_manager.close_connection()

    def open_menu(self):
        self.hide()
        self.menu = DatabaseApp()
        self.menu.show()

class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('MariaDB Connection')
        self.setGeometry(100, 100, 400, 200)

        # Layout
        layout = QVBoxLayout()

        self.table_label = QLabel('Table:')
        self.table_input = QLineEdit()
        layout.addWidget(self.table_label)
        layout.addWidget(self.table_input)

        # Retrieve data button
        self.connect_button = QPushButton('Retrieve Data')
        self.connect_button.clicked.connect(self.retrieve_data)
        layout.addWidget(self.connect_button)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Set layout to central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.db_manager = DBManager(
            host="localhost",
            user="root",
            password="root",
            database="projectdb"
        )
        try:
            self.db_manager.connect()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Failed to connect to database: {str(e)}")

    
    def retrieve_data(self):
        table = self.table_input.text()
        query = f"SELECT * FROM {table}"

        try:
            # Retrieve data from the database
            results, column_names = self.db_manager.execute_query(query)
            self.populate_table(results, column_names)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Failed to retrieve data: {str(e)}")


    def populate_table(self, data, column_names):
        """ Populate the QTableWidget with the database data. """
        self.table_widget.clear()
        self.table_widget.setColumnCount(len(column_names))
        self.table_widget.setHorizontalHeaderLabels(column_names)
        self.table_widget.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

def main():
    app = QApplication(sys.argv)
    login_window = LoginController()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
