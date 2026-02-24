import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../app/db
BASE_DIR = os.path.dirname(BASE_DIR)                  # .../app
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'new.sqlite')}"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


def get_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()

