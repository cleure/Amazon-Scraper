
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.products import *
from app.models.config import *

class SessionManager(object):
    def __init__(self, path):
        self.engine = sqlalchemy.create_engine(path, echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
