from fastapi import FastAPI
from app.expenses.routers import router as expenses_router
from app.expenses.database import engine


async def lifespan(app: FastAPI):
    print("Starting app ...")
    yield
    print("Closing database connections ...")
    engine.dispose()

app = FastAPI(
    title="Expense Manager API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(expenses_router)

