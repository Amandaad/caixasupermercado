from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db import Base, SessionLocal, engine
from app import models  # noqa: F401 - registers SQLAlchemy models
from app.seed import ensure_admin
from app.routers import auth, products

@asynccontextmanager
async def lifespan(_: FastAPI):
    # MVP bootstrap. For production deployments, replace create_all with Alembic migrations.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_admin(db)
    yield

app = FastAPI(title="Super AS API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router)
app.include_router(products.router)

@app.get("/health", tags=["Saúde"])
def health():
    return {"status": "ok", "service": "super-as-api"}

@app.get("/", tags=["Informações"])
def root():
    return {"name": "Super AS API", "docs": "/docs", "version": "0.1.0"}
