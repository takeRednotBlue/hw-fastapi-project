from datetime import datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel, ResponseContact


async def get_contacts(skip: int, limit: int,
                       user: User,  db: Session
                       ) -> list[ResponseContact] | None:
    statement = select(Contact).filter(Contact.user_id ==
                                       user.id).offset(skip).limit(limit)
    return db.execute(statement).scalars().fetchall()


async def get_contact_by_first_name(first_name: str, user: User, db: Session) -> ResponseContact | None:
    statement = (select(Contact).
                 filter(and_(Contact.first_name == first_name.title(),
                             Contact.user_id == user.id)))
    return db.execute(statement).scalar_one_or_none()


async def get_contact_by_last_name(last_name: str, user: User, db: Session) -> ResponseContact | None:
    statement = (select(Contact).
                 filter(and_(Contact.last_name == last_name.title(),
                             Contact.user_id == user.id)))
    return db.execute(statement).scalar_one_or_none()


async def get_contact_by_email(email: str, user: User, db: Session) -> ResponseContact | None:
    statement = (select(Contact).
                 filter(and_(Contact.email == email.lower(),
                             Contact.user_id == user.id)))
    return db.execute(statement).scalar_one_or_none()


async def get_contacts_by_birthday(interval: int, user: User, db: Session) -> list[ResponseContact] | None:
    start_date = datetime.now().date() - timedelta(days=interval)
    statement = select(Contact).filter(Contact.user_id == user.id)
    contacts = db.execute(statement).scalar_one_or_none()
    result = []
    for contact in contacts:
        if start_date <= contact.birthday.replace(year=start_date.year):
            result.append(contact)
    return result


async def create_contact(body: ContactModel, user: User, db: Session) -> ResponseContact:
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def get_contact(contact_id: int, user: User, db: Session) -> ResponseContact | None:
    statement = (select(Contact).
                 filter(and_(Contact.id == contact_id,
                             Contact.user_id == user.id)))
    return db.execute(statement).scalar_one_or_none()


async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session) -> ResponseContact | None:
    statement = (select(Contact).
                 filter(and_(Contact.id == contact_id,
                             Contact.user_id == user.id)))
    contact = db.execute(statement).scalar_one_or_none()
    if not contact:
        return None
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.phone = body.phone
    contact.email = body.email
    contact.birthday = body.birthday
    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, user: User, db: Session) -> ResponseContact | None:
    statement = (select(Contact).
                 filter(and_(Contact.id == contact_id,
                             Contact.user_id == user.id)))
    contact = db.execute(statement).scalar_one_or_none()
    if not contact:
        return None
    db.delete(contact)
    db.commit()
    return contact
