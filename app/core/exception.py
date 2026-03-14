class ExpenseNotFoundException(Exception):
    """Raised when an expense cannot be found."""


class NoExpensesFoundException(Exception):
    """Raised when no expenses exist for the given query."""


class DatabaseException(Exception):
    """Raised when a database operation fails."""


class InvalidMonthException(Exception):
    """Raised when the provided month is outside the range 1–12."""


class InvalidYearException(Exception):
    """Raised when the provided year is outside the allowed range."""


class CategoryNotFoundException(Exception):
    """Raised when the specified category does not exist."""


class UserAlreadyExistsException(Exception):
    """Raised when trying to create a user that already exists."""