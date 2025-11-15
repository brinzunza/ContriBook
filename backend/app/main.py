from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db
from .blockchain import blockchain
from .routers import auth, teams, contributions, verifications, reputation, blockchain as blockchain_router, archive
from .utils import ensure_directory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")

    # Initialize database
    init_db()
    print("Database initialized")

    # Initialize blockchain
    blockchain.init_chain()
    print("Blockchain initialized")

    # Ensure storage directories exist
    ensure_directory(settings.STORAGE_PATH)
    ensure_directory(settings.ENCRYPTED_STORAGE_PATH)
    ensure_directory(settings.ARCHIVE_PATH)
    print("Storage directories ready")

    yield

    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Academic and professional contribution tracking system with blockchain verification",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(contributions.router, prefix="/api")
app.include_router(verifications.router, prefix="/api")
app.include_router(reputation.router, prefix="/api")
app.include_router(blockchain_router.router, prefix="/api")
app.include_router(archive.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Verify blockchain integrity
    is_chain_valid = blockchain.verify_chain_integrity()

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "blockchain_valid": is_chain_valid
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
