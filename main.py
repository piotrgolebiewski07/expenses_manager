from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def frst_api():
    return {"Hello": "World"}
