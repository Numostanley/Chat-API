from apscheduler.schedulers.background import BackgroundScheduler

from ..authentication import schedulers as authentication_schedulers


def schedule():
    """
    register all scheduled job
    """
    try:
        scheduler = BackgroundScheduler(job_defaults={'max_instances': 3})
        scheduler.add_job(authentication_schedulers.delete_used_refresh_tokens_scheduler, 'interval', hours=3)
        scheduler.add_job(authentication_schedulers.delete_used_password_reset_tokens_scheduler, 'interval', minutes=3)
        scheduler.start()
    except Exception:  # noqa
        pass
