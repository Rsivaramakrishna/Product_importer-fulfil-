from celery import Celery
from .config import settings

celery_app = Celery(
    "product_importer",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}
