from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///new.sqlite"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


def get_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()

