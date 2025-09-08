# 🍯 Honey Site (Hybrid Database Implementation)

This project is a **honey shop web application** built with a **hybrid database architecture**, using both **SQLite (relational)** and **MongoDB (document-based)**.

---

## 🏗️ Architecture Diagram

![database diagram](diagram.png)

> The diagram shows how **SQLite** and **MongoDB** work together.

---

## 📊 Database Design

### SQLite
- User
- Address

### MongoDB
- Category
- Product
- Review
- Cart
- Order

---

## 🛒 Project Overview

The **Honey Site** is a hybrid e-commerce application that combines the strengths of **SQLite** and **MongoDB** to handle different kinds of data efficiently.  
It delivers a complete shopping experience where users can create accounts, browse products, manage their carts, place orders, and share feedback through reviews and ratings.

---

## 👤 User & Authentication
- User accounts are stored in **SQLite**.  
- Each user has:
  - Username, email, password, personal details  
  - One or more saved addresses (with one default)  

---

## 🛍️ Shopping & Catalog
- Product catalog is stored in **MongoDB**.  
- Each product belongs to a category and has:
  - Title, description, price, images  
  - Status (active/inactive)  

---

## 🛒 Cart Management
- Each user has a **shopping cart** stored in MongoDB.  
- Features:
  - Add or remove products  
  - Track quantities automatically  
  - Calculate total price in real time  

---

## ✅ Checkout & Orders
- When a user checks out, the **cart becomes an order**.  
- Orders are stored in MongoDB and include:
  - Ordered items and quantities  
  - Total amount  
  - Shipping address (from SQLite)  
  - Payment status and order status  
  - Unique order number  

---

## ⭐ Product Reviews
- After buying a product, users can leave a review.  
- A review contains:
  - Rating (1–5 stars)  
  - Comment text  
  - Link to the **user (SQLite)** and the **product (MongoDB)**  

---

## 🔗 Data Flow
1. **User signs up** → Stored in **SQLite**.  
2. **User browses products** → Data from **MongoDB**.  
3. **User adds items to cart** → Stored in **MongoDB**.  
4. **User checks out** → Order created in **MongoDB** with address from **SQLite**.  
5. **User reviews product** → Stored in **MongoDB**, linked to **SQLite user**.  

---

## 🎯 Why Hybrid Database?
- **SQLite** → Best for structured and relational data.
- **MongoDB** → Best for flexible, nested, and scalable data.
- Together, they provide a **realistic and efficient design** for an online store.

---

## 🚀 How to Run the Project

### 1️⃣ Clone the repository
```bash
git clone https://github.com/mohammadsadeg24/Software-engineering.git
cd Software-engineering
````

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Setup the databases

* **MongoDB**:  will run automatically via `mongodb_connector` (default: mongodb://localhost:27017)
* **SQLite**: will be created automatically (`db.sqlite3`) after migrations

  ```bash
  python manage.py migrate
  ```

### 4️⃣ Start the server

```bash
python manage.py createsuperuser
```

-----

### Exploring the Django SQLite Database 🔎

This guide provides a quick and easy way to inspect the database of your Django project directly from the command line.

#### 1\. List All Tables

You can list all the tables in your database using the `sqlite3` command-line tool.

  * First, ensure you have `sqlite3` installed and your project's `db.sqlite3` file exists.
  * Run the following command in your terminal from the project's root directory:

<!-- end list -->

```bash
sqlite3 db.sqlite3
```

  * Once inside the SQLite shell, use the `.tables` command to display all tables:

<!-- end list -->

```sql
.tables
```

This will show a list of all tables, including the default Django tables and any custom models you've created.

-----

#### 2\. View Table Schema (Attributes)

To see the structure of a specific table (i.e., its columns and data types), use the `.schema` command followed by the table name.

  * **Syntax:**

    ```sql
    .schema <table_name>
    ```

  * **Example:** To view the attributes of the `core_user` table:

    ```sql
    .schema core_user
    ```

This command will output the `CREATE TABLE` statement for that table, which details the column names, their data types (e.g., `varchar`, `integer`), and any constraints.

-----

#### 3\. Query Data from a Table

To see the actual data inside a table, use a standard SQL `SELECT` statement.

  * **To select all data:**

    ```sql
    SELECT * FROM <table_name>;
    ```

  * **Example:** To see all data in the `core_user` table:

    ```sql
    SELECT * FROM core_user;
    ```

  * **To select specific columns:**

    ```sql
    SELECT column1, column2 FROM <table_name>;
    ```

  * **To limit the number of rows (useful for large tables):**

    ```sql
    SELECT * FROM <table_name> LIMIT 10;
    ```

-----

#### 4\. Exit the SQLite Shell

When you are finished, you can exit the shell by typing:

```sql
.exit
```

Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 📄 .gitignore (Suggested)

```
__pycache__/
*.pyc
*.db
.env
/static/
media/
```

---

## 🙌 Author

Created with ❤️ by [Mohammadsadegh Heydari](https://github.com/mohammadsadeg24)  
Computer Engineering Student – Urmia University
