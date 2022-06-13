from unittest import TestCase

from node_nanny.utils import UsageMonitor


class UserUsage(TestCase):
    """Test the fetching of """

    def test_error_on_invalid_user(self) -> None:
        """Test a ``ValueError`` is raised when passed a username with no running processes"""

        with self.assertRaises(ValueError):
            UsageMonitor.user_usage('fake_username')
