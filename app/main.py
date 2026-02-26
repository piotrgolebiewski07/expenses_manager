# std
from contextlib import asynccontextmanager
from pathlib import Path

# third party
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError

# local
from app.api.expenses import router as expenses_router
from app.db.session import engine
from app.models.models import Base
from app.api.auth import router as auth_router
from app.core.exception import (ExpenseNotFoundException,
                                NoExpensesFoundException,
                                DatabaseException,
                                InvalidMonthException,
                                CategoryNotFoundException,
                                UserAlreadyExistsException
                                )


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


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


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok"}


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


@app.exception_handler(CategoryNotFoundException)
async def category_not_found_handler(request: Request, exc: CategoryNotFoundException):
    return JSONResponse(
        status_code=400,
        content={"detail": "Category not found"}
    )


@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    return JSONResponse(
        status_code=409,
        content={"detail": "User already exists"}
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    formatted_errors = []

    for err in errors:
        loc = err.get("loc", []) or []
        field = loc[-1] if loc else None

        ctx = err.get("ctx") or {}
        if ctx and "error" in ctx:
            message = str(ctx["error"])
        else:
            message = err.get("msg", "Invalid value")

        formatted_errors.append({
            "message": message,
            "field": field
        })

    return JSONResponse(
        status_code=422,
        content={"errors": formatted_errors}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "errors" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"errors": [{"message": str(exc.detail), "field": None}]},
    )


app.include_router(expenses_router)
app.include_router(auth_router)

