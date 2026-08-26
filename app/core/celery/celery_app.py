from celery import Celery
from celery.signals import worker_process_init

from app.core.config import settings
from app.core.tracing.config import setup_tracing

celery_app = Celery(
    "auction_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.modules.auction.application.tasks.auction_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@worker_process_init.connect
def _setup_worker_tracing(**kwargs) -> None:
    """NOT called just by `import celery_app` — that also happens inside the
    API process (auction_tasks.py needs `celery_app` to call .apply_async()),
    and setup_tracing("auction-platform-worker") running there would mislabel
    every API span as belonging to the worker service (which is exactly what
    happened before this fix: the API process would win the module-import
    race and permanently claim the wrong service name for its own spans).

    `worker_process_init` only fires once a real `celery worker` process is
    booting (in each forked child, for the default prefork pool) — so this
    is the one place worker-only setup belongs.
    """
    setup_tracing("auction-platform-worker")
