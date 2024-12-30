import datetime

from pydantic import BaseModel
from fastapi import FastAPI


app = FastAPI()


class ExpenseCreateDTO(BaseModel):
    name: str
    category: str
    price: int


class ExpenseDTO(BaseModel):
    id: int
    name: str
    category: str
    price: int
    datetime: datetime.datetime

    class Config:
        from_attributes = True


class Expense:

    def __init__(self, id: int, expense: str, category: str, price: int):
        self.id = id
        self.name = expense
        self.category = category
        self.price = price
        self.datetime = datetime.datetime.now()


EXPENSES = [
    Expense(1, "vegetables", "food", 40),
    Expense(2, "fruit", "food", 30),
    Expense(3, "phone", "fees", 70),
    Expense(4, "internet", "food", 200),
    Expense(5, "clothes", "shopping", 500)
]


@app.get("/expenses/", response_model=list[ExpenseDTO])
def read_expense_endpoint():
    return EXPENSES

@app.post("/expenses/", response_model=ExpenseDTO)
def create_expense_endpoint(dto: ExpenseCreateDTO):
    print(dto)

    # mock dodawanie do bazy danych
    expense = Expense(
        id=len(EXPENSES) + 1,
        expense=dto.name,
        category=dto.category,
        price=dto.price
    )
    EXPENSES.append(expense)

    # output
    dto = ExpenseDTO.from_orm(expense)
    return dto
