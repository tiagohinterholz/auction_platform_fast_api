import sentry_sdk

from app.core.config import settings


def setup_sentry() -> None:
    """No-op when SENTRY_DSN isn't set, so the app still runs fine for
    anyone who clones the repo without configuring Sentry.
    """
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        send_default_pii=False,
    )
