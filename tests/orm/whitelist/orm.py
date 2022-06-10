"""Tests for the ORM ``Whitelist`` table."""

from unittest import TestCase

from node_nanny.orm import Whitelist


class NullableColumns(TestCase):
    """Test columns that need to be nullable are nullable"""

    def test_expiration_nullable(self):
        """Values for the ``termination`` column should be nullable"""

        self.assertTrue(Whitelist.termination.nullable)
