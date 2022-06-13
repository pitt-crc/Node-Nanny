"""Object relational mapper for dealing with the application database."""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


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

    Relationships:
      - user (User): Many to one
    """

    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, nullable=False)
    memory = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)

    user = relationship('User', back_populates='notifications')


class Whitelist(Base):
    """Whitelist of users whose jobs should not be killed

    Table Fields:
      - id           (Integer): Primary key for this table
      - node          (String): The name of the node
      - termination (Datetime): When the whitelist entry expires

    Relationships:
      - user (User): Many to one
    """

    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    node = Column(String, nullable=False)
    termination = Column(DateTime)

    user = relationship('User', back_populates='whitelists')
