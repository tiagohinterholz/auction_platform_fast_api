from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings


def setup_tracing(app: FastAPI, service_name: str = "auction-platform-api") -> None:
    # Same escape hatch as setup_sentry(): no-op when unset, so the app
    # still runs (and the test suite, which forces this empty in
    # conftest.py, never tries to resolve "jaeger" as a real hostname).
    if not settings.OTEL_EXPORTER_ENDPOINT:
        return

    # Resource: "who am I" — service_name is what shows up in Jaeger's
    # Service dropdown. The worker will call this too, later, with its own
    # service_name ("auction-platform-worker"), so a trace crossing both
    # processes is visually distinguishable span by span.
    resource = Resource.create({SERVICE_NAME: service_name})

    # TracerProvider: the per-process factory that creates every span.
    provider = TracerProvider(resource=resource)

    # Where finished spans get sent. insecure=True: plain gRPC, no TLS,
    # talking to Jaeger over the Docker network.
    exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_ENDPOINT, insecure=True)

    # BatchSpanProcessor: buffers spans and ships them in batches instead
    # of one network call per span.
    provider.add_span_processor(BatchSpanProcessor(exporter))

    # Registers this provider as *the* one the whole process uses —
    # anything that calls opentelemetry.trace.get_tracer(...) from now on
    # (including the auto-instrumentation below) uses it.
    trace.set_tracer_provider(provider)

    # The actual "automatic" part: patches `app` so every request gets its
    # own span, with no manual span code needed in any route.
    FastAPIInstrumentor.instrument_app(app)
