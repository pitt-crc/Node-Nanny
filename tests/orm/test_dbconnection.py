from tempfile import NamedTemporaryFile
from unittest import TestCase

from node_nanny.orm import DBConnection


class DBConfiguration(TestCase):
    """Test the configuration of the DB connection via the ``configure`` method"""

    def test_connection_is_configured(self) -> None:
        """Test class attributes are set to reflect DB configuration"""

        # Use a temporary file to ensure we are using a unique URL
        with NamedTemporaryFile(suffix='.db') as temp:
            custom_url = f'sqlite:///{temp.name}'
            DBConnection.configure(custom_url)

        # Make sure each attribute is pointing to the new URL
        self.assertIsNotNone(DBConnection.connection)
        self.assertEqual(
            custom_url, DBConnection.connection.engine.url.render_as_string(),
            'Incorrect URL for `connection` attribute')

        self.assertIsNotNone(DBConnection.engine)
        self.assertEqual(
            custom_url, DBConnection.engine.url.render_as_string(),
            'Incorrect URL for `engine` attribute')

        self.assertIsNotNone(DBConnection.url)
        self.assertEqual(custom_url, DBConnection.url, 'Incorrect URL for `url` attribute')

        # Todo: I'm hopping on a call and will finish this after
        self.assertIsNotNone(DBConnection.session)
        self.assertEqual(False, DBConnection.session, 'Incorrect URL for `session` attribute')
