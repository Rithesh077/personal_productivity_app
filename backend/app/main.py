"""stride backend — FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.database import init_db
from app.routes import goals, tasks, analytics, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    """initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="Stride",
    description="Plan. Execute. Improve.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goals.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(tags.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
