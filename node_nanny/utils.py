"""Utilities for fetching and interacting with system data."""

import psutil
from pandas import DataFrame


class UsageMonitor:
    """Fetch current system usage information"""

    @staticmethod
    def _get_process_data(pid: int) -> dict:
        """Return the current system usage for a single running processes

        Args:
            pid: The ID of a currently running process

        Returns:
            A dictionary with system usage information for the given proces ID

        Raises:
            psutil.NoSuchProcess: If the given process ID can not be found
        """

        process = psutil.Process(pid)
        return {
            'PID': pid,
            'PNAME': process.name(),
            'USER': process.username(),
            'STATUS': process.status(),
            'CPU': process.cpu_percent(),
            'MEM': process.memory_percent()
        }

    @classmethod
    def current_usage(cls) -> DataFrame:
        """Return the current system usage for all running processes

        Returns:
            A ``DataFrame`` of currently running processes
        """

        data = []
        for process in psutil.pids():
            try:
                data.append(cls._get_process_data(process))

            # Some subprocesses may exit while fetching process info
            # Ignore test coverage since this error is pseudo-random
            except psutil.NoSuchProcess:  # pragma: no cover
                pass

        return DataFrame(data).set_index(['USER', 'PID'])

    @classmethod
    def user_usage(cls, username: str) -> DataFrame:
        """Return the current system usage for all processes tied to a given user

        Args:
            username: The name of the user to return usage for

        Returns:
            A ``DataFrame`` of running processes tied to the given user

        Raises:
            ValueError: If no running processes are found for the given user
        """

        try:
            return cls.current_usage().loc[username]

        except KeyError:
            raise ValueError(f'No running processes found for user {username}')
