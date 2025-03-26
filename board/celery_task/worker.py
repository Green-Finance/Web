from celery import Celery
from core.config import settings

board_celery = Celery(
    "board_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

board_celery.autodiscover_tasks(["celery_task.tasks"])
