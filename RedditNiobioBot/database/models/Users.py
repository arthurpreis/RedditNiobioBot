from . import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    points = Column(Integer, default=0)

    def __repr__(self):
        return "<User(id='%s', username='%s')>" % (self.id,
                                                   self.username)
