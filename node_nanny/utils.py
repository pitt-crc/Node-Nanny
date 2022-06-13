"""Utilities for fetching and interacting with system data."""

from pandas import DataFrame


class UsageMonitor:
    """Fetch current system usage information"""

    @staticmethod
    def current_usage() -> DataFrame:
        """Return the current system usage for all running processes

        Returns:
            A ``DataFrame`` of currently running processes
        """

        raise NotImplementedError

    def user_usage(self, username: str) -> DataFrame:
        """Return the current system usage for all processes tied to a given user

        Args:
            username: The name of the user to return usage for

        Returns:
            A ``DataFrame`` of running processes tied to the given user
        """

        raise NotImplementedError
