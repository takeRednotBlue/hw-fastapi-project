from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    statement = select(User).filter(User.email == email)
    return db.execute(statement).scalar_one_or_none()


async def create_user(body: UserModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image(default="robohash")
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, src_url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = src_url
    db.commit()
    return user
