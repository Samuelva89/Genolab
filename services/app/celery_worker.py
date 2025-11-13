from celery import Celery
from .core.config import settings

celery_app = Celery(
    'fungilap',
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(task_track_started=True)

celery_app.autodiscover_tasks(['app'])