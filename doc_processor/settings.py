# ⚙️ Django Settings for doc_processor project

from __future__ import annotations

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# 📂 Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 📄 Load environment variables
load_dotenv()


# 🚨 Security Settings
# 🔑 Secret Key (WARNING: Keep it secret in production!)
SECRET_KEY = "django-insecure-8l95lvwf-*hwi$m)fuewco14z)_9=@z_-*i_3%-i)d(tibg8f+"

# 🐞 Debug Mode (WARNING: Disable in production!)
DEBUG = True

# 🌐 Allowed Hosts
ALLOWED_HOSTS = ['*']  # Use specific domains in production


# 📦 Installed Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 🌐 API Framework
    'rest_framework',
    'drf_yasg',
    # 📝 Custom Apps
    'documents',
    'api',
]


# 🛡️ Middleware Stack
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# 🔗 URL Configuration
ROOT_URLCONF = "doc_processor.urls"


# 🛠️ Templates Configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Specify template directories here if needed
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# 🚪 WSGI Entry Point
WSGI_APPLICATION = "doc_processor.wsgi.application"


# 🗄️ Database Configuration
# For development: SQLite (consider using PostgreSQL/MySQL in production)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# 🔒 Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# 🛠️ Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


# 🌍 Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# 🖼️ Static Files Configuration
STATIC_URL = "static/"


# 🗝️ Default Primary Key Field Type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



