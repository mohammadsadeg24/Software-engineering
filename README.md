
# 🍯 Honey Shop – Django + HTML + SQLite + Bootstrap

This is a simple e-commerce web application designed as a project for **Software Engineering 2**. It simulates a basic honey store and is built with:

- 🐍 **Django** for backend logic and admin panel
- 🗃️ **SQLite** as the default database
- 🎨 **HTML/CSS + Bootstrap** for frontend UI
- 🌐 Responsive design ready for deployment

---

## 📁 Project Structure Overview

```
narm2/
├── manage.py                  # Django entry point
├── honey-html/                # Frontend assets (HTML, CSS, fonts)
│   ├── *.html                 # Pages like index, about, contact, shop
│   ├── css/                   # Styling files including Bootstrap
│   ├── fonts/                 # FontAwesome and others
│   └── images/                # Images used in UI (if any)
├── yourprojectname/           # Django project config (settings, urls)
└── shop/                      # Django app for core logic (models, views)
```

---

## 🚀 Features

- Static frontend pages: Home, About, Contact, Shop, Product Quality
- Responsive layout with modern styling
- Ready-to-integrate backend using Django
- SQLite-based development database (default)
- Admin interface for easy data management

---

## 🧠 How It Works

### 🔙 Backend (Django)
- Django views render templates or handle data endpoints
- Models and migrations manage database structure
- Can be extended with login, cart, order management

### 🖼️ Frontend (HTML + Bootstrap)
- Clean and mobile-friendly HTML templates
- Built with modular CSS and custom fonts
- HTML files reside in the `honey-html/` directory

---

## 🔧 How to Run the Project

### 🔹 Prerequisites
- Python 3.10+ installed
- `pip` package manager

### 🔹 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/mohammadsadeg24/Software-engineering.git
cd Software-engineering/narm2

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python manage.py runserver
```

Then open your browser at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🛠 Django Admin Panel

Create a superuser to manage content via the admin UI:

```bash
python manage.py createsuperuser
```

Then access: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 📄 .gitignore

Example entries:

```
__pycache__/
*.pyc
*.db
.env
/static/
/media/
```

---

## 🙌 Author

Created with ❤️ by [Mohammadsadegh Heydari](https://github.com/mohammadsadeg24)  
Computer Engineering Student – Urmia University
