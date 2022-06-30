"""Tests for the ``MonitorUtility`` class."""

from unittest import TestCase

from node_nanny.app import MonitorUtility


class AddUserToWhitelist(TestCase):
    """Test the addition of users to the whitelist"""

    def test_error_on_missing_node(self) -> None:
        """Test for value error on missing node name when global is False"""

        app = MonitorUtility('sqlite:///:memory:')
        with self.assertRaises(ValueError):
            app.add('test_user', node=None, _global=False)
