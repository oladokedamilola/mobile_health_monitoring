# health_monitoring/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_monitoring.settings.dev')  # adjust env
app = Celery('health_monitoring')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


from celery.schedules import crontab

app.conf.beat_schedule = {
    "check-health-alerts-every-10min": {
        "task": "notifications.tasks.check_user_health_alerts",
        "schedule": crontab(minute="*/10"),  # every 10 minutes
    },
}
