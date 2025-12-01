from celery import Celery
from .core.config import settings

celery_app = Celery(
    'genolab',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(task_track_started=True)

celery_app.autodiscover_tasks(['app'])