from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions.exceptions import DomainException

UNIQUE_CONSTRAINT_MESSAGES: dict[str, str] = {
    "users_cpf_key": "CPF já cadastrado.",
    "users_email_key": "E-mail já cadastrado.",
}
DEFAULT_CONFLICT_MESSAGE = "Registro já existe (violação de unicidade)."


def _constraint_name(exc: IntegrityError) -> str | None:
    """Best-effort extraction of the violated constraint name.

    SQLAlchemy's asyncpg dialect wraps the raw driver error in
    ``AsyncAdapt_asyncpg_dbapi.IntegrityError``, which doesn't expose
    ``constraint_name`` itself — the real asyncpg exception (which does)
    is chained as ``__cause__``.
    """
    for candidate in (exc.orig, getattr(exc.orig, "__cause__", None)):
        constraint_name = getattr(candidate, "constraint_name", None)
        if constraint_name:
            return constraint_name
    return None


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(DomainException)
    async def global_domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "error_type": exc.__class__.__name__},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        constraint_name = _constraint_name(exc)
        message = (
            UNIQUE_CONSTRAINT_MESSAGES.get(constraint_name, DEFAULT_CONFLICT_MESSAGE)
            if constraint_name
            else DEFAULT_CONFLICT_MESSAGE
        )
        return JSONResponse(
            status_code=409,
            content={"message": message, "error_type": "IntegrityError"},
        )
