from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.expenses.routers import router as expenses_router
from app.expenses.database import engine
from app.expenses.models import Base

from app.core.exception import ExpenseNotFoundException, NoExpensesFoundException, DatabaseException, \
    InvalidMonthException


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Starting app ...")
    yield
    print("Closing database connections ...")
    engine.dispose()


app = FastAPI(
    title="Expense Manager API",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(ExpenseNotFoundException)
async def expense_not_found_handler(request: Request, exc: ExpenseNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Expense not found"}
    )


@app.exception_handler(NoExpensesFoundException)
async def no_expenses_found_handler(request: Request, exc: NoExpensesFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "No expenses found"}
    )


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error"}
    )


@app.exception_handler(InvalidMonthException)
async def invalid_month_handler(request: Request, exc: InvalidMonthException):
    return JSONResponse(
        status_code=400,
        content={"detail": "Month must be between 1 and 12"}

    )
app.include_router(expenses_router)

