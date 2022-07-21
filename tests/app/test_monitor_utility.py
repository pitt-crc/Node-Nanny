"""Tests for the ``MonitorUtility`` class."""

from datetime import timedelta, date
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from sqlalchemy import select

from node_nanny import __file__ as package_file
from node_nanny.app import MonitorUtility
from node_nanny.orm import User, DBConnection, Whitelist, Node


class TestDBConfiguration(TestCase):
    """Test the configuration of the database location at init"""

    def test_default_db_sqlite(self) -> None:
        """Test the database defaults to SQLite in the package directory"""

        app_dir = Path(package_file).resolve().parent / 'monitor.db'

        MonitorUtility()
        self.assertEqual(f'sqlite:///{app_dir}', DBConnection.url)

    def test_custom_db_url(self) -> None:
        """Test the database defaults to SQLite in the package directory"""

        with NamedTemporaryFile(suffix='.db') as temp:
            custom_url = f'sqlite:///{temp.name}'
            MonitorUtility(custom_url)
            self.assertEqual(custom_url, DBConnection.url)


class AddUserToWhitelist(TestCase):
    """Test the addition of users to the whitelist"""

    def test_error_on_missing_node(self) -> None:
        """Test for value error on missing node name when global is False"""

        app = MonitorUtility('sqlite:///:memory:')
        with self.assertRaises(ValueError):
            app.add('test_user', node=None, _global=False)

    def test_new_user_is_whitelisted(self) -> None:
        """Test a whitelist record is created for a new user"""

        app = MonitorUtility('sqlite:///:memory:')

        username = 'test_user'
        user_query = select(User).where(User.name == username)
        with DBConnection.session() as session:
            user_record = session.execute(user_query).scalars().first()
            self.assertIsNone(user_record)

        app.add(username, node='test_node.domain.com')
        with DBConnection.session() as session:
            user_record = session.execute(user_query).scalars().first()
            self.assertTrue(user_record)
            self.assertTrue(user_record.whitelists)

    def test_whitelist_extended(self) -> None:
        """Test whitelist records are extended if they already exist"""

        username = 'test_user'
        app = MonitorUtility('sqlite:///:memory:')

        # Create a whitelist record and then extend the existing record
        app.add(username, node='node1.domain.com', duration=timedelta(days=1))
        app.add(username, node='node1.domain.com', duration=timedelta(days=2))

        # Define SQL queries to select each of the records above
        query = select(Whitelist).join(User).join(Node) \
            .where(User.name == username) \
            .where(Node.hostname == 'node1.domain.com')

        with DBConnection.session() as session:
            whitelist_record = session.execute(query).scalars().first()
            duration = whitelist_record.end_time - whitelist_record.start_time
            self.assertEqual(2, duration.days)


class RemoveUserFromWhitelist(TestCase):
    """Test the removal of users from the whitelist"""

    def test_end_time_updated(self) -> None:
        """Test the whitelist end time for removed users is set to today"""

        username = 'test_user'
        node = 'node1.domain.com'
        app = MonitorUtility('sqlite:///:memory:')

        app.add(username, node=node, duration=timedelta(days=100))
        app.remove(username, node=node)

        query = select(Whitelist).join(User).where(User.name == username)
        with DBConnection.session() as session:
            whitelist_record = session.execute(query).scalars().first()
            self.assertEqual(date.today(), whitelist_record.end_time.date())
