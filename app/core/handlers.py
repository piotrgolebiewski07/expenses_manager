# third party
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# local
from app.core.exception import (
    CategoryNotFoundException,
    DatabaseException,
    ExpenseNotFoundException,
    InvalidMonthException,
    InvalidYearException,
    NoExpensesFoundException,
    UserAlreadyExistsException,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(ExpenseNotFoundException)
    async def expense_not_found_handler(request: Request, exc: ExpenseNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Expense not found"}
        )

    @app.exception_handler(NoExpensesFoundException)
    async def no_expenses_found_handler(request: Request, exc: NoExpensesFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "No expenses found"}
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error"}
        )

    @app.exception_handler(InvalidMonthException)
    async def invalid_month_handler(request: Request, exc: InvalidMonthException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Month must be between 1 and 12"}
        )

    @app.exception_handler(InvalidYearException)
    async def invalid_year_handler(request: Request, exc: InvalidYearException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Year must be between 2000 and 2100"}
        )

    @app.exception_handler(CategoryNotFoundException)
    async def category_not_found_handler(request: Request, exc: CategoryNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Category not found"}
        )

    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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

