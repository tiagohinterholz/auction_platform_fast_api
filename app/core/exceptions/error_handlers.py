from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.exceptions import DomainException


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(DomainException)
    async def global_domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message, "error_type": exc.__class__.__name__},
        )
