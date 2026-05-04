from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions.error_handlers import setup_exception_handlers
from app.modules.users.routers.users_router import router as users_router

app = FastAPI(
    title="Auction Platform API",
    description="API for managing auctions, bids, and users in an auction platform.",
    version="1.0.0",
)

app.include_router(users_router, prefix="/api/v1")

setup_exception_handlers(app)


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})
