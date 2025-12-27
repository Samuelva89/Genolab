from celery import Celery
from .core.config import settings

celery_app = Celery(
    'genolab',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(task_track_started=True)

celery_app.autodiscover_tasks(['app'])