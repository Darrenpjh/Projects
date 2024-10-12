
# Pizza Boi App

This is a web-based pizza ordering application where staff and customers can interact with the system to manage pizza orders.

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Darrenpjh/Projects
   cd Projects
   ```

2. **Install the required libraries:**

   ```bash
   pip install Flask PyMySQL mysql-connector-python
   ```

3. **Import the Database:**

   - Create a new database within MySQL:
     ```sql
     CREATE DATABASE <new_database>;
     ```

   - Exit MySQL and return to the terminal.

   - Run the following command to import the database dump:
     ```bash
     mysql -u username -p new_database < datadump.sql
     ```

4. **Update `app.py`:**

   - Modify line 10 of `app.py` to configure your database credentials:
     ```python
     db_manager = DBManager(host='localhost', user=<database username>, password=<database password>, database=<the database that was imported into>)
     ```
     Example:
     ```python
     db_manager = DBManager(host='localhost', user='root', password='1234', database='project')
     ```

5. **Run the Application:**

   - Start the Flask development server:
     ```bash
     python app.py
     ```

   - Open a browser and navigate to `http://127.0.0.1:5000` to access the app.

## User Accounts

| Username  | Password  | Role        | Permissions                          |
|-----------|-----------|-------------|--------------------------------------|
| root      | root      | Staff    (0)| Able to access staff dashboard       |
| tom       | tom       | Customer (1)| Unable to access staff dashboard     |

## Required Libraries

- Flask
- PyMySQL or MySQL Connector Python (sql-connector-python)
- mysql-connector-python

To install the libraries, run:
```bash
pip install Flask PyMySQL mysql-connector-python
```

## Project Structure

```bash
PizzaBoiApp/
│
├── db_manager.py       # Communicating with the database
├── app.py              # Main application file (Flask server)
├── /templates          # HTML templates directory
│   ├── index.html      # Main page for customers
│   └── staff.html      # Staff management page
├── /static             # Static files directory
│   ├── styles.css      # Stylesheet for the website
│   └── /images         # Images directory
│       └── /pizzas     # Extract pizzas.zip here
└── README.md           # Project documentation (this file)
```
