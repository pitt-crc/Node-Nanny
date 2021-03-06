"""Test user notifications via the ``UserNotifier`` class."""

from datetime import datetime
from unittest import TestCase

import pandas as pd

from node_nanny.orm import DBConnection, Notification, User
from node_nanny.utils import UserNotifier


class GetNotificationHistory(TestCase):
    """Tests for the fetching of historical user notification data"""

    @classmethod
    def setUpClass(cls):
        """Establish a connection to a temporary testing database"""

        DBConnection.configure('sqlite:///:memory:')

    def test_empty_return_for_fake_user(self) -> None:
        """Returned dataframe should be empty if there have been no notifications"""

        notification_data = UserNotifier('fake_user_name').notification_history()
        self.assertTrue(notification_data.empty)

    @staticmethod
    def test_returns_data_from_db() -> None:
        """Test the returned dataframe matches data from the application database"""

        # Define dummy values to add into the database
        username = 'sam'
        data = dict(
            time=datetime(2015, 8, 12),
            memory=12,
            percentage=100,
            node='login0.domain.com'
        )

        # Create database records using the dummy data
        user = User(name=username)
        notification = Notification(**data, user=user, limit=80)
        with DBConnection.session() as session:
            session.add(user)
            session.add(notification)
            session.commit()

        # Ensure the returned dataframe matches the test data
        returned_df = UserNotifier(username).notification_history()
        expected_df = pd.DataFrame(data=[data])
        pd.testing.assert_frame_equal(expected_df, returned_df, check_like=True)
