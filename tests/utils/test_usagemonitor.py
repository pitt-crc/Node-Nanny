"""Tests for the fetching of system usage information by the ``UsageMonitor``
class.
"""

from unittest import TestCase

from node_nanny.utils import UsageMonitor


class UserUsage(TestCase):
    """Test the fetching of system usage information for a single user"""

    def test_error_on_invalid_user(self) -> None:
        """Test a ``ValueError`` is raised when passed a username with no running processes"""

        with self.assertRaises(ValueError):
            UsageMonitor.user_usage('fake_username')
