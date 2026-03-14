# std
from contextlib import asynccontextmanager
from pathlib import Path

# third party
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import Response

# local
from app.api.router import api_router
from app.core.handlers import register_exception_handlers
from app.db.session import engine


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("Starting app ...")
    yield
    print("Closing database connections ...")
    engine.dispose()


app = FastAPI(
    title="Expense Manager API",
    description="API for managing personal expenses with statistics, charts and export features.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok"}


register_exception_handlers(app)

app.include_router(api_router)

