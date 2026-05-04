from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions.error_handlers import setup_exception_handlers

app = FastAPI(
    title="Auction Platform API",
    description="API for managing auctions, bids, and users in an auction platform.",
    version="1.0.0",
)

setup_exception_handlers(app)

@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})


