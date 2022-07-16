"""Tests for the ORM ``Notification`` class."""

from unittest import TestCase

from node_nanny.orm import Notification


class PercentageValidation(TestCase):
    """Test value validation for the ``percentage`` column"""

    def test_value_is_assigned(self) -> None:
        """Test the validated value is assigned to the table instance"""

        percentage = 50
        notification = Notification(percentage=percentage)
        self.assertEqual(percentage, notification.percentage)

    def test_error_on_out_of_range(self) -> None:
        """Check for a ``ValueError`` when percentage is not between 0 and 100"""

        with self.assertRaises(ValueError):
            Notification(percentage=-1)

        with self.assertRaises(ValueError):
            Notification(percentage=101)


class LimitValidation(TestCase):
    """Test value validation for the ``limit`` column"""

    def test_zero_allowed(self):
        """Test zero is an allowed value"""

        notification = Notification(limit=0)
        self.assertEqual(0, notification.limit)

    def test_value_is_assigned(self) -> None:
        """Test the validated value is assigned to the table instance"""

        limit = 50
        notification = Notification(limit=limit)
        self.assertEqual(limit, notification.limit)

    def test_error_if_negative(self) -> None:
        """Check for a ``ValueError`` when limit is less than zero"""

        with self.assertRaises(ValueError):
            Notification(limit=-1)


class MemoryValidation(TestCase):
    """Test value validation for the ``memory`` column"""

    def test_zero_allowed(self):
        """Test zero is an allowed value"""

        notification = Notification(memory=0)
        self.assertEqual(0, notification.memory)

    def test_value_is_assigned(self) -> None:
        """Test the validated value is assigned to the table instance"""

        memory = 50
        notification = Notification(memory=memory)
        self.assertEqual(memory, notification.memory)

    def test_error_if_negative(self) -> None:
        """Check for a ``ValueError`` when limit is less than zero"""

        with self.assertRaises(ValueError):
            Notification(memory=-1)
