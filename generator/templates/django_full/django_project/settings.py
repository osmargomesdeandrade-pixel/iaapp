from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'replace-me'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = []
MIDDLEWARE = []
ROOT_URLCONF = 'django_project.urls'

TEMPLATES = []
WSGI_APPLICATION = 'django_project.wsgi.application'
