<<<<<<< HEAD
from fastapi import Body, FastAPI


app = FastAPI()


list_of_expenses = [
    {"id": "1", "expense": "milk", "category": "food", "price": 10},
    {"id": "2", "expense": "bread", "category": "food", "price": 5},
    {"id": "3", "expense": "water", "category": "fees", "price": 150},
    {"id": "4", "expense": "phone", "category": "fees", "price": 20}
    ]


@app.get("/list-of-expenses")
def read_all_expenses():
    return list_of_expenses


@app.get("/list_of_expenses/{expenses_id}")
def read_expenses_category(expenses_id: str):
    for x in list_of_expenses:
        if x.get('id') == expenses_id:
            return x


@app.get("/list_of_expenses/{category}")
def read_category_by_query(category: str):
    expenses = []
    for x in list_of_expenses:
        if x.get("category") == category:
            expenses.append(x)
    return expenses


@app.get("/list_of_expenses/{price}")
def read_price_by_query(price: int):
    list_of_price = []
    for x in list_of_expenses:
        if x.get("price") == price:
            list_of_price.append(x)
    return list_of_price


@app.post("/list_of_expenses/create_expense")
def create_expense(new_expense=Body()):
    list_of_expenses.append(new_expense)


@app.put("/list_of_expenses/update_expense")
def update_expense(updated_expense=Body()):
    for i in range(len(list_of_expenses)):
        if list_of_expenses[i].get("id") == updated_expense.get("id"):
            list_of_expenses[i] = updated_expense


@app.delete("/list_of_expenses/delete_expense/{expense_id}")
def delete_expense(expense_id: str):
    for i in range(len(list_of_expenses)):
        if list_of_expenses[i].get("id") == expense_id:
            list_of_expenses.pop(i)
            break

=======
>>>>>>> origin/main

