"""The ``app`` module defines the core application logic."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select

from .orm import User, Whitelist, DBConnection


class MonitorUtility:
    """Monitor system resource usage and manage currently running processes"""

    def __init__(self, url: str = 'sqlite:///monitor.db') -> None:
        """Configure the parent application

        Args:
            url: The URL of the application database
        """

        self.db = DBConnection()
        self.db.configure(url)

    def add(
            self,
            user: str,
            duration: Optional[timedelta] = None,
            node: Optional[str] = None,
            _global: bool = False
    ) -> None:
        """Whitelist a user to prevent their processes from being killed

        Args:
            user: The name of the user
            duration: How long to whitelist the user for
            node: The name of the node
            _global: Whitelist the user on all nodes
        """

        if node is None and not _global:
            raise ValueError('Must either specify a node name or set global to True.')

        if duration:
            termination = datetime.now() + duration

        else:
            termination = None

        with self.db.session() as session:
            # Create a record for the user if it does not already exist
            user_query = select(User).where(User.name == user)
            user_record = session.execute(user_query).scalars().first()
            if user_record is None:
                user_record = User(name=user)

            # Add a whitelist to the user record
            user_record.whitelists.append(
                Whitelist(
                    node=node,
                    termination=termination,
                    global_whitelist=_global
                )
            )

            session.add(user_record)
            session.commit()
