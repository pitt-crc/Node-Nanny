"""Tests for the ``MonitorUtility`` class."""

from unittest import TestCase

from sqlalchemy import select

from node_nanny.app import MonitorUtility
from node_nanny.orm import User


class AddUserToWhitelist(TestCase):
    """Test the addition of users to the whitelist"""

    def test_error_on_missing_node(self) -> None:
        """Test for value error on missing node name when global is False"""

        app = MonitorUtility('sqlite:///:memory:')
        with self.assertRaises(ValueError):
            app.add('test_user', node=None, _global=False)

    def test_user_is_whitelisted(self) -> None:
        """Test a whitelist record is created for the user"""

        app = MonitorUtility('sqlite:///:memory:')

        username = 'test_user'
        user_query = select(User).where(User.name == username)
        with app.db.session() as session:
            user_record = session.execute(user_query).scalars().first()
            self.assertIsNone(user_record)

        app.add(username, _global=True)
        with app.db.session() as session:
            user_record = session.execute(user_query).scalars().first()
            self.assertTrue(user_record)
            self.assertTrue(user_record.whitelists)
