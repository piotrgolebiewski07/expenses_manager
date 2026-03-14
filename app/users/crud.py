# third party
from sqlalchemy.orm import Session

# local
from app.core.exception import UserAlreadyExistsException
from app.core.security import hash_password
from app.models.models import User
from app.schemas.schemas import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise UserAlreadyExistsException()

    hashed_pw = hash_password(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

