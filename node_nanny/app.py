"""The ``app`` module defines the core application logic."""

import os
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import select

from .orm import User, Whitelist, DBConnection
from .utils import SystemUsage


class MonitorUtility:
    """Monitor system resource usage and manage currently running processes"""

    def __init__(self, url: Optional[str] = None) -> None:
        """Configure the parent application

        Args:
            url: Optionally use a custom application database
        """

        db_path = Path(__file__).resolve().parent / 'monitor.db'
        db_url = url or f'sqlite:///{db_path}'

        self._db = DBConnection
        self._db.configure(db_url)

    def whitelist(self) -> None:
        """Print out the current user whitelist including user and node names."""

        query = select([
            User.name.label('User'),
            Whitelist.global_whitelist.label('Global'),
            Whitelist.start_time.label('Start'),
            Whitelist.end_time.label('End')
        ]) \
            .select_from(User).join(Whitelist) \
            .where(Whitelist.end_time > datetime.now())

        # Execute the query with pandas and rely on the default DataFrame string representation
        whitelist_df = pd.read_sql(query, con=self._db.engine).set_index(['User', 'Global'])
        whitelist_df.Start = whitelist_df.Start.dt.round('1s')
        whitelist_df.End = whitelist_df.Start.dt.round('1s')

        print(whitelist_df)

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
        one_hundred_years_in_days = 36_500
        duration = duration or timedelta(days=one_hundred_years_in_days)

        with self._db.session() as session:
            # Create a record for the user if it doesn't not already exist
            user_query = select(User).where(User.name == user)
            user_record = session.execute(user_query).scalars().first()
            if user_record is None:
                user_record = User(name=user)

            # Create a whitelist record if it doesn't already exist
            whitelist_query = select(Whitelist).join(User) \
                .where(User.id == User.id) \
                .where(Whitelist.node == node) \
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
        with self._db.session() as session:
            for record in session.execute(query).scalars().all():
                record.end_time = now
                session.add(record)

            session.commit()

    @staticmethod
    def kill(user: str) -> None:
        """Terminate all processes launched by a given user"""

        user_processes = SystemUsage.user_usage(user)
        for pid in user_processes.index:
            try:
                os.kill(pid, signal.SIGKILL)

            except ProcessLookupError:
                pass
