from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .Comments import Comment
from .Users import User