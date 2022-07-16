"""Object relational mapper for dealing with the application database."""

import string

from sqlalchemy import Boolean, Column, Integer, String, DateTime, create_engine, ForeignKey, MetaData
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, validates

Base = declarative_base()


class User(Base):
    """User account data

    Table Fields:
      - id      (Integer): Primary key for this table
      - username (String): Unique account name

    Relationships:
      - notifications (Notifications): One to many
      - whitelists        (Whitelist): One to many
    """

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    notifications = relationship('Notification', back_populates='user', cascade="all,delete")
    whitelists = relationship('Whitelist', back_populates='user', cascade="all,delete")

    @validates('name')
    def validate_name(self, key: str, value: str) -> str:
        """Validate the given value is a valid username

        Args:
            key: The name of the column being validated
            value: The value being validated

        Returns:
            The valid value

        Raises:
            ValueError: If the value is not valid
        """

        if not value:
            raise ValueError(f'Value for {key} must be a non-empty string')

        has_whitespace = any([c in value for c in string.whitespace])
        if has_whitespace:
            raise ValueError(f'Value for {key} cannot contain whitespace')

        return value


class Notification(Base):
    """Record of user notification history

    Table Fields:
      - id         (Integer): Primary key for this table
      - time      (Datetime): Date and time of the notification
      - memory     (Integer): Total memory usage
      - percentage (Integer): Memory usage as a percentage of system memory
      - user_id    (Integer): Foreign key for the ``User.id`` table
      - node        (String): The name of the node
      - limit      (Integer): The memory limit that triggered the notification

    Relationships:
      - user (User): Many to one
    """

    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    time = Column(DateTime, nullable=False)
    memory = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    node = Column(String, nullable=False)
    limit = Column(Integer, nullable=False)

    user = relationship('User', back_populates='notifications')

    @validates('percentage')
    def _validate_percent_notified(self, key: str, value: int) -> int:
        """Validate the given value is between 0 and 100 (inclusive)

        Args:
            key: The name of the column being validated
            value: The value being validated

        Returns:
            The valid value

        Raises:
            ValueError: If the value is not valid
        """

        if 0 <= value <= 100:
            return value

        raise ValueError(f'Value for {key} column must be between 0 and 100 (got {value}).')


class Whitelist(Base):
    """Whitelist of users whose jobs should not be killed

    Table Fields:
      - id           (Integer): Primary key for this table
      - node          (String): The name of the node
      - termination (Datetime): When the whitelist entry expires
      - user_id      (Integer): Foreign key for the ``User.id`` table

    Relationships:
      - user (User): Many to one
    """

    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    node = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    global_whitelist = Column(Boolean, default=False, nullable=False)

    user = relationship('User', back_populates='whitelists')


class DBConnection:
    """A configurable connection to the application database"""

    connection: Connection = None
    engine: Engine = None
    url: str = None
    metadata: MetaData = Base.metadata
    session: sessionmaker = None

    @classmethod
    def configure(cls, url: str) -> None:
        """Update the connection information for the underlying database

        Changes made here will affect the entire running application

        Args:
            url: URL information for the application database
        """

        cls.engine = create_engine(url or cls.url)
        cls.metadata.create_all(cls.engine)
        cls.connection = cls.engine.connect()
        cls.session = sessionmaker(cls.engine)
