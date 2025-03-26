from celery import Celery
from core.config import settings

borad_celery = Celery(
    "board_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

borad_celery.autodiscover_tasks(["celery_task.tasks"])
