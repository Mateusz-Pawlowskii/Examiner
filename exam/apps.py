from django.apps import AppConfig
from django.conf import settings

class ExamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exam'
    # def ready(self):
    #     from .scheduler import scheduler
    #     if settings.SCHEDULER_AUTOSTART:
    #     	scheduler.start()