"""The ``app`` module defines the core application logic."""

import os
import signal

from .utils import SystemUsage


class MonitorUtility:
    """Monitor system resource usage and manage currently running processes"""

    @staticmethod
    def kill(user):
        """Terminate all processes launched by a given user"""

        user_processes = SystemUsage.user_usage(user)
        for pid in user_processes.index:
            try:
                os.kill(pid, signal.SIGKILL)

            except ProcessLookupError:
                pass
