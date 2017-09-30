from . import Base
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    parent_base36_id = Column(String(8), nullable=False)
    base36_id = Column(String(8), unique=True, nullable=False)
    from_user_id = Column(Integer,
                          ForeignKey('users.id'),
                          nullable=False)
    to_user_id = Column(Integer,
                        ForeignKey('users.id'),
                        nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    status = Column(String(10), default='TO_REPLY')

    from_user = relationship("User", foreign_keys='Comment.from_user_id')
    to_user = relationship("User", foreign_keys='Comment.to_user_id')

    def __repr__(self):
        return "<Comment(id='%s', base36_id='%s'" % (self.id,
                                                     self.base36_id)
