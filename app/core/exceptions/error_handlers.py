from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

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


# Every error response shares one envelope - {"message", "error_type"}, plus
# "errors" on validation failures - so clients read a single string field no
# matter which layer rejected the request (domain rule, auth, or body schema).
HTTP_ERROR_TYPES: dict[int, str] = {
    401: "UnauthorizedError",
    403: "ForbiddenError",
    404: "NotFoundError",
    405: "MethodNotAllowedError",
}


def _validation_errors(exc: RequestValidationError) -> list[dict[str, str]]:
    errors = []
    for error in exc.errors():
        # loc is ("body", "field", ...) / ("path", "id") - the location
        # prefix is noise for a client, the field path is what matters.
        field = ".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0])
        message = str(error["msg"]).removeprefix("Value error, ")
        errors.append({"field": field, "message": message})
    return errors


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": str(exc.detail),
                "error_type": HTTP_ERROR_TYPES.get(exc.status_code, "HTTPError"),
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = _validation_errors(exc)
        first = errors[0] if errors else {"field": "", "message": "Invalid request."}
        message = f"{first['field']}: {first['message']}" if first["field"] else first["message"]
        return JSONResponse(
            status_code=422,
            content={
                "message": message,
                "error_type": "ValidationError",
                "errors": errors,
            },
        )

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
