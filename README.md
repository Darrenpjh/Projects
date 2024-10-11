
# Pizza Boi App

This is a web-based pizza ordering application where staff and customers can interact with the system to manage pizza orders.

**app.py**
**Please change accordingly**
In line 10:
db_manager = DBManager(host='localhost', user=<database username>, password=<database password>, database=<the database that was imported into>)


## Project Structure

```bash
PizzaBoiApp/
│
├── db_manager.py       # Communicating with the database
├── app.py              # Main application file (Flask server)
├── /Templates          # HTML templates directory
│   ├── index.html      # Main page for customers
│   └── staff.html      # Staff management page
├── /static             # Static files directory
│   ├── styles.css      # Stylesheet for the website
│   └── /images         # Images directory
│       └── /pizzas     # Extract pizzas.zip here
└── README.md           # Project documentation (this file)
