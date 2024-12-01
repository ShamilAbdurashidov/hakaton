import os

from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = 'dj356tngo-mj-098023dregfe879fugohb(567fyt5dc(cr0#903t4fd2$bab6h'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'MonitoringConstructionSites',
        'USER': 'postgres',
        'PASSWORD': '!ShamiL19',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'storage', 'cache'),
        'TIMEOUT': 60,
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'storage', 'static')

# Генератор PDF
WKHTMLTOPDF = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
#WKHTMLTOPDF = '/usr/local/bin/wkhtmltopdf'