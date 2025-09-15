import os
from celery import Celery

# Configura el módulo settings por defecto de Django para el programa 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compushop.settings')
app = Celery('compushop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
