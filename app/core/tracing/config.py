from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings

_tracing_configured = False


def setup_tracing(service_name: str, app: FastAPI | None = None) -> None:
    """Call once per process, as early as possible:
    - API (main.py): setup_tracing("auction-platform-api", app)
    - worker (celery_app.py): setup_tracing("auction-platform-worker")
      — no `app`, there's no FastAPI object in that process.

    `service_name` is what shows up in Jaeger's Service dropdown — having
    two different names is how a trace crossing both processes is
    visually distinguishable span by span.
    """
    global _tracing_configured

    if not settings.OTEL_EXPORTER_ENDPOINT:
        return

    # uvicorn --reload's supervisor ends up re-importing main.py more than
    # once in the same process, which would otherwise call this twice (the
    # SDK logs "Overriding of current TracerProvider is not allowed" +
    # "Attempting to instrument while already instrumented" — harmless but
    # noisy, and a second TracerProvider()/exporter would be wasted work).
    # Unlike sentry_sdk.init(), OTel's instrumentors aren't safe to call
    # twice without complaining, so this needs its own explicit guard.
    if _tracing_configured:
        return
    _tracing_configured = True

    resource = Resource.create({SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    if app is not None:
        FastAPIInstrumentor.instrument_app(app)

    # SQLAlchemy/Redis: automatic child spans for every query/command,
    # nested under whatever span is currently active — no engine/client
    # argument needed, this hooks SQLAlchemy's/redis-py's own event system
    # process-wide.
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()

    # Celery already knows how to carry trace context through its own
    # task headers (Redis broker) — instrumenting both the side that calls
    # .apply_async() (the API, inside AuctionScheduledHandler) and the
    # side that executes the task (the worker) connects "schedule" and
    # "run the task" into ONE trace automatically. This does NOT cover
    # RabbitMQEventBus — that's a separate transport or own, with no such
    # automatic support (see the manual propagation in rabbitmq_event_bus.py).
    CeleryInstrumentor().instrument()
