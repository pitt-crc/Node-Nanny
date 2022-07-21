"""Tests for the ORM ``Whitelist`` table."""

from unittest import TestCase

from node_nanny.orm import Whitelist


class NullableColumns(TestCase):
    """Test columns that need to be nullable are nullable"""

    def test_start_end_times_required(self) -> None:
        """Values for the ``start_time`` and ``end_time`` columns are not nullable"""

        self.assertFalse(Whitelist.start_time.nullable)
        self.assertFalse(Whitelist.end_time.nullable)
