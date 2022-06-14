"""Test user notifications via the ``UserNotifier`` class."""

from unittest import TestCase

from node_nanny.orm import DAL
from node_nanny.utils import UserNotifier


class GetNotificationHistory(TestCase):
    """Tests for the fetching of historical user notification data"""

    @classmethod
    def setUpClass(cls):
        """Establish a connection to a temporary testing database"""

        DAL.db_init('sqlite:///:memory:')

    def test_empty_return_for_fake_user(self) -> None:
        """Returned dataframe should be empty if there have been no notifications"""

        notification_data = UserNotifier('fake_user_name').notification_history()
        self.assertTrue(notification_data.empty)
