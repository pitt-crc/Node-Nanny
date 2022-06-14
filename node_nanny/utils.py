from datetime import datetime
from email.message import EmailMessage
from smtplib import SMTP

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

        # Update the notification table in the database
        with DAL.session() as session:
            # If the user has not been notified before, create a new User record
            user_query = select(User).where(User.name == self._username)
            user = session.execute(user_query).scalars().first()
            if user is None:
                user = User(name=self._username)

            notification = Notification(
                user=user,
                node=node,
                time=datetime.now(),
                percentage=usage.MEM.sum()
            )

            session.add(user)
            session.add(notification)
            session.commit()

        msg = EmailMessage()
        msg.set_content("This is email text")
        msg["Subject"] = "Email subject"
        msg["From"] = "from_user@dummy.domain.edu"
        msg["To"] = "to_user@dummy.domain.edu"

        with SMTP("localhost") as smtp:
            smtp.send_message(msg)
