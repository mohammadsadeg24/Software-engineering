import os
from pathlib import Path
from urllib.parse import urlparse
from decouple import config
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
# DEBUG = config('DEBUG', default=False, cast=bool)  # Set to False for production
DEBUG = True  # Set to False for production
# Add your server's domain/IP and any domains that will access your API
ALLOWED_HOSTS = [
    '0.0.0.0', 
    'localhost', 
    '127.0.0.1',
    '0.0.0.0',  # Your server IP
    'yourdomain.com',  # Add your domain if you have one
    'www.yourdomain.com'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core', 
    'honey_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'honey_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'honey_site.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# MongoDB
MONGODB_SETTINGS = {
    "host": os.getenv("MONGODB_HOST", "mongodb://localhost:27017"),
    "db": os.getenv("MONGODB_DB", "honey_site"),
}

# CORS Settings - Fixed the typo and made more secure
CORS_ALLOW_CREDENTIALS = True

# For development - allows all origins (less secure)
# CORS_ALLOW_ALL_ORIGINS = True

# For production - specify exact origins that should access your API
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vue dev server
    "https://yourdomain.com",  # Your production frontend
    "https://www.yourdomain.com",
    f"http://65.109.218.152:8000",  # Your server
    f"https://65.109.218.152:8000",
]


# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'  # Where collectstatic puts files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Static files finders (optional - Django uses these by default)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'django.contrib.auth.backends.ModelBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'