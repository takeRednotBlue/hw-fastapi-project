from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repo_contacts
from src.schemas.contacts import ContactModel, ResponseContact
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts')

RequestLimiter = Depends(RateLimiter(times=10, seconds=60))


@router.get('/')
async def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        first_name: str = None, last_name: str = None, email: str = None,
                        current_user: User = Depends(
                            auth_service.get_current_user)
                        ) -> list[ResponseContact] | ResponseContact:
    """
    The list_contacts function returns a list of contacts.

    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter the contacts by last name
    :param email: str: Get the contact by email
    :param current_user: User: Get the user who is making the request
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repo_contacts.get_contacts(skip, limit, current_user, db)

    if first_name:
        contacts = await repo_contacts.get_contact_by_first_name(first_name, current_user, db)
    elif last_name:
        contacts = await repo_contacts.get_contact_by_last_name(last_name, current_user, db)
    elif email:
        contacts = await repo_contacts.get_contact_by_email(email, current_user, db)

    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no contacts")

    return contacts


@router.post('/', response_model=ResponseContact, dependencies=[RequestLimiter])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.create_contact(body, current_user, db)
    return contact


@router.get('/birthday', response_model=list[ResponseContact])
async def get_birthday(interval: int = 7, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repo_contacts.get_contacts_by_birthday(interval, current_user, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"In the next {interval} days there are no birthdays.")
    return contacts


@router.get('/{contact_id}', response_model=ResponseContact)
async def get_contact(contact_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.get_contact(contact_id, current_user, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


@router.put('/{contact_id}', response_model=ResponseContact, dependencies=[RequestLimiter])
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    new_contact = await repo_contacts.update_contact(body, contact_id, current_user, db)
    if not new_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return new_contact


@router.delete('/{contact_id}', response_model=ResponseContact, dependencies=[RequestLimiter])
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.delete_contact(contact_id, current_user, db)
    return contact
