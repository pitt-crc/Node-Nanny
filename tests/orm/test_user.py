"""Tests for the ORM ``User`` class."""

from unittest import TestCase

from node_nanny.orm import User


class NameValidation(TestCase):
    """Test value validation for the ``name`` column"""

    @staticmethod
    def test_valid_username():
        """Test no error is raised for a valid username"""

        User(name='username')

    def test_value_is_assigned(self) -> None:
        """Test the validated value is assigned to the table instance"""

        name = 'username'
        user = User(name=name)
        self.assertEqual(name, user.name)

    def test_empty_name(self):
        """Test for a ``ValueError`` when name is an empty string"""

        with self.assertRaises(ValueError):
            User(name='')

    def test_username_with_space(self):
        """Test for a ``ValueError`` when name has a space"""

        with self.assertRaises(ValueError):
            User(name=' ')

        with self.assertRaises(ValueError):
            User(name='user name')

    def test_username_with_whitespace(self):
        """Test for a ``ValueError`` when name has whitespace characters"""

        with self.assertRaises(ValueError):
            User(name='\n')

        with self.assertRaises(ValueError):
            User(name='\t')

        with self.assertRaises(ValueError):
            User(name='\r')
