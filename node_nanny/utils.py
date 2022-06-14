from pandas import DataFrame, read_sql
from sqlalchemy import select

from node_nanny.orm import Notification, User, DAL


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

        query = select(Notification).join(User).where(User.name == self._username)
        return read_sql(query, DAL.engine)

    def notify(self, node: str, usage: DataFrame) -> None:
        """Notify the user their running processes have been killed

        Args:
            node: Hostname of node their processes were running on
            usage: System information for the killed processes
        """

        raise NotImplementedError
