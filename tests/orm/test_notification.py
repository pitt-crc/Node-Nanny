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
