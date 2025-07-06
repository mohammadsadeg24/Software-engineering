
# 🍯 Honey Shop – Django + HTML + JavaScript + Bootstrap

This is a simple e-commerce web application designed as a project for **Software Engineering 2**. It simulates a basic honey store and is built with:

- 🐍 **Django** for backend logic and admin panel
- 🗃️ **SQLite** as the default database
- 🎨 **HTML/CSS + Bootstrap** for frontend UI
- ⚙️ **JavaScript + jQuery + custom scripts** for interactivity
- 🌐 Responsive design with modern components

---

## 📁 Project Structure Overview

```
narm2/
├── manage.py                  # Django entry point
├── honey-html/                # Frontend assets (HTML, CSS, JS, fonts)
│   ├── *.html                 # Pages like index, about, contact, shop
│   ├── css/                   # Styling files including Bootstrap
│   ├── js/                    # JavaScript (bootstrap.js, custom.js, jquery.js)
│   ├── fonts/                 # FontAwesome and others
│   └── images/                # Product and page images (if any)
├── yourprojectname/           # Django project config (settings, urls)
└── shop/                      # Django app for models, views, templates
```

---

## 🚀 Features

- Static pages: Home, About Us, Contact, Shop, Product Quality
- Responsive layout using Bootstrap
- Custom interactivity using `custom.js`
- Enhanced UI elements via `jQuery` and Bootstrap JS
- Django backend integration ready
- SQLite default database for development

---

## 🧠 How It Works

### 🔙 Backend (Django)
- Views and URLs serve templates or data
- Models define database schema
- Admin panel available for managing content

### 🖼️ Frontend (HTML + Bootstrap + JS)
- HTML templates in `honey-html/`
- CSS styling with `bootstrap.min.css`
- JS interaction via:
  - `bootstrap.min.js` – modal, dropdown, etc.
  - `jquery.min.js` – DOM manipulation
  - `custom.js` – project-specific scripts

---

## 🔧 How to Run the Project

### 🔹 Prerequisites
- Python 3.10+
- `pip` installed

### 🔹 Setup Instructions

```bash
git clone https://github.com/mohammadsadeg24/Software-engineering.git
cd Software-engineering/narm2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

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
