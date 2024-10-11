
# Pizza Boi App

This is a web-based pizza ordering application where staff and customers can interact with the system to manage pizza orders.

## Setup Instructions

**Please change the following in `app.py` accordingly:**
```python
# In line 10
db_manager = DBManager(host='localhost', user=<database username>, password=<database password>, database=<the database that was imported into>)

## User Accounts

| Username  | Password  | Role     | Permissions                          |
|-----------|-----------|----------|--------------------------------------|
| root      | root      | Staff    | Able to access staff dashboard       |
| tom       | tom       | Customer | Unable to access staff dashboard     |

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
