from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.expenses.models import Base


DATABASE_URL = "sqlite:///new.sqlite"


#Tworzenie silnika bazy danych
engine = create_engine(DATABASE_URL, echo=True)


# Konfiguracja sesji
Session = sessionmaker(bind=engine)


# Funkcja pomocnicza zarządzająca tworzeniem i zamykaniem sesji bazy danych
def get_session():
    db = Session()
    try:
        return db
    finally:
        db.close()


# Tworzenie tabel w bazie danych
Base.metadata.create_all(bind=engine)

