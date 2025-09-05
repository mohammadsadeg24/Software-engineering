
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
