import logging
import os

from celery import Celery
from django.conf import settings

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")


# Instantiate Celery object
app = Celery("webapp")

app.config_from_object(settings.CELERY_CONF)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
