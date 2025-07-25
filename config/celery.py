# config/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Load task-related config from Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Explicitly autodiscover tasks from specific apps
app.autodiscover_tasks(['loans', 'customers'])

# Debug task to confirm celery is running
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
