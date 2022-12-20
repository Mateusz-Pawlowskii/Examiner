import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now as timezone_now
from dateutil.relativedelta import relativedelta

from exam.models import Platform
from exam.functions import send_warning_mail


scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
def delete_inactive():
    now = timezone_now()
    platform_admins = User.objects.filter(groups=3)
    for admin in platform_admins:
        platform = Platform.objects.get(users=admin)
        if relativedelta(now, admin.last_login).months > 11 and not platform.inactive:
            platform.inactive = True
            platform.save()
            send_warning_mail(admin, platform)
        if relativedelta(now, admin.last_login).months > 12:
            User.objects.filter(platform=platform).delete()
            platform.delete()
        
def start():
    # if settings.DEBUG:
    #     logging.basicConfig()
    #     logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    scheduler.add_job(delete_inactive, 'cron', hour=0, name='clean_accounts', jobstore='default' , replace_existing=True)
    register_events(scheduler)
    scheduler.start()