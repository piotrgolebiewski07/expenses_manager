import datetime

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi import status

app = FastAPI()


class ExpenseCreateDTO(BaseModel):
    name: str
    category: str
    price: int
    

class ExpenseUpdateDTO(BaseModel):
    name: str | None = None
    category: str | None = None 
    price: int | None = None 


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

    # business logic here
    expenses = EXPENSES

    return expenses


@app.post("/expenses/")
def create_expense_endpoint(dto: ExpenseCreateDTO):

    # business logic here
    expense = Expense(
        id=len(EXPENSES) + 1,
        expense=dto.name,
        category=dto.category,
        price=dto.price
    )
    EXPENSES.append(expense)

    return expense


@app.put("/expenses/{id}", response_model=ExpenseDTO)
def update_expense(id: int, dto: ExpenseUpdateDTO):

    # validation
    if not any(expense.id == id for expense in EXPENSES):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found"
        )

    # business logic here
    for i in range(len(EXPENSES)):
        if EXPENSES[i].id == id:

            expense = EXPENSES[i]

            if dto.name:
                expense.name = dto.name
            if dto.category:
                expense.category = dto.category
            if dto.price:
                expense.price = dto.price

            EXPENSES[i] = expense
            
            return expense



@app.delete("/expenses/{id}")
def delete_expense(id: int):

    # business logic here
    for i in range(len(EXPENSES)):
        if EXPENSES[i].id == id:
            del EXPENSES[i]
            break
