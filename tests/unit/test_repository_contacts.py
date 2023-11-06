import unittest
from datetime import datetime, timedelta

from sqlalchemy import select

from src.database.models import Contact, User
from src.repository.contacts import (
    create_contact,
    delete_contact,
    get_contact,
    get_contact_by_email,
    get_contact_by_first_name,
    get_contact_by_last_name,
    get_contacts,
    get_contacts_by_birthday,
    update_contact,
)
from src.schemas.contacts import ContactModel
from tests.conftest import base_session

fake_contacts = [
    ContactModel(
        first_name="John",
        last_name="Wick",
        phone="+380930644885",
        email="my@dog.com",
        birthday=datetime.strftime(
            datetime.replace(datetime.now() - timedelta(days=8), year=1991),
            "%Y-%m-%d",
        ),  # Birthday is 8 days for testing get_contacts_by_birthday() func
    ),
    ContactModel(
        first_name="Mat",
        last_name="Dou",
        phone="+380930004885",
        email="programming@life.com",
        birthday=datetime.strftime(
            datetime.replace(datetime.now() - timedelta(days=10), year=1970),
            "%Y-%m-%d",
        ),  # Birthday is in 10 days for testing get_contacts_by_birthday()  func
    ),
]


def populate_db(db, user):
    for contact in fake_contacts:
        contact = Contact(**contact.model_dump())
        contact.user_id = user.id
        db.add(contact)
    db.commit()


# @pytest.mark.usefixtures("db")
class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = next(base_session())
        self.user = User(id=1)
        self.contact = ContactModel(
            first_name="Maksym",
            last_name="Klym",
            phone="+380936644885",
            email="test@example.com",
            birthday="1990-10-01",
        )
        populate_db(self.db, self.user)

    async def test_get_contacts_empty(self):
        user_no_contacts = User(id=2)
        result = await get_contacts(
            skip=0, limit=10, user=user_no_contacts, db=self.db
        )
        self.assertIsNone(result)

    async def test_create_contact(self):
        result = await create_contact(
            body=self.contact, user=self.user, db=self.db
        )
        self.assertTrue(result.id)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, self.contact.first_name)

    async def test_get_contact(self):
        test_contact_id = 1
        result = await get_contact(
            contact_id=test_contact_id, user=self.user, db=self.db
        )
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.user_id, self.user.id)

    async def test_get_contact_wrong(self):
        test_contact_id = 5
        result = await get_contact(
            contact_id=test_contact_id, user=self.user, db=self.db
        )
        self.assertIsNone(result)

    async def test_get_contact_by_first_name(self):
        result = await get_contact_by_first_name(
            first_name="John", user=self.user, db=self.db
        )
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.user_id, self.user.id)

    async def test_get_contact_by_first_name_wrong(self):
        wrong_first_name = "Wrong name"
        result = await get_contact_by_first_name(
            first_name=wrong_first_name, user=self.user, db=self.db
        )
        self.assertIsNone(result)

    async def test_get_contact_by_last_name(self):
        test_last_name = "Wick"
        result = await get_contact_by_last_name(
            last_name=test_last_name, user=self.user, db=self.db
        )
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.last_name, test_last_name)
        self.assertEqual(result.user_id, self.user.id)

    async def test_get_contact_by_last_name_wrong(self):
        wrong_last_name = "Wrong last name"
        result = await get_contact_by_last_name(
            last_name=wrong_last_name, user=self.user, db=self.db
        )
        self.assertIsNone(result)

    async def test_get_contact_by_email(self):
        test_email = "my@dog.com"
        result = await get_contact_by_email(
            email=test_email, user=self.user, db=self.db
        )
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.email, test_email)
        self.assertEqual(result.user_id, self.user.id)

    async def test_get_contact_by_email_wrong(self):
        wrong_email = "Wrong email"
        result = await get_contact_by_email(
            email=wrong_email, user=self.user, db=self.db
        )
        self.assertIsNone(result)

    async def test_get_contacts_by_birthday(self):
        test_interval = 10
        result = await get_contacts_by_birthday(
            interval=test_interval, user=self.user, db=self.db
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    async def test_get_contacts_by_birthday_no_birhdays(self):
        test_interval = 5
        result = await get_contacts_by_birthday(
            interval=test_interval, user=self.user, db=self.db
        )
        self.assertIsNone(result)

    async def test_update_contact(self):
        test_contact_id = 1
        result = await update_contact(
            body=self.contact,
            contact_id=test_contact_id,
            user=self.user,
            db=self.db,
        )
        self.assertEqual(result.first_name, self.contact.first_name)
        self.assertEqual(result.last_name, self.contact.last_name)
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.id, test_contact_id)
        self.assertEqual(result.email, self.contact.email)
        self.assertEqual(result.birthday, self.contact.birthday)
        self.assertEqual(result.phone, self.contact.phone)
        self.assertIsInstance(result, Contact)

    async def test_update_contact_wrong(self):
        test_contact_id = 5
        result = await update_contact(
            body=self.contact,
            contact_id=test_contact_id,
            user=self.user,
            db=self.db,
        )
        self.assertIsNone(result)

    async def test_delete_contact(self):
        test_contact_id = 1
        result = await delete_contact(
            contact_id=test_contact_id, user=self.user, db=self.db
        )
        check_delete = self.db.execute(
            select(Contact).filter(Contact.id == test_contact_id)
        ).scalar_one_or_none()
        self.assertEqual(result.id, test_contact_id)
        self.assertIsNone(check_delete)

    async def test_delete_contact_wrong(self):
        test_contact_id = 25
        result = await delete_contact(
            contact_id=test_contact_id, user=self.user, db=self.db
        )
        self.assertIsNone(result)
