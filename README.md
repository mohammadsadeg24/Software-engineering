
# 🍯 Honey Shop – Django + HTML + JavaScript + Bootstrap

This is a simple e-commerce web application designed as a project for **Software Engineering 2**. It simulates a basic honey store and is built with:

- 🐍 **Django** for backend logic and admin panel
- 🗃️ **SQLite** as the default database
- 🎨 **HTML/CSS + Bootstrap** for frontend UI
- ⚙️ **JavaScript + custom scripts** for interactivity
- 🌐 Responsive design with modern components

---

## 📁 Project Structure Overview

```
SOFTWARE-ENGINEERING/
├── backend/                # Frontend assets (HTML, CSS, JS, fonts)
│   ├── core/           # Django project config (settings, urls)
│   ├── shop/                      # Django app for models, views, templates
│       └── *.html                 # Pages like main, profile
│   └── manage.py                  # Django entry point

```

---

## 🚀 Features

- Static pages: Main, Profile
- Responsive layout using Bootstrap
- Enhanced UI elements via  Bootstrap JS
- Django backend integration ready
- SQLite default database for development

---

## 🧠 How It Works

### 🔙 Backend (Django)
- Views and URLs serve templates or data
- Models define database schema
- Admin panel available for managing content

### 🖼️ Frontend (HTML + Bootstrap + JS)
- HTML templates in `/backend/template/`
- CSS styling with `bootstrap.min.css`
- JS interaction via:
  - `bootstrap.min.js` – modal, dropdown, etc.


---

## 🔧 How to Run the Project

### 🔹 Prerequisites
- Python 3.10+
- `pip` installed

### 🔹 Setup Instructions

```bash
git clone https://github.com/mohammadsadeg24/Software-engineering.git
cd Software-engineering/narm2/backend

# Create virtual environment
pipenv install 
pipenv shell

# Install dependencies
pip install -r requirements.txt

# Run the development server
python manage.py runserver
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🛠 Django Admin Panel

Create superuser:

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

---

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
