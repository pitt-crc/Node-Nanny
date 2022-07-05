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

        DBConnection.configure(url)

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

        now = datetime.now()
        with DBConnection.session() as session:
            # Create a record for the user if it does not already exist
            user_query = select(User).where(User.name == user)
            user_record = session.execute(user_query).scalars().first()
            if user_record is None:
                user_record = User(name=user)

            # Create a whitelist record if it doesn't already exist
            whitelist_query = select(Whitelist).join(User) \
                .where(User.id == user.id) \
                .where(Whitelist.start_time < now) \
                .where(Whitelist.end_time > now)

            whitelist_record = session.execute(whitelist_query).scalars().first()
            if whitelist_record is None:
                whitelist_record = Whitelist(
                    node=node,
                    start_time=now,
                    global_whitelist=_global
                )

            # Add a whitelist to the user record
            whitelist_record.end_time = now + duration
            user_record.whitelists.append(whitelist_record)
            session.add(user_record)
            session.commit()
