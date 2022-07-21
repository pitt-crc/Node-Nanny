"""Tests for the ORM ``Node`` class."""

import string
from unittest import TestCase

from node_nanny.orm import Node


class HostnameValidation(TestCase):
    """Test value validation for the ``hostname`` column"""

    @staticmethod
    def test_valid_hostname():
        """Test no error is raised for a valid hostname"""

        Node(hostname='node1')

    @staticmethod
    def test_period_is_allowed():
        """Test periods are allowed in hostnames"""

        Node(hostname='node1.domain.com')

    def test_value_is_assigned(self) -> None:
        """Test the validated value is assigned to the table instance"""

        hostname = 'node1'
        node = Node(hostname=hostname)
        self.assertEqual(hostname, node.hostname)

    def test_empty_name(self):
        """Test for a ``ValueError`` when hostname is an empty string"""

        with self.assertRaises(ValueError):
            Node(hostname='')

    def test_special_characters(self):
        """Test for a ``ValueError`` when hostname has special characters"""

        for char in r'\/:*?“<>|':
            with self.assertRaises(ValueError, msg=f'No error raised for character "{char}"'):
                Node(hostname=char)

    def test_hostname_with_whitespace(self):
        """Test for a ``ValueError`` when hostname has whitespace characters"""

        for char in string.whitespace:
            with self.assertRaises(ValueError, msg=f'No error raised for character "{char}"'):
                Node(hostname=char)
