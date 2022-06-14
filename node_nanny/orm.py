"""Object relational mapper for dealing with the application database."""

from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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
    node = Column(String, nullable=False)
    termination = Column(DateTime)

    user = relationship('User', back_populates='whitelists')


class DataAccessLayer:
    """Data access layer for establishing connections with the application database"""

    connection = None
    engine = None
    conn_string = None
    metadata = Base.metadata
    session = None

    def db_init(self, conn_string: str) -> None:
        """Update the connection information for the underlying database

        Changes made here will affect the entire running application

        Args:
            conn_string: Connection information for the application database
        """

        self.engine = create_engine(conn_string or self.conn_string)
        self.metadata.create_all(self.engine)
        self.connection = self.engine.connect()
        self.session = sessionmaker(self.engine)


DAL = DataAccessLayer()
