import unittest

from sqlalchemy import select

from src.database.models import User
from src.repository.users import (
    confirmed_email,
    create_user,
    get_user_by_email,
    update_token,
    update_avatar,
)
from src.schemas.users import UserModel
from tests.conftest import base_session

db_user = UserModel(
    username="metalhead",
    email="metalhead@example.com",
    password="123456789",
)


def populate_db(user, db):
    user = User(**user.model_dump())
    db.add(user)
    db.commit()


class TestUsersRepo(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_user = UserModel(
            username="metalhead",
            email="metalhead@example.com",
            password="123456789",
        )
        self.db = next(base_session())
        self.gravar_url_prefix = "https://www.gravatar.com/avatar/"
        populate_db(self.db_user, self.db)

    async def test_create_user(self):
        test_user = UserModel(
            username="superman",
            email="superman@example.com",
            password="999999990",
        )

        user = await create_user(test_user, self.db)
        self.assertIsInstance(user, User)
        self.assertTrue(hasattr(user, "id"))
        self.assertEqual(user.username, test_user.username)
        self.assertEqual(user.email, test_user.email)
        self.assertEqual(user.password, test_user.password)
        self.assertTrue(user.created_at)
        self.assertFalse(user.confirmed)
        self.assertTrue(user.avatar.startswith(self.gravar_url_prefix))
        self.assertIsNone(user.refresh_token)

    async def test_get_user_by_email(self):
        user = await get_user_by_email(
            self.db_user.email,
            self.db,
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.db_user.username)
        self.assertEqual(user.email, self.db_user.email)
        self.assertEqual(user.password, self.db_user.password)

    async def test_get_user_by_email_wrong(self):
        wrong_email = "wrong_email"
        user = await get_user_by_email(
            wrong_email,
            self.db,
        )
        self.assertIsNone(user)

    async def test_update_token(self):
        test_token = "new token"
        user = self.db.execute(
            select(User).filter(User.email == self.db_user.email)
        ).scalar_one()
        await update_token(user, test_token, self.db)
        self.db.refresh(user)
        self.assertEqual(user.refresh_token, test_token)

    async def test_confirmed_email(self):
        user = self.db.execute(
            select(User).filter(User.email == self.db_user.email)
        ).scalar_one()
        await confirmed_email(user.email, self.db)
        self.db.refresh(user)
        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        test_avatar = "new avatar"
        user = self.db.execute(
            select(User).filter(User.email == self.db_user.email)
        ).scalar_one()
        await update_avatar(user.email, test_avatar, self.db)
        self.db.refresh(user)
        self.assertEqual(user.avatar, test_avatar)
