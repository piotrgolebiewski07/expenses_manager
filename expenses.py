from fastapi import FastAPI, Body
import datetime

app = FastAPI()


class Expense:

    def __init__(self, id_expense: int, expense: str, category: str, price: int, datetime):
        self.id_expense = id_expense
        self.expense = expense
        self.category = category
        self.price = price
        self.datetime = datetime.datetime.now()

EXPENSES = [
    Expense(1, "vegetables","food",40, datetime),
    Expense(2, "fruit","food",30, datetime),
    Expense(3, "phone","fees",70, datetime),
    Expense(4, "internet","food",200, datetime),
    Expense(5, "clothes","shopping",500, datetime)
]


@app.get("/expenses")
def read_all_expenses():
    return EXPENSES

@app.post("/expenses/create-expense")
def create_expense(expense_request=Body()):
    EXPENSES.append(expense_request)
