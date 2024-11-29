---

# Pizza Boi App

This is a web-based pizza ordering application where staff and customers can interact with the system to manage pizza orders. The app supports two backends: **Project 1** (MySQL) and **Project 2** (NoSQL with MongoDB).

---

## Setup Instructions for Project 1 (MySQL)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Darrenpjh/Projects
   cd Projects/project1
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

   - Modify the database credentials in `app.py`:
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

---

Here's the updated section for the **Project 2 (MongoDB)** setup to include the libraries you're using:  

---

## Setup Instructions for Project 2 (MongoDB)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Darrenpjh/Projects
   cd Projects/project2
   ```

2. **Install the required libraries:**

   ```bash
   pip install Flask pymongo bcrypt psutil
   ```

3. **Import the Database:**

   - Restore the MongoDB dump using `mongorestore`:
     ```bash
     mongorestore --host localhost --port <port_number> --db <database_name> ./mongodump/project
     ```

4. **Update `app.py`:**

   - Modify the database configuration in `app.py`:
     ```python
     from pymongo import MongoClient
     from bson.objectid import ObjectId
     import time
     import psutil
     import os
     import bcrypt

     client = MongoClient('<connection_string>')
     db = client.<database_name>  //Modify to your database name
     ```

5. **Run the Application:**

   - Start the Flask development server:
     ```bash
     python app.py
     ```

   - Open a browser and navigate to `http://127.0.0.1:5000` to access the app.

--- 

Let me know if you need further updates!
## User Accounts

| Username  | Password  | Role        | Permissions                          |
|-----------|-----------|-------------|--------------------------------------|
| root      | root      | Staff    (0)| Able to access staff dashboard       |
| staff     | staff	| Staff    (0)| 
| Gary      | 1234      | Customer (1)| Unable to access staff dashboard     |

---

## Required Libraries

### For Project 1 (MySQL)

- Flask  
- PyMySQL or MySQL Connector Python  
- mysql-connector-python  

### For Project 2 (MongoDB)

- Flask  
- pymongo
- bycryt
- psutil

To install all libraries, run:
```bash
pip install Flask PyMySQL mysql-connector-python pymongo bcrypt psutil
```

---

## Project Structure

```bash
Projects/
│
├───project1/          # MySQL-based implementation
│   ├───.idea/
│   ├───static/
│   │   └───images/
│   │       └───pizzas/
│   ├───Templates/
│   ├───__pycache__/
│   ├───db_manager.py  # Communicating with the MySQL database
│   ├───app.py         # Main application file for MySQL
│   └───datadump.sql   # MySQL database dump
│
└───project2/          # NoSQL-based implementation (MongoDB)
    ├───mongodump/     # MongoDB dump files
    │   └───project/
    ├───static/
    │   └───images/
    │       └───pizzas/
    ├───Templates/
    ├───__pycache__/
    ├───db_manager.py  # Communicating with the MongoDB database
    ├───app.py         # Main application file for MongoDB
```

---
