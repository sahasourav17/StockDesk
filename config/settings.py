import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host]

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users",
    "apps.audit",
    "apps.suppliers",
    "apps.products",
    "apps.stock",
    "apps.sales",
    "apps.finance",
    "apps.reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    DATABASES: dict[str, dict[str, Any]] = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "stock_management"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

UNFOLD = {
    "SITE_TITLE": "StockDesk",
    "SITE_HEADER": "StockDesk",
    "SITE_URL": "/admin/",
    "DASHBOARD_CALLBACK": "apps.reports.dashboard.dashboard_callback",
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Main",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                    {
                        "title": "Low Stock Products",
                        "icon": "inventory_2",
                        "link": "/admin/products/product/?low_stock=1",
                    },
                    {
                        "title": "Users",
                        "icon": "group",
                        "link": "/admin/users/user/",
                    },
                ],
            },
            {
                "title": "Inventory",
                "items": [
                    {
                        "title": "Suppliers",
                        "icon": "local_shipping",
                        "link": "/admin/suppliers/supplier/",
                    },
                    {
                        "title": "Products",
                        "icon": "inventory",
                        "link": "/admin/products/product/",
                    },
                    {
                        "title": "Stock Transactions",
                        "icon": "sync_alt",
                        "link": "/admin/stock/stocktransaction/",
                    },
                    {
                        "title": "Damage Records",
                        "icon": "broken_image",
                        "link": "/admin/stock/damagerecord/",
                    },
                ],
            },
            {
                "title": "Sales & Finance",
                "items": [
                    {
                        "title": "Sales",
                        "icon": "point_of_sale",
                        "link": "/admin/sales/sale/",
                    },
                    {
                        "title": "Due Transactions",
                        "icon": "payments",
                        "link": "/admin/finance/duetransaction/",
                    },
                ],
            },
            {
                "title": "Audit",
                "items": [
                    {
                        "title": "Audit Logs",
                        "icon": "history",
                        "link": "/admin/audit/auditlog/",
                    },
                ],
            }
        ]
    },
}

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
