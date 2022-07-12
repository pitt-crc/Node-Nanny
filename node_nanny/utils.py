"""Utilities for fetching and interacting with system data."""

from datetime import datetime
from email.message import EmailMessage
from smtplib import SMTP

import psutil
from pandas import DataFrame, read_sql
from sqlalchemy import select

from node_nanny.orm import Notification, User, DBConnection


class UserNotifier:
    """Handles the sending and tracking of user email notifications"""

    def __init__(self, username: str) -> None:
        """Manage email notifications for the given user

        Args:
            username: The name of the user to manage notifications for
        """

        self._username = username

    def get_user_email(self) -> str:
        """Return the email corresponding to the current user"""

        return self._username + '@pitt.edu'

    def notification_history(self) -> DataFrame:
        """Return a tabular summary of previous user notifications

        Returns:
            DataFrame with user notification history
        """

        query = select(
            Notification.node, Notification.time, Notification.memory, Notification.percentage
        ).join(User).where(User.name == self._username)

        return read_sql(query, DBConnection.engine)

    def notify(self, node: str, usage: DataFrame, limit: int) -> None:
        """Notify the user their running processes have been killed

        Args:
            node: Hostname of node their processes were running on
            usage: System information for the killed processes
            limit: The memory limit used to trigger the notification
        """

        # Update the notification table in the database
        with DBConnection.session() as session:
            # If the user has not been notified before, create a new User record
            user_query = select(User).where(User.name == self._username)
            user = session.execute(user_query).scalars().first()
            if user is None:
                user = User(name=self._username)

            notification = Notification(
                user=user,
                node=node,
                time=datetime.now(),
                percentage=usage.MEM.sum(),
                limit=limit
            )

            session.add(user)
            session.add(notification)
            session.commit()

        message = EmailMessage()
        message.set_content("This is email text")
        message["Subject"] = "Email subject"
        message["From"] = "from_user@dummy.domain.edu"
        message["To"] = self.get_user_email()

        with SMTP("localhost") as smtp:
            smtp.send_message(message)


class SystemUsage:
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
