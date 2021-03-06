"""Object relational mapper for dealing with the application database."""

from typing import Callable

from sqlalchemy import Boolean, Column, Integer, String, DateTime, create_engine, ForeignKey, MetaData
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session

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
    session: Callable[[], Session] = None

    @classmethod
    def configure(cls, url: str) -> None:
        """Update the connection information for the underlying database

        Changes made here will affect the entire running application

        Args:
            url: URL information for the application database
        """

        cls.url = url
        cls.engine = create_engine(cls.url)
        cls.metadata.create_all(cls.engine)
        cls.connection = cls.engine.connect()
        cls.session = sessionmaker(cls.engine)
