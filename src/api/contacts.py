from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repo_contacts
from src.schemas.contacts import ContactModel, ResponseContact
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts")

RequestLimiter = Depends(RateLimiter(times=10, seconds=60))


@router.get("/")
async def list_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    current_user: User = Depends(auth_service.get_current_user),
) -> list[ResponseContact] | ResponseContact:
    """
    Retrieves a list of contacts from the database.

    :param skip: The number of contacts to skip. Defaults to 0.
    :type skip: int
    :param limit: The maximum number of contacts to retrieve. Defaults to 100.
    :type limit: int
    :param db: The database session. Defaults to the result of the `get_db` function.
    :type db: Session
    :param first_name: The first name of the contacts to retrieve. Defaults to None.
    :type first_name: str
    :param last_name: The last name of the contacts to retrieve. Defaults to None.
    :type last_name: str
    :param email: The email of the contacts to retrieve. Defaults to None.
    :type email: str
    :param current_user: The current authenticated user. Defaults to the result of the `get_current_user` function.
    :type current_user: User

    :return: The list of contacts retrieved from the database.
    :rtype: list[ResponseContact] | ResponseContact

    :raises HTTPException: If there are no contacts in the database.
    """
    contacts = await repo_contacts.get_contacts(skip, limit, current_user, db)

    if first_name:
        contacts = await repo_contacts.get_contact_by_first_name(
            first_name, current_user, db
        )
    elif last_name:
        contacts = await repo_contacts.get_contact_by_last_name(
            last_name, current_user, db
        )
    elif email:
        contacts = await repo_contacts.get_contact_by_email(
            email, current_user, db
        )

    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no contacts",
        )

    return contacts


@router.post(
    "/",
    response_model=ResponseContact,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequestLimiter],
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Creates a new contact.

    :param body: The contact data to be created.
    :type body: ContactModel
    :param db: The database session. Defaults to Depends(get_db).
    :type db: Session, optional
    :param current_user: The current user. Defaults to Depends(auth_service.get_current_user).
    :type current_user: User, optional

    :return: The created contact.
    :rtype: Contact

    :raises: None
    """
    contact = await repo_contacts.create_contact(body, current_user, db)
    return contact


@router.get("/birthday", response_model=list[ResponseContact])
async def get_birthday(
    interval: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Get a list of contacts with birthdays within the next `interval` days.

    :param interval: The number of days to consider for birthdays. Defaults to 7.
    :type interval: int
    :param db: The database session. Defaults to the result of `get_db` dependency.
    :type db: Session
    :param current_user: The current authenticated user. Defaults to the result of `auth_service.get_current_user` dependency.
    :type current_user: User

    :return: A list of `ResponseContact` objects representing the contacts with birthdays within the next `interval` days.
    :rtype: list[ResponseContact]

    :raises HTTPException: If there are no contacts with birthdays within the next `interval` days.
    """
    contacts = await repo_contacts.get_contacts_by_birthday(
        interval, current_user, db
    )
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"In the next {interval} days there are no birthdays.",
        )
    return contacts


@router.get("/{contact_id}", response_model=ResponseContact)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a contact from the database based on the provided contact ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session to use for the query. Defaults to Depends(get_db).
    :type db: Session, optional
    :param current_user: The current user making the request. Defaults to Depends(auth_service.get_current_user).
    :type current_user: User, optional

    :return: The retrieved contact.
    :rtype: ResponseContact

    :raises HTTPException: If the contact is not found.
    """
    contact = await repo_contacts.get_contact(contact_id, current_user, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put(
    "/{contact_id}",
    response_model=ResponseContact,
    dependencies=[RequestLimiter],
)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Update a contact by its ID.

    :param body: The updated contact information.
    :type body: ContactModel
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User

    :return: The updated contact.
    :rtype: ResponseContact

    :raises HTTPException: If the contact is not found.
    """
    new_contact = await repo_contacts.update_contact(
        body, contact_id, current_user, db
    )
    if not new_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return new_contact


@router.delete(
    "/{contact_id}",
    response_model=ResponseContact,
    dependencies=[RequestLimiter],
)
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Deletes a contact from the database.

    :param contact_id: The ID of the contact to be deleted.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current user.
    :type current_user: User

    :return: The deleted contact.
    :rtype: Contact
    """
    contact = await repo_contacts.delete_contact(contact_id, current_user, db)
    return contact
