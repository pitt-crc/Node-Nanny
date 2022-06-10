from unittest import TestCase

from node_nanny.orm import Whitelist


class WhitelistExpirationNullable(TestCase):

    def test_expiration_nullable(self):
        """Values for the ``termination`` column should be nullable"""

        self.assertTrue(Whitelist.termination.nullable)
