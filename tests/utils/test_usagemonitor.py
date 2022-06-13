"""Tests for the fetching of system usage information by the ``UsageMonitor``
class.
"""

import os
from unittest import TestCase

import psutil
from pandas.api.types import is_float_dtype

from node_nanny.utils import UsageMonitor


class CurrentUsage(TestCase):
    """Test the fetching of system usage information for all running processes"""

    @classmethod
    def setUpClass(cls) -> None:
        """Fetch the current system usage data"""

        cls.usage_data = UsageMonitor.current_usage()

    def test_index_by_user_pid(self) -> None:
        """Test the returned dataframe is indexed by username and PID"""

        self.assertEqual(['USER', 'PID'], self.usage_data.index.names)

    def test_data_includes_cpu(self) -> None:
        """Test the returned data includes CPU information"""

        self.assertIn('CPU', self.usage_data.columns)
        self.assertTrue(is_float_dtype(self.usage_data.MEM.dtype), 'CPU column is not a float')

    def test_data_includes_mem(self) -> None:
        """Test the returned data includes memory information"""

        self.assertIn('MEM', self.usage_data.columns)
        self.assertTrue(is_float_dtype(self.usage_data.MEM.dtype), 'CPU column is not a float')


class UserUsage(TestCase):
    """Test the fetching of system usage information for a single user"""

    @classmethod
    def setUpClass(cls) -> None:
        """Make sure the test sure is not running as the user ``root``

        Username ``root`` is treated as an explicit escape.
        Running as ``root`` may invalidate that test.
        """

        if os.getlogin() == 'root':
            raise RuntimeError('DO not run the test suite as root.')

    def test_error_on_invalid_user(self) -> None:
        """Test a ``ValueError`` is raised when passed a username with no running processes"""

        with self.assertRaises(ValueError):
            UsageMonitor.user_usage('fake_username')

    def test_indexed_by_pid(self) -> None:
        """Test the returned dataframe is indexed by the process id"""

        user_usage = UsageMonitor.user_usage('root')
        self.assertEqual(['PID'], user_usage.index.names)

    def test_returned_data_matches_user(self) -> None:
        """Test the returned user data matches the requested user"""

        login_user = os.getlogin()
        for test_user in ('root', login_user):
            user_usage = UsageMonitor.user_usage(test_user)
            test_pid = user_usage.index[0]

            self.assertEqual(test_user, psutil.Process(test_pid).username(), f'PID {test_pid} does not match user {test_user}')
