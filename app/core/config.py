from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str
    REFRESH_TOKEN_EXPIRE_DAYS: int
    CORS_ORIGINS: str = "http://localhost:5173"
    LOG_FORMAT: str = "text"
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "development"
    EMAIL_PROVIDER: str = "mailpit"  # "mailpit" | "resend" | "console" (no-op, used in tests)
    EMAIL_FROM: str = "no-reply@auction-platform.local"
    MAILPIT_SMTP_HOST: str = "mailpit"
    MAILPIT_SMTP_PORT: int = 1025
    RESEND_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() #type: ignore
