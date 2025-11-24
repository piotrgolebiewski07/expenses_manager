from fastapi import HTTPException


def raise_not_found():
    raise HTTPException(status_code=404, detail="Expense not found")


def raise_bad_request():
    raise HTTPException(status_code=400, detail="Invalid request")


def raise_server_error():
    raise HTTPException(status_code=500, detail="Internal server error")


def raise_calculating_statistics():
    raise HTTPException(status_code=500, detail="Error calculating statistics")


def raise_generating_visualization():
    raise HTTPException(status_code=500, detail="Error generating visualization")

