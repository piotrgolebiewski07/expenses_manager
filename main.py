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
def read_expenses_endpoint():
    return EXPENSES


@app.post("/expenses/")
def create_expense_endpoint(expense_request: ExpenseCreateDTO):

    expense = Expense(
        id=len(EXPENSES) + 1,
        expense=expense_request.name,
        category=expense_request.category,
        price=expense_request.price
    )

    EXPENSES.append(expense)


@app.put("/expenses/{id}")
def update_expense(expense: ExpenseDTO):
    for i in range(len(EXPENSES)):
        if EXPENSES[i].id == expense.id:
            EXPENSES[i] = expense


@app.delete("/expenses/{id}")
def delete_expense(id: int):
    for i in range(len(EXPENSES)):
        if EXPENSES[i].id == id:
            del EXPENSES[i]
            break
