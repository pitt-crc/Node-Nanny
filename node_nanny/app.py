"""The ``app`` module defines the core application logic."""

import os
import platform
import signal
from copy import copy
from datetime import datetime, timedelta
from time import sleep
from typing import Optional, List

import pandas as pd
from sqlalchemy import select, or_

from .orm import User, Whitelist, DBConnection
from .utils import SystemUsage, UserNotifier


class MonitorUtility:
    """Monitor system resource usage and manage currently running processes"""

    def __init__(self, url: str = 'sqlite:///monitor.db') -> None:
        """Configure the parent application

        Args:
            url: The URL of the application database
        """

        self._db = DBConnection
        self._db.configure(url)
        self._hostname = platform.node()

    def scan(self, frequency: int, memory: int, wait: int = 0, min_usage: int = 0) -> None:
        """Scan for and kill and jobs running over a memory usage limit

        Jobs are not killed for whitelisted users.

        Args:
            frequency: How frequently to poll system usage in seconds
            memory: Start killing jobs when total memory usage exceeds this percentage
            wait: Allow system usage to exceed `memory` for a number of seconds before killing jobs
            min_usage: Never kill users using below the given percentage of memory
        """

        wait_time = 0
        while True:
            # Get the current memory usage (total and per user)
            node_usage = SystemUsage().current_usage()
            user_memory_usage = node_usage.MEM.groupby(level=0).sum()
            total_usage = user_memory_usage.sum()

            # If memory usage exceeds the ``memory`` argument, start killing users
            if total_usage > memory and wait_time > wait:
                users_to_kill = self._get_users_to_kill(min_usage, user_memory_usage)
                self._restore_system_memory(users_to_kill, memory)
                wait_time = 0

            elif total_usage < memory:
                wait_time = 0

            sleep(frequency)
            wait_time += frequency

    def _get_users_to_kill(self, min_usage: int, user_memory: pd.Series) -> List[str]:
        """Determine which users jobs should be killed

        Args:
            min_usage: Don't include usernames using less than the given memory percentage
            user_memory: Pandas series of memory usage percentage indexed by username

        Returns:
            A list of usernames sorted by increasing memory usage
        """

        # Query returns all users that are whitelisted globally or on the current hostname
        whitelisted_users_query = select(User.name) \
            .select_from(User).join(Whitelist) \
            .where(Whitelist.end_time > datetime.now()) \
            .where(or_(Whitelist.node == self._hostname, Whitelist.global_whitelist))

        # Identify what users are above the threshold
        min_usage_users = user_memory.drop(user_memory <= min_usage)
        user_list = min_usage_users.sort_values(ascending=True).index

        # Drop any whitelisted usernames
        with self._db.session() as session:
            whitelisted_users = session.execute(whitelisted_users_query).scalars().all()
            users_to_kill = user_list.drop(whitelisted_users).to_list()

        return users_to_kill

    def _restore_system_memory(self, usernames: List[str], memory_limit: int) -> None:
        """Terminate running user processes until memory usage drops below a given threshold

        Args:
            usernames: List of usernames to terminate jobs for
            memory_limit: Threshold to stop killing jobs at
        """

        usernames = copy(usernames)
        node_usage = SystemUsage().current_usage()
        total_usage = node_usage.MEM.sum()

        # Kill users until memory usage drops below threshold
        while usernames and total_usage > memory_limit:
            username = usernames.pop()
            self.kill(username)
            UserNotifier(username).notify(self._hostname, node_usage.loc[username], memory_limit)

            total_usage = SystemUsage().current_usage().MEM.sum()

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
