"""The ``app`` module defines the core application logic."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select

from .orm import User, Whitelist, DBConnection


class MonitorUtility:
    """Monitor system resource usage and manage currently running processes"""

    def remove(self, user: str, node: Optional[str], _global: bool = False) -> None:
        """Remove a user from the application whitelist

        Args:
            user: The name of the user
            node: The name of the node
            _global: Whitelist the user on all nodes
        """

        if node is None and not _global:
            raise ValueError('Must either specify a node name or set global to True.')

        query = select(Whitelist).join(User).where(User.name == user)
        if node:
            query = query.where(Whitelist.node == node)

        now = datetime.now()
        with DBConnection.session() as session:
            for record in session.execute(query).scalars().all():
                record.end_time = now
                session.add(record)

            session.commit()
